from pathlib import Path
import uuid

from openai import OpenAI
from pydub import AudioSegment

from langchain.chat_models import init_chat_model

from agents.innerflow_states import (
    InnerFlowState,
    BreathingOutput,
)


# =========================================================
# LLM
# =========================================================

llm = init_chat_model("openai:gpt-4o")


# =========================================================
# TTS Instruction
# =========================================================

BREATHING_AUDIO_INSTRUCTION = """
Voice Affect:
Extremely soft, warm, gentle, and soothing.

Tone:
Deeply calm, peaceful, and reassuring.
Sound like a professional guided breathing meditation instructor.

Pacing:
Very slow and unhurried.
Speak significantly slower than normal conversational speech.
Never rush through the instructions.

Pauses:
Use long, intentional pauses between each breathing instruction.
After every inhale instruction, allow enough silence for the listener
to complete the inhale.
After every hold instruction, allow enough silence for the listener
to complete the hold.
After every exhale instruction, allow enough silence for the listener
to complete the exhale.

Important:
The silence between instructions is an essential part of the experience.
Do not fill every moment with speech.

Overall:
Guide the listener gently and patiently.
The listener should have plenty of time to breathe before hearing
the next instruction.
"""


# =========================================================
# Sound Assets
# =========================================================

BREATHING_SOUNDS = {
    "singing_bowl": Path("assets/breathing_sounds/singing_bowl.mp3"),
    "bell": Path("assets/breathing_sounds/bell.mp3"),
}


# =========================================================
# Breathing Agent
# =========================================================


def breathing_agent(
    state: InnerFlowState,
):

    # -----------------------------------------------------
    # Flow Guide가 만든 Breathing Plan 가져오기
    # -----------------------------------------------------

    plan = next(
        (plan for plan in state["activity_plans"] if plan.activity == "breathing"),
        None,
    )

    if plan is None:

        return {"breathing_output": None}

    # -----------------------------------------------------
    # Structured Output
    # -----------------------------------------------------

    structured_llm = llm.with_structured_output(BreathingOutput)

    # -----------------------------------------------------
    # Breathing Content 생성
    # -----------------------------------------------------

    breathing_output = structured_llm.invoke(
        f"""
        너는 InnerFlow의 호흡 가이드이다. 언어는 반드시 사용자 언어 기반으로 작성한다.
        사용자 입력 언어 : {state["current_feeling"]}

        Flow Guide는 이미 사용자의 상태를 분석하고
        이번 호흡 경험의 방향을 설계했다.

        너는 사용자의 감정이나 상태를
        다시 분석하거나 판단하지 않는다.

        Flow Guide가 설계한 방향을 바탕으로
        사용자가 잠시 멈추고
        호흡을 통해 현재 순간으로 돌아올 수 있도록
        부드러운 호흡 경험을 설계한다.


        [이번 호흡의 목적]

        {plan.guidance.intention}


        [호흡의 분위기]

        {plan.guidance.tone}


        [집중할 대상]

        {plan.guidance.focus}


        [Flow Guide의 추천 이유]

        {plan.reason}


        다음 호흡 패턴 중
        이번 경험에 가장 적합한 하나를 선택한다.

        - box_breathing
        - 4_6_breathing
        - 4_7_8_breathing
        - coherent_breathing
        - natural_breathing


        초보자가 편안하게 따라 할 수 있는
        3분, 5분 중 하나의 시간을 선택한다.


        title에는 사용자가 이해하기 쉬운
        따뜻하고 편안한 제목을 작성한다.


        introduction에는
        호흡을 시작하기 전에 사용자가
        편안한 자세를 찾을 수 있도록
        짧고 부드러운 안내를 작성한다.


        script에는 실제 음성으로 읽을
        호흡 가이드 스크립트를 작성한다.

        사용자가 실제로 따라 할 수 있도록
        다음 요소를 자연스럽게 포함한다.

        - 호흡 시작 안내
        - 들숨 안내
        - 필요하다면 멈춤 안내
        - 날숨 안내
        - 반복적인 호흡 안내
        - 현재 순간으로 돌아오는 안내


        호흡 안내는 초보자도 쉽게 따라 할 수 있도록 한다.

        숨을 참는 것이 불편할 수 있는 사용자를 고려하여
        무리하게 숨을 참도록 강요하지 않는다.

        "해야 합니다"보다는
        "천천히 해보세요",
        "편안한 만큼만 머물러 보세요",
        "괜찮습니다"
        등의 부드러운 표현을 사용한다.

        inhale_seconds에는
        한 번 숨을 들이마시는 시간을 초 단위로 작성한다.

        hold_seconds에는
        숨을 멈추는 시간을 초 단위로 작성한다.

        숨을 참지 않는 호흡법이라면
        0으로 작성한다.

        exhale_seconds에는
        한 번 숨을 내쉬는 시간을 초 단위로 작성한다.

        sound에는
        호흡 경험에 사용할 소리를 선택한다.

        - singing_bowl
        - bell
        - none

        싱잉볼이나 벨은 배경음악이 아니라
        호흡 경험의 시작과 종료를 알려주는
        부드러운 신호로 사용한다.

        마지막에는
        사용자가 천천히 일상으로 돌아갈 수 있도록
        따뜻한 closing_message를 작성한다.
        """
    )

    # -----------------------------------------------------
    # State 저장
    # -----------------------------------------------------

    return {"breathing_output": breathing_output}


