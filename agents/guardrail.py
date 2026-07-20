from langchain.chat_models import init_chat_model

from agents.innerflow_states import (
    InnerFlowState,
    GuardrailOutput,
)


llm = init_chat_model("openai:gpt-4o")


def input_guardrail(
    state: InnerFlowState,
):

    structured_llm = llm.with_structured_output(GuardrailOutput)

    result = structured_llm.invoke(
        f"""
        너는 InnerFlow의 입력 검증 Guardrail이다.

        InnerFlow는 사용자가 자신의 마음과 몸의 상태를
        잠시 돌아보고, 현재 순간에 머물 수 있도록 돕는
        mindfulness와 wellness companion이다.

        사용자의 입력이 InnerFlow의 목적과 자연스럽게
        연결될 수 있는 내용인지 판단한다.


        [사용자 입력]
        {state["current_feeling"]}


        ## 판단 기준

        다음과 같은 내용은 적합한 입력이다.

        - 현재의 감정이나 기분에 대한 이야기
        - 몸이나 마음의 현재 상태
        - 오늘 하루에 대한 이야기
        - 스트레스, 피로, 긴장, 불안 등에 대한 이야기
        - 휴식이나 회복이 필요하다는 표현
        - 집중하거나 마음을 안정시키고 싶은 상태
        - 자신을 돌보고 싶은 마음
        - 요가, 호흡, 명상, 마음챙김 등
        InnerFlow 활동과 관련된 질문
        - 사용자의 웰니스와 자기돌봄에 도움이 될 수 있는 질문


        다음과 같은 내용은 부적합한 입력이다.

        - 프로그래밍 코드 작성이나 수정
        - 일반적인 기술 문제 해결
        - 수학 문제 풀이
        - 쇼핑이나 상품 추천
        - 여행 계획이나 맛집 추천
        - 일반적인 업무 요청
        - 번역이나 문서 작성
        - 기타 InnerFlow의 목적과 직접적인 관련이 없는 요청


        ## 중요한 판단 원칙

        입력이 짧거나 표현이 모호하더라도
        사용자의 현재 상태나 웰니스와 연결될 가능성이 있다면
        가능한 한 적합한 입력으로 판단한다.

        사용자가 자신의 감정을 명확하게 표현하지 않았다고 해서
        자동으로 부적합하다고 판단하지 않는다.


        ## Response 생성

        is_relevant가 True라면 response는 빈 문자열로 작성한다.

        is_relevant가 False라면 사용자의 요청에 맞춰
        짧고 따뜻한 안내 메시지를 작성한다.

        응답은 다음의 구조를 따른다.

        1. InnerFlow가 어떤 서비스를 제공하는지 간단하게 설명한다.
        2. 사용자가 요청한 내용은 InnerFlow에서 도와줄 수 없다고
        자연스럽게 알려준다.
        3. 대신 사용자가 자신의 마음이나 하루의 상태를
        편하게 이야기하도록 유도한다.

        사용자가 요청한 내용을 구체적으로 언급해도 좋다.

        예:

        사용자:
        "Java 코드 작성해줘"

        응답:
        "InnerFlow는 지금 당신의 마음이나 하루의 상태를
        함께 살펴보는 공간이에요.
        Java 코드 작성과 같은 도움을 드릴 수는 없지만,
        지금 어떤 기분인지, 오늘 하루는 어땠는지
        편하게 이야기해주세요. 🌿"


        응답은 2~3문장 이내로 작성한다.
        너무 딱딱하거나 기계적인 표현은 피한다.
        친절하고 따뜻한 InnerFlow의 분위기를 유지한다.
        """
    )

    if result.is_relevant:

        return {
            "is_relevant": True,
            "guardrail_message": "",
        }

    return {
        "is_relevant": False,
        "guardrail_message": result.response,
    }


def guardrail_router(state: InnerFlowState):
    if state["is_relevant"]:
        return "flow_guide"
    return "end"
