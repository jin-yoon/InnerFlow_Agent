from agents.innerflow_states import InnerFlowState, YogaOutput
from langchain.chat_models import init_chat_model
from langgraph.prebuilt import ToolNode
from openai import OpenAI
from langchain_core.tools import tool
import base64
import uuid
from pathlib import Path

llm = init_chat_model("openai:gpt-4o")


@tool
def generate_yoga_image(
    yoga_class: str,
    pose_names: list[str],
) -> str:
    """
    선택된 요가 스타일과 5개의 요가 자세를 기반으로 하나의 요가 안내 이미지를 생성한다.

    """

    prompt = f"""
    Create one beautiful instructional yoga sequence image
    for a wellness application.

    Yoga style:
    {yoga_class}

    Create a single image containing exactly these
    five yoga poses:

    1. {pose_names[0]}
    2. {pose_names[1]}
    3. {pose_names[2]}
    4. {pose_names[3]}
    5. {pose_names[4]}

    Show all five poses clearly in one image.

    Arrange the five poses in a clean and balanced layout.

    Each pose should be visually distinct
    and easy for a beginner to identify.

    IMPORTANT:
    Display the exact pose name next to or below
    each corresponding yoga pose.

    Use a calm, warm, minimal wellness aesthetic.

    Use a simple and clean background.
    """

    client = OpenAI()

    result = client.images.generate(
        model="gpt-image-1",
        prompt=prompt,
        quality="medium",
        size="1024x1024",
    )

    image_bytes = base64.b64decode(result.data[0].b64_json)

    output_dir = Path("generated_images")
    output_dir.mkdir(exist_ok=True)

    filename = output_dir / f"yoga_{uuid.uuid4().hex}.png"

    with open(filename, "wb") as file:
        file.write(image_bytes)

    return str(filename)


yoga_tool_node = ToolNode([generate_yoga_image])


def yoga_agent(
    state: InnerFlowState,
):

    # -----------------------------------------------------
    # Flow Guide가 만든 Yoga Plan 가져오기
    # -----------------------------------------------------

    plan = next(
        (plan for plan in state["activity_plans"] if plan.activity == "yoga"),
        None,
    )

    if plan is None:

        return {"activity_result": "요가 추천 정보를 찾지 못했습니다."}

    # -----------------------------------------------------
    # Yoga Content 생성
    # -----------------------------------------------------

    structured_llm = llm.with_structured_output(YogaOutput)

    yoga_output = structured_llm.invoke(
        f"""
        너는 InnerFlow의 요가 전문가이다. 언어는 반드시 사용자 언어 기반으로 작성한다.
        사용자 입력 언어 : {state["current_feeling"]}

        Flow Guide가 이미 사용자의 상태를 분석하고
        이번 요가 경험의 방향을 설계했다.

        너는 사용자의 감정이나 상태를
        다시 분석하거나 재해석하지 않는다.

        Flow Guide가 설계한 방향을 바탕으로
        사용자에게 적절한 요가 경험을 설계한다.


        [이번 요가의 목적]
        {plan.guidance.intention}


        [요가의 분위기]
        {plan.guidance.tone}


        [집중할 대상]
        {plan.guidance.focus}


        [Flow Guide의 추천 이유]
        {plan.reason}


        다음 네 가지 요가 스타일 중 이번 요가의 목적과 분위기에 가장 적합한 하나를 선택한다.
            - vinyasa
            - hatha
            - ashtanga
            - yin


        선택한 요가 스타일이 현재 Flow Guide의 방향에 적합한 이유를 class_reason에 작성한다.

        그리고 선택한 요가 스타일과
        Flow Guide가 설계한 목적에 적합한
        초보자도 수행할 수 있는
        요가 자세 5가지를 선택한다.

        각 요가 자세에 대해 다음 세 가지를 작성한다.


        1. name
        사용자가 알아보기 쉬운 정확한 요가 자세 이름은 영어로 저장한다.

        2. reason
        이번 요가 경험에서 이 자세를 추천하는 이유를 작성한다.

        3. instruction
        초보자가 따라 할 수 있도록
        간단하고 이해하기 쉬운
        자세 설명을 작성한다.


        5개의 자세는 서로 적절하게 연결되어
        하나의 요가 경험처럼 느껴지도록 구성한다.


        마지막에는 오늘의 요가 경험을
        마무리하는 따뜻한 closing_message를 작성한다.
        """
    )

    # -----------------------------------------------------
    # State에 Yoga Output 저장
    # -----------------------------------------------------

    return {
        "yoga_output": yoga_output,
    }


# =========================================================
# Yoga Tool Caller
# =========================================================


def yoga_tool_caller(
    state: InnerFlowState,
):

    yoga_output = state["yoga_output"]

    if yoga_output is None:

        return {"activity_result": "요가 정보를 생성하지 못했습니다."}

    image_path = generate_yoga_image.invoke(
        {
            "yoga_class": yoga_output.yoga_class,
            "pose_names": [pose.name for pose in yoga_output.poses],
        }
    )

    return {
        "yoga_image_path": image_path,
    }


# def save_yoga_image(state: InnerFlowState):

#     last_message = state["messages"][-1]

#     if not isinstance(last_message, ToolMessage):
#         raise ValueError("마지막 메시지가 ToolMessage가 아닙니다.")

#     image_path = last_message.content

#     return {"yoga_image_path": image_path}
