## InnerFlow

AI Wellness Companion for Mindfulness and Self-Awareness

InnerFlow는 사용자가 자신의 현재 감정과 상태를 잠시 돌아보고,
현재 순간에 머물며 자신에게 필요한 활동을 선택할 수 있도록 돕는 AI 기반 웰니스 컴패니언입니다.

단순히 사용자의 감정에 맞는 활동을 추천하는 것을 넘어,
**"지금 나는 어떤 상태인가?"**를 스스로 알아차리는 과정을 돕는 것을 목표로 합니다.

## 🌿 Project Overview

우리는 바쁜 일상 속에서 자신의 몸과 마음의 상태를 충분히 알아차리지 못한 채 하루를 보내곤 합니다.
InnerFlow는 사용자가 자신의 현재 상태를 자연스럽게 이야기하면, AI가 이를 판단하거나 해결하려 하기보다 현재의 상태를 인식하고 바라볼 수 있도록 돕고 관련된 활동을 교육합니다.

사용자의 하루 중 현재 시점과 상태를 고려하여 다음과 같은 활동을 제안합니다.

- 🧘 Yoga
- 🌬️ Breathing
- 🧠 Meditation

InnerFlow는 특정 활동을 강요하지 않습니다.

AI는 사용자의 현재 상태에 적합한 활동을 추천하지만,최종적으로 어떤 활동을 할지는 사용자가 직접 선택할 수 있도록 설계합니다.

## 💡 Core Concept

현재 상태를 이야기한다
↓
나의 상태를 알아차린다
↓
현재 순간에 잠시 머문다
↓
나에게 필요한 활동을 살펴본다
↓
내가 원하는 활동을 선택한다
↓
짧은 웰니스 경험을 시작한다

AI가 사용자를 대신해 답을 결정하는 것이 아니라,
사용자가 자신의 상태를 스스로 바라보고 선택할 수 있도록 돕는 것을 목표로 합니다.

🧭 User Flow

현재 구현된 기본 Flow는 다음과 같습니다.

User Input
│
│ 현재 상태 + 하루의 시점
▼
Flow Guide Agent
│
│ Awareness
│ Reflection Message
│ Mini Practice
│ Activity Recommendation
▼
Activity Router
│
├── Yoga Agent
│
├── Breathing Agent
│
└── Meditation Agent
│
▼
Activity Guidance

사용자는 다음 세 가지 시점 중 하나를 선택할 수 있습니다.

Morning — 하루의 시작
Pause — 하루를 보내는 중
Evening — 하루의 마무리

같은 감정이라도 하루의 시점에 따라 필요한 경험이 달라질 수 있기 때문에, InnerFlow는 session_type을 활동의 방향성을 결정하는 중요한 정보로 활용합니다.

예를 들어:

Morning → 활기차게 하루를 시작할 수 있는 방향
Pause → 현재 몸과 마음의 상태를 알아차리는 방향
Evening → 하루의 긴장을 풀고 마무리하는 방향
