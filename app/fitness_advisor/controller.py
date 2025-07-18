from fastapi import APIRouter
from app.fitness_advisor.models import DailyTracking, FitnessProfile
from app.fitness_advisor.service import analyze_profile


router = APIRouter()


@router.post("/analyze")
async def analyze_fitness(fitness_profile: FitnessProfile):
    return await analyze_profile(fitness_profile)

# @router.post("/profile")
# async def log_current_activity(fitness_profile: FitnessProfile, daily_tracking: DailyTracking):
#     return await log_current_activity(fitness_profile, daily_tracking)

# @router.post("/notification")
# async def generate_notification(fitness_profile: FitnessProfile, daily_tracking: DailyTracking):
#     return await generate_notification(fitness_profile, daily_tracking)

# @router.post("/behavioral")
# async def generate_behavioral_notification(fitness_profile: FitnessProfile, daily_tracking: DailyTracking):
#     return await generate_behavioral_notification(fitness_profile, daily_tracking)

