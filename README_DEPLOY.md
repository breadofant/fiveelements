# 배포 스크립트 사용 가이드

## 📦 파일 설명

### 1. `deploy.bat` - 일반 배포 (추천)
단계별로 확인하며 배포합니다.

**사용법:**
```bash
# 더블클릭하거나 터미널에서:
deploy.bat
```

**동작:**
1. 현재 브랜치 확인
2. 변경사항 표시
3. 배포 확인 (y/n)
4. app_main.py → app.py 복사
5. 커밋 메시지 입력
6. Git push
7. 배포 완료 안내

---

### 2. `deploy-quick.bat` - 빠른 배포
확인 없이 즉시 배포합니다.

**사용법:**
```bash
# 더블클릭하거나 터미널에서:
deploy-quick.bat
```

**동작:**
- 자동으로 커밋 메시지 생성 (날짜/시간)
- 즉시 push
- 5초 후 자동 종료

---

## 🎯 어떤 스크립트를 사용해야 하나?

| 상황 | 추천 스크립트 |
|------|--------------|
| 중요한 변경사항 | `deploy.bat` |
| 커밋 메시지 직접 작성 | `deploy.bat` |
| 빠르게 테스트 배포 | `deploy-quick.bat` |
| 자동화/스크립트 연동 | `deploy-quick.bat` |

---

## ⚠️ 주의사항

### 배포 전 확인:
- [ ] `app_main.py` 파일이 정상 작동하는지 로컬에서 테스트
- [ ] 민감한 정보(API 키 등)가 코드에 없는지 확인
- [ ] `.gitignore`에 제외할 파일이 설정되어 있는지 확인

### Git 인증:
처음 실행 시 Git 인증이 필요할 수 있습니다:
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

---

## 🔧 문제 해결

### 1. "Git 푸시 실패" 오류
**원인**: Git 인증 문제 또는 네트워크 오류

**해결**:
```bash
# GitHub 인증 확인
git remote -v

# Personal Access Token 재설정
# GitHub → Settings → Developer settings → Personal access tokens
```

### 2. "변경사항 없음" 메시지
**원인**: 이미 최신 코드가 푸시되어 있음

**확인**:
```bash
git status
```

### 3. 배포했는데 앱이 업데이트 안 됨
**해결**:
1. Streamlit Cloud 대시보드 (https://share.streamlit.io) 접속
2. 앱 카드 클릭
3. 우측 상단 ⋮ → **Reboot** 클릭

---

## 📱 배포 후 확인

배포 완료 후 1-2분 대기 후:
- **앱 URL**: https://mbti-fiveelement.streamlit.app/
- **대시보드**: https://share.streamlit.io

---

## 💡 팁

### 단축키 만들기:
1. `deploy.bat` 우클릭 → "바로가기 만들기"
2. 바로가기를 바탕화면 또는 빠른 실행에 추가
3. 속성 → "단축키" 설정 (예: Ctrl+Alt+D)

### VSCode에서 실행:
1. Ctrl+` (터미널 열기)
2. `deploy.bat` 입력

---

## 🚀 자동화 예시

### 시간 예약 배포 (Windows 작업 스케줄러):
```
작업 스케줄러 → 작업 만들기
트리거: 매일 오후 6시
작업: deploy-quick.bat 실행
```

### Git Hook 연동:
`.git/hooks/pre-push` 파일 생성:
```bash
#!/bin/sh
echo "자동 배포 중..."
cmd.exe /c "deploy-quick.bat"
```

---

## 📚 더 알아보기

- **Streamlit 공식 문서**: https://docs.streamlit.io/streamlit-cloud
- **GitHub Actions 자동 배포**: `.github/workflows/` 설정
- **CI/CD 파이프라인**: GitHub Actions + Streamlit Cloud 연동

---

**문의**: 문제가 있으면 `git status` 및 에러 메시지 스크린샷과 함께 이슈 제기
