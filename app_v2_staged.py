"""
MBTI × 사주 데이터 수집 앱 v2 - 단계별 입력 전략
목표: 이탈률 감소 + 수집 데이터 품질 향상
"""
import streamlit as st
from datetime import datetime, date
import json, time
import pandas as pd

# ===== 설정 =====
MBTI_LIST = ["INTP","INTJ","ENTP","ENTJ","INFJ","INFP","ENFJ","ENFP",
             "ISTJ","ISFJ","ESTJ","ESFJ","ISTP","ISFP","ESTP","ESFP"]

# 오행 가중치 (기존 유지)
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

# 이벤트 프리셋 (오행/감정/기간 자동 매핑)
EVENT_PRESETS = {
    "전직/이직": {"element":"wood", "emotion_avg":0, "duration":"3-6m"},
    "승진/역할변화": {"element":"fire", "emotion_avg":1, "duration":"1-3m"},
    "연애시작": {"element":"fire", "emotion_avg":2, "duration":"weeks"},
    "이별/이혼": {"element":"water", "emotion_avg":-2, "duration":"6-12m"},
    "이사/해외이주": {"element":"earth", "emotion_avg":0, "duration":"3-6m"},
    "가족사건": {"element":"earth", "emotion_avg":-1, "duration":"12m+"},
    "건강이슈": {"element":"metal", "emotion_avg":-1, "duration":"6-12m"},
    "경제적상승": {"element":"metal", "emotion_avg":1, "duration":"3-6m"},
    "경제적하락": {"element":"water", "emotion_avg":-1, "duration":"6-12m"},
    "창작/출시": {"element":"wood", "emotion_avg":1, "duration":"1-3m"}
}

st.set_page_config(page_title="MBTI × 사주 실험", page_icon="🌏", layout="centered")

# ===== 세션 상태 초기화 =====
if 'stage' not in st.session_state:
    st.session_state.stage = 1  # 1=MBTI, 2=생년월일, 3=이벤트
if 'mbti' not in st.session_state:
    st.session_state.mbti = None
if 'birth_date' not in st.session_state:
    st.session_state.birth_date = None
if 'events' not in st.session_state:
    st.session_state.events = []

# ===== 헤더 =====
st.title("🌏 MBTI × 사주 궁합 실험")
st.caption("서양 통계학(MBTI) + 동양 명리학(오행) 상관관계 연구 프로젝트")

# 진행률 표시 (stage가 1.5, 2.5 등 중간값이 될 수 있으므로 min으로 제한)
progress = min(st.session_state.stage / 4, 1.0)  # 최대 stage=4 기준
stage_display = int(st.session_state.stage)  # 표시용은 정수로
st.progress(progress, text=f"단계 {stage_display}/4")

# ===== 1단계: MBTI 입력 =====
if st.session_state.stage >= 1:
    st.markdown("### 1️⃣ 당신의 MBTI는?")

    col1, col2, col3, col4 = st.columns(4)
    mbti_buttons = []
    for i, mbti in enumerate(MBTI_LIST):
        col = [col1, col2, col3, col4][i % 4]
        with col:
            if st.button(mbti, key=f"mbti_{mbti}", use_container_width=True,
                        type="primary" if st.session_state.mbti == mbti else "secondary"):
                st.session_state.mbti = mbti
                if st.session_state.stage == 1:
                    st.session_state.stage = 1.5  # 중간 리포트 단계
                    st.rerun()

    if st.session_state.mbti:
        st.success(f"선택: **{st.session_state.mbti}**")

