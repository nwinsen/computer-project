# riot endpoints
from fastapi import APIRouter, Path, Response
from app.db.session import SessionDep
from app.config.vars import variables
from sqlalchemy import select
from app import models, services, schemas
from datetime import datetime
from typing import List


router = APIRouter()


@router.get("/riot/user/{puuid}/matches", response_model=List)
async def get_match_history(
    start_time: int | None = None,
    puuid: str = Path(...),
):
    match_history = services.get_ranked_match_history(puuid, start_time)
    # need to get riot id for each participant
    return match_history
    # query riot for each participant's name


# get request
@router.get(
    "/riot/user/{username}/{tagline}",
    response_model=schemas.RiotAccount | dict,
)
async def get_account_data_on_page_load(
    db: SessionDep,
    username: str = Path(min_length=5, max_length=16),
    tagline: str = Path(min_length=3, max_length=5),
):
    try:
        user = services.populate_user(username, tagline)
        if user is None:
            return {}
        return schemas.RiotAccount.model_validate(user)
    except Exception as e:
        return {}


@router.get("/riot/user/{puuid}/match/{match_id}", response_model=dict)
async def get_match_information(
    response: Response,
    db: SessionDep,
    match_id: str = Path(...),
    puuid: str = Path(...),
):
    # need to get riot id for each participant
    stmt = select(models.Match).where(models.Match.match_id == match_id)
    result = db.exec(stmt)
    match = result.scalar_one_or_none()
    if match:
        match = schemas.Match.model_validate(match)
        stmt = select(models.Player).where(
            models.Player.puuid == puuid, models.Player.match_id == match_id
        )
        result = db.exec(stmt)
        current_player = result.scalar_one_or_none()
        current_player = schemas.Player.model_validate(current_player)
        stmt = select(models.Stat).where(models.Stat.player_id == current_player.id)
        result = db.exec(stmt)
        current_player_stats = result.scalar_one_or_none()
        ret_dict = {
            "match": match,
            "player": current_player,
            "stats": current_player_stats,
        }
        response.headers["Cache-Control"] = "public, max-age=86400"
        response.headers["ETag"] = f"{match_id}-{puuid}"
        return ret_dict
    else:
        match_info = services.query_match_stats(match_id)
        if match_info is None:
            return {}
        match = services.create_game_from_matchdata(match_info)
        players = services.create_players_from_matchdata(match_info)
        db.add(match)
        db.add_all(players)
        db.commit()
        curr_player = None
        for player in players:
            stmt = select(models.Champion).where(
                models.Champion.champion_id == player.champion_id
            )
            result = db.exec(stmt)
            champion = result.scalar_one_or_none()
            if champion:
                if player.win == True:
                    champion.wins += 1
                else:
                    champion.losses += 1
                db.commit()
            else:
                if player.win == True:
                    db.add(
                        models.Champion(
                            champion_id=player.champion_id,
                            champion_name=player.champion_name,
                            wins=1,
                            losses=0,
                        )
                    )
                else:
                    db.add(
                        models.Champion(
                            champion_id=player.champion_id,
                            champion_name=player.champion_name,
                            wins=0,
                            losses=1,
                        )
                    )
                db.commit()
            if player.puuid == puuid:
                curr_player = player
        stats = services.create_stats_from_matchdata(players, match_info)
        db.add_all(stats)
        db.commit()
        db.refresh(match)
        for player in players:
            db.refresh(player)
        for stat in stats:
            db.refresh(stat)
        return_stat = None
        for stat in stats:
            if stat.player_id == curr_player.id:
                return_stat = stat
                break
    ret_dict = {"match": match, "player": curr_player, "stats": return_stat}
    response.headers["Cache-Control"] = "public, max-age=86400"
    response.headers["ETag"] = f"{match_id}-{puuid}"
    return ret_dict
    # query riot for each participant's name


@router.get("/riot/champions", response_model=list)
async def get_champions(db: SessionDep):
    stmt = select(models.Champion)
    result = db.exec(stmt)
    champions = result.scalars().all()
    return champions
