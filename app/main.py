from fastapi import FastAPI
from app.fitness_advisor.controller import router

app = FastAPI(title="AI Fitness Trainer")
app.include_router(router)

