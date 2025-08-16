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

# CORS setup - MUST be first middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server
        "http://127.0.0.1:3000",
        "http://localhost:5173",  # Vite dev server
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH", "HEAD"],
    allow_headers=[
        "Content-Type",
        "Authorization",
        "Accept",
        "Origin",
        "X-Requested-With",
        "Access-Control-Request-Method",
        "Access-Control-Request-Headers",
    ],
    expose_headers=["Content-Type", "Authorization"],
    max_age=3600,  # Cache preflight requests for 1 hour
)

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

# Auth middleware - MUST be last
app = AuthMiddleware(app)

# Run app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("run_gateway:app", host="0.0.0.0", port=8000, reload=True)