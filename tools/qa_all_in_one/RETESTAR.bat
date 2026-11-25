@echo off
setlocal
cd /d "%~dp0"
set "BASE=%LOCALAPPDATA%\FrontlineQA\20261125-151826-ab9c85"
if not exist "%BASE%\venv\Scripts\python.exe" (
    echo A instalacao anterior nao foi encontrada em %BASE%.
    pause
    exit /b 1
)
"%BASE%\venv\Scripts\python.exe" "%~dp0retest.py" --previous "%BASE%" --revision-file "%~dp0REVISION.txt" --destination "%~dp0."
set "RC=%ERRORLEVEL%"
echo Envie o ZIP RESULTADOS-RETESTE e o log SETUP-RETESTE, se houver erro.
echo Codigo de saida: %RC%
pause
exit /b %RC%
