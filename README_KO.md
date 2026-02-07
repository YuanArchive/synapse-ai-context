```
  ███████╗██╗   ██╗███╗   ██╗ █████╗ ██████╗ ███████╗███████╗
  ██╔════╝╚██╗ ██╔╝████╗  ██║██╔══██╗██╔══██╗██╔════╝██╔════╝
  ███████╗ ╚████╔╝ ██╔██╗ ██║███████║██████╔╝███████╗█████╗  
  ╚════██║  ╚██╔╝  ██║╚██╗██║██╔══██║██╔═══╝ ╚════██║██╔══╝  
  ███████║   ██║   ██║ ╚████║██║  ██║██║     ███████║███████╗
  ╚══════╝   ╚═╝   ╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝     ╚══════╝╚══════╝
                                                              
              🧠 AI 컨텍스트 증강 도구
```

<div align="center">

**대규모 코드베이스에서 AI 에이전트가 정확하게 작업할 수 있도록 지원**

[![Synapse CI](https://github.com/YuanArchive/synapse-ai-context/actions/workflows/ci.yml/badge.svg)](https://github.com/YuanArchive/synapse-ai-context/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![GitHub stars](https://img.shields.io/github/stars/YuanArchive/synapse-ai-context?style=social)](https://github.com/YuanArchive/synapse-ai-context)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/YuanArchive/synapse-ai-context/pulls)

🇺🇸 [English README](README.md) | 📖 [한국어 매뉴얼](docs/MANUAL_KO.md) | 🤖 [AI 세팅 가이드](docs/AGENT_BOOTSTRAP_KO.md)

> **"코드 1만 줄 넘어가니까 AI가 토큰만 쳐먹어서 빡쳐서 만듦."** — Yuan

> *"나는 프롬프트만 썼어. AI가 다 했어."* — Yuan, 2026

</div>

---

> [!WARNING]
> **본인 책임하에 사용하세요.** 이 툴은 새벽 3시에 환각 상태인 AI가 만들었습니다.
> - **버그 있나요?** 당근 빠따죠.
> - **테스트는요?** 돌아가긴 하더라고요.
> - **실무 사용?** 님 책임임.
> - **작동 하나요?** *내 컴퓨터*에선 잘 됨.

---

## 📋 목차

- [✨ 기능](#-기능)
- [📦 설치](#-설치)
- [🚀 빠른 시작](#-빠른-시작)
- [🤖 AI 연동](#-ai-연동)
- [📖 명령어](#-명령어)
- [🏗️ 아키텍처](#️-아키텍처)
- [🔧 문제 해결](#-문제-해결)
- [🤝 기여하기](#-기여하기)
- [📄 라이선스](#-라이선스)

---

## 🌍 다중 언어 지원 (Polyglot)
**Tree-sitter** 기반으로 다 씹어먹습니다.

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
![Go](https://img.shields.io/badge/Go-00ADD8?style=for-the-badge&logo=go&logoColor=white)
![Rust](https://img.shields.io/badge/Rust-000000?style=for-the-badge&logo=rust&logoColor=white)
![C++](https://img.shields.io/badge/C++-00599C?style=for-the-badge&logo=c%2B%2B&logoColor=white)
![Java](https://img.shields.io/badge/Java-ED8B00?style=for-the-badge&logo=openjdk&logoColor=white)

---


## ✨ 기능

<table>
<tr>
<td width="50%">

### 🔍 시맨틱 검색
키워드가 아닌 **의미**로 코드 검색. ChromaDB 벡터 임베딩 기반.

</td>
<td width="50%">

### 🕸️ 의존성 그래프
변경 시 **어디가 깨지는지** 파악. NetworkX 기반.

</td>
</tr>
<tr>
<td width="50%">

### 📊 증분 인덱싱
**변경된 파일만** 재인덱싱. MD5 해시 기반 변경 감지.

</td>
<td width="50%">

### 👁️ 파일 감시
코딩 중 **실시간** 자동 인덱싱. 장시간 세션을 위한 데몬 모드.

</td>
</tr>
<tr>
<td width="50%">

### 🧠 딥 씽크 모드
`--think` 플래그로 복잡한 버그에 대한 **Chain-of-Thought** 추론.

</td>
<td width="50%">

### 🗜️ 코드 압축
구조를 유지하면서 토큰 사용량을 줄이는 코드 **스켈레톤화**.

</td>
</tr>
</table>

---

## 🌍 다중 언어 지원 (Polyglot)
**Tree-sitter** 기반으로 다 씹어먹습니다.

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
![Go](https://img.shields.io/badge/Go-00ADD8?style=for-the-badge&logo=go&logoColor=white)
![Rust](https://img.shields.io/badge/Rust-000000?style=for-the-badge&logo=rust&logoColor=white)
![C++](https://img.shields.io/badge/C++-00599C?style=for-the-badge&logo=c%2B%2B&logoColor=white)
![Java](https://img.shields.io/badge/Java-ED8B00?style=for-the-badge&logo=openjdk&logoColor=white)

---

## 📦 설치

### 옵션 1: GitHub에서 설치 (권장)
```bash
pip install git+https://github.com/YuanArchive/synapse-ai-context.git
```

### 옵션 2: 개발 모드
```bash
git clone https://github.com/YuanArchive/synapse-ai-context.git
cd synapse-ai-context
pip install -e .
```

### 요구사항
- **Python 3.12+** (권장: 3.12.x)
- **C/C++ 컴파일러**: 일부 시스템에서 `tree-sitter` 컴파일을 위해 필요할 수 있습니다.
- 의존성 자동 설치: `chromadb`, `networkx`, `tree-sitter`, `watchdog`

### 🛡️ 권장 사항: 가상환경 사용

다른 프로젝트와의 의존성 충돌을 방지하기 위해 가상환경 사용을 강력히 권장합니다.

#### Windows
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install git+https://github.com/YuanArchive/synapse-ai-context.git
```

#### macOS / Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install git+https://github.com/YuanArchive/synapse-ai-context.git
```

---

## 🚀 빠른 시작

### 0️⃣ 설치 확인
설치 완료 후, Synapse가 정상적으로 설치되었는지 확인합니다:
```bash
synapse --help
```
명령어 목록이 나타나면 준비가 완료된 것입니다!

### 1️⃣ 초기화
```bash
cd your-project
synapse init
```

### 2️⃣ 분석
```bash
synapse analyze .           # 증분 분석 (빠름)
synapse analyze . --full    # 전체 재인덱싱
synapse analyze . --verbose # 디버그 모드
```

### 3️⃣ 검색
```bash
synapse search "로그인 핸들러"
synapse search "auth" --hybrid  # 벡터 + 그래프
```

### 4️⃣ 의존성 확인
```bash
synapse graph src/auth.py
```

### 5️⃣ 감시 시작 (선택)
```bash
synapse watch start --daemon
```

<details>
<summary>📂 <b>생성되는 디렉토리 구조</b></summary>

```
your-project/
├── .synapse/              # 인덱스 데이터베이스
│   ├── db/                # ChromaDB 벡터
│   ├── dependency_graph.gml
│   ├── file_hashes.json
│   └── INTELLIGENCE.md    # 자동 생성 아키텍처 문서
├── .agent/          
│   ├── AI_RULES_KO.md     # AI 에이전트 규칙 (한글)
│   └── AI_RULES_EN.md     # AI 에이전트 규칙 (영문)
└── docs/
    ├── SYNAPSE_MANUAL_KO.md
    └── AGENT_BOOTSTRAP.md
```

</details>

---

## 🤖 AI 연동

### AI 어시스턴트 빠른 설정

프롬프트에서 부트스트랩 파일을 태그하세요:

```
@docs/AGENT_BOOTSTRAP_KO.md 이 프로젝트 세팅해줘
```

AI가 자동으로 모든 설정 명령어를 실행합니다!

### 핵심 원칙 (AI 필수 준수)

| 규칙 | 명령어 |
|------|--------|
| 🔍 **Search Before Strike** | 수정 전 `synapse search <query>` |
| 🕸️ **Check the Graph** | 리팩토링 전 `synapse graph <file>` |
| 🧠 **Deep Think on Failure** | 막힐 때 `synapse ask "<error>" --think` |

### 전역 규칙 설정

```bash
# Antigravity / Gemini
cp AI_RULES_KO.md ~/.gemini/GEMINI.md

# Cursor
cp AI_RULES_KO.md your-project/.cursorrules
```

---

## 📖 명령어

| 명령어 | 설명 |
|--------|------|
| `synapse init` | 프로젝트 초기화 |
| `synapse analyze .` | 증분 분석 |
| `synapse analyze . --full` | 전체 재인덱싱 |
| `synapse analyze . --verbose` | 디버그 로깅 |
| `synapse search "<쿼리>"` | 시맨틱 검색 |
| `synapse search "<쿼리>" --hybrid` | 벡터 + 그래프 검색 |
| `synapse graph <파일>` | 의존성 표시 |
| `synapse ask "<질문>" --think` | 딥 추론 |
| `synapse context <파일>` | 계층적 컨텍스트 |
| `synapse skeleton <파일>` | 코드 스켈레톤화 |
| `synapse watch start` | 파일 감시 시작 |
| `synapse watch start --daemon` | 백그라운드 감시 |
| `synapse watch status` | 감시 상태 확인 |
| `synapse watch stop` | 감시 중지 |

---

## 🏗️ 아키텍처

```
synapse/
├── src/synapse/
│   ├── cli.py              # CLI 명령어 (Typer)
│   ├── analyzer.py         # 프로젝트 분석 엔진
│   ├── vector_store.py     # ChromaDB 통합
│   ├── graph.py            # 의존성 그래프 (NetworkX)
│   ├── parser.py           # Tree-sitter 코드 파싱
│   ├── watcher.py          # 파일 감시 (watchdog)
│   ├── hybrid_search.py    # 벡터 + 그래프 검색
│   ├── context_manager.py  # 계층적 컨텍스트
│   ├── compressor.py       # 코드 스켈레톤화
│   ├── exceptions.py       # 커스텀 예외
│   └── logger.py           # 로깅 시스템
├── docs/                   # 문서
└── tests/                  # 테스트 스위트
```

---

## 🔧 문제 해결

<details>
<summary><b>ChromaDB 오류</b></summary>

```bash
rm -rf .synapse/db
synapse analyze . --full
```

</details>

<details>
<summary><b>감시 응답 없음</b></summary>

```bash
synapse watch stop
synapse watch start --daemon
```

</details>

<details>
<summary><b>전체 초기화</b></summary>

```bash
rm -rf .synapse
synapse init
synapse analyze . --full
```

</details>

---

## 🤝 기여하기

**제발 고쳐주세요.** 저는 코딩을 할 줄 모릅니다. 이게 뭔지도 모르겠어요.

- 🐛 **버그 발견?** 이거 전체가 버그일 수도 있습니다.
- 💡 **파이썬 할 줄 아세요?** 살려주세요.
- 🔧 **PR 환영:** 제발 저를 구원해주세요.

---

## 📄 라이선스

MIT 라이선스 — 개인 및 상업적 사용 무료

---

<div align="center">

## 🙏 크레딧

**Yuan** 🧑‍💻 (핑프) + **AI** 🤖 (진짜 코드 짠 애)

> *"나는 프롬프트만 썼어, AI가 다 했어"*
> — 2026년 모든 개발자

---

**⭐ 유용하다면 Star를 눌러주세요!**

*Powered by Synapse & Antigravity*

</div>