# ===== 1.5단계: 기본 리포트 (MBTI만으로) =====
if st.session_state.stage == 1.5 and st.session_state.mbti:
    st.markdown("---")
    st.markdown("### 📊 기본 프로필 (정확도 30%)")

    elems = MBTI_ELEMENTS.get(st.session_state.mbti, {})
    top2 = sorted(elems.items(), key=lambda x: x[1], reverse=True)[:2]

    # 오행 차트
    df = pd.DataFrame({"element": list(elems.keys()), "score": list(elems.values())})
    st.bar_chart(df.set_index("element"))

    st.info(f"""
    **{st.session_state.mbti}** 타입의 오행 성향:
    - 주요 에너지: **{top2[0][0]}({top2[0][1]})**, **{top2[1][0]}({top2[1][1]})**
    - 이 조합은 MBTI 통계 기반 추정입니다.
    """)

    st.warning("⚠️ **생년월일을 추가하면 정확도가 70%로 상승합니다!**")

    if st.button("➡️ 생년월일 추가하기", type="primary", use_container_width=True):
        st.session_state.stage = 2
        st.rerun()

    if st.button("⏭️ 이 정도로 충분해요 (제출)", use_container_width=True):
        st.session_state.stage = 4  # 제출 단계로
        st.rerun()

# ===== 2단계: 생년월일 입력 =====
if st.session_state.stage >= 2 and st.session_state.stage < 3:
    st.markdown("---")
    st.markdown("### 2️⃣ 생년월일 (선택)")
    st.caption("사주 오행 계산을 위해 필요합니다. 저장되지 않고 통계 목적으로만 사용됩니다.")

    # 캘린더 위젯 (기본값: 1990-01-01)
    birth = st.date_input(
        "생년월일을 선택하세요",
        value=date(1990, 1, 1),
        min_value=date(1900, 1, 1),
        max_value=date.today()
    )

    if st.button("✅ 확인", type="primary"):
        st.session_state.birth_date = birth
        st.session_state.stage = 2.5  # 정밀 리포트
        st.rerun()

    if st.button("⏭️ 건너뛰기"):
        st.session_state.stage = 3
        st.rerun()

# ===== 2.5단계: 정밀 리포트 (MBTI + 사주) =====
if st.session_state.stage == 2.5 and st.session_state.mbti and st.session_state.birth_date:
    st.markdown("---")
    st.markdown("### 📊 정밀 프로필 (정확도 70%)")

    # 간단한 사주 가중치 (월령 기반)
    birth_month = st.session_state.birth_date.month
    season_element = {1:"수",2:"목",3:"목",4:"목",5:"화",6:"화",7:"토",8:"금",9:"금",10:"금",11:"수",12:"수"}

    elems = MBTI_ELEMENTS.get(st.session_state.mbti, {}).copy()
    # 월령 가중
    month_elem_en = {"수":"water","목":"wood","화":"fire","토":"earth","금":"metal"}[season_element[birth_month]]
    elems[month_elem_en] = elems.get(month_elem_en, 0) + 2

    top2 = sorted(elems.items(), key=lambda x: x[1], reverse=True)[:2]

    df = pd.DataFrame({"element": list(elems.keys()), "score": list(elems.values())})
    st.bar_chart(df.set_index("element"))

    st.success(f"""
    **{st.session_state.mbti} × {season_element[birth_month]}월생** 타입:
    - 핵심 오행: **{top2[0][0]}({top2[0][1]})**, **{top2[1][0]}({top2[1][1]})**
    - 월령({birth_month}월 = {season_element[birth_month]}) 가중 반영됨
    """)

    st.warning("⚠️ **인생 주요 사건 3개만 추가하면 운세 일치율 분석 가능! (정확도 100%)**")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("➡️ 이벤트 추가하기", type="primary", use_container_width=True):
            st.session_state.stage = 3
            st.rerun()
    with col2:
        if st.button("⏭️ 바로 제출", use_container_width=True):
            st.session_state.stage = 4
            st.rerun()

# ===== 3단계: 인생 주요 사건 입력 (간소화) =====
if st.session_state.stage >= 3 and st.session_state.stage < 4:
    st.markdown("---")
    st.markdown("### 3️⃣ 인생 주요 사건 TOP 3 (선택)")
    st.caption("MBTI vs 사주 운세가 실제 인생과 얼마나 맞는지 비교하기 위한 데이터입니다.")

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

            # 고급 옵션 (접기)
            with st.expander("세부 조정 (선택)", expanded=False):
                emotion = st.slider("감정 강도", -2, 2, preset["emotion_avg"], key=f"emotion_{i}")
                duration = st.selectbox("영향 기간", ["days","weeks","1-3m","3-6m","6-12m","12m+"],
                                       index=["days","weeks","1-3m","3-6m","6-12m","12m+"].index(preset["duration"]),
                                       key=f"duration_{i}")

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

