# 🚀 Synapse Agent Bootstrap

> **AI 에이전트 전용** — AI가 이 파일을 읽으면 아래 단계를 순서대로 실행합니다.

---

## 🎯 원라인 세팅

```bash
python -m synapse init && python -m synapse analyze . --full && python -m synapse watch start --daemon
```

---

## 📋 단계별 세팅

### Step 1: Synapse 초기화
```bash
python -m synapse init
```
- `.synapse/`, `.context/`, `.agent/` 디렉토리 생성
- `AI_RULES_KO.md`, `AI_RULES_EN.md` 자동 생성

### Step 2: 전체 인덱싱
```bash
python -m synapse analyze . --full
```
- 모든 코드 파일 파싱
- 벡터 인덱스 + 의존성 그래프 생성

### Step 3: Watcher 시작 (선택)
```bash
python -m synapse watch start --daemon
```
- 백그라운드 파일 감시
- 자동 증분 인덱싱

### Step 4: 아키텍처 파악
```bash
# 파일 읽기
.synapse/INTELLIGENCE.md
```
- 프로젝트 아키텍처 파악
- 핵심 모듈 및 의존성 이해

---

## ✅ 세팅 완료 체크리스트

위 명령어 실행 후 확인:

- [ ] `.synapse/` 디렉토리 존재
- [ ] `.synapse/dependency_graph.gml` 생성됨
- [ ] `python -m synapse watch status` → Running (선택)

---

## 🔧 문제 해결

| 문제 | 해결 |
|------|------|
| synapse 명령어 없음 | `pip install git+https://github.com/YuanArchive/synapse-ai-context.git` |
| ChromaDB 오류 | `rm -rf .synapse/db && python -m synapse analyze . --full` |
| Watcher 실패 | `python -m synapse watch stop && python -m synapse watch start --daemon` |

---

## 📖 세팅 후

세팅 완료 후 AI는 다음 규칙을 따릅니다:
1. 코드 수정 전 `python -m synapse search <query>` 실행
2. 리팩토링 전 `python -m synapse graph <file>` 확인
3. 에러 발생 시 `python -m synapse ask "<error>" --think` 실행

**규칙 상세**: `.agent/rules.md` 참조

---

**규칙 상세**: `.agent/rules.md` 참조

---

## 🔑 골든 프롬프트 (Golden Prompt)

이 프로젝트를 AI에게 인계할 때, 첫 마디(System Prompt)로 아래 내용을 사용하세요. 
자동으로 언어를 감지하여 적절한 규칙을 따르게 됩니다.

```text
You are controlled by the Synapse AI Protocol.

1. If I speak KOREAN:
   - Read `docs/AI_RULES_KO.md` immediately.
   - Prove you followed the 'Pre-Work' instructions in that file.

2. If I speak ENGLISH (or other languages):
   - Read `docs/AI_RULES_EN.md` immediately.
   - Prove you followed the 'Pre-Work' instructions in that file.

🚫 DO NOT answer my question until you have completed steps 1 & 2.
```

---

*Synapse v0.1.0 | *Powered by Synapse & Antigravity*
