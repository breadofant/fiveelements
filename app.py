# streamlit_app.py
# -------------------------------------------------------------
# 사주(간지·오행 단순화) → 가능한 MBTI 후보 스코어링 →
# 연도별 경험 수집("이 해에 이런 일이 있었을 것 같다 – 맞/틀?")
# -------------------------------------------------------------
# ⚠️ 간단화/교육용 모델입니다. 실제 명리 계산(년/월/일/시 기둥, 대운/세운, 음력 전환 등)
# 은 생략/근사했으며, 라이브러리 교체 지점(saju_engine)을 모듈화해 두었습니다.
# 사용자는 나중에 정확한 사주 엔진으로 교체할 수 있습니다.
# -------------------------------------------------------------

import streamlit as st
import pandas as pd
import json
import math
import hashlib
from dataclasses import dataclass
from typing import Dict, List, Tuple

st.set_page_config(page_title="사주 → MBTI → 연도별 경험 수집", layout="wide")

# =========================
# 0) 기본 테이블/유틸
# =========================
STEMS = ["갑","을","병","정","무","기","경","신","임","계"]  # 10간
BRANCHES = ["자","축","인","묘","진","사","오","미","신","유","술","해"]  # 12지
STEM_TO_YIN_YANG = {"갑":"양","을":"음","병":"양","정":"음","무":"양","기":"음","경":"양","신":"음","임":"양","계":"음"}
# 매우 단순화된 오행 매핑 (연간/연지 기준)
STEM_TO_ELEM = {"갑":"목","을":"목","병":"화","정":"화","무":"토","기":"토","경":"금","신":"금","임":"수","계":"수"}
BRANCH_TO_ELEM = {"자":"수","축":"토","인":"목","묘":"목","진":"토","사":"화","오":"화","미":"토","신":"금","유":"금","술":"토","해":"수"}
ELEM_LIST = ["목","화","토","금","수"]
ELEM_COLORS = {"목":"#22c55e","화":"#ef4444","토":"#eab308","금":"#6b7280","수":"#3b82f6"}

# 카테고리 후보 (연도별 가설 생성에 사용)
EVENT_CATS = [
    ("이동·이사", "주거지 이동/원거리 이동/팀 이동"),
    ("직장·커리어", "입사·이직·승진·프로젝트 피크/슬럼프"),
    ("연애·관계", "연애 시작/종결, 동료/가족 관계 변화"),
    ("건강·컨디션", "수면·질병·부상·체력 변화"),
    ("금전·투자", "수입 변동·빚·투자 수익/손실"),
    ("학습·자격", "공부 몰입/자격증/연구 성과"),
    ("창업·사이드", "부업/창업/콘텐츠·앱 론칭")
]

# 연도별 응답을 통해 MBTI 축(E/I, N/S, T/F, J/P)을 갱신하는 가중치 (교육용 근사)
EVENT_TO_AXIS_WEIGHTS = {
    "이동·이사": {"E": +0.40, "P": +0.30, "I": -0.20, "J": -0.20},
    "직장·커리어": {"J": +0.40, "T": +0.30, "P": -0.20},
    "연애·관계": {"F": +0.40, "E": +0.20, "T": -0.20},
    "건강·컨디션": {"I": +0.30, "J": +0.20},
    "금전·투자": {"T": +0.40, "J": +0.20, "F": -0.20},
    "학습·자격": {"N": +0.30, "J": +0.30, "S": -0.10, "P": -0.10},
    "창업·사이드": {"E": +0.30, "N": +0.30, "P": +0.30, "J": -0.20},
}

# =========================
# 1) 근사 사주 엔진 (연간/연지만)
# =========================
@dataclass
class SajuYearResult:
    year: int
    stem: str
    branch: str
    stem_elem: str
    branch_elem: str
    yin_yang: str


def ganzhi_of_year(year: int) -> Tuple[str, str]:
    """간지 계산(연간·연지): 1984년을 '갑자' 기준으로 단순 계산.
    실제로는 입춘 이전은 이전 해 간지를 쓰는 등 세부 규칙이 있으나 여기선 근사.
    """
    # 1984 = 갑자 (0 offset)
    offset = year - 1984
    stem = STEMS[offset % 10]
    branch = BRANCHES[offset % 12]
    return stem, branch


def saju_year_summary(year: int) -> SajuYearResult:
    s, b = ganzhi_of_year(year)
    return SajuYearResult(
        year=year,
        stem=s,
        branch=b,
        stem_elem=STEM_TO_ELEM[s],
        branch_elem=BRANCH_TO_ELEM[b],
        yin_yang=STEM_TO_YIN_YANG[s]
    )


