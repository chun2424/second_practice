# -*- coding: utf-8 -*-
"""
4회 모의고사 — 문항별 해설 자율학습 웹앱
실행:  streamlit run app.py
"""
import json
from pathlib import Path

import streamlit as st

DATA_PATH = Path(__file__).parent / "exam_data.json"

st.set_page_config(page_title="4회 모의고사", page_icon="✎", layout="centered")


# ──────────────────────────────────────────────────────────────
# 데이터
# ──────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    with open(DATA_PATH, encoding="utf-8") as f:
        data = json.load(f)
    qmap = {q["num"]: q for q in data["questions"]}
    smap = {s["id"]: s for s in data["sets"]}
    return data, qmap, smap


DATA, QMAP, SMAP = load_data()
NUMS = sorted(QMAP)

AREA_ORDER = ["독서", "문학", "화법과 작문"]
GRID = 9  # 번호판 한 줄 칸 수


# ──────────────────────────────────────────────────────────────
# 스타일  ─ 시험지·빨간펜 채점 모티프
# ──────────────────────────────────────────────────────────────
st.markdown(
    """
<style>
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard-dynamic-subset.css');
@import url('https://fonts.googleapis.com/css2?family=Gowun+Batang:wght@400;700&display=swap');

:root{
  --paper:#FBFAF7; --ink:#1C232B; --ink-soft:#5A6470;
  --rule:#E2DED4; --pen:#B3372C; --seal:#1F3A5F; --hi:#FFF0A8;
}
html, body, [class*="css"]{
  font-family:'Pretendard','Apple SD Gothic Neo','Malgun Gothic',sans-serif;
}
.stApp{ background:var(--paper); }
.block-container{ padding-top:4.2rem; padding-bottom:4rem; max-width:52rem; }

/* ── 표지 ── */
.eyebrow{
  font-size:.72rem; letter-spacing:.22em; color:var(--ink-soft);
  text-transform:uppercase; margin-bottom:.35rem;
}
.masthead{
  font-family:'Gowun Batang','Nanum Myeongjo','Apple SD Gothic Neo',Batang,serif; font-weight:700;
  font-size:2.9rem; line-height:1.1; color:var(--ink); margin:0 0 .3rem 0;
}
.masthead .no{ color:var(--pen); }
.subhead{ color:var(--ink-soft); font-size:.9rem; margin-bottom:1.1rem; }
.rule{ border:0; border-top:1.5px solid var(--ink); margin:.2rem 0 1.4rem 0; }
.rule-thin{ border:0; border-top:1px solid var(--rule); margin:1.6rem 0 1rem 0; }

/* ── 세트 머리 ── */
.setline{ display:flex; align-items:baseline; gap:.6rem; margin:.2rem 0 .45rem 0; }
.setno{
  font-variant-numeric:tabular-nums; font-size:.78rem; font-weight:700;
  color:var(--pen); border:1px solid var(--pen); border-radius:2px;
  padding:.05rem .35rem; white-space:nowrap;
}
.settitle{ font-family:'Gowun Batang','Nanum Myeongjo','Apple SD Gothic Neo',Batang,serif; font-size:1.02rem; color:var(--ink); }
.areatag{
  font-size:.75rem; letter-spacing:.18em; color:var(--ink-soft);
  border-bottom:1px solid var(--rule); display:block;
  padding-bottom:.3rem; margin:1.5rem 0 .9rem 0;
}

/* ── 번호 버튼 = 답안지 번호 칸 ── */
div.stButton > button,
div[data-testid="stButton"] > button{
  width:100%; min-height:2.5rem; border-radius:3px;
  font-variant-numeric:tabular-nums; font-weight:600;
  letter-spacing:.02em; transition:none; padding:.25rem .3rem;
}
div.stButton > button[kind="secondary"],
div[data-testid="stButton"] > button[kind="secondary"]{
  background:#fff; color:var(--ink); border:1px solid var(--rule);
}
div.stButton > button[kind="secondary"]:hover,
div[data-testid="stButton"] > button[kind="secondary"]:hover{
  border-color:var(--pen); color:var(--pen);
}
div.stButton > button[kind="primary"],
div[data-testid="stButton"] > button[kind="primary"]{
  background:var(--pen); color:#fff; border:1px solid var(--pen);
}
div.stButton > button[kind="primary"]:hover,
div[data-testid="stButton"] > button[kind="primary"]:hover{
  background:#912a21; border-color:#912a21; color:#fff;
}

/* ── 문항 화면 ── */
.qhead{ display:flex; align-items:flex-end; gap:.7rem; margin:.4rem 0 .1rem 0; }
.qno{
  font-family:'Gowun Batang','Nanum Myeongjo','Apple SD Gothic Neo',Batang,serif; font-size:2.6rem; font-weight:700;
  line-height:1; color:var(--pen); font-variant-numeric:tabular-nums;
}
.qtype{ font-size:.92rem; color:var(--ink-soft); padding-bottom:.35rem; }
.qprompt{
  font-family:'Gowun Batang','Nanum Myeongjo','Apple SD Gothic Neo',Batang,serif; font-size:1.12rem; line-height:1.65;
  color:var(--ink); border-left:3px solid var(--ink); padding:.55rem 0 .55rem .85rem;
  margin:.9rem 0 1.1rem 0; background:#fff;
}
.crumb{ font-size:.8rem; color:var(--ink-soft); margin-bottom:.2rem; }

/* ── 해설 본문 ── */
.exp{ font-size:.95rem; line-height:1.75; color:var(--ink); }
.exp p{ margin:.45rem 0; }
.exp .box{
  background:#fff; border:1px solid var(--rule); border-left:3px solid var(--seal);
  border-radius:3px; padding:.85rem 1rem; margin:.85rem 0;
}
.exp blockquote{
  margin:.5rem 0 .2rem 0; padding:.1rem 0 .1rem .8rem;
  border-left:2px solid var(--rule); color:#3D4650; font-size:.9rem;
}
.exp table{
  border-collapse:collapse; width:100%; margin:.7rem 0; font-size:.86rem;
  background:#fff;
}
.exp th, .exp td{
  border:1px solid var(--rule); padding:.42rem .6rem;
  vertical-align:top; text-align:left;
}
.exp th{ background:#F3F0E9; font-weight:600; }
.exp mark{ background:var(--hi); padding:0 .12em; }
.exp u{ text-decoration:underline; text-underline-offset:3px; }
.exp strong{ font-weight:700; }
.exp hr{ border:0; border-top:1px solid var(--rule); margin:1rem 0; }

/* ── 정답 카드 ── */
.answer{
  display:inline-flex; align-items:center; gap:.5rem;
  font-family:'Gowun Batang','Nanum Myeongjo','Apple SD Gothic Neo',Batang,serif; font-size:1.5rem; color:var(--pen);
  border:1.5px solid var(--pen); border-radius:3px; padding:.25rem .9rem;
}
.answer .lab{ font-family:'Pretendard',sans-serif; font-size:.75rem;
  letter-spacing:.15em; color:var(--ink-soft); }

/* 여백 정리 */
div[data-testid="stExpander"]{ border-color:var(--rule); background:#fff; }
</style>
""",
    unsafe_allow_html=True,
)


