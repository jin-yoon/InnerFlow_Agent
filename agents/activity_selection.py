from langgraph.types import interrupt
from agents.innerflow_states import InnerFlowState


def activity_selection_node(
    state: InnerFlowState,
):
    """
    Pause the graph after Flow Guide recommendations
    and wait for the user's activity selection.
    """

    selected_activity = interrupt(
        {
            "type": "activity_selection",
            "message": "어떤 활동을 함께해볼까요?",
            "options": [
                "yoga",
                "breathing",
                "meditation",
            ],
            "activity_plans": state.get(
                "activity_plans",
                [],
            ),
        }
    )

    return {
        "selected_activity": selected_activity,
    }


def activity_router(
    state: InnerFlowState,
):
    return state["selected_activity"]
