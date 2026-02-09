@echo off
REM Synapse 가상환경 빠른 활성화 스크립트

echo.
echo ======================================
echo   Synapse 가상환경 활성화
echo ======================================
echo.

if not exist ".venv\Scripts\activate.bat" (
    echo ❌ 가상환경을 찾을 수 없습니다.
    echo.
    echo 먼저 setup.bat를 실행하여 Synapse를 설치해주세요.
    echo.
    pause
    exit /b 1
)

call .venv\Scripts\activate.bat

echo.
echo ✅ Synapse 가상환경이 활성화되었습니다!
echo.
echo 사용 가능한 명령어:
echo   synapse --help       도움말 보기
echo   synapse init         프로젝트 초기화
echo   synapse analyze .    프로젝트 분석
echo   synapse search "..."  코드 검색
echo.

cmd /k
