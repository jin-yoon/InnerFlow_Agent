from agents.innerflow_states import InnerFlowState
from agents.flow_guide import flow_guide_agent
from agents.activity_selection import activity_router, activity_selection_node
from agents.yoga import yoga_agent, yoga_tool_caller, yoga_tool_node, save_yoga_image
from agents.meditation import meditation_agent, meditation_audio_generator
from agents.breathing import breathing_agent, breathing_audio_generator
from langgraph.graph import StateGraph, START, END
from agents.guardrail import input_guardrail, guardrail_router
from langgraph.checkpoint.memory import InMemorySaver

checkpointer = InMemorySaver()

graph_builder = StateGraph(InnerFlowState)

graph_builder.add_node("input_guardrail", input_guardrail)

graph_builder.add_node("flow_guide", flow_guide_agent)

graph_builder.add_node("activity_selection", activity_selection_node)

graph_builder.add_node("yoga", yoga_agent)
graph_builder.add_node("yoga_tool_caller", yoga_tool_caller)
graph_builder.add_node("yoga_image_tool", yoga_tool_node)
graph_builder.add_node("save_yoga_image", save_yoga_image)

graph_builder.add_node("meditation", meditation_agent)
graph_builder.add_node("meditation_audio_generator", meditation_audio_generator)

graph_builder.add_node("breathing", breathing_agent)
graph_builder.add_node("breathing_audio_generator", breathing_audio_generator)

graph_builder.add_edge(START, "input_guardrail")
graph_builder.add_conditional_edges(
    "input_guardrail",
    guardrail_router,
    {
        "flow_guide": "flow_guide",
        "end": END,
    },
)

graph_builder.add_edge("flow_guide", "activity_selection")

graph_builder.add_conditional_edges(
    "activity_selection",
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

graph = graph_builder.compile(
    checkpointer=checkpointer,
)
