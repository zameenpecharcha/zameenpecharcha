from sqlalchemy import MetaData, Table, Column, Integer, String, TIMESTAMP, ForeignKey

meta = MetaData()

posts = Table('posts', meta,
    Column('post_id', Integer, primary_key=True, autoincrement=True),
    Column('user_id', Integer, ForeignKey('users.user_id')),
    Column('title', String(100)),
    Column('content', String(1000)),
    Column('created_at', TIMESTAMP),
    Column('updated_at', TIMESTAMP),
) 