from pathlib import Path
import re
import tempfile
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
Deep, soft, warm, gentle, and soothing.
Create a sense of tranquility, safety, and inner calm.

Tone:
Calm, reassuring, peaceful, and compassionate.
Speak with genuine warmth and care.

Pacing:
Slow, deliberate, and unhurried.
Speak more slowly than ordinary conversation.
Do not rush from one sentence to the next.

Emotion:
Deeply soothing and comforting.
Never sound overly cheerful, dramatic, or energetic.

Pronunciation:
Smooth, soft, and natural articulation.
Slightly elongate vowels when appropriate to create a sense of ease.

Overall:
Sound like a calm and compassionate meditation guide.
The listener should feel gently accompanied,
not instructed or commanded.
"""


# =========================================================
# Pause Settings
# =========================================================

# 밀리초 단위
PAUSE_DURATIONS = {
    "[PAUSE]": 1500,
    "[LONG_PAUSE]": 3500,
}

PAUSE_PATTERN = r"(\[LONG_PAUSE\]|\[PAUSE\])"


# =========================================================
# Background Music
# =========================================================

BACKGROUND_MUSIC = {
    "piano": Path("assets/background_music/piano.mp3"),
    "rain": Path("assets/background_music/rain.mp3"),
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
        너는 InnerFlow의 명상 가이드이다.

        모든 내용은 반드시 사용자가 입력한 언어로 작성한다.

        [사용자 입력]
        {state["current_feeling"]}


        Flow Guide는 이미 사용자의 상태를 분석하고
        이번 명상 경험의 방향을 설계했다.

        너는 사용자의 감정이나 상태를
        다시 분석하거나 판단하지 않는다.

        Flow Guide가 설계한 방향을 바탕으로,
        사용자가 잠시 멈추고 자신의 상태를
        편안하게 알아차릴 수 있는 명상 경험을 설계한다.


        [이번 명상의 목적]
        {plan.guidance.intention}


        [명상의 분위기]
        {plan.guidance.tone}


        [집중할 대상]
        {plan.guidance.focus}


        [Flow Guide의 추천 이유]
        {plan.reason}


        다음 명상 유형 중 이번 명상의 목적에
        가장 적합한 하나를 선택한다.

        - breathing_meditation
        - body_scan
        - mindfulness
        - self_compassion
        - gratitude


        초보자도 부담 없이 따라 할 수 있도록
        1분, 3분, 5분중 하나의 명상 시간을 선택한다.

        사용자가 실제로 약 5분 동안 명상을 진행할 수 있을 만큼 충분히 긴 스크립트를 작성한다.

        각 문장은 짧게 작성하되,
        문장 수를 충분히 많이 작성한다.

        중간중간 [PAUSE]와 [LONG_PAUSE]를 자주 사용하여
        사용자가 실제로 호흡하고 몸의 감각을 느낄 시간을 제공한다.

        (예) 5분 명상이라면 아래 정도로 분배한다.
            도입 30초

            호흡 60초

            침묵 30초

            몸 인식 60초

            침묵 30초

            감정 바라보기 60초

            마무리 30초

        title에는 사용자가 이해하기 쉬운
        따뜻한 명상 제목을 작성한다.

        introduction에는 명상을 시작하기 전에
        사용자에게 안내할 짧은 메시지를 작성한다.

        script에는 실제 음성으로 읽을
        Guided Meditation 스크립트를 작성하며, guide에는 반드시 시작 introduction과 마무리 메세지를 함께 포함한다.

        script는 반드시 TTS 음성 생성에 적합하게 작성한다. 

        다음 규칙을 반드시 지킨다.

        1. 번호 목록을 사용하지 않는다.
        2. 글머리 기호를 사용하지 않는다.
        3. 괄호로 된 행동 지시를 작성하지 않는다.
        4. "(잠시 쉬고)", "(침묵)", "(호흡)" 등의 무대 지시를 작성하지 않는다.
        5. 마크다운 제목이나 기호를 사용하지 않는다.
        6. 한 문장에는 하나의 안내만 담는다.
        7. 문장은 짧고 부드럽게 작성한다.
        8. 쉼표나 말줄임표에만 의존해 쉼을 표현하지 않는다.

        짧은 쉼이 필요한 위치에는 정확히 다음 토큰을 사용한다.

        [PAUSE]

        조금 더 긴 침묵이 필요한 위치에는
        정확히 다음 토큰을 사용한다.

        [LONG_PAUSE]

        이 두 토큰 외에는 대괄호 표현을 사용하지 않는다.

        [PAUSE]는 일반적인 문장 사이,
        짧은 호흡 안내 뒤에 사용한다.

        [LONG_PAUSE]는 다음과 같은 경우에 사용한다.

        - 깊은 호흡을 느낄 시간을 줄 때
        - 몸의 감각을 알아차리게 할 때
        - 감정이나 생각을 가만히 바라보게 할 때
        - 시각화 경험을 충분히 느끼게 할 때

        토큰은 반드시 독립된 줄에 작성한다.

        예시:

        편안하게 자리를 잡아봅니다.

        [PAUSE]

        천천히 숨을 들이쉽니다.

        [LONG_PAUSE]

        몸이 바닥에 닿아 있는 감각을 느껴봅니다.

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

        background_music에는 이번 명상의 분위기와
        목적에 가장 적합한 배경음악을 하나 선택한다.

        선택 가능한 배경음악:
        - piano
        - rain
        - forest

        closing_message에는 사용자가 명상을 마무리하고일상으 로 돌아갈 수 있도록 따뜻한 메시지를 작성한다. 
        introduction과 closing_message에는 "[PAUSE]/[LONG_PAUSE]" 토큰을 포함하지 않는다.
        """
    )

    return {"meditation_output": meditation_output}


