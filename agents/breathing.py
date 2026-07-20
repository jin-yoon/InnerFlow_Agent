from pathlib import Path
import re
import tempfile
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
Soft, warm, clear, gentle, and grounding.

Tone:
Deep, calm, natural, and reassuring.
Sound like a modern wellness breathing coach.

Pacing:
Slow and unhurried.
Speak clearly, with enough space for the listener to follow.
Do not rush, but do not sound ceremonial or overly solemn.

Emotion:
Gentle, steady, supportive, and peaceful.

Important:
Do not chant.
Do not sing.
Do not sound religious, theatrical, ritualistic, or prayer-like.
Do not count numbers unless the input explicitly contains numbers.

Overall:
Guide the listener gently through a modern breathing exercise.
The listener should feel supported rather than commanded.
"""


# =========================================================
# Script Tokens
# =========================================================

INHALE_TOKEN = "[INHALE]"
HOLD_TOKEN = "[HOLD]"
EXHALE_TOKEN = "[EXHALE]"
SHORT_PAUSE_TOKEN = "[PAUSE]"
LONG_PAUSE_TOKEN = "[LONG_PAUSE]"

TOKEN_PATTERN = r"(\[INHALE\]|\[HOLD\]|\[EXHALE\]|" r"\[PAUSE\]|\[LONG_PAUSE\])"

SHORT_PAUSE_MS = 1200
LONG_PAUSE_MS = 2500


# =========================================================
# Background Sound Assets
# =========================================================

BREATHING_SOUNDS = {
    "birds": Path("assets/breathing_sounds/birds.mp3"),
    "ocean": Path("assets/breathing_sounds/ocean.mp3"),
    "singing_bowl": Path("assets/breathing_sounds/singing_bowl.mp3"),
}


# =========================================================
# Background Volume
# =========================================================

BACKGROUND_VOLUME = {
    "birds": -27,
    "ocean": -28,
    "singing_bowl": -30,
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
        너는 InnerFlow의 호흡 가이드이다.

        모든 내용은 반드시 사용자가 입력한 언어를 기준으로 작성한다.

        [사용자 입력 언어]: {state["current_feeling"]}


        Flow Guide는 이미 사용자의 상태를 분석하고
        이번 호흡 경험의 방향을 설계했다.

        너는 사용자의 감정이나 상태를
        다시 분석하거나 판단하지 않는다.

        Flow Guide가 설계한 방향을 바탕으로,
        사용자가 호흡을 통해 현재 순간으로
        부드럽게 돌아올 수 있는 경험을 설계한다.


        [이번 호흡의 목적]
        {plan.guidance.intention}


        [호흡의 분위기]
        {plan.guidance.tone}


        [집중할 대상]
        {plan.guidance.focus}


        [Flow Guide의 추천 이유]
        {plan.reason}


        다음 호흡 패턴 중 이번 경험에
        가장 적합한 하나를 선택한다.

        - box_breathing
        - 4_6_breathing
        - 4_7_8_breathing
        - coherent_breathing
        - natural_breathing


        초보자가 편안하게 따라 할 수 있도록
        3분 또는 5분 중 하나를 선택한다.


        title에는 사용자가 이해하기 쉬운
        따뜻하고 편안한 제목을 작성한다.


        introduction에는 호흡을 시작하기 전에
        편안한 자세를 찾을 수 있도록
        짧고 부드러운 안내를 작성한다.


        inhale_seconds에는 한 번 숨을 들이마시는
        시간을 초 단위 정수로 작성한다.

        hold_seconds에는 숨을 편안하게 머무르는
        시간을 초 단위 정수로 작성한다.

        숨을 머무르지 않는 호흡법이라면
        반드시 0으로 작성한다.

        exhale_seconds에는 한 번 숨을 내쉬는
        시간을 초 단위 정수로 작성한다.


        script에는 실제 음성으로 읽을
        호흡 가이드 스크립트를 작성한다.

        script의 시작에는 반드시
        호흡 연습이 곧 시작된다는
        자연스럽고 따뜻한 안내를 포함한다.

        script의 마지막에는 반드시
        호흡 연습이 마무리되었다는 안내와
        일상으로 천천히 돌아오도록 돕는
        부드러운 문장을 포함한다.


        script에서는 절대 숫자를 세지 않는다.

        다음과 같은 카운트다운을 작성하지 않는다.

        - 다섯, 넷, 셋, 둘, 하나
        - 오, 사, 삼, 이, 일
        - 5, 4, 3, 2, 1

        호흡 시간을 숫자로 읽어주지 않는다.

        대신 다음 토큰을 사용하여
        실제 호흡 시간을 표현한다.


        들숨 안내 문장 다음에는
        반드시 독립된 줄에 다음 토큰을 작성한다.

        [INHALE]


        숨을 머무르는 안내 문장 다음에는
        반드시 독립된 줄에 다음 토큰을 작성한다.

        [HOLD]


        날숨 안내 문장 다음에는
        반드시 독립된 줄에 다음 토큰을 작성한다.

        [EXHALE]


        일반적인 짧은 여유가 필요하면
        독립된 줄에 다음 토큰을 작성한다.

        [PAUSE]


        더 긴 휴식이나 자연스러운 호흡을
        느낄 시간이 필요하면
        독립된 줄에 다음 토큰을 작성한다.

        [LONG_PAUSE]


        hold_seconds가 0이라면
        [HOLD] 토큰을 사용하지 않는다.

        모든 토큰은 반드시 독립된 줄에 작성한다.

        토큰을 괄호 속 설명이나
        일반 문장 안에 넣지 않는다.


        예시:

        이제 천천히 호흡을 시작해 봅니다.

        [PAUSE]

        코를 통해 부드럽게 숨을 들이마셔 봅니다.

        [INHALE]

        편안한 만큼 잠시 머물러 봅니다.

        [HOLD]

        입이나 코를 통해 길게 숨을 내쉬어 봅니다.

        [EXHALE]

        몸의 긴장이 조금씩 풀리는 것을 느껴봅니다.

        [LONG_PAUSE]


        사용자가 실제로 호흡할 수 있도록
        들숨, 머무름, 날숨 안내를 여러 차례 반복한다.

        단, 모든 호흡마다 똑같은 문장을
        기계적으로 반복하지 않는다.

        초반에는 호흡 방법을 자세히 안내하고,
        중반에는 짧고 단순한 안내를 사용하며,
        후반에는 스스로 호흡을 이어갈 수 있도록
        말의 양을 조금 줄인다.


        사용자가 긴장하거나 불편함을 느끼지 않도록
        명령하거나 강요하는 표현을 피한다.

        다음과 같은 표현을 활용한다.

        - 천천히 해보세요
        - 편안한 만큼만 머물러 보세요
        - 힘들다면 자연스럽게 호흡해도 괜찮습니다
        - 자신의 리듬을 따라가도 괜찮습니다


        sound에는 이번 호흡 경험의 분위기와
        가장 잘 맞는 배경음을 하나 선택한다.

        선택 가능한 배경음:

        - birds
        - ocean
        - singing_bowl


        배경음 선택 기준:

        birds:
        가볍고 맑은 분위기,
        아침이나 기분 전환이 필요한 호흡

        ocean:
        안정적이고 반복적인 분위기,
        긴장 완화와 깊고 느린 호흡

        singing_bowl:
        고요하고 차분한 분위기,
        내면 집중과 정적인 호흡


        closing_message에는 호흡 연습이 끝난 뒤
        사용자에게 별도로 보여줄
        따뜻한 마무리 메시지를 작성한다.
        """
    )

    return {"breathing_output": breathing_output}