# =========================
# 2) 오행 → MBTI 후보 스코어 규칙(간단화)
# =========================
@dataclass
class MBTICandidate:
    code: str
    score: float
    notes: Dict[str, float]


# 각 지표별 가중치 규칙 (교육용·주관적 근사)
# - E/I: 양(목·화) vs 음(금·수) 비중 + 화/수 비율
# - N/S: 목·수 비중 높으면 N, 금·토 비중 높으면 S
# - T/F: 금/수 → T, 목/화 → F (토는 중화)
# - J/P: 금/토 → J, 목/화/수 → P


def infer_mbti_from_elements(elem_weights: Dict[str, float], yin_yang: str) -> List[MBTICandidate]:
    w = {e: elem_weights.get(e, 0.0) for e in ELEM_LIST}
    total = sum(w.values()) or 1.0
    p = {e: w[e]/total for e in w}

    notes = {}

    # E/I
    ei = 0.0
    ei += (p["목"] + p["화"]) * 0.9
    ei -= (p["금"] + p["수"]) * 0.9
    ei += (1 if yin_yang == "양" else -1) * 0.2
    notes["E-I"] = ei
    E = ei > 0

    # N/S
    ns = 0.0
    ns += (p["목"] + p["수"]) * 0.8
    ns -= (p["금"] + p["토"]) * 0.8
    ns += p["화"] * 0.2
    notes["N-S"] = ns
    N_ = ns > 0

    # T/F
    tf = 0.0
    tf += (p["금"] + p["수"]) * 0.9
    tf -= (p["목"] + p["화"]) * 0.9
    # 토는 균형 -> 0.0 반영
    notes["T-F"] = tf
    T = tf > 0

    # J/P
    jp = 0.0
    jp += (p["금"] + p["토"]) * 0.9
    jp -= (p["목"] + p["화"] + p["수"]) * 0.9
    notes["J-P"] = jp
    J = jp > 0

    code = f"{'E' if E else 'I'}{'N' if N_ else 'S'}{'T' if T else 'F'}{'J' if J else 'P'}"

    # 주변 후보도 함께 제시 (경계값 근처는 대체 후보 추가)
    cands = {code: 1.0}

    def near(x):
        return abs(x) < 0.15

    if near(ei):
        c = f"{'I' if E else 'E'}{'N' if N_ else 'S'}{'T' if T else 'F'}{'J' if J else 'P'}"
        cands[c] = 0.7
    if near(ns):
        c = f"{'E' if E else 'I'}{'S' if N_ else 'N'}{'T' if T else 'F'}{'J' if J else 'P'}"
        cands[c] = max(cands.get(c, 0), 0.7)
    if near(tf):
        c = f"{'E' if E else 'I'}{'N' if N_ else 'S'}{'F' if T else 'T'}{'J' if J else 'P'}"
        cands[c] = max(cands.get(c, 0), 0.7)
    if near(jp):
        c = f"{'E' if E else 'I'}{'N' if N_ else 'S'}{'T' if T else 'F'}{'P' if J else 'J'}"
        cands[c] = max(cands.get(c, 0), 0.7)

    out = []
    # 후보 점수는 각 축 거리 기반으로 재가중
    base = 0.25 * (abs(ei) + abs(ns) + abs(tf) + abs(jp))
    for k, v in cands.items():
        out.append(MBTICandidate(code=k, score=round(0.5*v + base, 3), notes=notes))

    out.sort(key=lambda x: x.score, reverse=True)
    return out[:5]


# =========================
# 3) 연도별 가설 생성 (결정적 해싱)
# =========================

def deterministic_topics(seed_text: str, year: int, k: int = 3) -> List[int]:
    """seed_text(year) → EVENT_CATS의 인덱스 k개를 결정적으로 선택"""
    h = hashlib.md5(f"{seed_text}-{year}".encode()).hexdigest()
    # 32 hex → 128 bits; 이를 4바이트씩 끊어 인덱스로 사용
    ints = [int(h[i:i+8], 16) for i in range(0, 32, 8)]
    picks = []
    pool = list(range(len(EVENT_CATS)))
    for i in range(min(k, len(pool))):
        idx = ints[i] % len(pool)
        picks.append(pool.pop(idx))
    return picks


