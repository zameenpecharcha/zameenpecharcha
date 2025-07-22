from fastapi import APIRouter, HTTPException
from ..utils.grpc_client import comments_client
from ..schema.comments_schema import Mutation, Query
import strawberry
from strawberry.asgi import GraphQL

router = APIRouter()

schema = strawberry.Schema(Query, Mutation)
graphql_app = GraphQL(schema)

router.add_route("/graphql", graphql_app)

@router.post("/comments")
async def create_comment(post_id: int, user_id: int, content: str):
    try:
        response = comments_client.create_comment(post_id, user_id, content)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/comments/{comment_id}")
async def get_comment(comment_id: int):
    try:
        response = comments_client.get_comment(comment_id)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/posts/{post_id}/comments")
async def get_post_comments(post_id: int, page: int = 1, page_size: int = 10):
    try:
        response = comments_client.get_post_comments(post_id, page, page_size)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/comments/{comment_id}")
async def update_comment(comment_id: int, content: str):
    try:
        response = comments_client.update_comment(comment_id, content)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/comments/{comment_id}")
async def delete_comment(comment_id: int):
    try:
        response = comments_client.delete_comment(comment_id)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/comments/{comment_id}/like")
async def like_comment(comment_id: int, user_id: int):
    try:
        response = comments_client.like_comment(comment_id, user_id)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/comments/{comment_id}/unlike")
async def unlike_comment(comment_id: int, user_id: int):
    try:
        response = comments_client.unlike_comment(comment_id, user_id)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 