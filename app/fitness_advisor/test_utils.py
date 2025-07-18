from app.fitness_advisor.models import (
        CookingSkillLevel, FitnessProfile, DailyTracking, 
        ActivityLevel, FitnessGoal,
)
from datetime import datetime, time

from app.fitness_advisor.service import get_contextual_notification



# Example usage function
async def example_usage():
    """Example showing how the behavioral notifications work"""
    # Create a sample profile for weight loss
    profile = FitnessProfile(
            name="Tunde",
            location="Lagos, Nigeria",
            desired_weight=75.0,
            cooking_skill_level=CookingSkillLevel.BEGINNER,
            intermittent_fasting=False,
            fasting_threshold=12,
            age=30,
            weight=80.0,
            height=170.0,
            health_conditions=["none"],
            dietary_restrictions=["none"],
            allergies=["none"],
            cuisine_preferences=["Nigerian"],
            injuries=["none"],
            gender="male",
            activity_level=ActivityLevel.MODERATE,
            fitness_goal=FitnessGoal.WEIGHT_LOSS,
            preferred_workout_time="morning",
            workout_days_per_week=4,
            daily_calorie_deficit=500,
            step_goal=10000
    )
    
    # Scenario 1: User has only walked 200 steps by noon
    tracking_1 = DailyTracking(
        date=datetime.now(),
        steps_taken=200,
        steps_goal=10000,
        calories_consumed=800,
        calories_goal=1500,
        meals_logged=["breakfast"],
        current_time=time(12, 0)
    )
    
    notification_1 = await get_contextual_notification(profile, tracking_1)
    if notification_1:
        print(f"Scenario 1 - Low steps by noon: {notification_1.message}")
    
    # Scenario 2: User hasn't logged lunch by 2 PM
    tracking_2 = DailyTracking(
        date=datetime.now(),
        steps_taken=5000,
        steps_goal=10000,
        calories_consumed=600,
        calories_goal=1500,
        meals_logged=["breakfast"],
        current_time=time(14, 0)
    )
    
    notification_2 = await get_contextual_notification(profile, tracking_2)
    if notification_2:
        print(f"Scenario 2 - No lunch logged: {notification_2.message}")
    
    # Scenario 3: User is approaching calorie limit
    tracking_3 = DailyTracking(
        date=datetime.now(),
        steps_taken=8000,
        steps_goal=10000,
        calories_consumed=1300,
        calories_goal=1500,
        meals_logged=["breakfast", "lunch"],
        current_time=time(16, 0)
    )
    
    notification_3 = await get_contextual_notification(profile, tracking_3)
    if notification_3:
        print(f"Scenario 3 - High calorie intake: {notification_3.message}")