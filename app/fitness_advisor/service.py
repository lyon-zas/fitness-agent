from pydantic_ai import Agent, RunContext
from app.fitness_advisor.models import ( FitnessProfile, FitnessReportResult, DailyTracking, 
    BehavioralNotification, NotificationType, FitnessGoal,
    CircleRank, FitnessCircle, CircleMember, CircleChallenge, AccountabilityCheck,
    InfluencerPost, CircleNotification
)
from typing import Optional, List, Dict
from datetime import datetime, time, timedelta
import uuid

fitness_agent = Agent(
    'gpt-4o',
    deps_type=FitnessProfile,
    output_type=FitnessReportResult,
    output_retries=3,
    system_prompt="Create personalized FitnessReportResult based on user's information provided. "
    "For notification messages call the get_notification tool and pick the single best one from the list you receive."
)

circle_agent = Agent(
    'gpt-4o',
    deps_type=tuple[FitnessProfile, FitnessCircle],
    output_type=CircleNotification,
    system_prompt="Generate circle-specific notifications and manage accountability features for fitness communities."
)

notification_agent = Agent(
    'gpt-4o',  
    output_type=list[str],
    system_prompt="Generate personalized notification messages based on the user's fitness goals and current status.",
)

behavioral_agent = Agent(
    'gpt-4o',
    deps_type=tuple[FitnessProfile, DailyTracking],
    output_type=BehavioralNotification,
    system_prompt="Generate contextual behavioral notifications based on user's current progress vs goals."
)

influencer_agent = Agent(
    'gpt-4o',
    deps_type=tuple[FitnessProfile, FitnessCircle],
    output_type=InfluencerPost,
    system_prompt="Generate motivational and educational content for fitness influencers to share with their followers."
)

@fitness_agent.system_prompt
async def add_user_fitness_data(ctx: RunContext[FitnessProfile]) -> str:
    fitness_data = ctx.deps
    return f"User fitness profile and goals: {fitness_data!r}"

@circle_agent.system_prompt
async def add_circle_context(ctx: RunContext[tuple[FitnessProfile, FitnessCircle]]) -> str:
    profile, circle = ctx.deps
    return f"""
    User Profile: {profile!r}
    Circle Info: {circle!r}
    
    Generate circle-specific notifications and manage accountability features.
    Consider the user's rank, circle goals, and community dynamics.
    """

@influencer_agent.system_prompt
async def add_influencer_context(ctx: RunContext[tuple[FitnessProfile, FitnessCircle]]) -> str:
    profile, circle = ctx.deps
    return f"""
    Influencer Profile: {profile!r}
    Circle Community: {circle!r}
    
    Generate engaging motivational content that resonates with the circle's fitness goals.
    Consider the influencer's rank and their ability to inspire followers.
    """

@fitness_agent.tool
async def get_notification(ctx: RunContext[FitnessProfile]) -> list[str]:
    fitness_data = ctx.deps
    result = await notification_agent.run(
        f"Generate 5 personalized notification messages for someone with fitness goal: {fitness_data.fitness_goal.value}. "
        f"Make them specific to their goal and encouraging for their fitness journey.")
    return result.output

@behavioral_agent.system_prompt
async def add_behavioral_context(ctx: RunContext[tuple[FitnessProfile, DailyTracking]]) -> str:
    profile, tracking = ctx.deps
    return f"""
    User Profile: {profile!r}
    Current Daily Progress: {tracking!r}
    
    Generate a behavioral notification based on their current progress vs goals.
    Consider their fitness goal, current time, and what they should be doing.
    """

