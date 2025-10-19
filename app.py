__APP_VERSION__ = "watcher-off-dotted-keys-2025-10-19"
st.caption(f"build: {__APP_VERSION__}")

import streamlit as st
from datetime import datetime
import json, time
import pandas as pd

# ===== 설정 =====
EVENT_OPTIONS = [
    "job_change","role_change","project_launch","relationship_change",
    "move_house","family_event","health_pause","finance_up","finance_down","creative_output"
]
MBTI_LIST = ["INTP","INTJ","ENTP","ENTJ","INFJ","INFP","ENFJ","ENFP",
             "ISTJ","ISFJ","ESTJ","ESFJ","ISTP","ISFP","ESTP","ESFP"]

# 오행 가중치 (샘플 ver 0.1)
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
    "ESFP": {"wood":5,"fire":4,"earth":2,"metal":1,"water":1}
}

st.set_page_config(page_title="MBTI × Five Elements", page_icon="🌏", layout="centered")
st.title("MBTI × Five Elements (오픈 실험 MVP)")
st.caption("MBTI 기반 오행 프로필 → 연도별 이벤트 라벨링 수집(선택). 데이터는 익명 저장됩니다.")

# --- 1) MBTI 입력 ---
mbti = st.selectbox("MBTI를 선택하세요", MBTI_LIST, index=MBTI_LIST.index("INTP"))
st.write("선택한 MBTI:", f"**{mbti}**")

# 오행 그래프
if mbti in MBTI_ELEMENTS:
    elems = MBTI_ELEMENTS[mbti]
    df = pd.DataFrame({"element": list(elems.keys()), "score": list(elems.values())})
    st.bar_chart(df.set_index("element"))

# --- 2) 사주(선택) — 8자리 숫자 입력(YYYYMMDD) ---
import re
from datetime import datetime, date

def parse_yyyymmdd(s: str):
    s = re.sub(r"\D", "", s or "")        # 숫자만 추출
    if len(s) != 8:
        return None, "YYYYMMDD 형식(8자리)으로 입력하세요."
    try:
        y, m, d = int(s[:4]), int(s[4:6]), int(s[6:8])
        dt = date(y, m, d)                # 유효 날짜 체크(윤년 포함)
    except ValueError:
        return None, "존재하지 않는 날짜입니다."
    # 범위 제한 (1900-01-01 ~ 오늘)
    if dt < date(1900,1,1):
        return None, "19000101 이후만 허용합니다."
    if dt > date.today():
        return None, "미래 날짜는 입력 불가입니다."
    return dt, None

with st.expander("사주(선택): 생년월일/출생시 (숫자만)"):
    birth_str = st.text_input(
        "생년월일 (YYYYMMDD, 예: 19901231) — 숫자만",
        value="", max_chars=8, help="19000101 ~ 오늘 사이"
    )
    birth_date, err = parse_yyyymmdd(birth_str)
    if err and birth_str:
        st.error(err)

    # 출생 시각도 숫자 4자리 HHMM로 받기(선택)
    time_str = st.text_input("출생시각 (HHMM, 예: 0930) — 선택", value="", max_chars=4)
    birth_time = None
    if time_str:
        tnum = re.sub(r"\D", "", time_str)
        if len(tnum) == 4 and 0 <= int(tnum[:2]) <= 23 and 0 <= int(tnum[2:]) <= 59:
            birth_time = f"{tnum[:2]}:{tnum[2:]}"
        else:
            st.error("출생시각은 HHMM 형식(0000~2359)으로 입력하세요.")

    time_accuracy = st.select_slider(
        "출생시각 정확도", options=["unknown","±30m","exact"], value="unknown"
    )


# --- 3) 연도별 이벤트 라벨링 ---
with st.expander("연도별 이벤트 추가(선택)"):
    years = st.multiselect("연도를 선택하세요 (최대 5개 추천)", list(range(2000, datetime.now().year+1)), default=[2017,2020,2022])
    event_payload = []
    for y in years:
        st.markdown(f"#### 📆 {y}")
        etypes = st.multiselect("어떤 일이 있었나요? (복수 선택 가능)", EVENT_OPTIONS, key=f"ev_{y}")
        emotion = st.slider("감정 강도 (-2~+2)", min_value=-2, max_value=2, value=0, key=f"em_{y}")
        duration = st.selectbox("영향 기간", ["days","weeks","1-3m","3-6m","6-12m","12m+"], key=f"du_{y}")
        # 오행 감성 라벨(간단)
        elem_tag = st.radio("그 사건을 한 단어로 표현하면?", ["wood","fire","earth","metal","water"], horizontal=True, key=f"el_{y}")
        if etypes:
            event_payload.append({
                "year": y,
                "types": etypes,
                "emotion": emotion,
                "duration": duration,
                "element_code": elem_tag
            })

# --- 4) 저장 (Google Sheet 또는 Supabase 중 택1) ---
st.markdown("---")
st.subheader("제출 & 리포트")
name_alias = st.text_input("닉네임(선택, 통계 공개 시 표기)", value="")
consent = st.checkbox("익명 통계 목적 수집에 동의합니다.", value=True)

def save_to_gsheet(row: dict):
    # 비활성화 시 주석 유지. 사용할 땐 secrets 설정 후 주석 해제.
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scopes)
        gc = gspread.authorize(creds)
        sh = gc.open_by_key(st.secrets["gsheet"]["SHEET_ID"])
        ws = sh.worksheet(st.secrets["gsheet"]["WORKSHEET"])  # 예: "responses"
        ws.append_row([
            time.strftime("%Y-%m-%d %H:%M:%S"),
            row.get("mbti",""),
            json.dumps(row.get("elements",{}), ensure_ascii=False),
            str(row.get("birth_date","")),
            str(row.get("birth_time","")),
            row.get("time_accuracy",""),
            json.dumps(row.get("events",[]), ensure_ascii=False),
            row.get("name_alias","")
        ])
        return True, "saved:gspread"
    except Exception as e:
        return False, f"gsheet error: {e}"

def save_to_supabase(row: dict):
    try:
        from supabase import create_client, Client
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["key"]
        table = st.secrets["supabase"]["table"]
        supabase: Client = create_client(url, key)
        res = supabase.table(table).insert(row).execute()
        if getattr(res, "data", None):
            return True, "saved:supabase"
        return False, str(res)
    except Exception as e:
        return False, f"supabase error: {e}"

if st.button("제출하기"):
    row = {
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "mbti": mbti,
        "elements": MBTI_ELEMENTS.get(mbti, {}),
        "birth_date": str(birth_date) if birth_date else "",
        "birth_time": birth_time if birth_time else "",   # ✅ 수정된 부분
        "time_accuracy": time_accuracy,
        "events": event_payload,
        "name_alias": name_alias
    }

    if not consent:
        st.warning("동의 체크가 필요합니다.")
    else:
        # 저장 경로 선택: secrets에 따라 자동 분기
        saved = False; msg = ""
        if "gcp_service_account" in st.secrets:
            saved, msg = save_to_gsheet(row)
        elif "supabase" in st.secrets:
            saved, msg = save_to_supabase(row)
        else:
            msg = "저장 백엔드가 설정되지 않았습니다. (secrets.toml 확인)"
        if saved:
            st.success("제출 완료! 개인 리포트를 생성합니다.")
        else:
            st.error(f"저장 실패: {msg}")

        # 간단 리포트
        st.markdown("### 개인 미니 리포트")
        st.json(row)
        st.info("TIP: 이 링크를 티스토리에 iframe으로 넣어 트래픽을 모으세요.")
