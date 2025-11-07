@echo off
REM ==============================================
REM Streamlit Cloud 배포 자동화 스크립트
REM ==============================================
chcp 65001 >nul
echo.
echo ========================================
echo   Streamlit Cloud 배포 시작
echo ========================================
echo.

REM 현재 브랜치 확인
for /f "tokens=*" %%i in ('git branch --show-current') do set BRANCH=%%i
echo [1/5] 현재 브랜치: %BRANCH%

REM Git 상태 확인
echo.
echo [2/5] 변경사항 확인 중...
git status --short
echo.

REM 사용자 확인
set /p CONFIRM="배포를 진행하시겠습니까? (y/n): "
if /i not "%CONFIRM%"=="y" (
    echo 배포가 취소되었습니다.
    pause
    exit /b
)

REM app_main.py를 app.py로 복사
echo.
echo [3/5] app_main.py를 app.py로 복사 중...
copy /Y app_main.py app.py >nul
echo ✓ 복사 완료

REM Git 커밋 메시지 입력
echo.
set /p COMMIT_MSG="커밋 메시지를 입력하세요 (Enter=기본 메시지): "
if "%COMMIT_MSG%"=="" set COMMIT_MSG=deploy: update Streamlit app

REM Git 커밋 및 푸시
echo.
echo [4/5] Git 커밋 및 푸시 중...
git add .
git commit -m "%COMMIT_MSG%"
if errorlevel 1 (
    echo 변경사항이 없거나 커밋에 실패했습니다.
    echo 이미 최신 상태일 수 있습니다.
) else (
    echo ✓ 커밋 완료
)

git push origin %BRANCH%
if errorlevel 1 (
    echo ✗ 푸시 실패!
    echo Git 인증 또는 네트워크를 확인하세요.
    pause
    exit /b 1
)
echo ✓ 푸시 완료

REM 배포 완료
echo.
echo [5/5] 배포 완료!
echo.
echo ========================================
echo   Streamlit Cloud에서 자동 배포 중...
echo ========================================
echo.
echo 1-2분 후 다음 URL에서 확인하세요:
echo https://mbti-fiveelement.streamlit.app/
echo.
echo 또는 Streamlit Cloud 대시보드:
echo https://share.streamlit.io
echo.
echo 배포 상태를 확인하려면 위 대시보드에서
echo 앱 카드를 클릭하세요.
echo ========================================
echo.
pause
