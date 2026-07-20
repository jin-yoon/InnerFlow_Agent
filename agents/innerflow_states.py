from typing import Literal
from langgraph.graph import MessagesState
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()


# =========================================================
# Guardrail
# =========================================================
class GuardrailOutput(BaseModel):
    is_relevant: bool
    response: str


# =========================================================
# FlowGuide
# =========================================================
class ActivityGuidance(BaseModel):
    intention: str

    tone: Literal[
        "energizing",
        "grounding",
        "calming",
        "restorative",
    ]

    focus: Literal[
        "body",
        "breath",
        "mind",
        "gratitude",
        "self_compassion",
    ]


class ActivityPlan(BaseModel):
    activity: Literal[
        "yoga",
        "breathing",
        "meditation",
    ]

    # 사용자에게 보여줄 추천 이유
    reason: str

    # Activity Agent에게 전달할 내부 정보
    guidance: ActivityGuidance


class FlowGuideOutput(BaseModel):

    awareness: str

    reflection_message: str

    mini_practice: str

    activity_plans: list[ActivityPlan]

    selected_activity: Literal["yoga", "breathing", "meditation"]


# =========================================================
# Yoga
# =========================================================


class YogaPose(BaseModel):
    name: str
    reason: str
    instruction: str


class YogaOutput(BaseModel):
    yoga_class: Literal[
        "vinyasa",
        "hatha",
        "ashtanga",
        "yin",
    ]

    class_reason: str

    poses: list[YogaPose] = Field(min_length=5, max_length=5)

    closing_message: str


# =========================================================
# Meditation
# =========================================================
class MeditationOutput(BaseModel):

    meditation_type: Literal[
        "breathing_meditation",
        "body_scan",
        "mindfulness",
        "self_compassion",
        "gratitude",
    ]

    duration_minutes: Literal[
        3,
        5,
        10,
    ]

    title: str

    introduction: str

    script: str

    background_music: Literal[
        "piano",
        "rain",
        "forest",
        # "none",
    ]

    closing_message: str


class ActivityOutput(BaseModel):
    activity_result: str


# =========================================================
# Breathiing
# =========================================================
class BreathingOutput(BaseModel):

    breathing_pattern: Literal[
        "box_breathing",
        "4_6_breathing",
        "4_7_8_breathing",
        "coherent_breathing",
        "natural_breathing",
    ]

    duration_minutes: Literal[
        1,
        3,
        5,
    ]

    title: str

    introduction: str

    script: str

    inhale_seconds: int

    hold_seconds: int

    exhale_seconds: int

    sound: Literal[
        "birds",
        "ocean",
        "singing_bowl",
    ]

    closing_message: str


# =========================================================
# InnerFlow State
# =========================================================
class InnerFlowState(MessagesState):

    # Input
    user_name: str

    session_type: Literal[
        "morning",
        "pause",
        "evening",
    ]

    current_feeling: str

    # Guardrail
    is_relevant: bool | None = None
    guardrail_message: str | None = None

    # Flow Guide
    awareness: str

    reflection_message: str

    mini_practice: str

    activity_plans: list[ActivityPlan]

    # Activity Router
    selected_activity: Literal["yoga", "breathing", "meditation"] | None

    # Activity Outputs
    yoga_output: YogaOutput | None = None

    breathing_output: BreathingOutput | None = None

    meditation_output: MeditationOutput | None = None

    # Activity Assets
    yoga_image_path: str | None = None

    breathing_audio_path: str | None = None

    meditation_audio_path: str | None = None
