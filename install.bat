@echo off

echo Checking for Python installation...
python --version > nul 2>&1
if %errorlevel% neq 0 (
  echo Python is not installed. Please install Python from https://www.python.org/downloads/ and try again.
  pause
  exit /b 1
)

echo Python found. Proceeding with dependency installation...

echo "Creating virtual environment..."
python -m venv .venv

echo "Activating virtual environment..."
call .venv\Scripts\activate.bat

echo Configuring pip...
python -m pip config set global.index-url "https://mirrors.aliyun.com/pypi/simple"

echo Installing dependencies from requirements.txt...
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
  echo Error installing dependencies. Please check your requirements.txt file and try again.
  pause
  exit /b 1
)


echo Playwright dependencies
REM playwright install chromium

echo Installation and configuration complete!

pause
