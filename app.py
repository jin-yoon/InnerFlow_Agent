import streamlit as st

from main import graph

st.set_page_config(
    page_title="InnerFlow",
    page_icon="🌿",
)

st.title("🌿 InnerFlow")
st.caption("A small moment to reconnect with yourself.")

name = st.text_input("이름")

SESSION_OPTIONS = {
    "하루의 시작 🌅": "morning",
    "하루를 보내는 중간 ☀️": "pause",
    "하루의 마무리 🌙": "evening",
}

selected_label = st.radio(
    "지금은 당신의 하루 중 어느 순간에 있나요?",
    list(SESSION_OPTIONS.keys()),
)

session_type = SESSION_OPTIONS[selected_label]

feeling = st.text_area(
    "지금 당신의 마음은 어떤가요?",
    placeholder="오늘 하루에 대해, 또는 지금의 마음에 대해 편하게 이야기해주세요.",
)

if st.button("Begin Today's InnerFlow"):

    with st.spinner("Listening to your flow..."):

        result = graph.invoke(
            {
                "user_name": name,
                "session_type": session_type,
                "current_feeling": feeling,
            }
        )

    st.divider()

    st.subheader("🌿 Awareness")
    st.write(result["awareness"])

    st.subheader("✨ Reflection")
    st.write(result["reflection_message"])

    st.subheader("🌬 Mini Practice")
    st.write(result["mini_practice"])

    st.divider()

    st.subheader(f"Recommended Activity : {result['selected_activity'].title()}")

    selected = next(
        p for p in result["activity_plans"] if p.activity == result["selected_activity"]
    )

    st.write(selected.reason)

    st.divider()

    st.subheader("Activity")

    st.write(result["activity_result"])
