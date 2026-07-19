import streamlit as st

from main import graph


# -------------------------
# Session State
# -------------------------

if "result" not in st.session_state:
    st.session_state.result = None


# -------------------------
# Page
# -------------------------

st.set_page_config(
    page_title="InnerFlow",
    page_icon="🌿",
)

st.title("🌿 InnerFlow")
st.caption("A small moment to reconnect with yourself.")


# -------------------------
# Input
# -------------------------

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


# -------------------------
# Run InnerFlow
# -------------------------

if st.button("Begin Today's InnerFlow"):
    with st.spinner("Listening to your flow..."):
        st.session_state.result = graph.invoke(
            {
                "user_name": name,
                "session_type": session_type,
                "current_feeling": feeling,
            }
        )


# -------------------------
# Display Result
# -------------------------

result = st.session_state.result

if result:

    st.divider()

    st.subheader("🌿 Awareness")
    st.write(result["awareness"])

    st.subheader("✨ Reflection")
    st.write(result["reflection_message"])

    st.subheader("🌬 Mini Practice")
    st.write(result["mini_practice"])

    st.divider()

    st.subheader(f"Recommended Activity : " f"{result['selected_activity'].title()}")

    selected = next(
        p for p in result["activity_plans"] if p.activity == result["selected_activity"]
    )

    st.write(selected.reason)

    st.divider()

    st.subheader("Activity")

    # =========================================================
    # Yoga
    # =========================================================
    if result["selected_activity"] == "yoga":

        yoga_output = result.get("yoga_output")

        if yoga_output:

            st.write(f"### {yoga_output.yoga_class.title()}")

            st.write(yoga_output.class_reason)

            image_path = result.get("yoga_image_path")
            if image_path:

                st.image(
                    image_path,
                    caption="Today's Yoga Flow",
                    use_container_width=True,
                )
            for i, pose in enumerate(
                yoga_output.poses,
                1,
            ):

                st.write(f"**{i}. {pose.name}**")

                st.write(pose.reason)

                st.write(pose.instruction)

            st.write(yoga_output.closing_message)

    # =========================================================
    # Meditation
    # =========================================================

    elif result["selected_activity"] == "meditation":

        meditation_output = result.get("meditation_output")

        if meditation_output:

            st.write(f"### {meditation_output.title}")

            st.write(f"🧘 {meditation_output.meditation_type}")

            st.write(f"⏱️ " f"{meditation_output.duration_minutes} minutes")

            st.write(meditation_output.introduction)

            st.divider()

            audio_path = result.get("meditation_audio_path")

            if audio_path:

                st.audio(
                    audio_path,
                    format="audio/mp3",
                )

            else:

                st.warning("Meditation audio was not generated.")

            st.write(meditation_output.script)

            st.divider()

            st.write(meditation_output.closing_message)

    # =========================================================
    # breathing
    # =========================================================

    elif result["selected_activity"] == "breathing":

        breathing_output = result.get("breathing_output")

        if breathing_output:

            st.write(f"### {breathing_output.title}")

            st.write(f"🫁 " f"{breathing_output.breathing_pattern}")

            st.write(f"⏱️ " f"{breathing_output.duration_minutes} minutes")

            st.write(breathing_output.introduction)

            st.divider()

            audio_path = result.get("breathing_audio_path")

            if audio_path:

                st.audio(
                    audio_path,
                    format="audio/mp3",
                )

            else:

                st.warning("Breathing audio was not generated.")

            st.divider()

            st.write(breathing_output.closing_message)
