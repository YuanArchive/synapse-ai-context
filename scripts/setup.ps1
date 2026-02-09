# Synapse 원클릭 설치 스크립트
# Windows PowerShell 5.1+ 필요

param(
    [switch]$SkipPythonInstall = $false,
    [switch]$NoConfirm = $false
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

# 색상 출력 함수
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Type = "Info"
    )
    
    switch ($Type) {
        "Success" { Write-Host "✅ $Message" -ForegroundColor Green }
        "Error"   { Write-Host "❌ $Message" -ForegroundColor Red }
        "Warning" { Write-Host "⚠️  $Message" -ForegroundColor Yellow }
        "Info"    { Write-Host "ℹ️  $Message" -ForegroundColor Cyan }
        "Step"    { Write-Host "`n🔹 $Message" -ForegroundColor Magenta }
        default   { Write-Host $Message }
    }
}

# 배너 출력
function Show-Banner {
    Write-Host @"

  ███████╗██╗   ██╗███╗   ██╗ █████╗ ██████╗ ███████╗███████╗
  ██╔════╝╚██╗ ██╔╝████╗  ██║██╔══██╗██╔══██╗██╔════╝██╔════╝
  ███████╗ ╚████╔╝ ██╔██╗ ██║███████║██████╔╝███████╗█████╗  
  ╚════██║  ╚██╔╝  ██║╚██╗██║██╔══██║██╔═══╝ ╚════██║██╔══╝  
  ███████║   ██║   ██║ ╚████║██║  ██║██║     ███████║███████╗
  ╚══════╝   ╚═╝   ╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝     ╚══════╝╚══════╝
                                                               
            🧠 AI 컨텍스트 증강 도구 - 원클릭 설치기
            
"@ -ForegroundColor Cyan
}

# Python 버전 확인
function Test-PythonVersion {
    param([string]$RequiredVersion = "3.12")
    
    try {
        $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
        if (-not $pythonCmd) {
            return $false
        }
        
        $version = & python --version 2>&1
        if ($version -match "Python (\d+\.\d+)\.(\d+)") {
            $major = $matches[1]
            $minor = $matches[2]
            $fullVersion = "$major.$minor"
            
            Write-ColorOutput "발견된 Python 버전: $fullVersion" "Info"
            
            if ($fullVersion -eq "3.12") {
                return $true
            } elseif ($fullVersion -in @("3.10", "3.11", "3.13")) {
                Write-ColorOutput "호환 가능한 Python 버전입니다 (3.10-3.13 지원)" "Warning"
                return $true
            } else {
                Write-ColorOutput "Python 3.12 권장 (현재: $fullVersion)" "Warning"
                return $false
            }
        }
        return $false
    } catch {
        return $false
    }
}

