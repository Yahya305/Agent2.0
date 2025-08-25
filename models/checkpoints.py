# from sqlalchemy import Column, Integer, String, Text, LargeBinary, JSON
# from sqlalchemy.dialects.postgresql import JSONB
# from sqlalchemy.orm import declarative_base
# from core.database import Base



# class CheckpointBlob(Base):
#     __tablename__ = "checkpoint_blobs"

#     thread_id = Column(Text, primary_key=True)
#     checkpoint_ns = Column(Text, primary_key=True, default="")
#     channel = Column(Text, primary_key=True)
#     version = Column(Text, primary_key=True)
#     type = Column(Text, nullable=False)
#     blob = Column(LargeBinary)

#     # indexes will be auto-created from Alembic if needed


# class CheckpointMigration(Base):
#     __tablename__ = "checkpoint_migrations"

#     v = Column(Integer, primary_key=True)


# class CheckpointWrite(Base):
#     __tablename__ = "checkpoint_writes"

#     thread_id = Column(Text, primary_key=True)
#     checkpoint_ns = Column(Text, primary_key=True, default="")
#     checkpoint_id = Column(Text, primary_key=True)
#     task_id = Column(Text, primary_key=True)
#     idx = Column(Integer, primary_key=True)
#     channel = Column(Text, nullable=False)
#     type = Column(Text)
#     blob = Column(LargeBinary, nullable=False)
#     task_path = Column(Text, default="")


# class Checkpoint(Base):
#     __tablename__ = "checkpoints"

#     thread_id = Column(Text, primary_key=True)
#     checkpoint_ns = Column(Text, primary_key=True, default="")
#     checkpoint_id = Column(Text, primary_key=True)
#     parent_checkpoint_id = Column(Text)
#     type = Column(Text)
#     checkpoint = Column(JSONB, nullable=False)
#     metadata_ = Column("metadata", JSONB, nullable=False, default=dict)
