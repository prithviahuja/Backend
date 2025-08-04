from fastapi import FastAPI
from pydantic import BaseModel
from notmain import api


app=FastAPI()

app.include_router(api)



