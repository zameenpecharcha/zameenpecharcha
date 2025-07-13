"""Update ID types to UUID and add new fields

Revision ID: 001
Revises: 
Create Date: 2024-03-19
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
import uuid

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create UUID extension if not exists
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    
    # 1. Update users table
    with op.batch_alter_table('users') as batch_op:
        # Add temporary UUID column
        batch_op.add_column(sa.Column('user_id_uuid', UUID(as_uuid=True), nullable=True))
        
        # Update with new UUIDs
        op.execute("UPDATE users SET user_id_uuid = uuid_generate_v4()")
        
        # Drop old PK and create new one
        batch_op.drop_constraint('users_pkey', type_='primary')
        batch_op.drop_column('user_id')
        batch_op.alter_column('user_id_uuid', new_column_name='user_id')
        batch_op.create_primary_key('users_pkey', ['user_id'])
        
        # Add new columns
        batch_op.add_column(sa.Column('updated_at', sa.TIMESTAMP(timezone=True)))
        batch_op.add_column(sa.Column('is_active', sa.Boolean(), server_default='true'))
        batch_op.add_column(sa.Column('is_deleted', sa.Boolean(), server_default='false'))
        batch_op.add_column(sa.Column('deleted_at', sa.TIMESTAMP(timezone=True)))
        batch_op.add_column(sa.Column('created_by', UUID(as_uuid=True)))
        batch_op.add_column(sa.Column('updated_by', UUID(as_uuid=True)))
        
        # Add indexes
        batch_op.create_index('ix_users_email', ['email'])
        batch_op.create_index('ix_users_phone', ['phone'])

    # 2. Update posts table
    with op.batch_alter_table('posts') as batch_op:
        # Similar UUID conversion process
        batch_op.add_column(sa.Column('id_uuid', UUID(as_uuid=True), nullable=True))
        op.execute("UPDATE posts SET id_uuid = uuid_generate_v4()")
        batch_op.drop_constraint('posts_pkey', type_='primary')
        batch_op.drop_column('id')
        batch_op.alter_column('id_uuid', new_column_name='id')
        batch_op.create_primary_key('posts_pkey', ['id'])
        
        # Update foreign key column
        batch_op.add_column(sa.Column('user_id_uuid', UUID(as_uuid=True), nullable=True))
        op.execute("""
            UPDATE posts p 
            SET user_id_uuid = u.user_id_uuid 
            FROM users u 
            WHERE p.user_id = u.user_id::text
        """)
        batch_op.drop_column('user_id')
        batch_op.alter_column('user_id_uuid', new_column_name='user_id')
        
        # Add new columns
        batch_op.add_column(sa.Column('like_count', sa.Integer(), server_default='0'))
        batch_op.add_column(sa.Column('comment_count', sa.Integer(), server_default='0'))
        batch_op.add_column(sa.Column('view_count', sa.Integer(), server_default='0'))
        batch_op.add_column(sa.Column('is_active', sa.Boolean(), server_default='true'))
        batch_op.add_column(sa.Column('is_deleted', sa.Boolean(), server_default='false'))
        batch_op.add_column(sa.Column('deleted_at', sa.TIMESTAMP(timezone=True)))
        batch_op.add_column(sa.Column('created_by', UUID(as_uuid=True)))
        batch_op.add_column(sa.Column('updated_by', UUID(as_uuid=True)))

    # 3. Create new likes table
    op.create_table(
        'likes',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('user_id', UUID(as_uuid=True), nullable=False),
        sa.Column('target_id', UUID(as_uuid=True), nullable=False),
        sa.Column('target_type', sa.String(50), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('is_deleted', sa.Boolean(), server_default='false'),
        sa.Column('deleted_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('created_by', UUID(as_uuid=True)),
        sa.Column('updated_by', UUID(as_uuid=True))
    )
    
    # Create indexes on likes table
    op.create_index('ix_likes_user_id', 'likes', ['user_id'])
    op.create_index('ix_likes_target_id', 'likes', ['target_id'])
    op.create_index('ix_likes_target_type', 'likes', ['target_type'])

def downgrade():
    # Drop new tables
    op.drop_table('likes')
    
    # Revert posts table
    with op.batch_alter_table('posts') as batch_op:
        # Remove new columns
        batch_op.drop_column('like_count')
        batch_op.drop_column('comment_count')
        batch_op.drop_column('view_count')
        batch_op.drop_column('is_active')
        batch_op.drop_column('is_deleted')
        batch_op.drop_column('deleted_at')
        batch_op.drop_column('created_by')
        batch_op.drop_column('updated_by')
        
        # Revert UUID columns to integer
        batch_op.add_column(sa.Column('id_int', sa.Integer(), nullable=True))
        op.execute("UPDATE posts SET id_int = row_number() OVER (ORDER BY created_at)")
        batch_op.drop_constraint('posts_pkey', type_='primary')
        batch_op.drop_column('id')
        batch_op.alter_column('id_int', new_column_name='id')
        batch_op.create_primary_key('posts_pkey', ['id'])

    # Revert users table
    with op.batch_alter_table('users') as batch_op:
        # Remove new columns
        batch_op.drop_column('updated_at')
        batch_op.drop_column('is_active')
        batch_op.drop_column('is_deleted')
        batch_op.drop_column('deleted_at')
        batch_op.drop_column('created_by')
        batch_op.drop_column('updated_by')
        
        # Remove indexes
        batch_op.drop_index('ix_users_email')
        batch_op.drop_index('ix_users_phone')
        
        # Revert UUID to integer
        batch_op.add_column(sa.Column('user_id_int', sa.Integer(), nullable=True))
        op.execute("UPDATE users SET user_id_int = row_number() OVER (ORDER BY created_at)")
        batch_op.drop_constraint('users_pkey', type_='primary')
        batch_op.drop_column('user_id')
        batch_op.alter_column('user_id_int', new_column_name='user_id')
        batch_op.create_primary_key('users_pkey', ['user_id']) 