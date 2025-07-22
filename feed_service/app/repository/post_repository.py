from sqlalchemy.orm import Session
from ..entity.post import Post
from typing import List, Optional
from sqlalchemy import func
import math

class PostRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, post: Post) -> Post:
        self.db.add(post)
        self.db.commit()
        self.db.refresh(post)
        return post

    def get_by_id(self, post_id: int) -> Optional[Post]:
        return self.db.query(Post).filter(Post.id == post_id).first()

    def get_by_user_id(self, user_id: int) -> List[Post]:
        return self.db.query(Post).filter(Post.user_id == user_id).all()

    def get_nearby_posts(self, latitude: float, longitude: float, radius_km: float = 10.0) -> List[Post]:
        # Calculate the approximate range of latitude and longitude for the given radius
        # 1 degree of latitude is approximately 111 km
        lat_range = radius_km / 111.0
        # 1 degree of longitude varies with latitude, so we use a conservative estimate
        lon_range = radius_km / (111.0 * math.cos(math.radians(latitude)))

        # First filter posts within the approximate bounding box
        posts = self.db.query(Post).filter(
            Post.latitude.between(latitude - lat_range, latitude + lat_range),
            Post.longitude.between(longitude - lon_range, longitude + lon_range)
        ).all()

        # Then calculate exact distances and filter
        nearby_posts = []
        for post in posts:
            distance = self._calculate_distance(
                latitude, longitude,
                post.latitude, post.longitude
            )
            if distance <= radius_km:
                post.distance = distance  # Add distance as a dynamic attribute
                nearby_posts.append(post)

        # Sort by distance
        return sorted(nearby_posts, key=lambda x: x.distance)

    def update(self, post: Post) -> Post:
        self.db.commit()
        self.db.refresh(post)
        return post

    def delete(self, post: Post) -> None:
        self.db.delete(post)
        self.db.commit()

    @staticmethod
    def _calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        # Haversine formula to calculate distance between two points
        R = 6371  # Earth's radius in kilometers
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        return R * c 