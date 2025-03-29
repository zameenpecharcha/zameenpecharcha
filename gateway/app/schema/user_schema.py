import typing
from datetime import datetime
import strawberry
from app.exception.UserException import REException
from app.utils.log_utils import log_msg
from app.utils.grpc_client import UserServiceClient
from typing import Optional
client = UserServiceClient()

@strawberry.type
class User:
    user_id: int
    name: str
    email: str
    phone: int
    profile_photo: Optional[str] = None  # Optional fields
    role: Optional[str] = None
    location: Optional[str] = None
    created_at: Optional[datetime] = None
    bio: Optional[str] = None
    password: Optional[str] = None


@strawberry.type
class Query:
    @strawberry.field
    def user(self, id: int) -> typing.Optional[User]:
        try:
            log_msg("info", f"Fetching user with ID {id}")
            response = client.get_user(id)

            if response is None:
                raise REException("USER_NOT_FOUND", "User does not exist", "Invalid ID provided")
            return User(
                user_id=response.id,
                name=response.name,
                email=response.email,
                phone=response.phone,
                profile_photo=getattr(response, "profile_photo", None),  # If missing, set None
                role=getattr(response, "role", None),
                location=getattr(response, "location", None),
                created_at=getattr(response, "created_at", None),
                bio=getattr(response, "bio", None),
                password=getattr(response, "password", None)
            )

        except REException as e:
            log_msg("error", f"Error fetching user: {e.message}")
            raise e.to_graphql_error()  # Convert to GraphQL error

        except Exception as e:
            log_msg("error", f"Unexpected error while fetching user {id}: {str(e)}")
            raise REException("UNKNOWN_ERROR", "An unexpected error occurred", "Internal server error").to_graphql_error()

@strawberry.type
class Mutation:
    @strawberry.mutation
    async def create_user(
        self, name: str, email: str, phone: int, password: str
    ) -> typing.Optional[User]:
        try:
            log_msg("info", f"Creating user {email}")
            response = client.create_user(name, email, phone, password)
            return User(user_id=response.id, name=response.name, email=response.email,
                        phone=response.phone,
                        )

        except Exception as e:
            log_msg("error", f"Unexpected error while creating user {email}: {str(e)}")
            raise REException(
                "USER_CREATION_FAILED",
                "Failed to create user",
                "Database error or invalid input",
            ).to_graphql_error()

