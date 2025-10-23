# 다음 단계 작업 목록

## 즉시 가능 (1시간 이내)

### A. 결과 페이지 스토리텔링 추가
```python
# MBTI × 오행 조합별 "당신은..." 문구
MBTI_ELEMENT_STORIES = {
    "INTP_metal": "당신은 분석의 칼날을 휘두르는 금속성 사색가...",
    "ENFP_wood": "당신은 봄의 새싹처럼 끊임없이 성장하는...",
    # ... 16 × 5 = 80개 조합
}
```
→ 지금 만들어줄까? (YAML 파일로 관리)

### B. 공유 이미지 자동 생성
```python
# PIL로 결과 카드 이미지 생성
- 상단: "나는 ENTP × 목화형"
- 중간: 오행 레이더 차트
- 하단: QR코드 (앱 링크)
→ 인스타/카톡 공유용
```

### C. URL 쿼리스트링으로 결과 고정
```python
# 예: ?mbti=INTP&bd=19900615&ref=friend123
# → 세션 초기값으로 자동 입력
# → 친구 초대 링크로 활용
```

---

## 단기 (1주 이내)

### D. Supabase 연동
```sql
-- 테이블 스키마
CREATE TABLE responses (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  mbti TEXT NOT NULL,
  birth_date DATE,
  events JSONB,
  mbti_elements JSONB,
  saju_elements JSONB,
  referrer TEXT  -- 친구 초대 추적
);

CREATE INDEX idx_mbti ON responses(mbti);
CREATE INDEX idx_birth_month ON responses(EXTRACT(MONTH FROM birth_date));
```

### E. 실시간 통계 대시보드
```python
# Streamlit 별도 페이지 (admin용)
- MBTI별 분포 (파이차트)
- 월별 제출 건수 (라인차트)
- 이벤트 타입 TOP 10 (바차트)
- 평균 오행 점수 (히트맵)
```

### F. A/B 테스트 설정
```python
# Streamlit 쿼리 파라미터로 분기
variant = st.query_params.get("variant", "A")
if variant == "A":
    # 기존 UI
elif variant == "B":
    # 실험 UI (예: 프로그레스바 위치 변경)
```

---

## 중기 (1개월)

### G. 친구 초대 시스템
```python
# 사용자마다 고유 코드 발급
user_code = hashlib.md5(f"{mbti}{timestamp}".encode()).hexdigest()[:8]

# 리포트 페이지에 표시
"친구 초대 링크: https://app.com/?ref={user_code}"

# DB에 referrer 추적
# → 5명 초대 시 "고급 리포트 잠금 해제"
```

### H. 이메일 알림
```python
# SendGrid or Resend
- 제출 완료: "리포트가 준비됐어요"
- 친구 초대 성공: "철수님이 가입했어요! (4/5)"
- 월간 통계: "이번 달 ENTP 유입 +30%"
```

### I. 대운/세운 계산 (진짜 사주)
```python
# python-saju 라이브러리 or 자체 구현
- 60갑자 변환 (양력 → 음력 → 간지)
- 십신 계산 (비견, 식신, 편재...)
- 대운 추출 (10년 주기)
→ "2024-2033년 당신의 대운은 丙寅..."
```

---

## 장기 (3개월+)

### J. Next.js 마이그레이션
```typescript
// SEO/OG 최적화
// pages/result/[id].tsx
export async function generateMetadata({ params }) {
  const data = await fetchResult(params.id);
  return {
    title: `${data.mbti} × ${data.element}형 리포트`,
    openGraph: {
      images: [`/api/og?mbti=${data.mbti}&...`]
    }
  };
}
```

### K. 유료 리포트
```python
# Stripe 결제 연동
- 기본 리포트: 무료
- 대운/세운 리포트: 5,000원
- PDF 다운로드: 3,000원
- 1:1 상담 예약: 30,000원
```

### L. 논문/백서 작성
```markdown
# MBTI와 사주 오행의 교차 타당도 연구
## N=2000 실증 데이터 기반

### 주요 발견
- INTP × 금(金) 상관계수 0.68 (p<0.001)
- "전직" 이벤트와 목(木) 에너지 OR=2.3
- MBTI만 vs MBTI+사주 예측 정확도: 62% → 79%

### 한계
- 자기보고식 데이터 편향
- 생존자 편향 (앱 사용자 = 자기계발 관심층)
```

---

## 우선순위 추천 (당신의 목표 기준)

### 🥇 1순위: 데이터 수집 극대화
→ **A (스토리텔링)** + **B (공유 이미지)** + **C (URL 고정)**
→ 바이럴 루프 완성 → 1주일 내 100명 달성 가능

### 🥈 2순위: 데이터 품질 확보
→ **D (Supabase)** + **E (통계 대시보드)**
→ 이상치 탐지, 중복 제거 자동화

### 🥉 3순위: 연구 신뢰도
→ **I (진짜 사주)** + **L (논문)**
→ 학술 가치 확보, 언론 보도 가능성

---

## 지금 내가 해줄 수 있는 것 (선택해줘)

1. **MBTI × 오행 조합 80개 스토리 YAML 생성** (10분)
2. **Supabase 테이블 스키마 + 연동 코드** (20분)
3. **URL 쿼리스트링 친구 초대 시스템** (15분)
4. **공유 이미지 자동 생성 (PIL)** (30분)
5. **A/B 테스트 설정 샘플** (10분)

또는 "일단 v2 실행해보고 싶어" 하면 그것부터 도와줄게!
