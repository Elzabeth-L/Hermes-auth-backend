from app.core.config import settings
from app.core.exceptions import ConflictException, UnauthorizedException
from app.models.user import UserInDB
from app.repositories.user_repository import UserRepository
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RegisterResponse,
)
from app.utils.jwt import create_access_token
from app.utils.security import hash_password, verify_password


class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def register_customer(self, payload: RegisterRequest) -> RegisterResponse:
        existing_user = await self.user_repository.find_by_email(payload.email)
        if existing_user:
            raise ConflictException("Email is already registered.")

        user = UserInDB(
            name=payload.name,
            email=payload.email,
            password_hash=hash_password(payload.password),
            role="customer",
        )
        await self.user_repository.create_user(user)
        return RegisterResponse(
            message="Registration successful. Please login.",
            redirect_to="/login",
        )

    async def login(self, payload: LoginRequest) -> LoginResponse:
        if self._is_admin_credentials(payload):
            return self._create_admin_login_response()

        user = await self.user_repository.find_by_email(payload.email)
        if not user or not verify_password(payload.password, user["password_hash"]):
            raise UnauthorizedException("Invalid email or password.")

        await self.user_repository.update_last_seen(user["_id"])
        token = create_access_token(
            subject=str(user["_id"]),
            email=user["email"],
            role="customer",
        )
        return LoginResponse(
            access_token=token,
            token_type="bearer",
            role="customer",
            redirect_to="/customer-dashboard",
        )

    def _is_admin_credentials(self, payload: LoginRequest) -> bool:
        admin_email = settings.admin_email.strip().lower()
        return payload.email == admin_email and payload.password == settings.admin_password

    def _create_admin_login_response(self) -> LoginResponse:
        admin_email = settings.admin_email.strip().lower()
        token = create_access_token(
            subject="admin",
            email=admin_email,
            role="admin",
        )
        return LoginResponse(
            access_token=token,
            token_type="bearer",
            role="admin",
            redirect_to="/admin-dashboard",
        )