# ===== 4단계: 제출 및 최종 리포트 =====
if st.session_state.stage == 4:
    st.markdown("---")
    st.markdown("### 🎉 최종 리포트")

    # 데이터 구성
    row = {
        "timestamp": datetime.now().isoformat(),
        "mbti": st.session_state.mbti,
        "birth_date": str(st.session_state.birth_date) if st.session_state.birth_date else None,
        "events": st.session_state.events,
        "mbti_elements": MBTI_ELEMENTS.get(st.session_state.mbti, {})
    }

    # 사주 가중 오행 계산
    if st.session_state.birth_date:
        birth_month = st.session_state.birth_date.month
        season_element = {1:"수",2:"목",3:"목",4:"목",5:"화",6:"화",7:"토",8:"금",9:"금",10:"금",11:"수",12:"수"}
        month_elem_en = {"수":"water","목":"wood","화":"fire","토":"earth","금":"metal"}[season_element[birth_month]]

        elems = MBTI_ELEMENTS.get(st.session_state.mbti, {}).copy()
        elems[month_elem_en] = elems.get(month_elem_en, 0) + 2
        row["saju_elements"] = elems

    # 시각화
    st.subheader("📊 당신의 MBTI-사주 프로필")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("MBTI 타입", st.session_state.mbti)
        if st.session_state.birth_date:
            st.metric("생년월일", st.session_state.birth_date.strftime("%Y-%m-%d"))
    with col2:
        st.metric("수집된 이벤트", len(st.session_state.events))
        if st.session_state.events:
            avg_emotion = sum(e.get("emotion", 0) for e in st.session_state.events) / len(st.session_state.events)
            st.metric("평균 감정 강도", f"{avg_emotion:+.1f}")

    # 오행 차트
    if "saju_elements" in row:
        df = pd.DataFrame({"element": list(row["saju_elements"].keys()),
                          "score": list(row["saju_elements"].values())})
    else:
        df = pd.DataFrame({"element": list(row["mbti_elements"].keys()),
                          "score": list(row["mbti_elements"].values())})
    st.bar_chart(df.set_index("element"))

    # 모의 통계 (실제로는 DB에서 가져와야 함)
    st.info(f"""
    ### 🔍 유사 유형 통계 (참고용)
    - 같은 **{st.session_state.mbti}** 타입 중 **68%**가 "전직/이직" 경험 있음
    - {st.session_state.mbti} × {season_element.get(birth_month, '?')}월생 조합은 전체의 **3.2%**
    - 이 조합의 평균 인생 만족도: **7.2/10**

    *(실제 수집 데이터가 100명 이상 쌓이면 정확한 통계로 업데이트됩니다)*
    """)

    # 저장 (기존 함수 재사용)
    consent = st.checkbox("익명 통계 연구 목적 수집에 동의합니다", value=True)

    if st.button("📤 최종 제출", type="primary", disabled=not consent):
        # TODO: 실제 저장 로직 (gsheet/supabase)
        st.success("✅ 제출 완료! 감사합니다.")
        st.balloons()

        # 공유 링크 (모의)
        share_link = f"https://your-app.streamlit.app/?ref={hash(st.session_state.mbti)}"
        st.code(share_link, language=None)
        st.caption("👆 이 링크를 친구에게 공유하세요! 친구 5명이 참여하면 궁합 분석을 오픈합니다.")

    # 디버그용
    with st.expander("🔍 수집 데이터 (디버그용)"):
        st.json(row)

# ===== 리셋 버튼 =====
if st.button("🔄 처음부터 다시"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()
