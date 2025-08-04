from fastapi import APIRouter,HTTPException
from redis_om import get_redis_connection,HashModel
from pydantic import BaseModel,Field

api=APIRouter()

redis=get_redis_connection(
    host="redis-16138.c283.us-east-1-4.ec2.redns.redis-cloud.com",
    port=16138,
    password="1TWUoFtAwamWLxTHb6pWj1m4wJ9uV5sn",
    decode_responses=True
)

class FeedbackIn(BaseModel):
    cook_name: str
    ratings: int = Field(..., ge=1, le=5)
    comments: str

class Feedback(HashModel):
    cook_name:str
    ratings:int
    comments:str

    class Meta:
        database=redis

@api.post("/feedback")
def give_feedback(feedback: FeedbackIn):
    try:
        fb = Feedback(
        cook_name=feedback.cook_name,
        ratings=feedback.ratings,
        comments=feedback.comments
        )
        fb.save()
        return fb
    

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save feedback: {str(e)}")

def format(pk:str):
    try:
        feedback=Feedback.get(pk)
        return{
        "id":feedback.pk,
        "cook_name":feedback.cook_name,
        "ratings":feedback.ratings,
        "comments":feedback.comments
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching feedback: {str(e)}")
    

@api.get("/feedback")
def all_feedbacks():
    return [format(pk) for pk in Feedback.all_pks()]

@api.get("/feedback/{pk}")
def get_feedback(pk: str):
    return format(pk) 

@api.delete("/feedback/{pk}")    
def delete_feedback(pk:str):
    try:        
        return Feedback.delete(pk)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting feedback: {str(e)}")

@api.put("/feedback/{pk}")
def update_feedback(pk: str, updated: FeedbackIn):
    try:
        feedback = Feedback.get(pk)
        if not feedback:
            raise HTTPException(status_code=404, detail="Feedback not found")
        
        feedback.ratings = updated.ratings
        feedback.comments = updated.comments
        feedback.save()
        return {"message": "Feedback updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating feedback: {str(e)}")
    

@api.get("/feedback/get_feedbacks/{cook_name}")
def get_all_feedbacks(cook_name:str):
    try:
        feedbacks = [format(pk) for pk in Feedback.all_pks()]
        cook_feedbacks=[fb for fb in feedbacks if fb["cook_name"].lower()==cook_name.lower()]
        if not cook_feedbacks:
                raise HTTPException(status_code=404, detail=f"No feedback found for {cook_name}")
        return cook_feedbacks
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching feedbacks for cook {cook_name}: {str(e)}")
    

@api.get("/feedback/get_average/{cook_name}")
def get_average(cook_name: str):
    try:
        feedbacks=get_all_feedbacks(cook_name)
        ratings=[fb["ratings"] for fb in feedbacks]
        if not ratings:
                raise HTTPException(status_code=404, detail="No ratings found for cook")

        average=sum(ratings)/len(ratings)
        return {
            "cook_name": cook_name,
            "average_rating": average,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating average: {str(e)}")




