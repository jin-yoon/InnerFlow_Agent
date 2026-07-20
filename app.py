import uuid
import streamlit as st
from main import graph


# =========================================================
# Page Config
# =========================================================

st.set_page_config(
    page_title="InnerFlow",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# =========================================================
# Style
# =========================================================

st.markdown(
    """
    <style>
    :root {
        --background: #fafcf9;
        --surface: #ffffff;
        --surface-soft: #f0f6ef;
        --primary: #6f8f78;
        --primary-hover: #5f7d68;
        --primary-dark: #2f4a37;
        --accent: #e7f0e5;
        --border: #e3ebe1;
        --text: #2f4135;
        --muted: #738077;
        --shadow: 0 18px 48px rgba(74, 98, 78, 0.08);
    }

    html,
    body,
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"] {
        background-color: #FAFCFA !important;
        color: #294332 !important;
    }

    [data-testid="stWidgetLabel"] p,
    .stRadio label,
    .stTextInput label,
    .stTextArea label {
        color: #52665A !important;
    }

    .stTextInput input,
    .stTextArea textarea {
        color: #294332 !important;
        background-color: #FFFFFF !important;
        -webkit-text-fill-color: #294332 !important;
    }

    .stTextInput input::placeholder,
    .stTextArea textarea::placeholder {
        color: #9AA99F !important;
        -webkit-text-fill-color: #9AA99F !important;
        opacity: 1 !important;
    }

    .stRadio div[role="radiogroup"] label p {
        color: #52665A !important;
    }
    [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }

    .stApp {
        background:
            radial-gradient(circle at 84% 8%, rgba(221, 235, 218, 0.62), transparent 25%),
            linear-gradient(180deg, #ffffff 0%, var(--background) 100%);
        color: var(--text);
    }

    .block-container {
        max-width: 1120px;
        padding-top: 1.5rem;
        padding-bottom: 4rem;
    }

    header[data-testid="stHeader"] {
        background: transparent;
    }

    #MainMenu,
    footer {
        visibility: hidden;
    }

    .innerflow-brand {
        color: var(--primary-dark);
        font-size: 1.55rem;
        font-weight: 720;
        letter-spacing: -0.03em;
        margin: 0.15rem 0 0.35rem;
    }

    .innerflow-caption {
        color: var(--muted);
        font-size: 0.95rem;
        margin-bottom: 2.5rem;
    }

    .center-page {
        text-align: center;
        padding-top: 4rem;
    }

    .page-title {
        max-width: 790px;
        margin: 0 auto 0.8rem;
        color: var(--primary-dark);
        font-size: clamp(2rem, 4vw, 3.35rem);
        line-height: 1.22;
        font-weight: 750;
        letter-spacing: -0.045em;
    }

    .page-subtitle {
        color: var(--muted);
        font-size: 1rem;
        line-height: 1.75;
        margin-bottom: 2.4rem;
    }

    .flow-card {
        background: rgba(255, 255, 255, 0.88);
        border: 1px solid var(--border);
        border-radius: 24px;
        padding: 1.65rem;
        margin-bottom: 1rem;
        box-shadow: var(--shadow);
        backdrop-filter: blur(12px);
    }

    .card-title {
        color: var(--primary-dark);
        font-size: 1.08rem;
        font-weight: 720;
        margin-bottom: 0.7rem;
        letter-spacing: -0.02em;
    }

    .recommendation-card {
        position: relative;
        overflow: hidden;
        max-width: 900px;
        min-height: 235px;
        margin: 1.2rem auto 1.25rem;
        padding: 2.1rem 2.3rem;
        border: 1px solid #dce7d9;
        border-radius: 28px;
        text-align: left;
        background:
            radial-gradient(circle at 88% 78%, rgba(255,255,255,0.85) 0 7%, transparent 8%),
            radial-gradient(ellipse at 91% 92%, rgba(139, 166, 136, 0.30) 0 20%, transparent 21%),
            radial-gradient(ellipse at 78% 98%, rgba(177, 199, 171, 0.30) 0 28%, transparent 29%),
            linear-gradient(105deg, #ffffff 0%, #f8fbf7 48%, #e5efe2 100%);
        box-shadow: 0 24px 60px rgba(72, 98, 76, 0.10);
    }

    .recommendation-card::after {
        content: "";
        position: absolute;
        right: -5%;
        bottom: -40px;
        width: 56%;
        height: 125px;
        opacity: 0.75;
        border-radius: 50% 50% 0 0;
        background:
            repeating-radial-gradient(
                ellipse at center,
                transparent 0 16px,
                rgba(111, 143, 120, 0.14) 17px 18px
            );
        transform: rotate(-4deg);
    }

    .recommendation-label {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        padding: 0.38rem 0.72rem;
        border-radius: 999px;
        background: rgba(232, 241, 229, 0.92);
        color: var(--primary);
        font-size: 0.88rem;
        font-weight: 700;
        margin-bottom: 1.25rem;
    }

    .recommendation-title {
        color: var(--primary-dark);
        font-size: 2rem;
        font-weight: 760;
        letter-spacing: -0.04em;
        margin-bottom: 0.85rem;
    }

    .recommendation-reason {
        position: relative;
        z-index: 1;
        max-width: 58%;
        color: #5c6e61;
        font-size: 1rem;
        line-height: 1.8;
    }

    .selection-note {
        text-align: center;
        color: var(--muted);
        font-size: 0.94rem;
        line-height: 1.75;
        margin: 1.25rem 0 2rem;
    }

    .activity-card {
        min-height: 250px;
        background: rgba(255, 255, 255, 0.94);
        border: 1px solid var(--border);
        border-radius: 24px;
        padding: 1.5rem 1.25rem;
        margin-bottom: 0.75rem;
        text-align: center;
        box-shadow: 0 14px 34px rgba(67, 92, 72, 0.07);
        transition: transform 180ms ease, box-shadow 180ms ease, border-color 180ms ease;
    }

    .activity-card:hover {
        transform: translateY(-3px);
        border-color: #cadac7;
        box-shadow: 0 22px 44px rgba(67, 92, 72, 0.11);
    }

    .activity-icon-shell {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 84px;
        height: 84px;
        margin: 0 auto 1.15rem;
        border-radius: 28px;
        background:
            radial-gradient(circle at 30% 25%, rgba(255,255,255,0.92), transparent 34%),
            linear-gradient(145deg, #f0f7ed, #dcead8);
        border: 1px solid rgba(111, 143, 120, 0.16);
        box-shadow:
            inset 0 1px 0 rgba(255,255,255,0.9),
            0 12px 24px rgba(78, 105, 82, 0.10);
        font-size: 2.35rem;
        line-height: 1;
        transform: rotate(-2deg);
        transition: transform 180ms ease;
    }

    .activity-card:hover .activity-icon-shell {
        transform: translateY(-2px) rotate(2deg) scale(1.03);
    }

    .activity-name {
        color: var(--primary-dark);
        font-size: 1.3rem;
        font-weight: 740;
        letter-spacing: -0.025em;
        margin-bottom: 0.75rem;
    }

    .activity-description {
        color: var(--muted);
        line-height: 1.75;
        font-size: 0.94rem;
    }

    .footer-message {
        max-width: 900px;
        margin: 2.2rem auto 0;
        padding: 1.15rem 1.5rem;
        text-align: center;
        color: #65756a;
        border-radius: 22px;
        background: linear-gradient(90deg, #f5f9f3, #edf4eb);
        border: 1px solid #e2ebe0;
    }

    .stButton > button,
    .stFormSubmitButton > button {
        min-height: 48px;
        border: 1px solid transparent;
        border-radius: 16px;
        background: linear-gradient(135deg, #7f9f87, #6d8e76);
        color: white;
        font-weight: 680;
        box-shadow: 0 8px 20px rgba(93, 126, 99, 0.16);
        transition: all 160ms ease;
    }

    .stButton > button:hover,
    .stFormSubmitButton > button:hover {
        background: linear-gradient(135deg, #71947a, #5f8068);
        color: white;
        border-color: transparent;
        transform: translateY(-1px);
        box-shadow: 0 12px 24px rgba(93, 126, 99, 0.22);
    }

    .stButton > button:focus:not(:active),
    .stFormSubmitButton > button:focus:not(:active) {
        border-color: #a7bfa8;
        box-shadow: 0 0 0 0.2rem rgba(111, 143, 120, 0.18);
    }

    /* Text input */
    .stTextInput input {
        background: #FFFFFF !important;
        color: #294332 !important;
        border: 1px solid #DCE8DE !important;
        border-radius: 18px !important;
        box-shadow: none !important;
        outline: none !important;
    }

    /* Text area */
    .stTextArea textarea {
        background: #FFFFFF !important;
        color: #294332 !important;
        border: 1px solid #DCE8DE !important;
        border-radius: 18px !important;
        box-shadow: none !important;
        outline: none !important;
    }

    .stTextInput input:focus,
    .stTextArea textarea:focus {
        border: 1.5px solid #6C8B74 !important;
        box-shadow: 0 0 0 2px rgba(108, 139, 116, 0.12) !important;
        outline: none !important;
    }

    div[data-testid="stExpander"] {
        border: 1px solid var(--border);
        border-radius: 18px;
        background: rgba(255,255,255,0.88);
    }

    div[data-testid="stAlert"] {
        border-radius: 18px;
    }

    audio {
        width: 100%;
    }

    .finish-quote {
        background: linear-gradient(135deg, #f3f8f1, #e9f1e6);
        border: 1px solid #dce8da;
        border-radius: 24px;
        padding: 1.9rem;
        color: var(--primary-dark);
        font-size: 1.2rem;
        line-height: 1.75;
        margin: 2rem 0;
    }

    @media (max-width: 760px) {
        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }

        .center-page {
            padding-top: 2rem;
        }

        .recommendation-card {
            min-height: auto;
            padding: 1.6rem;
        }

        .recommendation-reason {
            max-width: 100%;
        }
    }
    /* Text input 바깥 검은 테두리 제거 */
    [data-testid="stTextInput"] [data-baseweb="input"] {
        border: 1px solid #DCE8DE !important;
        box-shadow: none !important;
        background: #FFFFFF !important;
        border-radius: 18px !important;
    }

    /* Textarea 바깥 검은 테두리 제거 */
    [data-testid="stTextArea"] [data-baseweb="textarea"] {
        border: 1px solid #DCE8DE !important;
        box-shadow: none !important;
        background: #FFFFFF !important;
        border-radius: 18px !important;
    }

    /* 안쪽 input/textarea는 테두리 제거 */
    [data-testid="stTextInput"] input,
    [data-testid="stTextArea"] textarea {
        border: none !important;
        box-shadow: none !important;
        outline: none !important;
        background: transparent !important;
        color: #294332 !important;
    }

    /* 포커스 시에도 검정색 그림자 방지 */
    [data-testid="stTextInput"] [data-baseweb="input"]:focus-within,
    [data-testid="stTextArea"] [data-baseweb="textarea"]:focus-within {
        border: 1.5px solid #6C8B74 !important;
        box-shadow: 0 0 0 3px rgba(108, 139, 116, 0.12) !important;
    }

    /* Yoga expander 전체 박스 */
    [data-testid="stExpander"] {
        background-color: #FFFFFF !important;
        border: 1px solid #DCE8DE !important;
        border-radius: 18px !important;
        overflow: hidden !important;
        box-shadow: none !important;
    }

    /* Expander 제목 영역 */
    [data-testid="stExpander"] summary {
        background-color: #FFFFFF !important;
        color: #294332 !important;
        border-radius: 18px !important;
    }

    /* 펼쳐진 expander 제목 영역 */
    [data-testid="stExpander"] details[open] summary {
        background-color: #EDF5EE !important;
        color: #294332 !important;
    }

    /* 제목 글자 */
    [data-testid="stExpander"] summary p {
        color: #294332 !important;
        font-weight: 600 !important;
    }

    /* 왼쪽 화살표 아이콘 */
    [data-testid="stExpander"] summary svg {
        fill: #6C8B74 !important;
        color: #6C8B74 !important;
    }

    /* 펼쳐진 본문 */
    [data-testid="stExpander"] details > div {
        background-color: #FFFFFF !important;
        color: #294332 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# Session State
# =========================================================

DEFAULT_SESSION_STATE = {
    "page": "welcome",
    "result": None,
    "user_name": "",
    "session_type": "morning",
    "current_feeling": "",
}

for key, value in DEFAULT_SESSION_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = value


# =========================================================
# Utility
# =========================================================


def render_brand(show_home: bool = False):
    left, right = st.columns([8, 1])

    with left:
        st.markdown(
            """
            <div class="innerflow-brand">
                🌿 InnerFlow
            </div>
            """,
            unsafe_allow_html=True,
        )

    # if show_home:
    #     with right:
    #         if st.button(
    #             "🏠",
    #             key=f"home_{st.session_state.page}",
    #             help="처음으로 돌아가기",
    #             use_container_width=True,
    #         ):
    #             reset_innerflow()
    #             st.rerun()


def reset_innerflow():
    st.session_state.page = "welcome"
    st.session_state.result = None
    st.session_state.user_name = ""
    st.session_state.session_type = "morning"
    st.session_state.current_feeling = ""


def get_activity_plan(activity_name: str):
    result = st.session_state.result or {}
    activity_plans = result.get("activity_plans", [])

    return next(
        (plan for plan in activity_plans if plan.activity == activity_name),
        None,
    )


def get_activity_label(activity_name: str):
    labels = {
        "yoga": "요가",
        "breathing": "호흡",
        "meditation": "명상",
    }

    return labels.get(activity_name, activity_name)


# =========================================================
# 1. Welcome Page
# =========================================================


def render_welcome_page():
    render_brand()

    st.markdown(
        """
        <div class="innerflow-caption">
            A small moment to reconnect with yourself.
        </div>
        """,
        unsafe_allow_html=True,
    )

    left, center, right = st.columns([1, 2.2, 1])

    with center:
        with st.form("welcome_form"):
            name = st.text_input(
                "이름",
                value=st.session_state.user_name,
                placeholder="당신의 이름을 알려주세요.",
            )

            session_options = {
                "하루의 시작 🌅": "morning",
                "하루를 보내는 중간 ☀️": "pause",
                "하루의 마무리 🌙": "evening",
            }

            labels = list(session_options.keys())

            current_index = list(session_options.values()).index(
                st.session_state.session_type
            )

            selected_label = st.radio(
                "지금은 당신의 하루 중 어느 순간에 있나요?",
                labels,
                index=current_index,
            )

            feeling = st.text_area(
                "지금 당신의 마음은 어떤가요?",
                value=st.session_state.current_feeling,
                placeholder=(
                    "오늘 하루에 대해, 또는 지금의 마음에 대해 "
                    "편하게 이야기해주세요."
                ),
                height=145,
            )

            submitted = st.form_submit_button(
                "Begin Today's InnerFlow",
                use_container_width=True,
            )

        if submitted:
            if not name.strip():
                st.warning("ℹ️ 이름을 알려주세요.")
                return

            if not feeling.strip():
                st.warning("🧘 지금의 마음을 조금만 들려주세요.")
                return

            st.session_state.user_name = name.strip()
            st.session_state.session_type = session_options[selected_label]
            st.session_state.current_feeling = feeling.strip()
            st.session_state.page = "loading"

            st.rerun()


# =========================================================
# 2. Loading Page
# =========================================================


def render_loading_page():
    st.markdown(
        """
        <div class="center-page">
            <div style="font-size: 3rem;">⏳</div>
            <div class="page-title">
                당신의 하루를 천천히 살펴보고 있어요...
            </div>
            <div class="page-subtitle">
                잠시만 기다려주세요.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    try:
        result = graph.invoke(
            {
                "user_name": st.session_state.user_name,
                "session_type": st.session_state.session_type,
                "current_feeling": st.session_state.current_feeling,
                "selected_activity": None,
            }
        )

        st.session_state.result = result

        if not result.get("is_relevant", True):
            st.session_state.page = "guardrail"
        else:
            st.session_state.page = "reflection"

        st.rerun()

    except Exception as error:
        st.error("InnerFlow를 준비하는 중 문제가 발생했습니다.")
        st.exception(error)

        if st.button("처음으로 돌아가기"):
            reset_innerflow()
            st.rerun()


# =========================================================
# Guardrail Page
# =========================================================


def render_guardrail_page():
    render_brand(show_home=True)

    result = st.session_state.result or {}

    left, center, right = st.columns([1, 2, 1])

    with center:
        st.markdown(
            """
            <div class="center-page">
                <div style="font-size: 2.5rem;">🧭</div>
                <div class="page-title">
                    잠시 방향을 다시 맞춰볼까요?
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.info(
            result.get(
                "guardrail_message",
                (
                    "InnerFlow는 지금의 감정이나 하루의 상태를 "
                    "돌아보는 이야기를 함께해요."
                ),
            )
        )

        if st.button(
            "다시 이야기하기",
            use_container_width=True,
        ):
            st.session_state.page = "welcome"
            st.session_state.result = None
            st.rerun()


# =========================================================
# 3. Awareness & Reflection Page
# =========================================================


def render_reflection_page():
    render_brand(show_home=True)

    result = st.session_state.result or {}
    user_name = st.session_state.user_name

    st.markdown(
        f"""
        <div class="page-title">
            안녕하세요, {user_name}님 ✨
        </div>
        <div class="page-subtitle">
            당신의 하루를 돌아본 결과예요.
        </div>
        """,
        unsafe_allow_html=True,
    )

    awareness = result.get("awareness")
    reflection = result.get("reflection_message")
    mini_practice = result.get("mini_practice")

    if awareness:
        st.markdown(
            f"""
            <div class="flow-card">
                <div class="card-title">🌿 Awareness</div>
                <div>{awareness}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if reflection:
        st.markdown(
            f"""
            <div class="flow-card">
                <div class="card-title">☀️ Reflection</div>
                <div>{reflection}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if mini_practice:
        st.markdown(
            f"""
            <div class="flow-card">
                <div>{mini_practice}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")

    if st.button(
        "나에게 맞는 활동 살펴보기",
        use_container_width=True,
    ):
        st.session_state.page = "activity_selection"
        st.rerun()


# =========================================================
# 4. Activity Selection Page
# =========================================================


def render_activity_selection_page():
    render_brand(show_home=True)

    result = st.session_state.result or {}
    activity_plans = result.get("activity_plans", [])

    activity_labels = {
        "yoga": "요가",
        "breathing": "호흡",
        "meditation": "명상",
    }

    if activity_plans:
        top_plan = activity_plans[0]
        recommended_activity = activity_labels.get(
            top_plan.activity,
            top_plan.activity,
        )
        recommended_reason = top_plan.reason
    else:
        recommended_activity = "활동"
        recommended_reason = "지금의 상태에 맞는 활동을 편안하게 선택해보세요."

    st.markdown(
        f"""<div>
<div class="recommendation-card">
<div class="recommendation-label">✦ 오늘의 추천</div>
<div class="recommendation-title">{recommended_activity}</div>
<div class="recommendation-reason">{recommended_reason}</div>
</div>
</div>""",
        unsafe_allow_html=True,
    )

    st.markdown(
        """<div class="selection-note">오늘의 추천은 하나의 제안일 뿐이에요. 지금 나에게 가장 필요한 시간을 선택해보세요.</div>""",
        unsafe_allow_html=True,
    )

    activities = [
        {
            "name": "yoga",
            "icon": "🧘",
            "title": "요가",
            "description": "몸을 움직이며<br>긴장을 풀어주는 시간",
        },
        {
            "name": "breathing",
            "icon": "🌬️",
            "title": "호흡",
            "description": "천천히 호흡하며<br>마음을 안정시키는 시간",
        },
        {
            "name": "meditation",
            "icon": "🕯️",
            "title": "명상",
            "description": "마음을 차분히 하고<br>오늘을 바라보는 시간",
        },
    ]

    columns = st.columns(3, gap="medium")

    for column, activity in zip(columns, activities):
        with column:
            st.markdown(
                f"""<div class="activity-card">
<div class="activity-icon-shell">{activity["icon"]}</div>
<div class="activity-name">{activity["title"]}</div>
<div class="activity-description">{activity["description"]}</div>
</div>""",
                unsafe_allow_html=True,
            )

            if st.button(
                f"{activity['title']} 선택하기  →",
                key=f"select_{activity['name']}",
                use_container_width=True,
            ):
                run_selected_activity(activity["name"])

    st.markdown(
        """<div class="footer-message">지금 이 순간, 당신을 위한 선택을 응원합니다. </div>""",
        unsafe_allow_html=True,
    )


def run_selected_activity(activity_name: str):
    st.session_state.page = "activity_loading"
    st.session_state.pending_activity = activity_name
    st.rerun()


# =========================================================
# Activity Loading
# =========================================================


def render_activity_loading_page():
    activity_name = st.session_state.get("pending_activity")
    activity_label = get_activity_label(activity_name)

    st.markdown(
        f"""
        <div class="center-page">
            <div style="font-size: 3rem;">🧘🏻‍♀️</div>
            <div class="page-title">
                오늘의 {activity_label} 활동을 준비하고 있어요
            </div>
            <div class="page-subtitle">
                잠시만 기다려주세요.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    try:
        previous_result = st.session_state.result or {}

        activity_input = {
            **previous_result,
            "user_name": st.session_state.user_name,
            "session_type": st.session_state.session_type,
            "current_feeling": st.session_state.current_feeling,
            "selected_activity": activity_name,
            # 이전 활동 결과 초기화
            "yoga_output": None,
            "yoga_image_path": None,
            "meditation_output": None,
            "meditation_audio_path": None,
            "breathing_output": None,
            "breathing_audio_path": None,
        }

        result = graph.invoke(activity_input)

        st.session_state.result = result
        st.session_state.page = "activity"
        st.rerun()

    except Exception as error:
        st.error("활동을 준비하는 중 문제가 발생했습니다.")
        st.exception(error)

        if st.button("활동 선택으로 돌아가기"):
            st.session_state.page = "activity_selection"
            st.rerun()


# =========================================================
# 5. Activity Page
# =========================================================


def render_activity_page():
    render_brand(show_home=True)

    result = st.session_state.result or {}
    selected_activity = result.get("selected_activity")

    back_col, empty_col = st.columns([1, 7])

    with back_col:
        if st.button("< BACK"):
            st.session_state.page = "activity_selection"
            st.rerun()

    if selected_activity == "yoga":
        render_yoga_activity(result)

    elif selected_activity == "meditation":
        render_meditation_activity(result)

    elif selected_activity == "breathing":
        render_breathing_activity(result)

    else:
        st.warning("선택된 활동 정보를 찾지 못했습니다.")

    st.write("")

    if st.button(
        "오늘의 InnerFlow 마무리하기",
        use_container_width=True,
    ):
        st.session_state.page = "finish"
        st.rerun()


# =========================================================
# Yoga Activity
# =========================================================


def render_yoga_activity(result):
    yoga_output = result.get("yoga_output")

    if not yoga_output:
        st.warning("요가 결과를 찾지 못했습니다.")
        return

    st.markdown(
        f"""
        <div class="page-title">
            🧘 오늘의 요가 클래스
        </div>
        <div class="page-subtitle">
            {yoga_output.class_reason}
        </div>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns([1, 1.35], gap="large")

    with left:
        st.markdown(
            f"""
            <div class="flow-card">
                <div class="card-title">
                    {yoga_output.yoga_class.title()}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        for index, pose in enumerate(
            yoga_output.poses,
            start=1,
        ):
            with st.expander(
                f"{index}. {pose.name}",
                expanded=index == 1,
            ):
                st.write(pose.reason)
                st.write(pose.instruction)

    with right:
        image_path = result.get("yoga_image_path")

        if image_path:
            st.image(
                image_path,
                caption="Today's Yoga Flow",
                use_container_width=True,
            )

        st.markdown(
            f"""
            <div class="flow-card">
                <div class="card-title">
                    오늘의 한 줄 코칭
                </div>
                <div>
                    {yoga_output.closing_message}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# =========================================================
# Meditation Activity
# =========================================================


def render_meditation_activity(result):
    output = result.get("meditation_output")

    if not output:
        st.warning("명상 결과를 찾지 못했습니다.")
        return

    st.markdown(
        f"""
        <div class="page-title">
            🕯️ {output.title}
        </div>
        <div class="page-subtitle">
            마음을 잠시 내려놓고 현재에 머물러보세요.
        </div>
        """,
        unsafe_allow_html=True,
    )

    info_col1, info_col2 = st.columns(2)

    with info_col1:
        st.info(f"🧘 {output.meditation_type}")

    with info_col2:
        st.info(f"⏱️ {output.duration_minutes} minutes")

    st.markdown(
        f"""
        <div class="flow-card">
            <div class="card-title">
                명상을 시작하기 전에
            </div>
            <div>
                {output.introduction}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    audio_path = result.get("meditation_audio_path")

    if audio_path:
        st.audio(
            audio_path,
            format="audio/mp3",
        )
    else:
        st.warning("Meditation audio was not generated.")

    st.markdown(
        f"""
        <div class="flow-card">
            <div class="card-title">
                마무리
            </div>
            <div>
                {output.closing_message}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# Breathing Activity
# =========================================================


def render_breathing_activity(result):
    output = result.get("breathing_output")

    if not output:
        st.warning("호흡 결과를 찾지 못했습니다.")
        return

    st.markdown(
        f"""
        <div class="page-title">
            🌬️ {output.title}
        </div>
        <div class="page-subtitle">
            자신의 속도에 맞춰 천천히 따라가 보세요.
        </div>
        """,
        unsafe_allow_html=True,
    )

    info_col1, info_col2 = st.columns(2)

    with info_col1:
        st.info(f"🫁 {output.breathing_pattern}")

    with info_col2:
        st.info(f"⏱️ {output.duration_minutes} minutes")

    st.markdown(
        f"""
        <div class="flow-card">
            <div class="card-title">
                호흡을 시작하기 전에
            </div>
            <div>
                {output.introduction}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    audio_path = result.get("breathing_audio_path")

    if audio_path:
        st.audio(
            audio_path,
            format="audio/mp3",
        )
    else:
        st.warning("Breathing audio was not generated.")

    st.markdown(
        f"""
        <div class="flow-card">
            <div class="card-title">
                마무리
            </div>
            <div>
                {output.closing_message}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# 6. Finish Page
# =========================================================


def render_finish_page():
    render_brand(show_home=True)

    user_name = st.session_state.user_name

    left, center, right = st.columns([1, 2.2, 1])

    with center:
        st.markdown(
            f"""
            <div class="center-page">
                <div style="font-size: 3rem;">✨</div>
                <div class="page-subtitle">
                    작은 멈춤이 내일의 나를
                    더욱 단단하게 만들어요.
                </div>
                <div class="finish-quote">
                    지금 이 순간이 당신의 삶을
                    만들어갑니다.<br>
                    오늘도 당신을 응원합니다,
                    {user_name}님
                </div>
                <div style="color: #7a827b;">
                    오늘의 InnerFlow를 마쳤어요.
                    <br>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(
            "홈으로 돌아가기",
            use_container_width=True,
        ):
            reset_innerflow()
            st.rerun()


# =========================================================
# Page Router
# =========================================================

PAGE_RENDERERS = {
    "welcome": render_welcome_page,
    "loading": render_loading_page,
    "guardrail": render_guardrail_page,
    "reflection": render_reflection_page,
    "activity_selection": render_activity_selection_page,
    "activity_loading": render_activity_loading_page,
    "activity": render_activity_page,
    "finish": render_finish_page,
}

current_page = st.session_state.page
renderer = PAGE_RENDERERS.get(
    current_page,
    render_welcome_page,
)

renderer()
