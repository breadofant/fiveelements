"""
MBTI × 사주 앱 v3 - 풍성한 콘텐츠 버전
: 스토리텔링 + 비주얼 강화 + 궁합 분석
"""
import streamlit as st
from datetime import datetime, date
import json, time
import pandas as pd
import yaml
from pathlib import Path

# ===== 설정 =====
MBTI_LIST = ["INTP","INTJ","ENTP","ENTJ","INFJ","INFP","ENFJ","ENFP",
             "ISTJ","ISFJ","ESTJ","ESFJ","ISTP","ISFP","ESTP","ESFP"]

# 오행 가중치
MBTI_ELEMENTS = {
    "INTP": {"wood":3,"fire":1,"earth":2,"metal":5,"water":2},
    "INTJ": {"wood":2,"fire":1,"earth":2,"metal":4,"water":4},
    "ENTP": {"wood":5,"fire":2,"earth":1,"metal":3,"water":1},
    "ENFP": {"wood":5,"fire":4,"earth":1,"metal":1,"water":2},
    "INFJ": {"wood":2,"fire":3,"earth":1,"metal":2,"water":5},
    "INFP": {"wood":3,"fire":4,"earth":1,"metal":1,"water":4},
    "ISTJ": {"wood":1,"fire":1,"earth":5,"metal":4,"water":1},
    "ISFP": {"wood":3,"fire":3,"earth":2,"metal":1,"water":4},
    "ESTJ": {"wood":1,"fire":2,"earth":5,"metal":4,"water":1},
    "ESFJ": {"wood":2,"fire":5,"earth":4,"metal":1,"water":1},
    "ISTP": {"wood":2,"fire":1,"earth":3,"metal":5,"water":1},
    "ESTP": {"wood":4,"fire":2,"earth":3,"metal":3,"water":1},
    "ESFP": {"wood":5,"fire":4,"earth":2,"metal":1,"water":1},
    "ENFJ": {"wood":3,"fire":4,"earth":2,"metal":1,"water":3}
}

# 오행 한글 매핑
ELEMENT_KR = {"wood":"목","fire":"화","earth":"토","metal":"금","water":"수"}
ELEMENT_COLOR = {"wood":"#2ecc71","fire":"#e74c3c","earth":"#f39c12","metal":"#95a5a6","water":"#3498db"}

# 이벤트 프리셋
EVENT_PRESETS = {
    "전직/이직": {"element":"wood", "emotion_avg":0, "duration":"3-6m"},
    "승진/역할변화": {"element":"fire", "emotion_avg":1, "duration":"1-3m"},
    "연애시작": {"element":"fire", "emotion_avg":2, "duration":"weeks"},
    "이별/이혼": {"element":"water", "emotion_avg":-2, "duration":"6-12m"},
    "이사/해외이주": {"element":"earth", "emotion_avg":0, "duration":"3-6m"},
    "가족사건": {"element":"earth", "emotion_avg":-1, "duration":"12m+"},
    "건강이슈": {"element":"metal", "emotion_avg":-1, "duration":"6-12m"},
    "경제적상승": {"element":"metal", "emotion_avg":1, "duration":"3-6m"},
    "경제적하락": {"water": "water", "emotion_avg":-1, "duration":"6-12m"},
    "창작/출시": {"element":"wood", "emotion_avg":1, "duration":"1-3m"}
}

