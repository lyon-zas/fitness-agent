from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from enum import Enum
from datetime import datetime, time

class ActivityLevel(str, Enum):
    SEDENTARY = "sedentary"
    LIGHT = "light"
    MODERATE = "moderate"
    VERY_ACTIVE = "very_active"
    ATHLETE = "athlete"

class CookingSkillLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "expert"

class FitnessGoal(str, Enum):
    HEALTHY_LIVING = "healthy_living"
    WEIGHT_GAIN = "weight_gain"
    WEIGHT_LOSS = "weight_loss"
    MUSCLE_GAIN = "muscle_gain"
    STRENGTH = "strength"

class CircleRank(str, Enum):
    FOLLOWER = "follower"
    MEMBER = "member"
    LEADER = "leader"
    INFLUENCER = "influencer"
    COMMUNITY_INFLUENCER = "community_influencer"
    BIG_INFLUENCER = "big_influencer"

class NotificationType(str, Enum):
    STEP_REMINDER = "step_reminder"
    MEAL_REMINDER = "meal_reminder"
    WORKOUT_REMINDER = "workout_reminder"
    PROGRESS_CELEBRATION = "progress_celebration"
    CALORIE_WARNING = "calorie_warning"
    HYDRATION_REMINDER = "hydration_reminder"
    CIRCLE_CHALLENGE = "circle_challenge"
    ACCOUNTABILITY_CHECK = "accountability_check"
    INFLUENCER_MOTIVATION = "influencer_motivation"

class SkippedMeal(str, Enum):
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"
    BREAKFAST_LUNCH = "breakfast_lunch"
    LUNCH_DINNER = "lunch_dinner"
    DINNER_SNACK = "dinner_snack"
    BREAKFAST_DINNER = "breakfast_dinner"
    BREAKFAST_LUNCH_DINNER = "breakfast_lunch_dinner"
    BREAKFAST_LUNCH_DINNER_SNACK = "breakfast_lunch_dinner_snack"

class CircleMember(BaseModel):
    user_id: str
    name: str
    rank: CircleRank
    fitness_goal: FitnessGoal
    current_streak: int = 0
    total_points: int = 0
    followers_count: int = 0
    following_count: int = 0
    last_active: datetime
    profile_picture: Optional[str] = None
    bio: Optional[str] = None
    location: str
    is_online: bool = False

class FitnessCircle(BaseModel):
    circle_id: str
    name: str
    description: str
    created_by: str  # user_id of creator
    members: List[CircleMember] = []
    max_members: int = 100
    is_public: bool = True
    tags: List[str] = []
    created_at: datetime
    last_activity: datetime
    total_challenges_completed: int = 0
    circle_goal: FitnessGoal
    circle_theme: Optional[str] = None

class CircleChallenge(BaseModel):
    challenge_id: str
    circle_id: str
    title: str
    description: str
    challenge_type: str  # "steps", "workout", "nutrition", "streak"
    target_value: int
    duration_days: int
    points_reward: int
    created_by: str
    participants: List[str] = []  # user_ids
    completed_by: List[str] = []  # user_ids
    start_date: datetime
    end_date: datetime
    is_active: bool = True

class AccountabilityCheck(BaseModel):
    check_id: str
    circle_id: str
    initiated_by: str
    target_members: List[str]  # user_ids to check on
    message: str
    check_type: str  # "daily", "weekly", "challenge", "motivation"
    created_at: datetime
    responses: Dict[str, str] = {}  # user_id -> response
    is_completed: bool = False

class InfluencerPost(BaseModel):
    post_id: str
    influencer_id: str
    circle_id: str
    content: str
    post_type: str  # "motivation", "progress", "challenge", "tip"
    media_urls: List[str] = []
    likes: int = 0
    comments: List[str] = []
    created_at: datetime
    is_featured: bool = False

class DailyTracking(BaseModel):
    date: datetime
    steps_taken: int = 0
    steps_goal: int = 10000
    calories_consumed: int = 0
    calories_goal: int = 0
    meals_logged: List[str] = []
    workouts_completed: List[str] = []
    water_intake: float = 0.0  # in liters
    water_goal: float = 2.5  # in liters
    current_time: Optional[time] = None

class FitnessProfile(BaseModel):
    age: int
    weight: float
    height: float
    name: str
    location: str
    gender: str
    desired_weight: float
    activity_level: ActivityLevel
    fitness_goal: FitnessGoal
    health_conditions: List[str] = []
    dietary_restrictions: List[str] = []
    cooking_skill_level: CookingSkillLevel
    intermittent_fasting: bool
    skipped_meals: List[SkippedMeal] = []
    fasting_threshold: int
    allergies: List[str] = []
    cuisine_preferences: List[str] = []
    injuries: List[str] = []
    preferred_workout_time: str
    available_equipment: List[str] = []
    workout_days_per_week: int
    daily_calorie_deficit: int = 0  # For weight loss goals
    daily_calorie_surplus: int = 0  # For muscle gain goals
    step_goal: int = 10000
    water_goal: float = 2.5
    circle_rank: CircleRank = CircleRank.FOLLOWER
    circles_joined: List[str] = []  # circle_ids
    followers: List[str] = []  # user_ids
    following: List[str] = []  # user_ids

class Exercise(BaseModel):
    name: str
    sets: int
    reps: int
    rest_time: int = Field(..., description="Rest time in seconds")

class Meal(BaseModel):
    name: str
    calories: int
    protein: float
    carbs: float
    fats: float
    timing: str = Field(..., description="breakfast, lunch, dinner, snack")
    logged: bool = False
    logged_time: Optional[datetime] = None

class FitnessReportResult(BaseModel):
    workout_plan: List[Exercise] = Field(description="Customized workout routine")
    meal_plan: List[Meal] = Field(description="Daily meal plan")
    daily_calories: int = Field(description="Recommended daily caloric intake")
    macros: dict = Field(description="Recommended macro split (protein, carbs, fats)")
    tips: List[str] = Field(description="Personalized fitness and nutrition tips")
    weekly_schedule: dict = Field(description="Weekly workout and meal timing schedule")
    notification_message: str = Field(description="Personalized notification message based on fitness goal")

class BehavioralNotification(BaseModel):
    notification_type: NotificationType
    message: str
    urgency: str = Field(description="low, medium, high")
    context: Dict = Field(description="Additional context for the notification")
    suggested_action: Optional[str] = None

class CircleNotification(BaseModel):
    notification_type: NotificationType
    message: str
    circle_id: str
    sender_id: str
    recipient_ids: List[str] = []
    challenge_id: Optional[str] = None
    post_id: Optional[str] = None
    urgency: str = Field(description="low, medium, high")
    created_at: datetime
    is_read: bool = False