# =========================================================
# TTS Segment 생성
# =========================================================


def generate_tts_segment(
    client: OpenAI,
    text: str,
    output_path: Path,
) -> None:
    """
    하나의 안내 문장을 TTS 파일로 생성한다.
    """

    response = client.audio.speech.create(
        model="gpt-4o-mini-tts",
        voice="sage",
        input=text,
        instructions=BREATHING_AUDIO_INSTRUCTION,
        speed=0.9,
    )

    response.write_to_file(output_path)


# =========================================================
# Breathing Voice 생성
# =========================================================


def generate_breathing_voice(
    script: str,
    inhale_seconds: int,
    hold_seconds: int,
    exhale_seconds: int,
) -> str:
    """
    스크립트를 토큰 단위로 나눈다.

    각 안내 문장은 개별 TTS로 생성하고,
    호흡 토큰 위치에는 정확한 길이의
    무음을 삽입한다.
    """

    client = OpenAI()

    output_dir = Path("generated_audio/breathing/voice")

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    filename = output_dir / (f"breathing_voice_{uuid.uuid4().hex}.mp3")

    # -----------------------------------------------------
    # Script 분리
    # -----------------------------------------------------

    parts = re.split(
        TOKEN_PATTERN,
        script,
    )

    combined_voice = AudioSegment.empty()

    # -----------------------------------------------------
    # 임시 TTS 파일 폴더
    # -----------------------------------------------------

    with tempfile.TemporaryDirectory() as temp_dir:

        temp_dir_path = Path(temp_dir)

        segment_number = 0

        for part in parts:

            cleaned_part = part.strip()

            if not cleaned_part:
                continue

            # ---------------------------------------------
            # 들숨 시간
            # ---------------------------------------------

            if cleaned_part == INHALE_TOKEN:

                duration_ms = (
                    max(
                        int(inhale_seconds),
                        1,
                    )
                    * 1000
                )

                combined_voice += AudioSegment.silent(duration=duration_ms)

                continue

            # ---------------------------------------------
            # 머무름 시간
            # ---------------------------------------------

            if cleaned_part == HOLD_TOKEN:

                if hold_seconds > 0:

                    combined_voice += AudioSegment.silent(
                        duration=int(hold_seconds) * 1000
                    )

                continue

            # ---------------------------------------------
            # 날숨 시간
            # ---------------------------------------------

            if cleaned_part == EXHALE_TOKEN:

                duration_ms = (
                    max(
                        int(exhale_seconds),
                        1,
                    )
                    * 1000
                )

                combined_voice += AudioSegment.silent(duration=duration_ms)

                continue

            # ---------------------------------------------
            # 일반적인 짧은 쉼
            # ---------------------------------------------

            if cleaned_part == SHORT_PAUSE_TOKEN:

                combined_voice += AudioSegment.silent(duration=SHORT_PAUSE_MS)

                continue

            # ---------------------------------------------
            # 긴 쉼
            # ---------------------------------------------

            if cleaned_part == LONG_PAUSE_TOKEN:

                combined_voice += AudioSegment.silent(duration=LONG_PAUSE_MS)

                continue

            # ---------------------------------------------
            # 일반 안내 문장 TTS
            # ---------------------------------------------

            segment_path = temp_dir_path / (f"segment_{segment_number}.mp3")

            generate_tts_segment(
                client=client,
                text=cleaned_part,
                output_path=segment_path,
            )

            segment_audio = AudioSegment.from_file(
                segment_path,
                format="mp3",
            )

            combined_voice += segment_audio

            segment_number += 1

    # -----------------------------------------------------
    # 생성 결과 확인
    # -----------------------------------------------------

    if len(combined_voice) == 0:

        raise ValueError("호흡 스크립트에서 생성할 " "음성 내용을 찾지 못했습니다.")

    # -----------------------------------------------------
    # 하나의 Voice 파일로 저장
    # -----------------------------------------------------

    combined_voice.export(
        filename,
        format="mp3",
    )

    return str(filename)