def year_hypotheses(birth_year: int, dominant_elem: str, year: int) -> List[Tuple[str, str]]:
    seed = f"{birth_year}-{dominant_elem}"
    idxs = deterministic_topics(seed, year, k=3)
    return [EVENT_CATS[i] for i in idxs]


# =========================
# 4) 세션 상태 & 데이터 모델
# =========================
@dataclass
class ProfileInput:
    name: str
    birth_year: int
    birth_month: int
    birth_day: int
    mbti_known: str  # 사용자가 알고 있는 MBTI(Optional)


if "experience_db" not in st.session_state:
    st.session_state.experience_db = {}  # year → {category: yes/no/skip, notes}
if "elem_tweak" not in st.session_state:
    st.session_state.elem_tweak = {e: 0.0 for e in ELEM_LIST}
if "profile" not in st.session_state:
    st.session_state.profile = None


# =========================
# 5) 사이드바 입력
# =========================
with st.sidebar:
    st.header("입력")
    colA, colB = st.columns([1,1])
    with colA:
        name = st.text_input("이름(선택)", value="")
    with colB:
        known_mbti = st.text_input("현재 MBTI(선택)", value="").upper().strip()

    by = st.number_input("출생 연도", min_value=1900, max_value=2100, value=1989, step=1)
    bm = st.number_input("출생 월", min_value=1, max_value=12, value=7, step=1)
    bd = st.number_input("출생 일", min_value=1, max_value=31, value=17, step=1)

    st.markdown("---")
    st.caption("오행 가중치 미세조정 (사주 엔진 교체 전 임시 튜닝) – 값은 ±2 범위 권장")
    cols = st.columns(5)
    tweak = {}
    for i, e in enumerate(ELEM_LIST):
        with cols[i]:
            tweak[e] = st.slider(e, -2.0, 2.0, st.session_state.elem_tweak.get(e, 0.0), 0.1)
    st.session_state.elem_tweak = tweak

    st.markdown("---")
    start_year = st.number_input("경험 수집 시작 연도", min_value=by, max_value=2100, value=max(by+10, 2000))
    end_year = st.number_input("경험 수집 종료 연도", min_value=start_year, max_value=2100, value=max(start_year, 2025))

    if st.button("프로필 업데이트/적용"):
        st.session_state.profile = ProfileInput(name=name, birth_year=int(by), birth_month=int(bm), birth_day=int(bd), mbti_known=known_mbti)
        st.toast("프로필을 적용했습니다.")


# =========================
# 6) 본문 레이아웃
# =========================
st.title("🧭 사주 → 가능한 MBTI → 🗂️ 연도별 경험 수집")

if st.session_state.profile is None:
    st.info("좌측 사이드바에서 출생정보를 입력하고 '프로필 업데이트/적용'을 눌러주세요.")
    st.stop()

P: ProfileInput = st.session_state.profile

# --- 6-1) 사주(연) 요약 & 오행 비중 근사
yr = saju_year_summary(P.birth_year)
base_elem = {e: 0.0 for e in ELEM_LIST}
# 연간·연지에 동일 비중(0.5, 0.5) 부여 + 사용자의 튜닝
base_elem[yr.stem_elem] += 0.5
base_elem[yr.branch_elem] += 0.5
for e in ELEM_LIST:
    base_elem[e] += st.session_state.elem_tweak.get(e, 0.0)

# 음수 방지 + 정규화
minv = min(base_elem.values())
if minv < 0:
    base_elem = {k: v - minv for k, v in base_elem.items()}
S = sum(base_elem.values()) or 1.0
weights = {k: v/S for k, v in base_elem.items()}

dominant_elem = max(weights, key=lambda k: weights[k])

col1, col2 = st.columns([1.2, 1])
with col1:
    st.subheader("사주(연) 요약 – 간지/오행 근사")
    st.write(
        f"**{P.birth_year}년생** → 연간 **{yr.stem}({yr.yin_yang})** · 연지 **{yr.branch}**,\n"
        f"오행: 간(**{yr.stem_elem}**) + 지(**{yr.branch_elem}**)\n"
        f"→ 근사 가중치: {', '.join([f'{k}:{weights[k]:.2f}' for k in ELEM_LIST])}"
    )

    st.caption("※ 실제 사주는 월/일/시 기둥, 절입/입춘, 대운/세운 등을 반영해야 하며 본 앱은 연구용 근사입니다.")

