from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.auth import router as auth_router
from app.core.config import settings
from app.database.mongodb import close_mongo_connection, connect_to_mongo
from app.middleware.error_handler import register_exception_handlers


def create_app() -> FastAPI:
    app = FastAPI(
        title="Hermes Authentication Service",
        description="Authentication APIs for the Hermes insurance platform.",
        version="1.0.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)
    app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])

    @app.get("/health", tags=["Health"])
    async def health_check() -> dict[str, str]:
        return {"status": "ok", "service": "hermes-auth"}

    app.add_event_handler("startup", connect_to_mongo)
    app.add_event_handler("shutdown", close_mongo_connection)
    return app


app = create_app()
