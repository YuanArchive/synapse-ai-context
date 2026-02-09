#!/bin/bash
# Synapse 크로스 플랫폼 통합 설치 스크립트
# OS를 자동 감지하여 적절한 설치 스크립트 실행

set -e

# 색상 정의
GREEN='\033[0;32m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║         Synapse AI Context Tool - 통합 설치기                ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo

# OS 감지
OS="$(uname -s 2>/dev/null || echo 'Unknown')"

case "$OS" in
    Darwin*)
        echo -e "${GREEN}🍎 macOS 감지됨 - setup.sh 실행${NC}"
        echo
        chmod +x ./scripts/setup.sh
        ./scripts/setup.sh
        ;;
    Linux*)
        echo -e "${GREEN}🐧 Linux 감지됨 - setup.sh 실행${NC}"
        echo
        chmod +x ./scripts/setup.sh
        ./scripts/setup.sh
        ;;
    MINGW*|MSYS*|CYGWIN*)
        echo -e "${GREEN}🪟 Windows 감지됨 - setup.ps1 실행${NC}"
        echo
        powershell -ExecutionPolicy Bypass -File ./scripts/setup.ps1
        ;;
    *)
        echo -e "${RED}❌ 지원하지 않는 OS: $OS${NC}"
        echo
        echo "지원 OS:"
        echo "  - macOS (Apple Silicon / Intel)"
        echo "  - Linux (Ubuntu, Debian, etc.)"
        echo "  - Windows 10/11"
        echo
        exit 1
        ;;
esac
