from fastapi import APIRouter
from app.schema.comments_schema import Mutation, Query
import strawberry
from strawberry.asgi import GraphQL

comments_router = APIRouter()

schema = strawberry.Schema(Query, Mutation)
graphql_app = GraphQL(schema)

comments_router.add_route("/graphql", graphql_app) 