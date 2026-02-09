#!/bin/bash
# Synapse 원클릭 설치 스크립트 (macOS/Linux)
# Bash 4.0+ 필요

set -e  # 에러 시 즉시 종료

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# 출력 함수
print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_info() { echo -e "${CYAN}ℹ️  $1${NC}"; }
print_step() { echo -e "\n${MAGENTA}🔹 $1${NC}"; }

# 배너 출력
show_banner() {
    echo -e "${CYAN}"
    cat << 'EOF'

  ███████╗██╗   ██╗███╗   ██╗ █████╗ ██████╗ ███████╗███████╗
  ██╔════╝╚██╗ ██╔╝████╗  ██║██╔══██╗██╔══██╗██╔════╝██╔════╝
  ███████╗ ╚████╔╝ ██╔██╗ ██║███████║██████╔╝███████╗█████╗  
  ╚════██║  ╚██╔╝  ██║╚██╗██║██╔══██║██╔═══╝ ╚════██║██╔══╝  
  ███████║   ██║   ██║ ╚████║██║  ██║██║     ███████║███████╗
  ╚══════╝   ╚═╝   ╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝     ╚══════╝╚══════╝
                                                               
            🧠 AI 컨텍스트 증강 도구 - 원클릭 설치기
            
EOF
    echo -e "${NC}"
}

# OS 및 아키텍처 감지
detect_system() {
    print_step "시스템 정보 감지 중..."
    
    OS="$(uname -s)"
    ARCH="$(uname -m)"
    USE_METAL=false
    
    case "$OS" in
        Darwin*)
            if [ "$ARCH" = "arm64" ]; then
                print_success "🍎 macOS Apple Silicon (M1/M2) 감지됨"
                OS_TYPE="macos_arm"
                USE_METAL=true
                PYTHON_CMD="python3"
            else
                print_success "🍎 macOS Intel 감지됨"
                OS_TYPE="macos_intel"
                PYTHON_CMD="python3"
            fi
            ;;
        Linux*)
            print_success "🐧 Linux 감지됨"
            OS_TYPE="linux"
            PYTHON_CMD="python3"
            ;;
        *)
            print_error "지원하지 않는 OS: $OS"
            exit 1
            ;;
    esac
    
    print_info "아키텍처: $ARCH"
    
    if [ "$USE_METAL" = true ]; then
        print_info "Metal 가속 사용 가능"
    fi
}

# Python 버전 확인
check_python() {
    print_step "Python 버전 확인 중..."
    
    if command -v python3.12 &> /dev/null; then
        PYTHON_CMD="python3.12"
        VERSION=$(python3.12 --version 2>&1 | awk '{print $2}')
        print_success "Python 3.12 발견: $VERSION"
        return 0
    elif command -v python3 &> /dev/null; then
        VERSION=$(python3 --version 2>&1 | awk '{print $2}')
        MAJOR=$(echo $VERSION | cut -d. -f1)
        MINOR=$(echo $VERSION | cut -d. -f2)
        
        if [ "$MAJOR" = "3" ] && [ "$MINOR" -ge 10 ] && [ "$MINOR" -le 13 ]; then
            PYTHON_CMD="python3"
            print_success "호환 가능한 Python 버전: $VERSION"
            return 0
        else
            print_warning "Python $VERSION 발견됨 (3.10~3.13 권장)"
            return 1
        fi
    else
        print_error "Python이 설치되지 않았습니다"
        return 1
    fi
}

# Homebrew 설치 (macOS)
install_homebrew() {
    if [[ "$OS_TYPE" != macos* ]]; then
        return 0
    fi
    
    print_step "Homebrew 확인 중..."
    
    if command -v brew &> /dev/null; then
        print_success "Homebrew 이미 설치됨"
        return 0
    fi
    
    print_warning "Homebrew가 설치되지 않았습니다"
    read -p "Homebrew를 설치하시겠습니까? (y/N): " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_warning "Homebrew 설치를 건너뜁니다"
        return 1
    fi
    
    print_info "Homebrew 설치 중... (시간이 걸릴 수 있습니다)"
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    
    # PATH에 Homebrew 추가
    if [ "$ARCH" = "arm64" ]; then
        eval "$(/opt/homebrew/bin/brew shellenv)"
    else
        eval "$(/usr/local/bin/brew shellenv)"
    fi
    
    print_success "Homebrew 설치 완료"
}

