from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import strawberry
from strawberry.fastapi import GraphQLRouter
from .schema.auth_schema import Query as AuthQuery, Mutation as AuthMutation
from .schema.user_schema import Query as UserQuery, Mutation as UserMutation
from .schema.posts_schema import Query as PostsQuery, Mutation as PostsMutation

# Combine queries and mutations
@strawberry.type
class Query(AuthQuery, UserQuery, PostsQuery):
    pass

@strawberry.type
class Mutation(AuthMutation, UserMutation, PostsMutation):
    pass

# Create GraphQL schema
schema = strawberry.Schema(query=Query, mutation=Mutation)

# Create FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add GraphQL routes
graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/api/v1/graphql")

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy"}

# API routes
# app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"]) # This line is removed as per the new_code
# app.include_router(user_router, prefix="/api/v1/users", tags=["users"]) # This line is removed as per the new_code
# app.include_router(comments_router, prefix="/api/v1/comments", tags=["comments"]) # This line is removed as per the new_code
# app.include_router(posts_router, prefix="/api/v1/posts", tags=["posts"]) # This line is removed as per the new_code
# app.include_router(property_router, prefix="/api/v1/properties", tags=["properties"]) # This line is removed as per the new_code

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)