# Chocolatey 설치 확인 및 설치
function Install-Chocolatey {
    Write-ColorOutput "Chocolatey 설치 확인 중..." "Step"
    
    if (Get-Command choco -ErrorAction SilentlyContinue) {
        Write-ColorOutput "Chocolatey 이미 설치됨" "Success"
        return $true
    }
    
    Write-ColorOutput "Chocolatey가 설치되지 않았습니다." "Warning"
    Write-ColorOutput "Chocolatey는 Python 자동 설치를 위해 필요합니다." "Info"
    
    if (-not $NoConfirm) {
        $response = Read-Host "Chocolatey를 설치하시겠습니까? (Y/N)"
        if ($response -ne 'Y' -and $response -ne 'y') {
            Write-ColorOutput "Chocolatey 설치를 건너뜁니다." "Warning"
            return $false
        }
    }
    
    Write-ColorOutput "Chocolatey 설치 중... (관리자 권한 필요)" "Info"
    
    try {
        Set-ExecutionPolicy Bypass -Scope Process -Force
        [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
        Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
        
        # PATH 갱신
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
        
        Write-ColorOutput "Chocolatey 설치 완료" "Success"
        return $true
    } catch {
        Write-ColorOutput "Chocolatey 설치 실패: $_" "Error"
        return $false
    }
}

# Python 설치
function Install-Python {
    Write-ColorOutput "Python 3.12 설치 중..." "Step"
    
    if (-not (Install-Chocolatey)) {
        Write-ColorOutput "Python 자동 설치를 건너뜁니다. 수동으로 Python 3.12를 설치해주세요." "Warning"
        Write-ColorOutput "다운로드: https://www.python.org/downloads/" "Info"
        return $false
    }
    
    try {
        Write-ColorOutput "choco를 통해 Python 3.12 설치 중... (시간이 걸릴 수 있습니다)" "Info"
        choco install python312 -y --force
        
        # PATH 갱신
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
        
        # 설치 확인
        Start-Sleep -Seconds 5
        & refreshenv
        
        if (Test-PythonVersion) {
            Write-ColorOutput "Python 3.12 설치 완료" "Success"
            return $true
        } else {
            Write-ColorOutput "Python 설치 후 버전 확인 실패" "Error"
            return $false
        }
    } catch {
        Write-ColorOutput "Python 설치 실패: $_" "Error"
        return $false
    }
}

# 가상환경 생성
function New-VirtualEnvironment {
    param([string]$VenvPath = ".venv")
    
    Write-ColorOutput "가상환경 생성 중..." "Step"
    
    if (Test-Path $VenvPath) {
        Write-ColorOutput "가상환경이 이미 존재합니다: $VenvPath" "Warning"
        
        if (-not $NoConfirm) {
            $response = Read-Host "기존 가상환경을 삭제하고 재생성하시겠습니까? (Y/N)"
            if ($response -eq 'Y' -or $response -eq 'y') {
                Remove-Item -Recurse -Force $VenvPath
                Write-ColorOutput "기존 가상환경 삭제됨" "Info"
            } else {
                Write-ColorOutput "기존 가상환경 사용" "Info"
                return $true
            }
        }
    }
    
    try {
        & python -m venv $VenvPath
        Write-ColorOutput "가상환경 생성 완료: $VenvPath" "Success"
        return $true
    } catch {
        Write-ColorOutput "가상환경 생성 실패: $_" "Error"
        return $false
    }
}

# Synapse 설치
function Install-Synapse {
    param([string]$VenvPath = ".venv")
    
    Write-ColorOutput "Synapse 설치 중..." "Step"
    
    $pythonExe = Join-Path $VenvPath "Scripts\python.exe"
    $pipExe = Join-Path $VenvPath "Scripts\pip.exe"
    
    if (-not (Test-Path $pythonExe)) {
        Write-ColorOutput "가상환경 Python을 찾을 수 없습니다: $pythonExe" "Error"
        return $false
    }
    
    try {
        Write-ColorOutput "pip 업그레이드 중..." "Info"
        & $pythonExe -m pip install --upgrade pip | Out-Host
        
        Write-ColorOutput "Synapse 설치 중... (시간이 걸릴 수 있습니다)" "Info"
        & $pipExe install git+https://github.com/YuanArchive/synapse-ai-context.git | Out-Host
        
        Write-ColorOutput "Synapse 설치 완료" "Success"
        return $true
    } catch {
        Write-ColorOutput "Synapse 설치 실패: $_" "Error"
        return $false
    }
}

# VS Code 설정
function Set-VSCodeSettings {
    Write-ColorOutput "VS Code 설정 구성 중..." "Step"
    
    $vscodeDir = ".vscode"
    $settingsFile = Join-Path $vscodeDir "settings.json"
    
    if (-not (Test-Path $vscodeDir)) {
        New-Item -ItemType Directory -Path $vscodeDir -Force | Out-Null
    }
    
    $workspaceFolder = (Get-Location).Path.Replace('\', '/')
    
    $settings = @{
        "python.defaultInterpreterPath" = "$workspaceFolder/.venv/Scripts/python.exe"
        "python.terminal.activateEnvironment" = $true
        "python.formatting.provider" = "black"
        "terminal.integrated.env.windows" = @{
            "PATH" = "$workspaceFolder/.venv/Scripts;`${env:PATH}"
        }
    } | ConvertTo-Json -Depth 5
    
    try {
        $settings | Out-File -FilePath $settingsFile -Encoding UTF8 -Force
        Write-ColorOutput "VS Code 설정 생성 완료: $settingsFile" "Success"
        return $true
    } catch {
        Write-ColorOutput "VS Code 설정 생성 실패: $_" "Error"
        return $false
    }
}

# 설치 검증
function Test-Installation {
    param([string]$VenvPath = ".venv")
    
    Write-ColorOutput "설치 검증 중..." "Step"
    
    $synapseExe = Join-Path $VenvPath "Scripts\synapse.exe"
    
    if (-not (Test-Path $synapseExe)) {
        Write-ColorOutput "synapse.exe를 찾을 수 없습니다" "Error"
        return $false
    }
    
    try {
        $output = & $synapseExe --help 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "Synapse 정상 작동 확인" "Success"
            return $true
        } else {
            Write-ColorOutput "Synapse 실행 오류" "Error"
            return $false
        }
    } catch {
        Write-ColorOutput "Synapse 검증 실패: $_" "Error"
        return $false
    }
}

# 완료 메시지
function Show-CompletionMessage {
    Write-Host @"

╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║  ✅ Synapse 설치가 완료되었습니다!                            ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

📌 다음 단계:

1️⃣  VS Code에서 프로젝트를 다시 여세요 (또는 창 새로고침)
   - 가상환경이 자동으로 인식됩니다

2️⃣  터미널에서 Synapse를 사용하세요:
   
   # 가상환경 활성화 (자동)
   .\.venv\Scripts\Activate.ps1
   
   # Synapse 명령어 (python -m 접두사 불필요!)
   synapse --help
   synapse init
   synapse analyze .
   synapse search "쿼리"

3️⃣  AI 에이전트 설정:
   - .agent/AI_RULES_KO.md 파일이 자동 생성되었습니다
   - AI가 이 규칙을 따라 Synapse를 사용합니다

💡 Tip: VS Code 터미널은 가상환경을 자동으로 활성화합니다!

🚀 Happy Coding with Synapse!

"@ -ForegroundColor Green
}

# 메인 실행
function Main {
    Show-Banner
    
    Write-ColorOutput "Synapse 원클릭 설치를 시작합니다...`n" "Info"
    
    # 1. Python 확인 및 설치
    if (-not $SkipPythonInstall) {
        if (-not (Test-PythonVersion)) {
            Write-ColorOutput "Python 3.12가 설치되지 않았습니다." "Warning"
            if (-not (Install-Python)) {
                Write-ColorOutput "`n설치를 중단합니다. Python을 수동으로 설치한 후 다시 실행해주세요." "Error"
                exit 1
            }
        } else {
            Write-ColorOutput "Python 3.12 확인됨" "Success"
        }
    }
    
    # 2. 가상환경 생성
    if (-not (New-VirtualEnvironment)) {
        Write-ColorOutput "`n가상환경 생성 실패" "Error"
        exit 1
    }
    
    # 3. Synapse 설치
    if (-not (Install-Synapse)) {
        Write-ColorOutput "`nSynapse 설치 실패" "Error"
        exit 1
    }
    
    # 4. VS Code 설정
    Set-VSCodeSettings | Out-Null
    
    # 5. 검증
    if (-not (Test-Installation)) {
        Write-ColorOutput "`n설치 검증 실패" "Error"
        exit 1
    }
    
    # 완료 메시지
    Show-CompletionMessage
}

# 스크립트 실행
Main
