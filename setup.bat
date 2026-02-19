@echo off
REM Setup script for Generador de Recursos Evangelísticos (Windows)
REM This script sets up both backend and frontend environments

echo ==========================================
echo Generador de Recursos Evangelísticos
echo Setup Script (Windows)
echo ==========================================
echo.

REM Check Python version
echo Checking Python version...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python not found. Please install Python 3.10 or higher.
    pause
    exit /b 1
)

REM Check Node version
echo Checking Node.js version...
node --version
if %errorlevel% neq 0 (
    echo ERROR: Node.js not found. Please install Node.js 18 or higher.
    pause
    exit /b 1
)

echo.
echo ==========================================
echo Setting up Backend
echo ==========================================
cd backend

REM Create virtual environment
if not exist "venv" (
    echo Creating Python virtual environment...
    python -m venv venv
) else (
    echo Virtual environment already exists
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing Python dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Create .env if it doesn't exist
if not exist ".env" (
    echo Creating .env file from template...
    copy .env.example .env
) else (
    echo .env file already exists
)

echo Backend setup complete
cd ..

echo.
echo ==========================================
echo Setting up Frontend
echo ==========================================
cd frontend

REM Install dependencies
echo Installing Node.js dependencies...
call npm install

REM Create .env if it doesn't exist
if not exist ".env" (
    echo Creating .env file from template...
    copy .env.example .env
) else (
    echo .env file already exists
)

echo Frontend setup complete
cd ..

echo.
echo ==========================================
echo Setup Complete!
echo ==========================================
echo.
echo To start the application:
echo.
echo 1. Start the backend (in one terminal):
echo    cd backend
echo    venv\Scripts\activate
echo    uvicorn main:app --reload --host 0.0.0.0 --port 8000
echo.
echo 2. Start the frontend (in another terminal):
echo    cd frontend
echo    npm run dev
echo.
echo 3. Open your browser to: http://localhost:5173
echo.
pause
