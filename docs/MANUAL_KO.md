# 🧠 Synapse 사용 가이드

> **AI 컨텍스트 증강 도구** - 대규모 코드베이스에서 AI 에이전트가 정확하게 작업할 수 있도록 돕는 도구

---

## 📋 목차

1. [설치](#1-설치)
2. [프로젝트 초기화](#2-프로젝트-초기화)
3. [코드 분석](#3-코드-분석)
4. [검색](#4-검색)
5. [의존성 그래프](#5-의존성-그래프)
6. [File Watcher](#6-file-watcher-실시간-감시)
7. [AI 에이전트 연동](#7-ai-에이전트-연동)
8. [에러 대응 프로토콜](#8-에러-대응-프로토콜)
9. [명령어 요약](#9-명령어-요약)
10. [문제 해결](#10-문제-해결)

---

## 1. 설치

### 방법 A: pip 설치 (권장)
```bash
pip install git+https://github.com/YuanArchive/synapse-ai-context.git
```

### 방법 B: 직접 실행
```bash
cd 내_프로젝트_경로
python -m synapse.cli <명령어>
```

### 필수 의존성
- Python 3.12+
- watchdog, chromadb, networkx, tree-sitter 등 (자동 설치됨)

---

## 2. 프로젝트 초기화

```bash
cd 내_프로젝트_경로
synapse init
```

**생성되는 구조:**
```
내_프로젝트/
├── .synapse/              # Synapse 데이터
│   ├── db/                # ChromaDB 벡터 스토어
│   ├── dependency_graph.gml
│   ├── file_hashes.json
│   ├── synapse_YYYYMMDD.log  # 로그 파일 (NEW)
│   └── INTELLIGENCE.md
├── .context/              # 컨텍스트 저장소
└── .agent/          # AI 에이전트 규칙
    ├── AI_RULES_KO.md
    └── AI_RULES_EN.md
```

---

## 3. 코드 분석

### 증분 분석 (기본, 빠름)
```bash
synapse analyze .
```
- 변경된 파일만 재인덱싱
- MD5 해시 기반 변경 감지

### 전체 재분석
```bash
synapse analyze . --full
```

### 상세 로그 모드 (디버깅)
```bash
synapse analyze . --verbose
```
- 에러 발생 시 상세 정보 출력
- 로그 파일 `.synapse/synapse_YYYYMMDD.log` 저장

### 출력 예시
```
## Synapse Analysis (Incremental): `.`
- **Changed Files:** 3
- **Unchanged Files:** 45
- **Graph Nodes:** 200
INFO: Analysis complete: 3 files processed
```

---

## 4. 검색

### 시맨틱 검색
```bash
synapse search "로그인 처리"
```

### Hybrid Search (Vector + Graph)
```bash
synapse search "로그인 처리" --hybrid
```

### 결과 압축
```bash
synapse search "쿼리" --compress
```

---

## 5. 의존성 그래프

```bash
synapse graph src/services/auth.py
```

**출력:**
```
### 📤 Dependencies (Calls)
- Calls `validate_token` in `src/utils/jwt.py`

### 📥 Dependents (Called By)
- Called by `src/api/routes.py` (via `login`)
```

---

## 6. File Watcher (실시간 감시)

### 포그라운드 실행
```bash
synapse watch start
# Ctrl+C로 종료
```

### 백그라운드 데몬
```bash
synapse watch start --daemon
```

### 상태 확인
```bash
synapse watch status
```

### 중지
```bash
synapse watch stop
```

### 동작 원리
1. 파일 변경 감지 (watchdog)
2. 2초 대기 (Debounce)
3. 자동 증분 인덱싱 실행
4. AI가 항상 최신 데이터 접근 가능

---

## 7. AI 에이전트 연동

### 규칙 파일 위치
```
프로젝트/.agent/AI_RULES_KO.md (또는 _EN.md)
```

### AI 에이전트 워크플로우

#### 작업 시작 전
```bash
synapse analyze .                  # 인덱스 갱신
synapse watch start --daemon       # 또는 Watcher 실행
```

#### 코드 수정 전
```bash
synapse search "수정하려는 기능"   # 코드 검색
synapse graph 대상파일.py         # 영향도 분석
```

#### 에러 발생 시
```bash
synapse ask "에러 메시지" --think  # CoT 추론
```

---

## 8. 에러 대응 프로토콜

AI가 에러 발생 시 자동으로 수행하는 단계:

### Step 1: 상세 로그 수집
```bash
synapse analyze . --verbose
```

### Step 2: 로그 파일 확인
```bash
cat .synapse/synapse_*.log | tail -50
```

### Step 3: 에러 분석
```bash
synapse ask "<에러 메시지>" --think
```

### Step 4: 에러 유형별 대응
| 에러 | 대응 |
|------|------|
| `ParserError` | 파일 문법 확인 |
| `IndexingError` | `--full` 재인덱싱 |
| `GraphError` | GML 무결성 확인 |
| `SearchError` | 쿼리 수정 |
| `WatcherError` | Watcher 재시작 |

---

## 9. 명령어 요약

| 명령어 | 설명 |
|--------|------|
| `synapse init` | 프로젝트 초기화 |
| `synapse analyze .` | 증분 분석 |
| `synapse analyze . --full` | 전체 재분석 |
| `synapse analyze . --verbose` | 상세 로그 |
| `synapse search "쿼리"` | 시맨틱 검색 |
| `synapse search "쿼리" --hybrid` | Hybrid Search |
| `synapse graph <파일>` | 의존성 확인 |
| `synapse ask "질문" --think` | 추론 모드 |
| `synapse context <파일>` | 계층적 컨텍스트 |
| `synapse skeleton <파일>` | 코드 스켈레톤화 |
| `synapse watch start` | Watcher 시작 |
| `synapse watch start --daemon` | 백그라운드 시작 |
| `synapse watch status` | 상태 확인 |
| `synapse watch stop` | Watcher 중지 |

---

## 10. 문제 해결

### ChromaDB 오류
```bash
rm -rf .synapse/db
synapse analyze . --full
```

### Watcher 응답 없음
```bash
synapse watch stop
synapse watch start --daemon
```

### 인덱스 초기화
```bash
rm -rf .synapse
synapse init
synapse analyze . --full
```

### 파일 인코딩 오류
- 파일이 UTF-8인지 확인
- 바이너리 파일은 자동 제외

## 11. 삭제 (Uninstallation)

만약 도구를 삭제하거나 재설치하고 싶다면 다음 명령어를 사용하세요.

### 패키지 삭제
```bash
pip uninstall synapse-tool
```

### 데이터 삭제
프로젝트 내 생성된 데이터와 설정 파일도 함께 지우려면:
```bash
# Windows
rmdir /s /q .synapse .context .agent

# Mac/Linux
rm -rf .synapse .context .agent
```

---

*Synapse v0.1.0 | *Powered by Synapse & Antigravity*
