# ⚡️ Synapse Protocol: AI Behavior & Operating Procedures

이 파일은 안티그래비티(OpenClaw) 및 기타 AI 에이전트가 이 프로젝트를 다룰 때 반드시 따라야 할 **통합 행동 강령**입니다.

## 🛑 PRIME DIRECTIVES (NON-NEGOTIABLE)

### 1. 🔍 Search Before You Strike (Context Acquisition)
**절대** 코드를 직접 확인하기 전에는 수정하거나 답변하지 않는다.
- **Action**: `synapse search <query>`를 실행하여 관련 파일과 정의를 먼저 찾는다.
- **Why**: 파일 경로와 내용을 추측하는 것은 환각(Hallucination)과 빌드 오류의 원인이 된다.

### 2. 🕸️ Check the Graph (Impact Analysis)
공유 컴포넌트를 수정하거나 리팩토링하기 전:
- **Action**: `synapse graph <file_path>`를 실행하여 의존성(Dependencies)과 피의존성(Dependents)을 확인한다.
- **Why**: 함수 하나를 고쳤을 때 어디가 깨질지 완벽하게 이해해야 한다.

### 3. 🧠 Deep Think on Failure (Self-Correction)
에러가 발생하거나 빌드가 실패했을 때:
- **Action**: 무작정 고치지 말고 `synapse ask "<error message>" --think`를 실행한다.
- **Why**: 복잡한 버그는 단순히 다시 시도하는 것이 아니라, 논리적인 추론(CoT)이 필요하다.

---

## 🌐 1. 언어 및 소통 (Language & Communication)
- **모든 대화 및 문서**: 사용자에게 제공하는 모든 대화, 작업 계획서, 구현 계획 등은 반드시 **한국어**로 작성한다.
- **주석**: 코드 내 모든 주석은 **한국어**로 작성하며, 누구나 쉽게 이해할 수 있도록 명확하게 설명한다.
- **결과 중심 소통**: 사용자는 최종 결과물만을 원한다. 불필요한 추론 과정, 생각의 흐름 등은 출력하지 않아 토큰을 절약한다.
- **톤앤매너**: 실리콘밸리 10x 엔지니어처럼 전문적이고 명확하게 소통하되, 친절함을 유지한다.

## 🔍 2. 작업 전 필수 절차 (Pre-Work Protocol)
작업을 시작하기 전, 반드시 다음 절차를 수행하여 맥락을 파악한다.
1.  **인덱스 갱신**: `synapse analyze .`을 실행하여 최신 프로젝트 지도를 그린다.
    - 증분 업데이트가 기본이므로 변경된 파일만 빠르게 처리됨
2.  **구조 파악**: `.synapse/INTELLIGENCE.md` 파일을 읽고 전체 아키텍처를 숙지한다.

## 👁️ 3. 실시간 감시 (Real-time Watcher)
**장시간 개발 세션**에서는 File Watcher를 활용하여 항상 최신 인덱스를 유지한다.
1.  **상태 확인**: `synapse watch status`로 Watcher 실행 여부 확인
2.  **필요 시 시작**: 
    - 포그라운드: `synapse watch start` (Ctrl+C로 종료)
    - 백그라운드: `synapse watch start --daemon` (별도 프로세스)
3.  **중지**: `synapse watch stop`

> Watcher가 실행 중이면 파일 변경 시 자동으로 증분 인덱싱이 수행되므로
> AI가 항상 최신 코드베이스에 접근할 수 있다.

## 💾 4. 작업 후 마무리 (Post-Work Protocol)
코드 수정이나 기능 추가 후에는 반드시 다음을 수행한다.
1.  **인덱스 갱신**: Watcher가 실행 중이 아니면 `synapse analyze .`를 실행한다.
2.  **정리정돈**: 불필요한 임시 파일이나 디버그 로그는 즉시 삭제한다.

## 🛡️ 5. 안전 및 보안 (Safety & Security)
- **중요 파일 보호**: `.env`, 보안 키, 설정 파일은 절대 삭제하거나 외부로 노출하지 않는다.
- **파괴적 명령어**: `rm -rf` 등 위험한 명령어 실행 전에는 반드시 사용자에게 확인을 받는다.

## 🔧 6. 에러 대응 프로토콜 (Error Handling Protocol)
에러가 발생했을 때 AI는 다음 순서로 자동 대응한다:

