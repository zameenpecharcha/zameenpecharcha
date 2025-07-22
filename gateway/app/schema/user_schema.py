import typing
import strawberry
from app.exception.UserException import REException
from app.utils.log_utils import log_msg
from app.utils.grpc_client import UserServiceClient

client = UserServiceClient()

@strawberry.type
class User:
    userId: int = strawberry.field(name="userId")
    name: str
    email: str
    phone: int
    role: str
    location: str

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
                userId=response.id,
                name=response.name,
                email=response.email,
                phone=response.phone,
                role=response.role,
                location=response.location
            )

        except Exception as e:
            log_msg("error", f"Error fetching user: {str(e)}")
            raise REException(
                "USER_NOT_FOUND",
                "Failed to fetch user",
                str(e)
            ).to_graphql_error()

@strawberry.type
class Mutation:
    @strawberry.mutation
    async def create_user(
        self, name: str, email: str, phone: int, password: str, role: str, location: str
    ) -> typing.Optional[User]:
        try:
            log_msg("info", f"Creating user {email}")
            response = client.create_user(name, email, phone, password, role, location)
            return User(
                userId=response.id,
                name=response.name,
                email=response.email,
                phone=response.phone,
                role=response.role,
                location=response.location
            )

        except Exception as e:
            log_msg("error", f"Unexpected error while creating user {email}: {str(e)}")
            raise REException(
                "USER_CREATION_FAILED",
                "Failed to create user",
                str(e)
            ).to_graphql_error()

