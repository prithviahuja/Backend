from fastapi import APIRouter
from pydantic import BaseModel


api=APIRouter()

feed_back={}

class Feedback(BaseModel):
    cook_id:int
    ratings:int
    comments:str


@api.post("/feedback")
def give_feedback(feedback:Feedback):
    feed_back[feedback.cook_id]=feedback
    return {"message":"feedback stored"}

@api.get("/feedback/{id}")
def get_cook_feedback(id:int):
    feedback=feed_back.get(id)
    if feedback:
        return feedback
    return {"error": "Feedback not found"}
