from agents.innerflow_states import InnerFlowState
from agents.flow_guide import flow_guide_agent
from agents.activity_selection import activity_router
from agents.yoga import yoga_agent, yoga_tool_caller, yoga_tool_node, save_yoga_image
from agents.meditation import meditation_agent, meditation_audio_generator
from agents.breathing import breathing_agent, breathing_audio_generator
from langgraph.graph import StateGraph, START, END
from agents.guardrail import input_guardrail, guardrail_router


# =========================================================
# Router
# =========================================================


def start_router(state: InnerFlowState) -> str:
    """
    첫 실행인지, 활동 실행인지 구분합니다.

    selected_activity가 없으면:
        Guardrail → Flow Guide

    selected_activity가 있으면:
        선택한 활동 실행
    """

    selected_activity = state.get("selected_activity")

    if selected_activity in {
        "yoga",
        "breathing",
        "meditation",
    }:
        return "activity"

    return "flow_guide"


def activity_router_node(
    state: InnerFlowState,
):
    """
    실제 작업은 하지 않고,
    activity_router가 다음 노드를 결정하도록 하는 중간 노드입니다.
    """

    return {}


# =========================================================
# Graph
# =========================================================
graph_builder = StateGraph(InnerFlowState)

graph_builder.add_node("input_guardrail", input_guardrail)
graph_builder.add_node("flow_guide", flow_guide_agent)
graph_builder.add_node("activity_router", activity_router_node)

graph_builder.add_node("yoga", yoga_agent)
graph_builder.add_node("yoga_tool_caller", yoga_tool_caller)
graph_builder.add_node("yoga_image_tool", yoga_tool_node)
graph_builder.add_node("save_yoga_image", save_yoga_image)

graph_builder.add_node("meditation", meditation_agent)
graph_builder.add_node("meditation_audio_generator", meditation_audio_generator)

graph_builder.add_node("breathing", breathing_agent)
graph_builder.add_node("breathing_audio_generator", breathing_audio_generator)

# =========================================================
# Start
# =========================================================

graph_builder.add_conditional_edges(
    START,
    start_router,
    {
        "flow_guide": "input_guardrail",
        "activity": "activity_router",
    },
)
graph_builder.add_conditional_edges(
    "input_guardrail",
    guardrail_router,
    {
        "flow_guide": "flow_guide",
        "end": END,
    },
)

graph_builder.add_edge("flow_guide", END)

graph_builder.add_conditional_edges(
    "activity_router",
    activity_router,
    {
        "yoga": "yoga",
        "breathing": "breathing",
        "meditation": "meditation",
    },
)


graph_builder.add_edge("yoga", "yoga_tool_caller")
graph_builder.add_edge("yoga_tool_caller", "yoga_image_tool")
graph_builder.add_edge("yoga_image_tool", "save_yoga_image")
graph_builder.add_edge("save_yoga_image", END)


graph_builder.add_edge("meditation", "meditation_audio_generator")
graph_builder.add_edge("meditation_audio_generator", END)

graph_builder.add_edge("breathing", "breathing_audio_generator")
graph_builder.add_edge("breathing_audio_generator", END)

graph = graph_builder.compile()