# 스토리 로드
@st.cache_data
def load_stories():
    story_path = Path("data/element_stories.yaml")
    if story_path.exists():
        with open(story_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    return {}

st.set_page_config(page_title="MBTI × 오행 궁합", page_icon="🌏", layout="wide")

# CSS 커스터마이징
st.markdown("""
<style>
    .element-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        color: white;
        margin: 10px 0;
    }
    .metric-card {
        background: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #667eea;
    }
    .story-box {
        background: #ffffff;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin: 15px 0;
    }
</style>
""", unsafe_allow_html=True)

# ===== 세션 상태 =====
if 'stage' not in st.session_state:
    st.session_state.stage = 1
if 'mbti' not in st.session_state:
    st.session_state.mbti = None
if 'birth_date' not in st.session_state:
    st.session_state.birth_date = None
if 'events' not in st.session_state:
    st.session_state.events = []

# ===== 헤더 =====
st.title("🌏 MBTI × 오행 궁합 분석")
st.caption("서양 심리학(MBTI) + 동양 명리학(오행)의 만남")

# 진행률
progress = min(st.session_state.stage / 4, 1.0)
stage_display = int(st.session_state.stage)
st.progress(progress, text=f"진행률: {int(progress*100)}%")

# ===== 1단계: MBTI 입력 =====
if st.session_state.stage >= 1:
    st.markdown("### 1️⃣ 당신의 MBTI를 선택하세요")

    col1, col2, col3, col4 = st.columns(4)
    for i, mbti in enumerate(MBTI_LIST):
        col = [col1, col2, col3, col4][i % 4]
        with col:
            button_type = "primary" if st.session_state.mbti == mbti else "secondary"
            if st.button(mbti, key=f"mbti_{mbti}", use_container_width=True, type=button_type):
                st.session_state.mbti = mbti
                if st.session_state.stage == 1:
                    st.session_state.stage = 1.5
                    st.rerun()

    if st.session_state.mbti:
        st.success(f"✅ 선택: **{st.session_state.mbti}**")

# ===== 1.5단계: 기본 프로필 =====
if st.session_state.stage == 1.5 and st.session_state.mbti:
    st.markdown("---")
    st.markdown("## 📊 당신의 기본 에너지 프로필")

    elems = MBTI_ELEMENTS.get(st.session_state.mbti, {})
    top2 = sorted(elems.items(), key=lambda x: x[1], reverse=True)[:2]
    top_element = top2[0][0]

    # 스토리 로드
    stories = load_stories()
    mbti_story = stories.get(st.session_state.mbti, {})
    element_story = mbti_story.get(top_element, {})

    # 타입 카드
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown(f"""
        <div class="element-card">
            <h2>{element_story.get('emoji', '✨')} {element_story.get('title', st.session_state.mbti)}</h2>
            <p style='font-size: 1.2em;'>주요 오행: {ELEMENT_KR[top_element]}({top2[0][1]}) · {ELEMENT_KR[top2[1][0]]}({top2[1][1]})</p>
        </div>
        """, unsafe_allow_html=True)

        # 키워드
        keywords = element_story.get('keywords', [])
        if keywords:
            st.markdown("**핵심 키워드**")
            st.write(" · ".join(keywords))

    with col2:
        # 레이더 차트 (간단한 막대 차트로 대체)
        df = pd.DataFrame({
            "오행": [ELEMENT_KR[k] for k in elems.keys()],
            "점수": list(elems.values())
        })
        st.bar_chart(df.set_index("오행"))

    # 성격 해석
    if element_story.get('personality'):
        st.markdown(f"""
        <div class="story-box">
            <h3>🎭 성격 해석</h3>
            <p style='font-size: 1.1em; line-height: 1.6;'>{element_story['personality']}</p>
        </div>
        """, unsafe_allow_html=True)

    # 커리어
    col1, col2 = st.columns(2)
    with col1:
        if element_story.get('career'):
            st.markdown("**💼 추천 커리어**")
            for career in element_story['career']:
                st.write(f"• {career}")

    with col2:
        if element_story.get('relationships'):
            st.markdown("**❤️ 관계 스타일**")
            st.write(element_story['relationships'])

    st.warning("⚠️ **생년월일을 추가하면 사주 기반 정밀 분석이 가능합니다! (+40% 정확도)**")

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("➡️ 생년월일 추가하기", type="primary", use_container_width=True):
            st.session_state.stage = 2
            st.rerun()
    with col_b:
        if st.button("⏭️ 이 정도로 충분 (제출)", use_container_width=True):
            st.session_state.stage = 4
            st.rerun()

# ===== 2단계: 생년월일 =====
if st.session_state.stage >= 2 and st.session_state.stage < 3:
    st.markdown("---")
    st.markdown("### 2️⃣ 생년월일을 선택하세요")
    st.caption("음력 변환 및 월령(月令) 분석에 사용됩니다.")

    birth = st.date_input(
        "생년월일",
        value=date(1990, 1, 1),
        min_value=date(1900, 1, 1),
        max_value=date.today()
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ 확인", type="primary", use_container_width=True):
            st.session_state.birth_date = birth
            st.session_state.stage = 2.5
            st.rerun()
    with col2:
        if st.button("⏭️ 건너뛰기", use_container_width=True):
            st.session_state.stage = 3
            st.rerun()

# ===== 2.5단계: 정밀 프로필 =====
if st.session_state.stage == 2.5 and st.session_state.mbti and st.session_state.birth_date:
    st.markdown("---")
    st.markdown("## 🔮 사주 기반 정밀 에너지 분석")

    # 월령 계산
    birth_month = st.session_state.birth_date.month
    season_element_kr = {1:"수",2:"목",3:"목",4:"목",5:"화",6:"화",7:"토",8:"금",9:"금",10:"금",11:"수",12:"수"}
    season_element = season_element_kr[birth_month]
    month_elem_en = {"수":"water","목":"wood","화":"fire","토":"earth","금":"metal"}[season_element]

    # 월령 가중
    elems = MBTI_ELEMENTS.get(st.session_state.mbti, {}).copy()
    elems[month_elem_en] = elems.get(month_elem_en, 0) + 2

    top2 = sorted(elems.items(), key=lambda x: x[1], reverse=True)[:2]
    top_element = top2[0][0]

    # 스토리 로드
    stories = load_stories()
    mbti_story = stories.get(st.session_state.mbti, {})
    element_story = mbti_story.get(top_element, {})

    # 타입 카드 (강화)
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown(f"""
        <div class="element-card">
            <h2>{element_story.get('emoji', '✨')} {element_story.get('title', st.session_state.mbti)}</h2>
            <p style='font-size: 1.2em;'>{st.session_state.mbti} × {season_element}월생</p>
            <p>핵심 에너지: {ELEMENT_KR[top_element]}({top2[0][1]}) · {ELEMENT_KR[top2[1][0]]}({top2[1][1]})</p>
        </div>
        """, unsafe_allow_html=True)

        st.info(f"📅 {birth_month}월생은 **{season_element}(元)**의 기운이 강합니다.")

    with col2:
        df = pd.DataFrame({
            "오행": [ELEMENT_KR[k] for k in elems.keys()],
            "점수": list(elems.values())
        })
        st.bar_chart(df.set_index("오행"))

    # 성격 + 커리어
    col1, col2 = st.columns(2)
    with col1:
        if element_story.get('personality'):
            st.markdown(f"""
            <div class="story-box">
                <h3>🎭 성격 프로필</h3>
                <p style='line-height: 1.6;'>{element_story['personality']}</p>
            </div>
            """, unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='story-box'><h3>💼 커리어 적성</h3>", unsafe_allow_html=True)
        for career in element_story.get('career', []):
            st.write(f"• {career}")
        st.markdown("</div>", unsafe_allow_html=True)

    # 오행 균형 분석
    st.markdown("### ⚖️ 오행 균형 분석")
    max_val = max(elems.values())
    min_val = min(elems.values())
    balance_score = 100 - int((max_val - min_val) / max_val * 100)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("균형도", f"{balance_score}%", delta="적정" if balance_score > 60 else "불균형")
    with col2:
        strongest = max(elems, key=elems.get)
        st.metric("최강 에너지", ELEMENT_KR[strongest], f"+{elems[strongest]}")
    with col3:
        weakest = min(elems, key=elems.get)
        st.metric("부족 에너지", ELEMENT_KR[weakest], f"{elems[weakest]}")

    if balance_score < 60:
        st.warning(f"💡 **Tip**: {ELEMENT_KR[weakest]} 에너지를 보충하는 활동(명상, 자연, 창작 등)을 권장합니다.")

    st.warning("⚠️ **인생 주요 사건 3개만 추가하면 운세 일치율 비교 가능! (+30% 정확도)**")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("➡️ 이벤트 추가하기", type="primary", use_container_width=True):
            st.session_state.stage = 3
            st.rerun()
    with col2:
        if st.button("⏭️ 바로 제출", use_container_width=True):
            st.session_state.stage = 4
            st.rerun()

# ===== 3단계: 이벤트 입력 =====
if st.session_state.stage >= 3 and st.session_state.stage < 4:
    st.markdown("---")
    st.markdown("### 3️⃣ 인생 주요 사건 (최대 5개)")
    st.caption("MBTI vs 사주가 실제 인생 패턴과 얼마나 일치하는지 비교합니다.")

    num_events = st.number_input("몇 개 추가할까요?", min_value=0, max_value=5, value=3)

    events_collected = []
    for i in range(num_events):
        with st.expander(f"📌 사건 {i+1}", expanded=(i==0)):
            col1, col2 = st.columns([1, 2])
            with col1:
                year = st.number_input("연도", min_value=1990, max_value=datetime.now().year,
                                      value=2020, key=f"year_{i}")
            with col2:
                event_type = st.selectbox("어떤 일?", list(EVENT_PRESETS.keys()), key=f"event_{i}")

            preset = EVENT_PRESETS[event_type]
            events_collected.append({
                "year": year,
                "type": event_type,
                "element": preset["element"],
                "emotion": preset["emotion_avg"],
                "duration": preset["duration"]
            })

    st.session_state.events = events_collected

    if st.button("✅ 완료 및 제출", type="primary", use_container_width=True):
        st.session_state.stage = 4
        st.rerun()

# ===== 4단계: 최종 리포트 =====
if st.session_state.stage == 4:
    st.markdown("---")
    st.markdown("## 🎉 당신의 MBTI × 오행 종합 리포트")

    # 데이터 구성
    row = {
        "timestamp": datetime.now().isoformat(),
        "mbti": st.session_state.mbti,
        "birth_date": str(st.session_state.birth_date) if st.session_state.birth_date else None,
        "events": st.session_state.events,
        "mbti_elements": MBTI_ELEMENTS.get(st.session_state.mbti, {})
    }

    # 사주 가중
    if st.session_state.birth_date:
        birth_month = st.session_state.birth_date.month
        season_element_kr = {1:"수",2:"목",3:"목",4:"목",5:"화",6:"화",7:"토",8:"금",9:"금",10:"금",11:"수",12:"수"}
        season_element = season_element_kr[birth_month]
        month_elem_en = {"수":"water","목":"wood","화":"fire","토":"earth","금":"metal"}[season_element]

        elems = MBTI_ELEMENTS.get(st.session_state.mbti, {}).copy()
        elems[month_elem_en] = elems.get(month_elem_en, 0) + 2
        row["saju_elements"] = elems
    else:
        elems = MBTI_ELEMENTS.get(st.session_state.mbti, {})

    top_element = max(elems, key=elems.get)

    # 스토리
    stories = load_stories()
    mbti_story = stories.get(st.session_state.mbti, {})
    element_story = mbti_story.get(top_element, {})

    # 헤더 카드
    st.markdown(f"""
    <div class="element-card" style="text-align: center;">
        <h1>{element_story.get('emoji', '✨')} {element_story.get('title', st.session_state.mbti)}</h1>
        <h3>{st.session_state.mbti} × {ELEMENT_KR[top_element]}형</h3>
        <p>{' · '.join(element_story.get('keywords', []))}</p>
    </div>
    """, unsafe_allow_html=True)

    # 메트릭
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("MBTI", st.session_state.mbti)
    with col2:
        st.metric("핵심 오행", ELEMENT_KR[top_element])
    with col3:
        if st.session_state.birth_date:
            st.metric("월령", season_element)
        else:
            st.metric("월령", "미입력")
    with col4:
        st.metric("수집 이벤트", len(st.session_state.events))

    # 차트 + 해석
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 📊 에너지 분포")
        df = pd.DataFrame({
            "오행": [ELEMENT_KR[k] for k in elems.keys()],
            "점수": list(elems.values())
        })
        st.bar_chart(df.set_index("오행"))

    with col2:
        st.markdown("### 🎭 종합 해석")
        st.write(element_story.get('personality', "해석 데이터 준비 중입니다."))

        st.markdown("**💼 추천 커리어**")
        for career in element_story.get('career', [])[:3]:
            st.write(f"• {career}")

    # 궁합 분석 (간단한 모의 통계)
    if st.session_state.events:
        st.markdown("### 🔮 운세 vs 실제 인생 일치율")

        # 이벤트 오행 분석
        event_elements = {}
        for evt in st.session_state.events:
            elem = evt.get('element', 'wood')
            event_elements[elem] = event_elements.get(elem, 0) + 1

        # 가장 많은 이벤트 오행
        if event_elements:
            dominant_event_elem = max(event_elements, key=event_elements.get)

            # 일치율 계산 (간단한 로직)
            if dominant_event_elem == top_element:
                match_rate = 85 + (event_elements[dominant_event_elem] * 3)
            else:
                match_rate = 65 + (event_elements.get(top_element, 0) * 5)

            match_rate = min(match_rate, 95)  # 최대 95%

            st.progress(match_rate / 100)
            st.metric("일치율", f"{match_rate}%", delta="높음" if match_rate > 75 else "보통")

            st.info(f"""
            💡 **분석**: 당신의 주요 인생 사건은 **{ELEMENT_KR[dominant_event_elem]}** 에너지와 연관이 깊습니다.
            이는 당신의 MBTI-사주 프로필({ELEMENT_KR[top_element]}형)과 {match_rate}% 일치합니다!
            """)

    # 공유 링크 (모의)
    st.markdown("---")
    st.markdown("### 📤 결과 공유하기")
    share_code = hash(f"{st.session_state.mbti}{top_element}")
    share_link = f"https://your-app.streamlit.app/?code={abs(share_code)}"

    col1, col2 = st.columns([3, 1])
    with col1:
        st.code(share_link, language=None)
    with col2:
        st.button("📋 복사", use_container_width=True)

    st.caption("👆 친구에게 공유하고 궁합을 비교해보세요!")

    # 제출
    consent = st.checkbox("익명 통계 연구 목적 수집에 동의합니다", value=True)

    if st.button("📤 최종 제출", type="primary", disabled=not consent, use_container_width=True):
        # TODO: 실제 저장 로직
        st.success("✅ 제출 완료! 감사합니다.")
        st.balloons()

    # 디버그
    with st.expander("🔍 수집 데이터 (디버그용)"):
        st.json(row)

# ===== 리셋 버튼 =====
if st.button("🔄 처음부터 다시"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()