# =========================================================
# TTS 한 구간 생성
# =========================================================


def generate_tts_segment(
    client: OpenAI,
    text: str,
    output_path: Path,
) -> None:
    """
    하나의 텍스트 구간을 TTS 음성으로 생성한다.
    """

    response = client.audio.speech.create(
        model="gpt-4o-mini-tts",
        voice="onyx",
        input=text,
        instructions=AUDIO_INSTRUCTION,
        speed=0.95,
        response_format="mp3",
    )

    response.write_to_file(output_path)


# =========================================================
# TTS Audio 생성 + 무음 삽입
# =========================================================


def generate_meditation_voice(
    script: str,
) -> str:
    """
    스크립트를 PAUSE 토큰 기준으로 나눈다.

    각 텍스트 구간을 개별 TTS로 생성한 후,
    토큰 위치에 정해진 길이의 무음을 삽입한다.
    """

    client = OpenAI()

    output_dir = Path("generated_audio/voice")

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    filename = output_dir / (f"meditation_voice_" f"{uuid.uuid4().hex}.mp3")

    # -----------------------------------------------------
    # 토큰과 텍스트를 분리
    # -----------------------------------------------------

    parts = re.split(
        PAUSE_PATTERN,
        script
        + "[LONG_PAUSE] [LONG_PAUSE] 오늘의 명상 경험을 함께해주셔서 감사합니다. 하루의 나머지 시간도 평온하게 보내세요. [LONG_PAUSE] [LONG_PAUSE] ",
    )

    combined_voice = AudioSegment.empty()

    # -----------------------------------------------------
    # 임시 TTS 파일 생성
    # -----------------------------------------------------

    with tempfile.TemporaryDirectory() as temp_dir:

        temp_dir_path = Path(temp_dir)

        segment_number = 0

        for part in parts:

            cleaned_part = part.strip()

            if not cleaned_part:
                continue

            # ---------------------------------------------
            # Pause 토큰이면 무음 삽입
            # ---------------------------------------------

            if cleaned_part in PAUSE_DURATIONS:

                silence_duration = PAUSE_DURATIONS[cleaned_part]

                silence = AudioSegment.silent(duration=silence_duration)

                combined_voice += silence

                continue

            # ---------------------------------------------
            # 일반 텍스트이면 TTS 생성
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
    # 하나의 Voice 파일로 저장
    # -----------------------------------------------------

    if len(combined_voice) == 0:
        raise ValueError("명상 스크립트에서 생성할 " "음성 문장을 찾지 못했습니다.")

    combined_voice.export(
        filename,
        format="mp3",
    )

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
        raise FileNotFoundError("Background music not found: " f"{background_path}")

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

    filename = output_dir / (f"meditation_{uuid.uuid4().hex}.mp3")

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
    # 1. 구간별 TTS 생성 + 무음 삽입
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
