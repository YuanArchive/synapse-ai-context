@echo off
REM Synapse 원클릭 설치 - CMD 래퍼 스크립트
REM 이 스크립트를 더블클릭하면 PowerShell 설치 스크립트가 실행됩니다

echo.
echo =====================================================
echo   Synapse AI Context Tool - 원클릭 설치
echo =====================================================
echo.
echo PowerShell 설치 스크립트를 실행합니다...
echo.

REM ExecutionPolicy 우회하여 PowerShell 스크립트 실행
powershell -ExecutionPolicy Bypass -File "%~dp0setup.ps1"

if errorlevel 1 (
    echo.
    echo ❌ 설치 중 오류가 발생했습니다.
    echo.
    pause
    exit /b 1
)

echo.
echo ✅ 설치가 완료되었습니다!
echo.
pause
