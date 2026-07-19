from pathlib import Path
import uuid

from openai import OpenAI
from pydub import AudioSegment
from langchain.chat_models import init_chat_model

from agents.innerflow_states import (
    InnerFlowState,
    MeditationOutput,
)


# =========================================================
# LLM
# =========================================================

llm = init_chat_model("openai:gpt-4o")


# =========================================================
# TTS Voice Instruction
# =========================================================

AUDIO_INSTRUCTION = """
Voice Affect:
Soft, warm, gentle, and soothing.
Create a sense of tranquility, safety, and inner calm.

Tone:
Calm, reassuring, peaceful, and compassionate.
Speak with genuine warmth and care.

Pacing:
Slow, deliberate, and unhurried.
Allow the listener enough time to follow each instruction comfortably.

Emotion:
Deeply soothing and comforting.
Never sound overly cheerful, dramatic, or energetic.

Pronunciation:
Smooth, soft, and natural articulation.
Slightly elongate vowels when appropriate to create a sense of ease.

Pauses:
Use intentional, gentle pauses between instructions.
Allow longer pauses after breathing instructions,
body awareness prompts, and visualization guidance.
Do not rush to fill the silence.

Overall:
Sound like a calm and compassionate meditation guide.
The listener should feel gently accompanied,
not instructed or commanded.
"""


# =========================================================
# Background Music
# =========================================================

BACKGROUND_MUSIC = {
    "ambient": Path("assets/background_music/ambient.mp3"),
    "piano": Path("assets/background_music/piano.mp3"),
    "rain": Path("assets/background_music/rain.mp3"),
    "ocean": Path("assets/background_music/ocean.mp3"),
    "forest": Path("assets/background_music/forest.mp3"),
}


# =========================================================
# Meditation Agent
# =========================================================


def meditation_agent(
    state: InnerFlowState,
):

    # -----------------------------------------------------
    # Flow Guide가 만든 Meditation Plan 가져오기
    # -----------------------------------------------------

    plan = next(
        (plan for plan in state["activity_plans"] if plan.activity == "meditation"),
        None,
    )

    if plan is None:

        return {"meditation_output": None}

    # -----------------------------------------------------
    # Structured Output
    # -----------------------------------------------------

    structured_llm = llm.with_structured_output(MeditationOutput)

    # -----------------------------------------------------
    # Meditation Content 생성
    # -----------------------------------------------------

    meditation_output = structured_llm.invoke(
        f"""
        너는 InnerFlow의 명상 가이드이다. 언어는 반드시 사용자 언어 기반으로 작성한다.
        사용자 입력 언어 : {state["current_feeling"]}

        Flow Guide는 이미 사용자의 상태를 분석하고
        이번 명상 경험의 방향을 설계했다.

        너는 사용자의 감정이나 상태를
        다시 분석하거나 판단하지 않는다.

        Flow Guide가 설계한 방향을 바탕으로
        사용자가 잠시 멈추고
        자신의 상태를 편안하게 알아차릴 수 있는
        명상 경험을 설계한다.


        [이번 명상의 목적]
        {plan.guidance.intention}


        [명상의 분위기]
        {plan.guidance.tone}


        [집중할 대상]
        {plan.guidance.focus}


        [Flow Guide의 추천 이유]
        {plan.reason}


        다음 명상 유형 중
        이번 명상의 목적에 가장 적합한 하나를 선택한다.

        - breathing_meditation
        - body_scan
        - mindfulness
        - self_compassion
        - gratitude


        초보자도 부담 없이 따라 할 수 있는
        3분, 5분, 10분 중 하나의 명상 시간을 선택한다.


        title에는 사용자가 이해하기 쉬운
        따뜻한 명상 제목을 작성한다.


        introduction에는
        명상을 시작하기 전에 사용자에게
        안내할 짧은 메시지를 작성한다.


        script에는 실제 음성으로 읽을
        Guided Meditation 스크립트를 작성한다.

        사용자가 직접 따라 할 수 있도록
        매우 자연스럽고 천천히 진행되는
        명상 가이드 형식으로 작성한다.

        스크립트에는 필요에 따라 다음 요소를 포함한다.

        - 호흡 안내
        - 몸의 감각 알아차리기
        - 현재 순간에 머무르기
        - 부드러운 자기 인식
        - 짧은 침묵과 여유

        사용자가 긴장하거나 불편함을 느끼지 않도록
        명령하거나 강요하는 표현을 피한다.

        "해야 합니다"보다는
        "천천히 해보세요",
        "괜찮습니다",
        "원한다면"과 같은
        부드러운 표현을 사용한다.


        background_music에는
        이번 명상의 분위기와 목적에 가장 적합한
        배경음악을 하나 선택한다.

        선택 가능한 배경음악:
        - piano
        - rain
        - forest
        - none


        마지막에는
        사용자가 명상을 마무리하고
        일상으로 돌아갈 수 있도록
        따뜻한 closing_message를 작성한다.
        """
    )

    # -----------------------------------------------------
    # State에 Meditation Output 저장
    # -----------------------------------------------------

    return {"meditation_output": meditation_output}


