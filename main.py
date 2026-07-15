from typing import Literal
from langgraph.graph import MessagesState
from langgraph.graph import StateGraph, START, END
from langchain.chat_models import init_chat_model
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

llm = init_chat_model("openai:gpt-4o")


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


class InnerFlowState(MessagesState):
    # Input
    user_name: str
    session_type: Literal["morning", "pause", "evening"]
    current_feeling: str

    # Flow Guide
    awareness: str
    reflection_message: str
    mini_practice: str

    activity_plans: list[ActivityPlan]

    # MVP에서는 GPT가 결정
    selected_activity: Literal["yoga", "breathing", "meditation"]

    # Activity Output
    activity_result: str


class FlowGuideOutput(BaseModel):

    awareness: str

    reflection_message: str

    mini_practice: str

    activity_plans: list[ActivityPlan]

    selected_activity: Literal["yoga", "breathing", "meditation"]


class ActivityOutput(BaseModel):
    activity_result: str


def flow_guide_agent(state: InnerFlowState):
    structured_llm = llm.with_structured_output(FlowGuideOutput)
    response = structured_llm.invoke(
        f"""
    너는 InnerFlow의 Flow Guide Agent이다.

    역할
    - 사용자의 현재 상태를 알아차리도록 돕는다.
    - 현재 시점(morning/pause/evening)을 고려한다.
    - 감정을 해결하려 하지 않는다.
    - 짧은 마음챙김 경험을 제공한다.
    - 요가, 호흡, 명상을 모두 추천하지만,
    현재 상태에 가장 적합한 활동 하나를 selected_activity로 선택한다.

    사용자 정보

    이름
    {state["user_name"]}

    현재 시점
    {state["session_type"]}

    현재 상태
    {state["current_feeling"]}

    activity_plans에는

    - yoga
    - breathing
    - meditation

    세 가지 모두 작성한다.

    각 activity에는

    - reason
    - guidance
        - intention
        - tone
        - focus

    를 포함한다.

    selected_activity에는
    가장 추천하는 활동 하나를 선택한다.

    **중요**
    절대로 상담사처럼 말하지 않는다.
    절대로 AI처럼 분석하지 않는다.

    친한 요가 선생님처럼
    따뜻하고 자연스럽게 이야기한다.

    "당신은 ~~입니다."
    같은 표현은 사용하지 않는다.

    "오늘 정말 애쓰셨네요."
    "많이 지치셨겠어요."

    같이 사람에게 이야기하듯 작성한다.

    반드시 아래 형식에 맞게 응답한다.

    awareness:
    현재 상태를 따뜻하게 알아차리는 문장 (2~3문장)

    reflection_message:
    현재 사용자에게 전하고 싶은 짧은 성찰 문장 (1~2문장)

    mini_practice:
    10~20초 정도 수행할 수 있는 아주 짧은 마음챙김 활동

    activity_plans:
    요가, 호흡, 명상을 모두 작성

    selected_activity:
    세 활동 중 하나만 선택
    """
    )

    return {
        "awareness": response.awareness,
        "reflection_message": response.reflection_message,
        "mini_practice": response.mini_practice,
        "activity_plans": response.activity_plans,
        "selected_activity": response.selected_activity,
    }


def activity_router(state: InnerFlowState):
    return state["selected_activity"]


def yoga_agent(state: InnerFlowState):
    plan = next(
        (plan for plan in state["activity_plans"] if plan.activity == "yoga"), None
    )

    if plan is None:
        return {"activity_result": "요가 추천 정보를 찾지 못했습니다."}

    response = llm.invoke(
        f"""
    너는 요가 전문가이다.

    Flow Guide가 이미 사용자의 상태를 분석했다.
    너는 다시 감정을 분석하지 않는다.

    이번 요가의 목적

    {plan.guidance.intention}

    분위기

    {plan.guidance.tone}

    집중할 대상

    {plan.guidance.focus}

    추천 이유

    {plan.reason}

    위 내용을 바탕으로

    1. 시작 안내
    2. 초보자도 가능한 요가 자세 3가지
    3. 각 자세를 추천한 이유
    4. 마무리 한 문장

    을 작성해줘.
    """
    )

    return {"activity_result": response.content}


def breathing_agent(state: InnerFlowState):
    plan = next(
        (plan for plan in state["activity_plans"] if plan.activity == "breathing"), None
    )

    if plan is None:
        return {"activity_result": "호흡 추천 정보를 찾지 못했습니다."}
    response = llm.invoke(
        f"""
        너는 호흡 코치이다.

        Flow Guide가 이미 현재 상태를 분석했다.

        이번 호흡의 목적

        {plan.guidance.intention}

        분위기

        {plan.guidance.tone}

        집중할 대상

        {plan.guidance.focus}

        추천 이유

        {plan.reason}

        약 1분 정도 진행할 수 있는
        호흡 가이드를 작성해줘.

        TTS로 읽기 좋은 자연스러운 문장으로 작성해줘.
        """
    )

    return {"activity_result": response.content}


def meditation_agent(state: InnerFlowState):

    plan = next(
        (plan for plan in state["activity_plans"] if plan.activity == "meditation"),
        None,
    )

    if plan is None:
        return {"activity_result": "명상 추천 정보를 찾지 못했습니다."}

    response = llm.invoke(
        f"""
        너는 명상 가이드이다.

        Flow Guide가 이미 사용자의 상태를 분석했다.

        이번 명상의 목적

        {plan.guidance.intention}

        분위기

        {plan.guidance.tone}

        집중할 대상

        {plan.guidance.focus}

        추천 이유

        {plan.reason}

        약 2분 정도 진행할 수 있는
        초보자용 명상 스크립트를 작성해줘.

        차분하고 따뜻한 말투를 사용해줘.
        """
    )

    return {"activity_result": response.content}


graph_builder = StateGraph(InnerFlowState)

graph_builder.add_node("flow_guide", flow_guide_agent)
graph_builder.add_node("yoga", yoga_agent)
graph_builder.add_node("breathing", breathing_agent)
graph_builder.add_node("meditation", meditation_agent)

graph_builder.add_edge(START, "flow_guide")
graph_builder.add_conditional_edges(
    "flow_guide",
    activity_router,
    {"yoga": "yoga", "breathing": "breathing", "meditation": "meditation"},
)
graph_builder.add_edge("yoga", END)
graph_builder.add_edge("breathing", END)
graph_builder.add_edge("meditation", END)

graph = graph_builder.compile()