# Circle Management Functions
async def create_fitness_circle(
    creator_profile: FitnessProfile,
    name: str,
    description: str,
    circle_goal: FitnessGoal,
    max_members: int = 100,
    is_public: bool = True,
    tags: List[str] = []
) -> FitnessCircle:
    """Create a new fitness accountability circle"""
    
    # Create circle with creator as first member
    circle = FitnessCircle(
        circle_id=str(uuid.uuid4()),
        name=name,
        description=description,
        created_by=creator_profile.name,
        circle_goal=circle_goal,
        max_members=max_members,
        is_public=is_public,
        tags=tags,
        created_at=datetime.now(),
        last_activity=datetime.now()
    )
    
    # Add creator as first member with appropriate rank
    creator_rank = CircleRank.LEADER if creator_profile.circle_rank in [CircleRank.INFLUENCER, CircleRank.COMMUNITY_INFLUENCER, CircleRank.BIG_INFLUENCER] else CircleRank.MEMBER
    
    creator_member = CircleMember(
        user_id=creator_profile.name,
        name=creator_profile.name,
        rank=creator_rank,
        fitness_goal=creator_profile.fitness_goal,
        last_active=datetime.now(),
        location=creator_profile.location,
        is_online=True
    )
    
    circle.members.append(creator_member)
    creator_profile.circles_joined.append(circle.circle_id)
    
    return circle

async def join_circle(profile: FitnessProfile, circle: FitnessCircle) -> bool:
    """Add a user to a fitness circle"""
    if len(circle.members) >= circle.max_members:
        return False
    
    if profile.name in [member.user_id for member in circle.members]:
        return False  # Already a member
    
    # Determine initial rank based on profile
    initial_rank = CircleRank.FOLLOWER
    if profile.circle_rank in [CircleRank.INFLUENCER, CircleRank.COMMUNITY_INFLUENCER, CircleRank.BIG_INFLUENCER]:
        initial_rank = CircleRank.MEMBER
    
    new_member = CircleMember(
        user_id=profile.name,
        name=profile.name,
        rank=initial_rank,
        fitness_goal=profile.fitness_goal,
        last_active=datetime.now(),
        location=profile.location,
        is_online=True
    )
    
    circle.members.append(new_member)
    profile.circles_joined.append(circle.circle_id)
    circle.last_activity = datetime.now()
    
    return True

async def create_circle_challenge(
    creator_profile: FitnessProfile,
    circle: FitnessCircle,
    title: str,
    description: str,
    challenge_type: str,
    target_value: int,
    duration_days: int,
    points_reward: int
) -> Optional[CircleChallenge]:
    """Create a new challenge in a fitness circle"""
    
    # Check if user has permission to create challenges
    creator_member = next((m for m in circle.members if m.user_id == creator_profile.name), None)
    if not creator_member or creator_member.rank not in [CircleRank.LEADER, CircleRank.INFLUENCER, CircleRank.COMMUNITY_INFLUENCER, CircleRank.BIG_INFLUENCER]:
        return None
    
    challenge = CircleChallenge(
        challenge_id=str(uuid.uuid4()),
        circle_id=circle.circle_id,
        title=title,
        description=description,
        challenge_type=challenge_type,
        target_value=target_value,
        duration_days=duration_days,
        points_reward=points_reward,
        created_by=creator_profile.name,
        start_date=datetime.now(),
        end_date=datetime.now() + timedelta(days=duration_days)
    )
    
    # Add all circle members as participants
    challenge.participants = [member.user_id for member in circle.members]
    
    return challenge

async def initiate_accountability_check(
    initiator_profile: FitnessProfile,
    circle: FitnessCircle,
    target_members: List[str],
    message: str,
    check_type: str
) -> Optional[AccountabilityCheck]:
    """Initiate an accountability check on specific members"""
    
    # Check if user has permission to initiate checks
    initiator_member = next((m for m in circle.members if m.user_id == initiator_profile.name), None)
    if not initiator_member or initiator_member.rank not in [CircleRank.LEADER, CircleRank.INFLUENCER, CircleRank.COMMUNITY_INFLUENCER, CircleRank.BIG_INFLUENCER]:
        return None
    
    # Verify target members are in the circle
    valid_targets = [member.user_id for member in circle.members if member.user_id in target_members]
    
    check = AccountabilityCheck(
        check_id=str(uuid.uuid4()),
        circle_id=circle.circle_id,
        initiated_by=initiator_profile.name,
        target_members=valid_targets,
        message=message,
        check_type=check_type,
        created_at=datetime.now()
    )
    
    return check

