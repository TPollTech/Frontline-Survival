@echo off
setlocal
cd /d "%~dp0"
if not exist "%~dp0QA_UNIVERSAL.bat" goto missing
call "%~dp0QA_UNIVERSAL.bat"
exit /b %ERRORLEVEL%
:missing
echo Use the new QA_UNIVERSAL.bat from the repository.
pause
exit /b 1
