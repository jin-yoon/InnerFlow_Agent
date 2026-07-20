from agents.innerflow_states import InnerFlowState


def activity_router(state: InnerFlowState) -> str:
    selected_activity = state.get("selected_activity")

    if selected_activity in {
        "yoga",
        "breathing",
        "meditation",
    }:
        return selected_activity

    raise ValueError(f"지원하지 않는 활동입니다: {selected_activity}")