async def create_influencer_post(
    influencer_profile: FitnessProfile,
    circle: FitnessCircle,
    content: str,
    post_type: str,
    media_urls: List[str] = []
) -> Optional[InfluencerPost]:
    """Create a motivational post from an influencer"""
    
    # Check if user is an influencer
    if influencer_profile.circle_rank not in [CircleRank.INFLUENCER, CircleRank.COMMUNITY_INFLUENCER, CircleRank.BIG_INFLUENCER]:
        return None
    
    post = InfluencerPost(
        post_id=str(uuid.uuid4()),
        influencer_id=influencer_profile.name,
        circle_id=circle.circle_id,
        content=content,
        post_type=post_type,
        media_urls=media_urls,
        created_at=datetime.now()
    )
    
    return post

async def generate_circle_notification(
    profile: FitnessProfile,
    circle: FitnessCircle,
    notification_type: NotificationType,
    message: str,
    recipient_ids: List[str] = []
) -> CircleNotification:
    """Generate a circle-specific notification"""
    
    notification = CircleNotification(
        notification_type=notification_type,
        message=message,
        circle_id=circle.circle_id,
        sender_id=profile.name,
        recipient_ids=recipient_ids,
        urgency="medium",
        created_at=datetime.now()
    )
    
    return notification

async def promote_member_rank(circle: FitnessCircle, member_id: str, new_rank: CircleRank) -> bool:
    """Promote a member's rank in the circle"""
    member = next((m for m in circle.members if m.user_id == member_id), None)
    if not member:
        return False
    
    member.rank = new_rank
    circle.last_activity = datetime.now()
    return True

async def update_member_progress(
    circle: FitnessCircle,
    member_id: str,
    steps_taken: int = 0,
    calories_consumed: int = 0,
    workouts_completed: int = 0
) -> bool:
    """Update a member's progress and potentially promote them"""
    member = next((m for m in circle.members if m.user_id == member_id), None)
    if not member:
        return False
    
    # Update member stats
    member.last_active = datetime.now()
    member.is_online = True
    
    # Simple promotion logic based on activity
    if member.current_streak >= 7 and member.rank == CircleRank.FOLLOWER:
        member.rank = CircleRank.MEMBER
    elif member.total_points >= 1000 and member.rank == CircleRank.MEMBER:
        member.rank = CircleRank.LEADER
    
    circle.last_activity = datetime.now()
    return True

async def get_circle_leaderboard(circle: FitnessCircle) -> List[CircleMember]:
    """Get circle leaderboard sorted by points and streaks"""
    return sorted(circle.members, key=lambda x: (x.total_points, x.current_streak), reverse=True)

async def generate_influencer_content(
    influencer_profile: FitnessProfile,
    circle: FitnessCircle
) -> InfluencerPost:
    """Generate AI-powered influencer content"""
    result = await influencer_agent.run(
        f"Generate a motivational post for a {influencer_profile.circle_rank.value} in a {circle.circle_goal.value} circle. "
        f"Make it engaging and specific to the circle's fitness goals.",
        deps=(influencer_profile, circle)
    )
    return result.output

# Enhanced behavioral notification with circle context
async def get_contextual_notification_with_circle(
    profile: FitnessProfile, 
    tracking: DailyTracking, 
    circle: Optional[FitnessCircle] = None
) -> Optional[BehavioralNotification]:
    """Get contextual notification considering circle membership"""
    
    # Get base notification
    base_notification = await get_contextual_notification(profile, tracking)
    
    if circle and base_notification:
        # Enhance notification with circle context
        member = next((m for m in circle.members if m.user_id == profile.name), None)
        if member:
            # Add circle-specific motivation
            if member.rank in [CircleRank.INFLUENCER, CircleRank.COMMUNITY_INFLUENCER, CircleRank.BIG_INFLUENCER]:
                base_notification.message += f"\n\n💪 As a {member.rank.value}, your progress inspires {len(profile.followers)} followers!"
            elif member.current_streak > 0:
                base_notification.message += f"\n\n🔥 You're on a {member.current_streak}-day streak! Keep it up!"
    
    return base_notification

async def analyze_profile(profile: FitnessProfile) -> FitnessReportResult:
    result = await fitness_agent.run("Create a personalized fitness and nutrition plan.", deps=profile)
    return result.output

