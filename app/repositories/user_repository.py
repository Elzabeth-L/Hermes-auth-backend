from datetime import datetime, timezone
from typing import Any

from bson import ObjectId
from pymongo.errors import DuplicateKeyError

from app.database.mongodb import get_database
from app.models.user import UserInDB


class UserRepository:
    @property
    def collection(self):
        return get_database().users

    async def create_user(self, user: UserInDB) -> dict[str, Any]:
        document = user.model_dump(mode="python")
        try:
            result = await self.collection.insert_one(document)
        except DuplicateKeyError:
            raise
        document["_id"] = result.inserted_id
        return document

    async def find_by_email(self, email: str) -> dict[str, Any] | None:
        return await self.collection.find_one({"email": email})

    async def delete_by_id(self, user_id: ObjectId) -> None:
        await self.collection.delete_one({"_id": user_id})

    async def update_last_seen(self, user_id: ObjectId) -> None:
        await self.collection.update_one(
            {"_id": user_id},
            {"$set": {"updated_at": datetime.now(timezone.utc)}},
        )
