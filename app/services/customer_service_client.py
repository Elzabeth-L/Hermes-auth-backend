from typing import Any

import httpx

from app.core.config import settings
from app.core.exceptions import UpstreamServiceException


class CustomerServiceClient:
    async def create_customer_profile(
        self,
        *,
        auth_user_id: str,
        name: str,
        email: str,
    ) -> None:
        url = self._customer_endpoint_url()
        payload: dict[str, Any] = {
            "auth_user_id": auth_user_id,
            "name": name,
            "email": email,
        }

        try:
            async with httpx.AsyncClient(
                timeout=settings.customer_service_timeout_seconds,
            ) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
        except httpx.HTTPError as exc:
            raise UpstreamServiceException(
                "Customer profile creation failed. Please try registering again."
            ) from exc

    def _customer_endpoint_url(self) -> str:
        base_url = settings.customer_service_url.rstrip("/")
        return f"{base_url}/customer/post-customer"
