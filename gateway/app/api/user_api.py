from fastapi import APIRouter
from app.schema.user_schema import Mutation, Query
from strawberry.asgi import GraphQL
import strawberry
user = APIRouter()

schema = strawberry.Schema(Query, Mutation)
graphql_app = GraphQL(schema)

user.add_route("/graphql", graphql_app)