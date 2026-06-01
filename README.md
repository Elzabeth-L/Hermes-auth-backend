# Hermes Authentication Service

Backend-only FastAPI authentication service for the Hermes insurance platform. This service owns customer registration and one shared login endpoint for both customers and the configured admin account. It does not implement frontend screens, customer dashboards, admin dashboards, or dashboard business logic.

## Project Overview

Hermes Authentication Service provides JWT-based authentication APIs backed by MongoDB or Azure Cosmos DB using the Mongo API. Customer passwords are hashed with bcrypt and never returned in API responses.

Core capabilities:

- Customer registration with validation and unique normalized email storage
- Shared login that authenticates customers with bcrypt password verification
- Shared login that recognizes configured admin credentials and returns the admin redirect
- JWT access tokens containing `sub`, `email`, and `role`
- Clean architecture-style package layout

## Folder Structure

```text
app/
+-- main.py
+-- api/
|   +-- v1/
|       +-- auth.py
+-- core/
|   +-- config.py
|   +-- exceptions.py
+-- database/
|   +-- mongodb.py
+-- middleware/
|   +-- error_handler.py
+-- models/
|   +-- user.py
+-- repositories/
|   +-- user_repository.py
+-- schemas/
|   +-- auth.py
+-- services/
|   +-- auth_service.py
+-- utils/
    +-- jwt.py
    +-- security.py
```

## Local Setup Instructions

1. Create and activate a virtual environment.

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies.

```bash
pip install -r requirements.txt
```

3. Create a local `.env` file from `.env.example`.

```bash
cp .env.example .env
```

On Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

4. Update `.env` with your MongoDB or Azure Cosmos DB Mongo API URI and JWT secret.

5. Start the API.

```bash
uvicorn app.main:app --reload
```

The API will be available at:

- Swagger UI: `http://127.0.0.1:8000/docs`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`
- Health check: `http://127.0.0.1:8000/health`

## Environment Variables

```env
MONGODB_URI=<COSMOS_DB_MONGO_URI_PLACEHOLDER>
DATABASE_NAME=hermes_auth
JWT_SECRET=<JWT_SECRET>
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60
ADMIN_EMAIL=admin@hermes.com
ADMIN_PASSWORD=Admin@12345
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

`MONGODB_URI` can point to local MongoDB during development or Azure Cosmos DB using the Mongo API in deployed environments.

`CORS_ORIGINS` should contain the frontend URLs that are allowed to call this API. Use comma-separated values for multiple frontend environments.

## API Documentation

### Register Customer

`POST /api/v1/auth/register`

Request body:

```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "Secure@123",
  "confirm_password": "Secure@123"
}
```

Success response:

```json
{
  "message": "Registration successful. Please login.",
  "redirect_to": "/login"
}
```

Validation rules:

- `name` is required and must be at least 2 characters
- `email` is required, must be valid, normalized to lowercase, and unique
- `password` is required and must include uppercase, lowercase, number, and special character
- `confirm_password` must match `password`

### Login

`POST /api/v1/auth/login`

This is the only login endpoint. Customer credentials return a customer token and customer dashboard redirect. The configured admin credentials return an admin token and admin dashboard redirect.

Customer request body:

```json
{
  "email": "john@example.com",
  "password": "Secure@123"
}
```

Customer success response:

```json
{
  "access_token": "<jwt-token>",
  "token_type": "bearer",
  "role": "customer",
  "redirect_to": "/customer-dashboard"
}
```

Admin request body using the same endpoint:

```json
{
  "email": "admin@hermes.com",
  "password": "Admin@12345"
}
```

Admin success response:

```json
{
  "access_token": "<jwt-token>",
  "token_type": "bearer",
  "role": "admin",
  "redirect_to": "/admin-dashboard"
}
```

## Error Responses

Duplicate email:

```json
{
  "detail": "Email is already registered."
}
```

Invalid login:

```json
{
  "detail": "Invalid email or password."
}
```

Validation failures return FastAPI `422 Unprocessable Entity` responses with field-level details.

## Database

Collection: `users`

Example document:

```json
{
  "_id": "ObjectId",
  "name": "John Doe",
  "email": "john@example.com",
  "password_hash": "$2b$12$...",
  "role": "customer",
  "created_at": "2026-06-01T10:00:00Z",
  "updated_at": "2026-06-01T10:00:00Z"
}
```

The service creates a unique index on `users.email` during startup.

## Frontend Developer Integration Guide

### Customer Registration Flow

Frontend Route: `/register`

Backend Endpoint: `POST /api/v1/auth/register`

Expected Success Redirect: `/login`

### Shared Login Flow

Frontend Route: `/login`

Backend Endpoint: `POST /api/v1/auth/login`

Expected Customer Success Redirect: `/customer-dashboard`

Expected Admin Success Redirect: `/admin-dashboard`

There is no separate admin login page or admin login endpoint. If the user enters the configured admin credentials on `/login`, the backend responds with `role: "admin"` and `redirect_to: "/admin-dashboard"`.


### What To Share With Frontend Team

- Auth service base URL for each environment, for example `http://localhost:8000`
- Register endpoint: `POST /api/v1/auth/register`
- Shared login endpoint: `POST /api/v1/auth/login`
- There is no separate admin login endpoint
- Frontend login page should use `/login` for both customers and admin
- Store the returned `access_token` securely on the client side
- Send authenticated dashboard requests with this header:

