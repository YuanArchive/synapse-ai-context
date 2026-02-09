# 성능 튜닝 가이드

Synapse AI의 성능을 최적화하기 위한 설정 가이드입니다.

## 🎛️ 환경 변수 설정

### SYNAPSE_BATCH_SIZE (배치 크기)

임베딩 벡터 생성 시 한 번에 처리할 문서 수를 제어합니다.

**기본값**: `12`

**권장 설정**:
| GPU VRAM | 배치 크기 | 설명 |
|----------|----------|------|
| CPU 전용 | 4~8 | 메모리 절약 |
| 8GB | 8~12 | 안정적 |
| 12GB (RTX 3080 Ti) | 12~16 | **권장** |
| 16GB+ | 16~32 | 최대 성능 |

**사용 예시** (PowerShell):
```powershell
# 배치 크기 16으로 증가 (GPU VRAM 충분 시)
$env:SYNAPSE_BATCH_SIZE = "16"
synapse analyze .

# 배치 크기 8로 감소 (메모리 부족 시)
$env:SYNAPSE_BATCH_SIZE = "8"
synapse analyze .
```

**사용 예시** (CMD):
```cmd
set SYNAPSE_BATCH_SIZE=16
synapse analyze .
```

**사용 예시** (Linux/Mac):
```bash
export SYNAPSE_BATCH_SIZE=16
synapse analyze .
```

---

## 🔧 CLI 옵션

### --workers (병렬 처리 워커 수)

파일 파싱 및 인덱싱을 병렬로 처리할 프로세스 수입니다.

**기본값**: CPU 코어 수

**사용 예시**:
```bash
# 워커 4개로 병렬 처리
synapse analyze . --workers 4

# 워커 8개 (대규모 프로젝트)
synapse analyze . -w 8

# 전체 재인덱싱 + 워커 6개
synapse analyze . --full --workers 6
```

**권장 설정**:
| GPU VRAM | 워커 수 | 배치 크기 | 종합 성능 |
|----------|---------|----------|----------|
| CPU 전용 | 2~4 | 4~8 | 느림 |
| 8GB | 2~4 | 8~12 | 보통 |
| 12GB (RTX 3080 Ti) | 4~6 | 12~16 | **빠름** |
| 16GB+ | 6~8 | 16~32 | 매우 빠름 |

---

## 🚀 최적 성능 조합 (RTX 3080 Ti)

```powershell
# GPU 메모리 12GB를 최대 활용
$env:SYNAPSE_BATCH_SIZE = "16"
synapse analyze . --workers 4
```

**예상 성능**:
- 1000개 파일: **3~5분** (CPU 전용: 20~25분)
- 인덱싱 속도: **500+ files/min** (CPU: 100 files/min)
- GPU 사용률: 80~90%
- 시스템 RAM: 2~4GB (CPU: 8~12GB)

---

## ⚠️ 문제 해결

### GPU 메모리 부족 (`CUDA out of memory`)

**증상**:
```
RuntimeError: CUDA out of memory. Tried to allocate X.XX GiB
```

**해결책**:
1. 배치 크기 감소:
   ```powershell
   $env:SYNAPSE_BATCH_SIZE = "8"
   ```

2. 워커 수 감소:
   ```bash
   synapse analyze . --workers 2
   ```

3. 둘 다 조절:
   ```powershell
   $env:SYNAPSE_BATCH_SIZE = "4"
   synapse analyze . --workers 2
   ```

### 시스템 RAM 부족

**증상**: 프로세스가 느려지거나 중단됨

**해결책**:
- 워커 수 감소: `--workers 2`
- 배치 크기 감소: `SYNAPSE_BATCH_SIZE=8`

### 너무 느린 인덱싱

**확인 사항**:
1. GPU가 실제로 사용되는지 확인:
   ```bash
   nvidia-smi
   ```

2. PyTorch CUDA 활성화 확인:
   ```bash
   python -c "import torch; print(torch.cuda.is_available())"
   ```

3. 워커 수 증가:
   ```bash
   synapse analyze . --workers 6
   ```

---

## 📊 벤치마크 예시

**테스트 환경**: RTX 3080 Ti, 1000개 Python 파일

| 설정 | 배치 크기 | 워커 | 소요 시간 | GPU 사용률 |
|------|----------|------|----------|------------|
| 기본 (CPU) | 12 | 4 | 25분 | 0% |
| GPU 기본 | 12 | 4 | 5분 | 60% |
| GPU 최적화 | 16 | 6 | **3분** | **85%** |
| GPU 공격적 | 32 | 8 | 2.5분 | 95% (주의) |

> **주의**: "GPU 공격적" 설정은 메모리 부족 위험이 있습니다.
