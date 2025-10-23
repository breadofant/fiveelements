# Streamlit Cloud 배포 가이드

## 왜 배포가 필요한가?

| 항목 | 로컬 실행 (지금) | Streamlit Cloud 배포 |
|------|----------------|---------------------|
| PC 상태 | **PC 켜두어야 함** | PC 꺼도 됨 |
| 접속 범위 | 같은 Wi-Fi만 | **전세계 누구나** |
| 주소 | 192.168.x.x | your-app.streamlit.app |
| 비용 | 무료 | **무료** (1개 앱) |
| 유지보수 | 수동 재시작 | 자동 |

---

## 배포 3단계

### 1단계: GitHub에 코드 푸시 (5분)

```bash
# rebase 정리
git rebase --abort 2>/dev/null || true

# 불필요한 파일 삭제
rm -f nul _ul

# .gitignore 업데이트
echo ".claude/" >> .gitignore
echo "nul" >> .gitignore
echo "_ul" >> .gitignore

# v3 앱만 메인으로 설정 (app.py로 이름 변경)
cp app_v3_rich.py app_main.py

# 커밋
git add .
git commit -m "feat: add rich MBTI x Five Elements app (v3)"
git push origin main
```

---

### 2단계: Streamlit Cloud 연결 (3분)

1. **https://share.streamlit.io** 접속
2. **GitHub로 로그인**
3. **New app** 클릭
4. 설정:
   - Repository: `fiveelements`
   - Branch: `main`
   - Main file path: `app_main.py`
5. **Deploy!** 클릭

---

### 3단계: 배포 완료! (2분 대기)

배포되면 주소가 생성됨:
```
https://your-username-fiveelements.streamlit.app
```

이 주소를 핸드폰에서 바로 접속 가능!

---

## 트러블슈팅

### 1. YAML 파일 인식 안 됨
**원인**: `data/element_stories.yaml` 경로 문제

**해결**:
```python
# app_main.py에서 수정
story_path = Path(__file__).parent / "data" / "element_stories.yaml"
```

### 2. requirements.txt 누락
**해결**:
```bash
echo "pyyaml" >> requirements.txt
git add requirements.txt
git commit -m "fix: add pyyaml dependency"
git push
```

### 3. secrets 설정 (DB 연동 시)
Streamlit Cloud 대시보드에서:
- Settings > Secrets
- `secrets.toml` 내용 붙여넣기

---

## 배포 후 관리

### 업데이트 방법
```bash
# 코드 수정 후
git add .
git commit -m "update: improve UI"
git push

# → Streamlit Cloud가 자동으로 재배포 (1분)
```

### 로그 확인
- Streamlit Cloud 대시보드 > Manage app > Logs

### 앱 종료/재시작
- Streamlit Cloud 대시보드 > 앱 카드 > ⋯ > Reboot

---

## 다음 단계 (선택)

### 커스텀 도메인 연결
```
your-app.streamlit.app → mbti-saju.com
```
→ Streamlit Cloud 유료 플랜 필요 ($20/월)

### DB 연동
- Supabase (무료 500MB)
- Google Sheets (무료)

### 분석 추가
- Google Analytics
- Hotjar (사용자 행동 분석)

---

## 지금 바로 배포할까?

아래 명령어 복사해서 터미널에 붙여넣기:

```bash
# 1. rebase 정리 + 불필요한 파일 삭제
git rebase --abort 2>/dev/null; rm -f nul _ul

# 2. 메인 앱 설정
cp app_v3_rich.py app_main.py

# 3. gitignore 업데이트
echo -e ".claude/\nnul\n_ul" >> .gitignore

# 4. pyyaml 의존성 추가
echo "pyyaml" >> requirements.txt

# 5. 커밋 & 푸시
git add .
git commit -m "feat: deploy MBTI x Five Elements v3"
git push origin main
```

그 다음:
1. https://share.streamlit.io 접속
2. GitHub 로그인
3. New app → fiveelements → app_main.py 선택
4. Deploy!

---

**배포하면**: PC 꺼도 핸드폰으로 언제든 접속 가능! 🚀