async def generate_behavioral_notification(profile: FitnessProfile, tracking: DailyTracking) -> BehavioralNotification:
    """Generate contextual behavioral notifications based on real-time progress"""
    result = await behavioral_agent.run(
        "Analyze the user's current progress and generate an appropriate behavioral notification.",
        deps=(profile, tracking)
    )
    return result.output

async def check_step_progress(profile: FitnessProfile, tracking: DailyTracking) -> Optional[BehavioralNotification]:
    """Check if user is behind on step goals and generate appropriate notification"""
    current_time = tracking.current_time or datetime.now().time()
    steps_remaining = tracking.steps_goal - tracking.steps_taken
    
    # If it's past noon and they've taken very few steps
    if current_time >= time(12, 0) and tracking.steps_taken < 2000:
        return BehavioralNotification(
            notification_type=NotificationType.STEP_REMINDER,
            message=f"🚶‍♂️ Only {tracking.steps_taken} steps by noon! You need {steps_remaining} more steps to reach your {tracking.steps_goal} goal. A 30-minute walk could add ~3,000 steps!",
            urgency="high",
            context={"steps_taken": tracking.steps_taken, "steps_goal": tracking.steps_goal, "time": str(current_time)},
            suggested_action="Take a 30-minute walk or break up movement throughout the day"
        )
    
    return None

async def check_meal_logging(profile: FitnessProfile, tracking: DailyTracking) -> Optional[BehavioralNotification]:
    """Check if user has logged their meals and generate appropriate notification"""
    current_time = tracking.current_time or datetime.now().time()
    
    # Check for breakfast logging (before 10 AM)
    if current_time >= time(10, 0) and "breakfast" not in tracking.meals_logged:
        return BehavioralNotification(
            notification_type=NotificationType.MEAL_REMINDER,
            message="🍳 Haven't logged breakfast yet? Starting your day with a balanced meal helps maintain your metabolism and energy levels!",
            urgency="medium",
            context={"meals_logged": tracking.meals_logged, "time": str(current_time)},
            suggested_action="Log your breakfast or plan your next meal"
        )
    
    # Check for lunch logging (around 2 PM)
    elif current_time >= time(14, 0) and "lunch" not in tracking.meals_logged:
        return BehavioralNotification(
            notification_type=NotificationType.MEAL_REMINDER,
            message="🥗 Time for lunch! Don't skip meals - it can lead to overeating later. Aim for protein and veggies to stay on track with your goals.",
            urgency="medium",
            context={"meals_logged": tracking.meals_logged, "time": str(current_time)},
            suggested_action="Log your lunch or plan a healthy meal"
        )
    
    return None

async def check_calorie_progress(profile: FitnessProfile, tracking: DailyTracking) -> Optional[BehavioralNotification]:
    """Check calorie intake vs goals and generate appropriate notification"""
    if profile.fitness_goal == FitnessGoal.WEIGHT_LOSS:
        calories_remaining = tracking.calories_goal - tracking.calories_consumed
        if tracking.calories_consumed > tracking.calories_goal * 0.8:  # 80% of goal
            return BehavioralNotification(
                notification_type=NotificationType.CALORIE_WARNING,
                message=f"⚠️ You've consumed {tracking.calories_consumed} calories today. Only {calories_remaining} calories left to stay within your weight loss target!",
                urgency="high",
                context={"calories_consumed": tracking.calories_consumed, "calories_goal": tracking.calories_goal},
                suggested_action="Choose lower-calorie options for remaining meals"
            )
    
    return None

async def get_contextual_notification(profile: FitnessProfile, tracking: DailyTracking) -> Optional[BehavioralNotification]:
    """Get the most appropriate notification based on current context"""
    # Check step progress first (most urgent)
    step_notification = await check_step_progress(profile, tracking)
    if step_notification:
        return step_notification
    
    # Check meal logging
    meal_notification = await check_meal_logging(profile, tracking)
    if meal_notification:
        return meal_notification
    
    # Check calorie progress
    calorie_notification = await check_calorie_progress(profile, tracking)
    if calorie_notification:
        return calorie_notification
    
    # If no specific issues, generate a general behavioral notification
    return await generate_behavioral_notification(profile, tracking)

