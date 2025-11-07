@echo off
REM ==============================================
REM Quick Deploy (no confirmation)
REM ==============================================
echo.
echo Quick Deploy Starting...
echo.

REM Copy app_main.py to app.py
copy /Y app_main.py app.py >nul

REM Generate commit message with timestamp
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do set DATE=%%a-%%b-%%c
for /f "tokens=1-2 delims=: " %%a in ('time /t') do set TIME=%%a:%%b
set COMMIT_MSG=deploy: auto-deploy %DATE% %TIME%

REM Git commit and push
git add .
git commit -m "%COMMIT_MSG%"
git push

echo.
echo Deploy complete! Check in 1-2 minutes.
echo https://mbti-fiveelement.streamlit.app/
echo.
timeout /t 5
