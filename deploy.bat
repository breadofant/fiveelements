@echo off
REM ==============================================
REM Streamlit Cloud Deploy Automation
REM ==============================================
echo.
echo ========================================
echo   Streamlit Cloud Deploy
echo ========================================
echo.

REM Check current branch
for /f "tokens=*" %%i in ('git branch --show-current') do set BRANCH=%%i
echo [1/5] Current branch: %BRANCH%

REM Show git status
echo.
echo [2/5] Checking changes...
git status --short
echo.

REM User confirmation
set /p CONFIRM="Continue deploy? (y/n): "
if /i not "%CONFIRM%"=="y" (
    echo Deploy cancelled.
    pause
    exit /b
)

REM Copy app_main.py to app.py
echo.
echo [3/5] Copying app_main.py to app.py...
copy /Y app_main.py app.py >nul
echo Done!

REM Get commit message
echo.
set /p COMMIT_MSG="Commit message (Enter for default): "
if "%COMMIT_MSG%"=="" set COMMIT_MSG=deploy: update Streamlit app

REM Git commit and push
echo.
echo [4/5] Git commit and push...
git add .
git commit -m "%COMMIT_MSG%"
if errorlevel 1 (
    echo No changes to commit or commit failed.
) else (
    echo Commit successful!
)

git push origin %BRANCH%
if errorlevel 1 (
    echo Push failed!
    echo Check your Git authentication or network.
    pause
    exit /b 1
)
echo Push successful!

REM Deploy complete
echo.
echo [5/5] Deploy complete!
echo.
echo ========================================
echo   Streamlit Cloud is deploying...
echo ========================================
echo.
echo Check in 1-2 minutes:
echo https://mbti-fiveelement.streamlit.app/
echo.
echo Or visit dashboard:
echo https://share.streamlit.io
echo.
echo Click app card to check deploy status.
echo ========================================
echo.
pause