# Python 설치
install_python() {
    print_step "Python 3.12 설치 중..."
    
    if [[ "$OS_TYPE" == macos* ]]; then
        # macOS - Homebrew 사용
        if ! command -v brew &> /dev/null; then
            print_error "Homebrew가 필요합니다. 수동으로 Python 3.12를 설치해주세요."
            print_info "다운로드: https://www.python.org/downloads/"
            return 1
        fi
        
        print_info "Homebrew를 통해 Python 3.12 설치 중..."
        brew install python@3.12
        
        # PATH 업데이트
        if [ "$ARCH" = "arm64" ]; then
            export PATH="/opt/homebrew/opt/python@3.12/bin:$PATH"
        else
            export PATH="/usr/local/opt/python@3.12/bin:$PATH"
        fi
        
        PYTHON_CMD="python3.12"
        
    else
        # Linux - deadsnakes PPA 권장
        print_error "Linux에서는 수동으로 Python 3.12를 설치해주세요."
        print_info "Ubuntu/Debian: sudo add-apt-repository ppa:deadsnakes/ppa && sudo apt install python3.12"
        return 1
    fi
    
    if check_python; then
        print_success "Python 3.12 설치 완료"
        return 0
    else
        print_error "Python 설치 실패"
        return 1
    fi
}

# 가상환경 생성
create_venv() {
    print_step "가상환경 생성 중..."
    
    VENV_PATH=".venv"
    
    if [ -d "$VENV_PATH" ]; then
        print_warning "가상환경이 이미 존재합니다: $VENV_PATH"
        read -p "기존 가상환경을 삭제하고 재생성하시겠습니까? (y/N): " -n 1 -r
        echo
        
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf "$VENV_PATH"
            print_info "기존 가상환경 삭제됨"
        else
            print_info "기존 가상환경 사용"
            return 0
        fi
    fi
    
    $PYTHON_CMD -m venv "$VENV_PATH"
    print_success "가상환경 생성 완료: $VENV_PATH"
}

# Synapse 설치
install_synapse() {
    print_step "Synapse 설치 중..."
    
    # 가상환경 활성화
    source .venv/bin/activate
    
    print_info "pip 업그레이드 중..."
    python -m pip install --upgrade pip --quiet
    
    print_info "Synapse 설치 중... (시간이 걸릴 수 있습니다)"
    
    # Apple Silicon Metal 지원
    if [ "$USE_METAL" = true ]; then
        print_info "🍎 Apple Silicon 감지 - Metal 백엔드 설정 중..."
        # PyTorch는 기본적으로 MPS를 지원
        pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu --quiet
    fi
    
    pip install git+https://github.com/YuanArchive/synapse-ai-context.git
    
    print_success "Synapse 설치 완료"
}

# VS Code 설정
setup_vscode() {
    print_step "VS Code 설정 구성 중..."
    
    VSCODE_DIR=".vscode"
    SETTINGS_FILE="$VSCODE_DIR/settings.json"
    
    mkdir -p "$VSCODE_DIR"
    
    WORKSPACE_FOLDER="$(pwd)"
    
    cat > "$SETTINGS_FILE" << EOF
{
  "python.defaultInterpreterPath": "\${workspaceFolder}/.venv/bin/python",
  "python.terminal.activateEnvironment": true,
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": false,
  "python.linting.flake8Enabled": true,
  "terminal.integrated.env.osx": {
    "PATH": "\${workspaceFolder}/.venv/bin:\${env:PATH}"
  },
  "terminal.integrated.env.linux": {
    "PATH": "\${workspaceFolder}/.venv/bin:\${env:PATH}"
  },
  "files.exclude": {
    "**/__pycache__": true,
    "**/*.pyc": true,
    ".venv": false
  },
  "search.exclude": {
    "**/.venv": true,
    "**/node_modules": true,
    "**/__pycache__": true
  }
}
EOF
    
    print_success "VS Code 설정 생성 완료: $SETTINGS_FILE"
}