with col2:
    st.subheader("오행 비중")
    df_elem = pd.DataFrame({"오행": ELEM_LIST, "비중": [weights[e] for e in ELEM_LIST]})
    st.bar_chart(df_elem.set_index("오행"), color=[ELEM_COLORS[e] for e in ELEM_LIST])

# --- 6-2) MBTI 후보 추론
st.subheader("가능한 MBTI 후보")
mbti_cands = infer_mbti_from_elements(weights, yr.yin_yang)

# 6-2.5) 사건 기반 사후 갱신 로직 (사주 기반 사전 → 연도 응답 기반 사후)

def _sigmoid(x: float, t: float = 1.0):
    return 1.0/(1.0+math.exp(-x/t))

@dataclass
class MBTIPosterior:
    axis: Dict[str, float]  # E,I,N,S,T,F,J,P 확률
    top_codes: List[Tuple[str, float]]  # [(type, prob)]


def _axis_prob_from_notes(notes: Dict[str, float]) -> Dict[str, float]:
    # notes: {"E-I": x, "N-S": y, ...}  → 축 확률로 변환
    e = _sigmoid(notes.get("E-I", 0.0), t=1.2)
    n = _sigmoid(notes.get("N-S", 0.0), t=1.2)
    t = _sigmoid(notes.get("T-F", 0.0), t=1.2)
    j = _sigmoid(notes.get("J-P", 0.0), t=1.2)
    axis = {
        "E": e, "I": 1-e,
        "N": n, "S": 1-n,
        "T": t, "F": 1-t,
        "J": j, "P": 1-j,
    }
    return axis


def _apply_event_update(axis: Dict[str, float], exp_db: Dict[int, Dict[str, Dict[str, str]]]) -> Dict[str, float]:
    # axis: 초기 확률(0~1). 각 응답에 따라 로지트 공간에서 가중치 더하기
    def to_logit(p):
        p = min(max(p, 1e-6), 1-1e-6)
        return math.log(p/(1-p))
    def to_prob(z):
        return 1.0/(1.0+math.exp(-z))

    z = {k: to_logit(v) for k, v in axis.items()}

    for cats in exp_db.values():
        for cat, v in cats.items():
            ans = v.get("ans", "모름/패스")
            if cat not in EVENT_TO_AXIS_WEIGHTS:
                continue
            for k, w in EVENT_TO_AXIS_WEIGHTS[cat].items():
                if ans == "맞다":
                    z[k] += w
                elif ans == "틀리다":
                    z[k] -= w
                # 모름/패스: 영향 없음

    return {k: to_prob(zv) for k, zv in z.items()}


def _type_prob_from_axis(axis: Dict[str, float]) -> List[Tuple[str, float]]:
    types = []
    for e in ("E","I"):
        for n in ("N","S"):
            for t in ("T","F"):
                for j in ("J","P"):
                    code = f"{e}{n}{t}{j}"
                    prob = axis[e]*axis[n]*axis[t]*axis[j]
                    types.append((code, prob))
    s = sum(p for _, p in types) or 1.0
    types = [(c, p/s) for c, p in types]
    types.sort(key=lambda x: x[1], reverse=True)
    return types


def compute_posterior(mbti_cands: List[MBTICandidate]) -> MBTIPosterior:
    if not mbti_cands:
        # 균등 사전
        axis0 = {k: 0.5 for k in ["E","I","N","S","T","F","J","P"]}
    else:
        axis0 = _axis_prob_from_notes(mbti_cands[0].notes)

    axis1 = _apply_event_update(axis0, st.session_state.experience_db)
    top_codes = _type_prob_from_axis(axis1)[:5]
    return MBTIPosterior(axis=axis1, top_codes=top_codes)

posterior = compute_posterior(mbti_cands)

# 안내 문구
lead = f"당신의 사주로 본 1차 MBTI 추정은 **{mbti_cands[0].code}** 입니다." if mbti_cands else "사주 기반 1차 추정 불가"
lead += " 사건 응답을 반영해 후보 범위를 좁혔습니다."
st.success(lead)

p_cols = st.columns(5)
for i, (code, prob) in enumerate(posterior.top_codes):
    if i < len(p_cols):
        with p_cols[i]:
            st.metric(label=f"사후 후보 #{i+1}", value=code, delta=f"{prob*100:.1f}%")

c_cols = st.columns(min(4, len(mbti_cands)))
for i, c in enumerate(mbti_cands[:4]):
    with c_cols[i]:
        st.metric(label=f"사전 #{i+1}", value=c.code, delta=f"score {c.score}")

