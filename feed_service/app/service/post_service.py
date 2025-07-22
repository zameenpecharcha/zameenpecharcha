from typing import List, Optional
from ..entity.post import Post
from ..repository.post_repository import PostRepository
from sqlalchemy.orm import Session

class PostService:
    def __init__(self, db: Session):
        self.repository = PostRepository(db)

    def create_post(self, user_id: int, content: str, latitude: float, longitude: float, location_name: str) -> Post:
        post = Post(
            user_id=user_id,
            content=content,
            latitude=latitude,
            longitude=longitude,
            location_name=location_name
        )
        return self.repository.create(post)

    def get_post(self, post_id: int) -> Optional[Post]:
        return self.repository.get_by_id(post_id)

    def get_user_posts(self, user_id: int) -> List[Post]:
        return self.repository.get_by_user_id(user_id)

    def get_nearby_posts(self, latitude: float, longitude: float, radius_km: float = 10.0) -> List[Post]:
        return self.repository.get_nearby_posts(latitude, longitude, radius_km)

    def update_post(self, post_id: int, content: str, latitude: Optional[float] = None, 
                   longitude: Optional[float] = None, location_name: Optional[str] = None) -> Optional[Post]:
        post = self.repository.get_by_id(post_id)
        if not post:
            return None

        post.content = content
        if latitude is not None:
            post.latitude = latitude
        if longitude is not None:
            post.longitude = longitude
        if location_name is not None:
            post.location_name = location_name

        return self.repository.update(post)

    def delete_post(self, post_id: int) -> bool:
        post = self.repository.get_by_id(post_id)
        if not post:
            return False

        self.repository.delete(post)
        return True 