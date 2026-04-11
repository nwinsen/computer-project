"""Monitoring endpoints: health checks and frontend error tracking.

TODO:
1. Import FastAPI APIRouter, Request, BaseModel from pydantic, Optional from typing
2. Import get_logger from app.core.logging
3. Create router = APIRouter()
4. Create logger = get_logger(__name__)
5. Create FrontendErrorPayload Pydantic model with fields:
   - message: str (required)
   - source: Optional[str] = None
   - lineno: Optional[int] = None
   - colno: Optional[int] = None
   - stack: Optional[str] = None
   - url: Optional[str] = None
   - user_agent: Optional[str] = None
6. Create GET /health endpoint that returns {"status": "ok", "service": "lolapp-backend"}
7. Create POST /monitoring/frontend-error endpoint that:
   - Accepts FrontendErrorPayload
   - Takes Request parameter to get client info
   - Logs as error with extra={event, message, source, lineno, colno, stack, url, user_agent, client_ip}
   - Returns {"received": True}

See docs/observability.md for full implementation details.
"""

from fastapi import APIRouter

# TODO: Implement according to docs/observability.md