```http
Authorization: Bearer <access_token>
```

Frontend routing behavior should use `redirect_to` from the API response:

```json
{
  "access_token": "<jwt-token>",
  "token_type": "bearer",
  "role": "customer",
  "redirect_to": "/customer-dashboard"
}
```

```json
{
  "access_token": "<jwt-token>",
  "token_type": "bearer",
  "role": "admin",
  "redirect_to": "/admin-dashboard"
}
```

### What To Share With Dashboard Microservice Teams

Dashboard services should treat this Auth service as the login/token issuer. They should not implement their own login screens or password checks.

JWT payload contains:

```json
{
  "sub": "user-or-admin-id",
  "email": "user@example.com",
  "role": "customer"
}
```

For admin tokens, `role` will be `admin`.

Dashboard services should:

- Require `Authorization: Bearer <access_token>` on protected APIs
- Verify JWT signature using the same `JWT_SECRET` and `JWT_ALGORITHM`
- Check `role` before allowing access
- Allow `role: "customer"` for customer dashboard APIs
- Allow `role: "admin"` for admin dashboard APIs
- Use `sub` as the authenticated identity
- Use `email` only as a readable identifier, not as the primary authorization control

### What To Share With Database/Infrastructure Team

This service needs:

- MongoDB or Azure Cosmos DB Mongo API connection string
- Database name, default: `hermes_auth`
- Collection name: `users`
- Unique index on `users.email`

The service creates the unique email index on startup, but infrastructure can also provision it explicitly.

Required runtime environment variables:

```env
MONGODB_URI=<real MongoDB or Cosmos DB Mongo API URI>
DATABASE_NAME=hermes_auth
JWT_SECRET=<strong shared JWT secret>
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60
ADMIN_EMAIL=<real admin email>
ADMIN_PASSWORD=<temporary admin password>
CORS_ORIGINS=<frontend URLs allowed to call auth service>
```

### What You Should Change Before Team Integration

Update these values in your real `.env` or deployment secrets:

- Replace `MONGODB_URI` placeholder with the real Cosmos DB Mongo API URI
- Replace `JWT_SECRET` with a long random secret
- Replace `ADMIN_PASSWORD` before sharing or deploying
- Set `CORS_ORIGINS` to the frontend URLs used by your team
- Confirm the final deployed Auth service base URL and share it with frontend/dashboard teams

Recommended code-level next steps before production:

- Move admin credentials from config-only login to a database-backed admin user or secure identity provider
- Add a `/api/v1/auth/me` or `/api/v1/auth/verify-token` endpoint if dashboard teams prefer token introspection instead of local JWT validation
- Add automated API tests for register, customer login, admin login, duplicate email, and invalid credentials
- Add rate limiting for `/api/v1/auth/login`

## Security Considerations

- Passwords are hashed with bcrypt before storage.
- Plain text passwords are never persisted or returned.
- JWT secret is loaded from environment variables.
- Customer emails are normalized to lowercase before lookup and storage.
- The `users.email` field has a unique database index.
- Authentication failures return generic credential errors.
- Admin credentials are configurable and should be moved to a secure identity store or secrets manager before production.
- Replace placeholder secrets before deploying.

## Future Improvements

- Add refresh tokens and token revocation.
- Add email verification for customer registration.
- Add forgot password and reset password flows.
- Store admin users in the database with role-based access control.
- Add rate limiting for login endpoints.
- Add audit logging for authentication events.
- Restrict CORS origins per environment.
- Add automated tests and CI checks.