# =========================================================
# Background Sound Mix
# =========================================================


def mix_breathing_audio(
    voice_path: str,
    sound: str,
) -> str:
    """
    호흡 음성 전체에 선택된 배경음을
    낮은 볼륨으로 반복하여 삽입한다.
    """

    sound_path = BREATHING_SOUNDS.get(sound)

    if sound_path is None:
        return voice_path

    if not sound_path.exists():

        raise FileNotFoundError(f"Breathing sound not found: {sound_path}")

    # -----------------------------------------------------
    # Audio Load
    # -----------------------------------------------------

    voice = AudioSegment.from_file(voice_path)

    background = AudioSegment.from_file(sound_path)

    # -----------------------------------------------------
    # 빈 배경음 파일 방지
    # -----------------------------------------------------

    if len(background) == 0:

        raise ValueError(f"Breathing sound is empty: {sound_path}")

    # -----------------------------------------------------
    # Voice 길이까지 Background 반복
    # -----------------------------------------------------

    repeated_background = AudioSegment.empty()

    while len(repeated_background) < len(voice):

        repeated_background += background

    repeated_background = repeated_background[: len(voice)]

    # -----------------------------------------------------
    # Background Volume 조절
    # -----------------------------------------------------

    volume_reduction = BACKGROUND_VOLUME.get(
        sound,
        -28,
    )

    repeated_background = repeated_background + volume_reduction

    # -----------------------------------------------------
    # 자연스러운 Fade
    # -----------------------------------------------------

    fade_duration = min(
        2000,
        len(repeated_background) // 4,
    )

    if fade_duration > 0:

        repeated_background = repeated_background.fade_in(fade_duration).fade_out(
            fade_duration
        )

    # -----------------------------------------------------
    # Voice + Background
    # -----------------------------------------------------

    final_audio = repeated_background.overlay(voice)

    # -----------------------------------------------------
    # Save
    # -----------------------------------------------------

    output_dir = Path("generated_audio/breathing/final")

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    filename = output_dir / (f"breathing_{uuid.uuid4().hex}.mp3")

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
    # 1. 안내 음성 + 정확한 호흡 공백 생성
    # -----------------------------------------------------

    voice_path = generate_breathing_voice(
        script=breathing_output.script,
        inhale_seconds=breathing_output.inhale_seconds,
        hold_seconds=breathing_output.hold_seconds,
        exhale_seconds=breathing_output.exhale_seconds,
    )

    # -----------------------------------------------------
    # 2. 전체 구간에 Background Sound 추가
    # -----------------------------------------------------

    final_audio_path = mix_breathing_audio(
        voice_path=voice_path,
        sound=breathing_output.sound,
    )

    # -----------------------------------------------------
    # 3. State 저장
    # -----------------------------------------------------

    return {"breathing_audio_path": final_audio_path}
