import logging
import os

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app import models  # noqa: F401
from app.routers.v1 import auth, budgets, categories, invites, members, transactions
from app.core.config import settings
from app.core.exceptions import AppError

logger = logging.getLogger("app")

app = FastAPI(
    title="CoBudget API",
    description="API для обліку особистих і спільних фінансів",
    version="0.1.0",
)

app.include_router(auth.router)
app.include_router(budgets.router)
app.include_router(categories.router)
app.include_router(transactions.router)
app.include_router(invites.budget_invites_router)
app.include_router(invites.invites_router)
app.include_router(members.router)


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(status_code=exc.status_code, content={"error": {"code": exc.code, "message": exc.message}})


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception while processing %s %s", request.method, request.url)
    return JSONResponse(
        status_code=500,
        content={"error": {"code": "INTERNAL_ERROR", "message": "Внутрішня помилка сервера"}},
    )


@app.get("/health")
def health_check():
    return {"status": "ok", "environment": settings.ENVIRONMENT}


if not os.environ.get("VERCEL"):
    app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")