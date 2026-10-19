@echo off
setlocal
cd /d "%~dp0"
echo ========================================
echo        MOTORGUARD - UNIVESP
 echo ========================================
where py >nul 2>&1
if %errorlevel%==0 (
  set "PYTHON=py -3"
) else (
  set "PYTHON=python"
)
if not exist ".venv\Scripts\python.exe" (
  %PYTHON% -m venv .venv
  if errorlevel 1 (echo Falha ao criar ambiente virtual. & pause & exit /b 1)
)
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 (echo Falha ao instalar dependencias. & pause & exit /b 1)
echo Treinando modelo no ambiente instalado...
.venv\Scripts\python.exe -m ml.train
if errorlevel 1 (echo Falha no treinamento. & pause & exit /b 1)
start "" "http://127.0.0.1:8000"
.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
pause
