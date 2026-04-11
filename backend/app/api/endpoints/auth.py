from fastapi import APIRouter, Response, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select

from app.db.session import SessionDep
from app import models, schemas, utils, crud, config

router = APIRouter()


@router.get("/user/verify-token")
async def verify_token(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    token = auth_header.split(" ")[1]
    utils.crypt.decode_access_token(token)
    return {"message": "Token is valid"}


@router.post("/user/login")
async def auth_login(user: schemas.UserIn, db: SessionDep, response: Response):
    result = crud.user.get_by_email(db, user.email)
    if not result:
        raise HTTPException(status_code=400, detail="Email not found")
    verified = utils.verify_password(user.password, result["hashed_password"])
    if not verified:
        raise HTTPException(status_code=400, detail="Incorrect password")
    access_token_expires = config.variables.ACCESS_TOKEN_EXPIRY
    refresh_token_expires = config.variables.REFRESH_TOKEN_EXPIRY
    response.set_cookie(
        key="refresh_token",
        value=utils.crypt.create_refresh_token(result["email"], refresh_token_expires),
        httponly=True,
        max_age=refresh_token_expires,
        expires=refresh_token_expires,
        path="/",
    )
    return {
        "access_token": utils.crypt.create_access_token(
            result["email"], access_token_expires
        )
    }


@router.post("/user/signup", response_model=schemas.UserOut)
async def auth_signup(user: schemas.UserIn, db: SessionDep):
    if (
        db.exec(select(models.User).where(models.User.email == user.email.lower()))
        .scalars()
        .all()
    ):
        raise HTTPException(status_code=400, detail="Email already exists.")
    user = crud.user.create_user(db, user)
    # redirect to account successfully created, login now.
    return user


@router.get("/user/refresh")
async def refresh_token(request: Request):
    token = request.cookies.get("refresh_token")
    user_email = utils.crypt.decode_refresh_token(token)
    if user_email:
        access_token_expires = config.variables.ACCESS_TOKEN_EXPIRY
        return {
            "access_token": utils.crypt.create_access_token(
                user_email, access_token_expires
            )
        }
    else:
        raise HTTPException(status_code=403, detail="Invalid token")


@router.get("/user/logout")
async def logout(response: Response):
    response.delete_cookie(key="refresh_token", path="/")
    return {"message": "Successfully logged out"}


# TODO: 2 factor auth, forgot password, logout, jwt functionality