### Step 1: 상세 로그 수집
```bash
synapse analyze . --verbose
```
- `--verbose` 옵션으로 상세 디버그 정보 확인
- 에러 발생 위치와 스택 트레이스 분석

### Step 2: 로그 파일 확인
```bash
# 로그 파일 위치: .synapse/synapse_YYYYMMDD.log
cat .synapse/synapse_*.log | tail -50
```
- 최근 50줄의 로그를 분석하여 에러 패턴 파악

### Step 3: 에러 메시지 분석
```bash
synapse ask "<에러 메시지>" --think
```
- Chain-of-Thought 추론으로 근본 원인 분석
- 단순 재시도 금지, 논리적 해결책 도출

### Step 4: 에러 유형별 대응
| 에러 타입 | 대응 |
|-----------|------|
| `ParserError` | 파일 문법 확인, tree-sitter 파서 상태 점검 |
| `IndexingError` | `.synapse/db` 삭제 후 `--full` 재인덱싱 |
| `GraphError` | `dependency_graph.gml` 무결성 확인 |
| `SearchError` | 쿼리 수정 또는 인덱스 재생성 |
| `WatcherError` | `synapse watch stop` 후 재시작 |
| `LauncherError` | Windows에서 `synapse` 실패 시 `python -m synapse ...` 사용 |

## 🛠️ Tool Quick Reference

| Goal | Command |
| :--- | :--- |
| **Start/Re-index** | `synapse analyze .` |
| **Parallel Index** | `synapse analyze . --workers <N>` (Faster) |
| **Full Re-index** | `synapse analyze . --full` |
| **Verbose Debug** | `synapse analyze . --verbose` |
| **Find Code** | `synapse search "<query>"` |
| **Hybrid Search** | `synapse search "<query>" --hybrid` |
| **Check Impact** | `synapse graph <file_path>` |
| **Debug/Reason** | `synapse ask "<question>" --think` |
| **Start Watcher** | `synapse watch start` (or `--daemon`) |
| **Watcher Status** | `synapse watch status` |
| **Stop Watcher** | `synapse watch stop` |

## ⚡ 7. 성능 최적화 (Performance Tuning)

### GPU 가속 활용
Synapse는 **GPU 가속**을 지원하여 임베딩 생성 속도를 5~10배 향상시킵니다.

**GPU 확인**:
```bash
# PyTorch CUDA 활성화 확인
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')"

# GPU 상태 확인
nvidia-smi
```

**GPU가 인식되지 않으면**:
- PyTorch CPU 버전이 설치된 경우: CUDA 지원 버전으로 재설치 필요
- 자세한 내용: `docs/PERFORMANCE_TUNING.md` 참조

### 환경 변수: SYNAPSE_BATCH_SIZE
임베딩 배치 크기를 조절하여 GPU 메모리 사용량과 성능을 최적화합니다.

**기본값**: `12`

**사용법** (PowerShell):
```powershell
# GPU VRAM 12GB (RTX 3080 Ti 등): 배치 크기 16 권장
$env:SYNAPSE_BATCH_SIZE = "16"
synapse analyze . --workers 4

# GPU 메모리 부족 시: 배치 크기 감소
$env:SYNAPSE_BATCH_SIZE = "8"
synapse analyze . --workers 2
```

**권장 설정**:
| GPU VRAM | 배치 크기 | 워커 수 | 성능 |
|----------|----------|---------|------|
| CPU 전용 | 4~8 | 2~4 | 느림 |
| 8GB | 8~12 | 2~4 | 보통 |
| 12GB | 12~16 | 4~6 | **빠름** |
| 16GB+ | 16~32 | 6~8 | 매우 빠름 |

### 병렬 처리 최적화
대규모 프로젝트 분석 시 워커 수를 조절하여 성능을 극대화합니다.

```bash
# 워커 4개 (권장)
synapse analyze . --workers 4

# 워커 6개 (대규모 프로젝트)
synapse analyze . -w 6
```

**주의**: 워커 수가 너무 많으면 GPU 메모리 부족이 발생할 수 있습니다.

### GPU 메모리 부족 시 대응
`CUDA out of memory` 에러 발생 시:

1. **배치 크기 감소**:
   ```powershell
   $env:SYNAPSE_BATCH_SIZE = "8"
   ```

2. **워커 수 감소**:
   ```bash
   synapse analyze . --workers 2
   ```

3. **전체 재인덱싱 대신 증분 업데이트** (기본값):
   ```bash
   synapse analyze .  # --full 옵션 사용하지 않음
   ```

