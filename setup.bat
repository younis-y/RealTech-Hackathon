@echo off
REM Veo Setup Script for Windows
REM Initializes the 3-layer architecture environment

echo =========================================
echo Veo 3-Layer Architecture Setup
echo =========================================
echo.

REM Check Python version
echo Checking Python version...
python --version >nul 2>&1
if errorlevel 1 (
    echo X Python not found. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo √ Found Python %PYTHON_VERSION%
echo.

REM Create virtual environment
if not exist "venv" (
    echo Creating Python virtual environment...
    python -m venv venv
    echo √ Virtual environment created
) else (
    echo √ Virtual environment already exists
)
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo √ Virtual environment activated
echo.

REM Install dependencies
echo Installing Python dependencies...
python -m pip install --upgrade pip
pip install -r execution\requirements.txt
echo √ Dependencies installed
echo.

REM Create .env if it doesn't exist
if not exist ".env" (
    echo Creating .env file from template...
    copy .env.template .env
    echo √ .env file created
    echo ! IMPORTANT: Edit .env and add your API keys before running scripts
) else (
    echo √ .env file already exists
)
echo.

REM Ensure .tmp directory exists
if not exist ".tmp" (
    echo Creating .tmp directory...
    mkdir .tmp
    echo √ .tmp directory created
) else (
    echo √ .tmp directory already exists
)
echo.

REM Verify directory structure
echo Verifying directory structure...
if exist "directives" (
    echo   √ directives\
) else (
    echo   X directives\ missing
    mkdir directives
    echo     Created directives\
)

if exist "execution" (
    echo   √ execution\
) else (
    echo   X execution\ missing
    mkdir execution
    echo     Created execution\
)

if exist ".tmp" (
    echo   √ .tmp\
) else (
    echo   X .tmp\ missing
    mkdir .tmp
    echo     Created .tmp\
)
echo.

echo =========================================
echo Setup Complete!
echo =========================================
echo.
echo Directory Structure:
dir /b directives\*.md 2>nul | find /c ".md" > temp_count.txt
set /p DIRECTIVE_COUNT=<temp_count.txt
del temp_count.txt
echo   Directives: %DIRECTIVE_COUNT% files
dir /b execution\*.py 2>nul | find /c ".py" > temp_count.txt
set /p SCRIPT_COUNT=<temp_count.txt
del temp_count.txt
echo   Execution scripts: %SCRIPT_COUNT% files
echo   Temp directory: .tmp\
echo.
echo Next Steps:
echo.
echo 1. Edit .env file and add your API keys
echo    notepad .env
echo.
echo 2. Test ScanSan API (requires SCANSAN_API_KEY):
echo    python execution\scansan_api.py SW1A E1
echo.
echo 3. Test explanation generator (requires ANTHROPIC_API_KEY):
echo    python execution\generate_explanation.py
echo.
echo 4. Read the documentation:
echo    - README.md: Project overview
echo    - directives\MASTER_ORCHESTRATION.md: AI orchestration guide
echo    - Agents.md: Architecture details
echo.
echo Start using the AI orchestrator by asking:
echo    "I'm a student looking for housing in London..."
echo.
echo =========================================
echo.
pause
