from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine

# Create a SQLAlchemy engine to connect to the PostgreSQL database
engine = create_engine("postgresql://postgres:admin123@localhost/quizzes_data",echo=True)

Base=declarative_base()

# Create a sessionmaker bound to the engine for managing database sessions
SessionLocal=sessionmaker(bind=engine)