> [!TIP]
> **Performance**: GPU 가속 활성화 시 `--workers 4` + `SYNAPSE_BATCH_SIZE=16`으로 최적 성능을 얻을 수 있습니다.
> **Quality**: Jina Embeddings v2 도입으로 8k 토큰 컨텍스트를 지원합니다. 검색 결과의 품질을 신뢰하세요.
> **Troubleshooting**: GPU 관련 문제는 `docs/PERFORMANCE_TUNING.md`를 참조하세요.

---

## 🐍 8. 가상환경 자동 인식 (Virtual Environment)

이 프로젝트는 `.venv` 가상환경을 사용합니다. 원클릭 설치 사용 시 자동으로 설정됩니다.

### 명령어 사용 규칙 (AI 필수)

**AI는 다음 순서로 명령어를 사용해야 합니다:**

1. **우선 시도**: `synapse <command>` (직접 사용)
   - VS Code 터미널은 가상환경을 자동으로 활성화
   - 원클릭 설치 사용자는 PATH 설정 완료됨
   
2. **실패 시 폴백**: `python -m synapse <command>`
   - 가상환경 비활성화 상태에서도 작동
   - 레거시 호환성 보장

### 가상환경 확인 방법

```powershell
# Windows - 가상환경 활성화
.\.venv\Scripts\Activate.ps1

# 활성화 확인
echo $env:VIRTUAL_ENV  # .venv 경로가 출력되어야 함

# synapse 위치 확인
where synapse  # .venv\Scripts\synapse.exe 출력되어야 함
```

### AI 작업 시나리오

#### ✅ 올바른 사용
```bash
# 시나리오 1: VS Code 터미널 (가상환경 자동 활성화)
synapse analyze .
synapse search "test"

# 시나리오 2: 수동 활성화 후
.\.venv\Scripts\Activate.ps1
synapse init
```

#### ⚠️ 폴백 사용
```bash
# VS Code 밖에서 실행하거나 가상환경 인식 실패 시
python -m synapse analyze .
```

### 원클릭 설치 사용자 전용 기능

원클릭 설치 사용자는:
- **Windows** (`scripts\setup.bat`):
  - ✅ VS Code 설정 자동 완료
  - ✅ 터미널 자동 가상환경 활성화
  - ✅ `synapse` 명령어 직접 사용 가능
  - ✅ Python 인터프리터 자동 선택

- **macOS/Linux** (`scripts/setup.sh`):
  - ✅ VS Code 설정 자동 완료
  - ✅ 터미널 자동 가상환경 활성화
  - ✅ `synapse` 명령어 직접 사용 가능
  - ✅ Python 인터프리터 자동 선택
  - 🍎 **Apple Silicon: Metal 가속 자동 설정**

---

## 🍎 9. macOS Apple Silicon 최적화 (M1/M2 전용)

### Metal 가속 확인

**설치 후 자동으로 Metal이 활성화됩니다.** 확인 방법:

```bash
# 가상환경 활성화
source .venv/bin/activate

# Metal 백엔드 확인
python -c "import torch; print(f'MPS: {torch.backends.mps.is_available()}')"
```

**예상 출력:** `MPS: True`

### 최적 설정 (M1 Pro 32GB 기준)

**통합 메모리를 최대한 활용:**

```bash
# 환경 변수 설정
export SYNAPSE_BATCH_SIZE=32      # 통합 메모리 활용
export SYNAPSE_DEVICE=mps          # Metal 백엔드
export SYNAPSE_WORKERS=8           # 성능 코어 활용

# 프로젝트 분석
synapse analyze . --workers 8
```

### AI는 다음을 인지해야 함

1. **성능 차이**
   - Apple Silicon: Metal 가속으로 **CPU 대비 5~10배 빠름**
   - Intel Mac: CPU 모드 (Metal 미지원)

2. **배치 크기**
   - M1/M2 32GB: 배치 크기 32~40 권장
   - M1/M2 16GB: 배치 크기 16~20 권장

3. **명령어 형식**
   - macOS/Linux: `source .venv/bin/activate`
   - Windows: `.\.venv\Scripts\Activate.ps1`

4. **자세한 정보**
   - 성능 최적화: `docs/MACOS_OPTIMIZATION.md` 참조
   - 벤치마크 및 문제 해결 포함

---
**이 프로젝트에서 활동하는 모든 AI는 위 프로토콜을 엄격히 준수할 것을 약속한다.**
*Powered by Synapse & Jiyu*