with st.expander("추론 근거(스코어 축)"):
    if mbti_cands:
        st.json(mbti_cands[0].notes)
    if P.mbti_known:
        st.info(f"사용자 입력 MBTI: **{P.mbti_known}** (비교용)")

# --- 6-3) 연도별 경험 수집
st.subheader("연도별 경험 수집 – \"이 해에 이런 일이 있었을 것 같다\"")

help_txt = (
    "각 연도별로 제시되는 2~3개 테마에 대해 **맞다/틀리다/건너뛰기**를 선택하고, 필요하면 메모를 남겨주세요.\n"
    "선택 내용은 아래 표에 누적되며, CSV/JSON으로 내보낼 수 있습니다."
)
st.caption(help_txt)

name_seed = P.name or "anon"

years = list(range(int(start_year), int(end_year) + 1))

for y in years:
    with st.container(border=True):
        st.markdown(f"### 📅 {y}년")
        hyps = year_hypotheses(P.birth_year, dominant_elem, y)
        # 상태 로드
        year_state = st.session_state.experience_db.get(y, {})

        for cat, desc in hyps:
            key = f"{y}-{cat}"
            prev = year_state.get(cat, {}).get("ans", "미선택")
            cols = st.columns([1, 2, 2])
            with cols[0]:
                ans = st.radio(f"{cat}", ["맞다","틀리다","모름/패스"], index={"맞다":0,"틀리다":1,"모름/패스":2}.get(prev,2), key=key)
            with cols[1]:
                st.write(f"_{desc}_")
            with cols[2]:
                memo = st.text_input("메모(선택)", value=year_state.get(cat, {}).get("memo", ""), key=f"{key}-memo")

            # 저장
            if y not in st.session_state.experience_db:
                st.session_state.experience_db[y] = {}
            st.session_state.experience_db[y][cat] = {"ans": ans, "memo": memo}

# --- 6-4) 데이터 요약/다운로드
st.markdown("---")
st.subheader("응답 요약 & 내보내기")

# 테이블 구성
rows = []
for y, cats in sorted(st.session_state.experience_db.items()):
    for cat, v in cats.items():
        rows.append({
            "이름": P.name,
            "출생연도": P.birth_year,
            "연도": y,
            "테마": cat,
            "응답": v.get("ans"),
            "메모": v.get("memo", ""),
            "우세오행": dominant_elem,
            "MBTI_사전": mbti_cands[0].code if mbti_cands else "",
            "MBTI_사후1": posterior.top_codes[0][0] if posterior.top_codes else "",
            "사후1_확률(%)": round((posterior.top_codes[0][1]*100) if posterior.top_codes else 0.0, 1)
        })

if rows:
    out_df = pd.DataFrame(rows)
    st.dataframe(out_df, use_container_width=True, hide_index=True)

    c1, c2 = st.columns(2)
    with c1:
        st.download_button(
            "CSV 다운로드",
            data=out_df.to_csv(index=False).encode("utf-8-sig"),
            file_name=f"experience_{P.name or 'anon'}.csv",
            mime="text/csv",
        )
    with c2:
        st.download_button(
            "JSON 다운로드",
            data=json.dumps(rows, ensure_ascii=False, indent=2).encode("utf-8"),
            file_name=f"experience_{P.name or 'anon'}.json",
            mime="application/json",
        )
else:
    st.info("아직 응답 데이터가 없습니다. 위에서 연도별로 선택을 진행해 주세요.")

# --- 6-5) 모델 교체 가이드
with st.expander("사주 엔진 교체 가이드 (전문가용)"):
    st.markdown(
        """
        **정확도 향상을 위해** 다음 중 하나로 `saju_engine`을 교체하세요.

        1) **음력 변환 + 4기둥 계산**: `korean_lunar_calendar`, `lunardate` 등으로 절입 반영.
        2) **대운/세운 적용**: 월지 기준 대운 산출 후 연운과 충합·생극으로 테마 가중치 계산.
        3) **오행 정밀 가중**: 일간(日干) 중심으로 용희기신 판단 → E/I, N/S, T/F, J/P 규칙식 개선.

        교체 포인트:
        - `ganzhi_of_year(year)`
        - `saju_year_summary(year)` 결과를 (년/월/일/시)로 확장
        - `weights` 계산부를 정교화하여 `infer_mbti_from_elements()`에 전달
        """
    )

st.caption("© 연구·실험용 샘플. 개인 데이터는 로컬 브라우저 세션에만 저장됩니다.")