def html(fragment: str):
    """해설 HTML 출력 (Streamlit 버전에 따라 st.html / st.markdown)."""
    block = f'<div class="exp">{fragment}</div>'
    if hasattr(st, "html"):
        st.html(block)
    else:
        st.markdown(block, unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────
# 상태
# ──────────────────────────────────────────────────────────────
if "current" not in st.session_state:
    st.session_state.current = None       # None이면 메인 화면
if "done" not in st.session_state:
    st.session_state.done = set()         # 학습 완료 문항


def go(num):
    st.session_state.current = num


def home():
    st.session_state.current = None


# ──────────────────────────────────────────────────────────────
# 사이드바
# ──────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 문항 바로가기")
    pick = st.selectbox(
        "문항 번호",
        NUMS,
        index=NUMS.index(st.session_state.current) if st.session_state.current else 0,
        format_func=lambda n: f"{n:02d}번 · {QMAP[n]['area']} · {QMAP[n]['type']}",
        label_visibility="collapsed",
    )
    if st.button("이동", key="jump"):
        go(pick)
        st.rerun()

    st.divider()
    st.markdown(f"**학습 진도** {len(st.session_state.done)} / {len(NUMS)}")
    st.progress(len(st.session_state.done) / len(NUMS))
    if st.button("진도 초기화", key="reset"):
        st.session_state.done = set()
        st.rerun()

    st.divider()
    st.caption("EBS 2027 수능완성 국어영역 · 실전 모의고사 4회")


# ──────────────────────────────────────────────────────────────
# 메인 화면 — 문항 번호판
# ──────────────────────────────────────────────────────────────
def render_home():
    st.markdown(
        '<div class="eyebrow">EBS 2027 수능완성 · 국어영역</div>'
        '<h1 class="masthead"><span class="no">4회</span> 모의고사</h1>'
        '<div class="subhead">문항 번호를 누르면 그 문제의 해설이 열립니다. '
        "전 45문항 · 독서 17 · 문학 17 · 화법과 작문 11</div>"
        '<hr class="rule">',
        unsafe_allow_html=True,
    )

    for area in AREA_ORDER:
        sets = [s for s in DATA["sets"]
                if s["questions"] and QMAP[s["questions"][0]]["area"] == area]
        if not sets:
            continue
        first, last = sets[0]["questions"][0], sets[-1]["questions"][-1]
        st.markdown(
            f'<div class="areatag">{area} · {first:02d}–{last:02d}번</div>',
            unsafe_allow_html=True,
        )
        for s in sets:
            st.markdown(
                f'<div class="setline"><span class="setno">{s["label"]}</span>'
                f'<span class="settitle">{s["title"]}</span></div>',
                unsafe_allow_html=True,
            )
            nums = s["questions"]
            cols = st.columns(GRID)
            for i, n in enumerate(nums):
                with cols[i % GRID]:
                    done = n in st.session_state.done
                    st.button(
                        f"{n:02d}",
                        key=f"btn{n}",
                        type="primary" if done else "secondary",
                        on_click=go,
                        args=(n,),
                    )
            st.write("")

    st.markdown('<hr class="rule-thin">', unsafe_allow_html=True)
    st.caption("● 표시된 번호는 학습 완료로 체크한 문항입니다.")


# ──────────────────────────────────────────────────────────────
# 문항 화면
# ──────────────────────────────────────────────────────────────
def render_question(num):
    q = QMAP[num]
    s = SMAP[q["set_id"]]
    idx = NUMS.index(num)

    nav = st.columns([1.2, 1, 1, 3])
    with nav[0]:
        st.button("← 전체 목록", key="back", on_click=home)
    with nav[1]:
        st.button("‹ 이전", key="prev", disabled=idx == 0,
                  on_click=go, args=(NUMS[idx - 1],) if idx > 0 else (num,))
    with nav[2]:
        st.button("다음 ›", key="next", disabled=idx == len(NUMS) - 1,
                  on_click=go, args=(NUMS[idx + 1],) if idx < len(NUMS) - 1 else (num,))

    st.markdown('<hr class="rule-thin">', unsafe_allow_html=True)
    st.markdown(
        f'<div class="crumb">{q["area"]} · {s["label"]} {s["title"]}</div>'
        f'<div class="qhead"><span class="qno">{num:02d}</span>'
        f'<span class="qtype">{q["type"]}</span></div>',
        unsafe_allow_html=True,
    )

    if q["prompt"]:
        st.markdown(f'<div class="qprompt">{q["prompt"]}</div>', unsafe_allow_html=True)

    with st.expander("정답 확인", expanded=False):
        st.markdown(
            f'<div class="answer"><span class="lab">정답</span>{q["answer"]}</div>',
            unsafe_allow_html=True,
        )

    if s["intro"].strip():
        with st.expander("지문 구조 분석 · 세트 개요", expanded=False):
            html(s["intro"])

    st.markdown('<hr class="rule-thin">', unsafe_allow_html=True)
    html(q["html"])

    if s["wrap"].strip():
        st.markdown('<hr class="rule-thin">', unsafe_allow_html=True)
        with st.expander("이 세트 총정리 · 등급을 올리는 원칙", expanded=False):
            html(s["wrap"])

    st.markdown('<hr class="rule-thin">', unsafe_allow_html=True)
    checked = st.checkbox("이 문항 학습 완료", value=num in st.session_state.done,
                          key=f"done{num}")
    if checked:
        st.session_state.done.add(num)
    else:
        st.session_state.done.discard(num)


# ──────────────────────────────────────────────────────────────
if st.session_state.current is None:
    render_home()
else:
    render_question(st.session_state.current)