# 설치 검증
verify_installation() {
    print_step "설치 검증 중..."
    
    # 가상환경 활성화
    source .venv/bin/activate
    
    # synapse 명령어 확인
    if command -v synapse &> /dev/null; then
        print_success "synapse 명령어 확인됨"
    else
        print_error "synapse 명령어를 찾을 수 없습니다"
        return 1
    fi
    
    # Metal 백엔드 확인 (Apple Silicon)
    if [ "$USE_METAL" = true ]; then
        print_info "Metal 백엔드 확인 중..."
        MPS_AVAILABLE=$(python -c "import torch; print(torch.backends.mps.is_available())" 2>/dev/null || echo "false")
        
        if [ "$MPS_AVAILABLE" = "True" ]; then
            print_success "🍎 Metal Performance Shaders (MPS) 활성화됨"
        else
            print_warning "Metal 백엔드를 사용할 수 없습니다 (CPU 모드로 동작)"
        fi
    fi
    
    # synapse 버전 확인
    VERSION=$(synapse --help 2>&1 | head -1 || echo "")
    if [ -n "$VERSION" ]; then
        print_success "Synapse 정상 작동 확인"
    else
        print_error "Synapse 실행 오류"
        return 1
    fi
    
    return 0
}

# 완료 메시지
show_completion() {
    echo
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                                                              ║"
    echo "║  ✅ Synapse 설치가 완료되었습니다!                            ║"
    echo "║                                                              ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo
    echo "📌 다음 단계:"
    echo
    echo "1️⃣  가상환경 활성화:"
    echo "   source .venv/bin/activate"
    echo
    echo "2️⃣  Synapse 명령어 사용:"
    echo "   synapse --help"
    echo "   synapse init"
    echo "   synapse analyze ."
    echo "   synapse search \"쿼리\""
    echo
    
    if [ "$USE_METAL" = true ]; then
        echo "🍎 Apple Silicon 최적화 설정:"
        echo "   export SYNAPSE_BATCH_SIZE=32"
        echo "   export SYNAPSE_DEVICE=mps"
        echo "   synapse analyze . --workers 8"
        echo
    fi
    
    echo "3️⃣  VS Code에서 프로젝트 열기:"
    echo "   - 터미널이 자동으로 가상환경을 활성화합니다"
    echo "   - Python 인터프리터가 자동으로 선택됩니다"
    echo
    echo "💡 Tip: VS Code 터미널은 가상환경을 자동으로 활성화합니다!"
    echo
    echo "🚀 Happy Coding with Synapse!"
    echo
}

# 메인 실행
main() {
    show_banner
    
    print_info "Synapse 원클릭 설치를 시작합니다..."
    echo
    
    # 1. 시스템 감지
    detect_system
    
    # 2. Python 확인 및 설치
    if ! check_python; then
        print_warning "Python 3.12가 설치되지 않았습니다."
        
        if [[ "$OS_TYPE" == macos* ]]; then
            install_homebrew
            if ! install_python; then
                print_error "설치를 중단합니다. Python을 수동으로 설치한 후 다시 실행해주세요."
                exit 1
            fi
        else
            print_error "설치를 중단합니다. Python 3.12를 수동으로 설치한 후 다시 실행해주세요."
            exit 1
        fi
    fi
    
    # 3. 가상환경 생성
    if ! create_venv; then
        print_error "가상환경 생성 실패"
        exit 1
    fi
    
    # 4. Synapse 설치
    if ! install_synapse; then
        print_error "Synapse 설치 실패"
        exit 1
    fi
    
    # 5. VS Code 설정
    setup_vscode
    
    # 6. 검증
    if ! verify_installation; then
        print_error "설치 검증 실패"
        exit 1
    fi
    
    # 완료 메시지
    show_completion
}

# 스크립트 실행
main "$@"
