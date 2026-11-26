@echo off
setlocal
cd /d "%~dp0"
if not exist "live_catalog.json" goto missing
where py.exe >nul 2>&1
if errorlevel 1 goto fallback
py -3.11 -c "import sys" >nul 2>&1
if errorlevel 1 goto fallback
py -3.11 "%~dp0serve_offline.py" --port 0 --open
goto finished
:fallback
where python.exe >nul 2>&1
if errorlevel 1 goto missingpython
python "%~dp0serve_offline.py" --port 0 --open
goto finished
:missing
echo Extraia todo o ZIP do Asset Studio antes de abrir.
pause
exit /b 1
:missingpython
echo Python nao encontrado. Este Studio usa o Python ja instalado, sem instalar dependencias.
pause
exit /b 1
:finished
set "RC=%ERRORLEVEL%"
if not "%RC%"=="0" pause
exit /b %RC%