# =========================================================
# TTS Voice 생성
# =========================================================


def generate_breathing_voice(
    script: str,
) -> str:

    client = OpenAI()

    output_dir = Path("generated_audio/breathing/voice")

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    filename = output_dir / f"breathing_voice_{uuid.uuid4().hex}.mp3"

    response = client.audio.speech.create(
        model="gpt-4o-mini-tts",
        voice="onyx",
        input=script,
        instructions=BREATHING_AUDIO_INSTRUCTION,
        speed=0.9,
    )

    response.write_to_file(filename)

    return str(filename)


# =========================================================
# Singing Bowl / Bell Mix
# =========================================================


def mix_breathing_audio(
    voice_path: str,
    sound: str,
) -> str:

    # -----------------------------------------------------
    # Sound 없음
    # -----------------------------------------------------

    if sound == "none":

        return voice_path

    sound_path = BREATHING_SOUNDS.get(sound)

    if sound_path is None:

        return voice_path

    if not sound_path.exists():

        raise FileNotFoundError(f"Breathing sound not found: " f"{sound_path}")

    # -----------------------------------------------------
    # Audio Load
    # -----------------------------------------------------

    voice = AudioSegment.from_file(voice_path)

    cue = AudioSegment.from_file(sound_path)

    # -----------------------------------------------------
    # Cue Volume
    # -----------------------------------------------------

    cue = cue - 8

    # -----------------------------------------------------
    # 시작 / 종료 Cue
    # -----------------------------------------------------

    final_audio = voice.overlay(
        cue,
        position=0,
    )

    final_audio = final_audio.overlay(
        cue,
        position=max(
            0,
            len(voice) - len(cue),
        ),
    )

    # -----------------------------------------------------
    # Save
    # -----------------------------------------------------

    output_dir = Path("generated_audio/breathing/final")

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    filename = output_dir / f"breathing_{uuid.uuid4().hex}.mp3"

    final_audio.export(
        filename,
        format="mp3",
    )

    return str(filename)


# =========================================================
# Breathing Audio Generator
# =========================================================


def breathing_audio_generator(
    state: InnerFlowState,
):

    breathing_output = state.get("breathing_output")

    if breathing_output is None:

        return {"breathing_audio_path": None}

    # -----------------------------------------------------
    # 1. TTS 생성
    # -----------------------------------------------------

    voice_path = generate_breathing_voice(breathing_output.script)

    # -----------------------------------------------------
    # 2. Singing Bowl / Bell 추가
    # -----------------------------------------------------

    final_audio_path = mix_breathing_audio(
        voice_path=voice_path,
        sound=breathing_output.sound,
    )

    # -----------------------------------------------------
    # 3. State 저장
    # -----------------------------------------------------

    return {"breathing_audio_path": final_audio_path}
