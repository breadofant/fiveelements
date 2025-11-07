@echo off
REM ==============================================
REM 빠른 배포 스크립트 (확인 없이 즉시 배포)
REM ==============================================
chcp 65001 >nul
echo.
echo 🚀 빠른 배포 시작...
echo.

REM app_main.py를 app.py로 복사
copy /Y app_main.py app.py >nul

REM 현재 시간으로 커밋 메시지 생성
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do set DATE=%%a-%%b-%%c
for /f "tokens=1-2 delims=: " %%a in ('time /t') do set TIME=%%a:%%b
set COMMIT_MSG=deploy: auto-deploy %DATE% %TIME%

REM Git 커밋 및 푸시
git add .
git commit -m "%COMMIT_MSG%"
git push

echo.
echo ✅ 배포 완료! 1-2분 후 확인하세요.
echo 🌐 https://mbti-fiveelement.streamlit.app/
echo.
timeout /t 5