# =========================================================
# TTS Audio 생성
# =========================================================


def generate_meditation_voice(
    script: str,
) -> str:

    client = OpenAI()

    output_dir = Path("generated_audio/voice")

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    filename = output_dir / f"meditation_voice_{uuid.uuid4().hex}.mp3"

    response = client.audio.speech.create(
        model="gpt-4o-mini-tts",
        voice="marin",
        input=script,
        instructions=AUDIO_INSTRUCTION,
        speed=0.9,
    )

    response.write_to_file(filename)

    return str(filename)


# =========================================================
# Background Music Mix
# =========================================================


def mix_meditation_audio(
    voice_path: str,
    background_music: str,
) -> str:

    # -----------------------------------------------------
    # Background Music 확인
    # -----------------------------------------------------

    if background_music == "none":

        return voice_path

    background_path = BACKGROUND_MUSIC.get(background_music)

    if background_path is None:

        return voice_path

    if not background_path.exists():

        raise FileNotFoundError(f"Background music not found: " f"{background_path}")

    # -----------------------------------------------------
    # Audio 불러오기
    # -----------------------------------------------------

    voice = AudioSegment.from_file(voice_path)

    background = AudioSegment.from_file(background_path)

    # -----------------------------------------------------
    # Background Music 길이 맞추기
    # -----------------------------------------------------

    while len(background) < len(voice):

        background += background

    background = background[: len(voice)]

    # -----------------------------------------------------
    # Background Volume 낮추기
    # -----------------------------------------------------

    background = background - 22

    # -----------------------------------------------------
    # Voice + Background Mix
    # -----------------------------------------------------

    final_audio = background.overlay(voice)

    # -----------------------------------------------------
    # Final Audio 저장
    # -----------------------------------------------------

    output_dir = Path("generated_audio/final")

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    filename = output_dir / f"meditation_{uuid.uuid4().hex}.mp3"

    final_audio.export(
        filename,
        format="mp3",
    )

    return str(filename)


# =========================================================
# Meditation Audio Generator
# =========================================================


def meditation_audio_generator(
    state: InnerFlowState,
):

    meditation_output = state.get("meditation_output")

    if meditation_output is None:

        return {"meditation_audio_path": None}

    # -----------------------------------------------------
    # 1. TTS Voice 생성
    # -----------------------------------------------------

    voice_path = generate_meditation_voice(meditation_output.script)

    # -----------------------------------------------------
    # 2. Background Music + Voice Mix
    # -----------------------------------------------------

    final_audio_path = mix_meditation_audio(
        voice_path=voice_path,
        background_music=(meditation_output.background_music),
    )

    # -----------------------------------------------------
    # 3. State에 최종 Audio Path 저장
    # -----------------------------------------------------

    return {"meditation_audio_path": final_audio_path}
