from sqlalchemy import String, Integer, Column
from database import Base, engine
import JSON

def create_tables():
    Base.metadata.create_all(engine)

class Quiz(Base):
    __tablename__ = "quizzes"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    questions = Column(JSON)
    options = Column(JSON) 