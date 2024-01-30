from fastapi import FastAPI,status,HTTPException
from pydantic import BaseModel
from database import SessionLocal
import models

app=FastAPI()
# Open a database session
db = SessionLocal()

# Define a Pydantic BaseModel with ORM mode enabled, to get rid of can't read serialized response error
class OurBaseModel(BaseModel):
    class Config:
        orm_mode=True

# Define a Pydantic model for a quiz question
class Question(OurBaseModel):
    statement: str
    options: list[str]

# Define a Pydantic model for creating a quiz
class QuizCreate(OurBaseModel):
    title: str
    questions: list[Question]

# Define a Pydantic model for user quiz submission
class UserSubmission(OurBaseModel):
    quiz_id: int
    answers: dict

# API Endpoints
@app.post("/quizzes", response_model=models.Quiz)
def create_quiz(quiz: QuizCreate):
    # Open a new session for database operations
    db = SessionLocal()

    # Create a new instance of the Quiz model with data from the request
    db_quiz = models.Quiz(**quiz.dict())
    
    # Add the new quiz to the database
    db.add(db_quiz)
    db.commit()

    # Refresh the quiz instance to get the updated data
    db.refresh(db_quiz)
    db.close()

    # Return the created quiz as the API response
    return db_quiz

@app.get("/quizzes/{quiz_id}", response_model=models.Quiz)
def get_quiz(quiz_id: int):
    db = SessionLocal()
    db_quiz = db.query(models.Quiz).filter(models.Quiz.id == quiz_id).first()
    db.close()
    if db_quiz is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz not found")
    return db_quiz

@app.post("/submit")
def submit_quiz(submission: UserSubmission):
    db = SessionLocal()

    # Query the database for the quiz with the specified ID
    db_quiz = db.query(models.Quiz).filter(models.Quiz.id == submission.quiz_id).first()
    db.close()

    # Check if the quiz was not found, raise a 404 error
    if db_quiz is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz not found")

    return {"message": "your quiz is submitted successfully and your response is recorded"}

    

@app.get("/result/{quiz_id}")
def get_quiz_result(quiz_id: int):
    db = SessionLocal()
    db_quiz = db.query(models.Quiz).filter(models.Quiz.id == quiz_id).first()
    
    if db_quiz is None:
        db.close()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz not found")
    

    # Get user answers from the submitted quiz
    user_answers = quiz_id.answers

    # Get correct answers from the database
    correct_answers = db_quiz.questions


    # Calculate the user's score(sum is used to adds up all the 1 value, counting the number of correct answers and zip() will work like iterator that aggregates elements from 'user_answer' and 'correct_answers' dictionaries)
    score = sum(1 for user_option, correct_option in zip(user_answers.values(), correct_answers.values()) if user_option == correct_option)

    result_summary = {
        "quiz_title": db_quiz.title,
        "user_score": score,
        "total_questions": len(correct_answers)
    }

    return result_summary