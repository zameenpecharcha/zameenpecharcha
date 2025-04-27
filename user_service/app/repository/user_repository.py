from user_service.app.entity.user_entity import users
from sqlalchemy.orm import sessionmaker
from user_service.app.utils.db_connection import get_db_engine

SessionLocal = sessionmaker(bind=get_db_engine())

# def get_user_by_id(user_id):
#     session = SessionLocal()
#     user = session.execute(users.select().where(users.c.user_id == user_id)).fetchone()
#     session.close()
#     return user

def get_user_by_id(id):
    session = SessionLocal()
    query = users.select().with_only_columns(
        users.c.name,
        users.c.email,
        users.c.phone,
        users.c.password
    ).where(users.c.id == id)
    user = session.execute(query).fetchone()
    session.close()
    return user

def create_user(name, email, phone, password):
    session = SessionLocal()
    result = session.execute(users.insert().returning(users.c.user_id).values(
        name=name, email=email, phone=phone, password=password
    ))
    session.commit()
    session.close()
    #print("===result.scalar()===",result.scalar())
    return result.scalar()  # This will return the inserted user_id


# def get_user_by_id(user_id):
#     session = SessionLocal()
#     try:
#         result = session.execute(
#             users.select().where(users.c.user_id == user_id)
#         ).fetchone()
#         if result:
#             user = dict(result)
#             user.pop('password', None)  # Remove sensitive info
#             return user
#         return None
#     finally:
#         session.close()

# def create_user(name, email, phone, password, profile_photo=None, role=None, location=None, bio=None):
#     session = SessionLocal()
#     try:
#         result = session.execute(
#             users.insert().returning(users).values(
#                 name=name,
#                 email=email,
#                 phone=phone,
#                 password=password,
#                 profile_photo=profile_photo,
#                 role=role,
#                 location=location,
#                 bio=bio,
#                 created_at=datetime.utcnow()
#             )
#         )
#         session.commit()
#         user = result.fetchone()
#         if user:
#             user_data = dict(user)
#             user_data.pop('password', None)  # Remove sensitive info
#             return user_data
#         return None
#     finally:
#       session.close()
