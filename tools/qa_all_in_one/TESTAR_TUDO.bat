@echo off
setlocal
cd /d "%~dp0"
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0bootstrap.ps1"
set "RC=%ERRORLEVEL%"
echo.
echo Envie o ZIP RESULTADOS criado na pasta deste inicializador.
echo Codigo de saida: %RC%
pause
exit /b %RC%
