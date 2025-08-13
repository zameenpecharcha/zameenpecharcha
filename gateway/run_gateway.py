import strawberry
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.schema.auth_schema import Query as AuthQuery, Mutation as AuthMutation
from app.schema.user_schema import Query as UserQuery, Mutation as UserMutation
from app.schema.posts_schema import Query as PostsQuery, Mutation as PostsMutation
from app.schema.property_schema import Query as PropertyQuery, Mutation as PropertyMutation
from app.middleware.auth_middleware import AuthMiddleware
from strawberry.fastapi import GraphQLRouter

import logging

# Logging setup
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Define GraphQL schema
@strawberry.type
class Query(AuthQuery, UserQuery, PostsQuery, PropertyQuery): pass

@strawberry.type
class Mutation(AuthMutation, UserMutation, PostsMutation, PropertyMutation): pass

schema = strawberry.Schema(query=Query, mutation=Mutation)

# Load environment variables from .env (repo root or gateway dir)
load_dotenv()

# Initialize app
app = FastAPI()

# Mount GraphQL route
graphql_app = GraphQLRouter(
    schema=schema,
    graphql_ide="graphiql",
    path="/graphql"
)
app.include_router(graphql_app, prefix="/api/v1")

# Health check
@app.get("/health")
def health_check():
    return {"status": "healthy"}

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app = AuthMiddleware(app)

# Run app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("run_gateway:app", host="0.0.0.0", port=8000, reload=True)
