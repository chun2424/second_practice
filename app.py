
App · PY
# -*- coding: utf-8 -*-
"""
4회 모의고사 (화법과 작문) — 문항별 해설 자율학습 웹앱
실행:  streamlit run app.py
"""
import html as _html
import json
import re
from pathlib import Path
 
import streamlit as st
 
HERE = Path(__file__).parent
DATA_PATH = HERE / "exam_data.json"
PASSAGE_PATH = HERE / "passages.json"
 
SCHOOL = "청명고등학교"
BRAND = "춘샘의 정리"
 
st.set_page_config(page_title="4회 모의고사 (화법과 작문)", page_icon="✎",
                   layout="centered")
 
 
# ──────────────────────────────────────────────────────────────
# 데이터
# ──────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    if not DATA_PATH.exists():
        here = sorted(p.name for p in HERE.iterdir())
        st.error(
            "exam_data.json 을 찾을 수 없습니다.\n\n"
            f"찾은 경로: `{DATA_PATH}`\n\n"
            f"이 폴더에 있는 파일: {here}\n\n"
            "app.py 와 같은 위치에 exam_data.json 을 올려 주세요. "
            "(GitHub 는 대소문자를 구분합니다)"
        )
        st.stop()
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    passages = {}
    if PASSAGE_PATH.exists():
        raw = json.loads(PASSAGE_PATH.read_text(encoding="utf-8"))
        passages = {k: v for k, v in raw.items() if not k.startswith("_")}
    qmap = {q["num"]: q for q in data["questions"]}
    smap = {s["id"]: s for s in data["sets"]}
    return data, qmap, smap, passages
 
 
DATA, QMAP, SMAP, PASSAGES = load_data()
NUMS = sorted(QMAP)
AREA_ORDER = ["독서", "문학", "화법과 작문"]
GRID = 9                    # 번호판 한 줄 칸 수
TITLE = "4회 모의고사 (화법과 작문)"
 
 
# ──────────────────────────────────────────────────────────────
# 스타일
# ──────────────────────────────────────────────────────────────
st.markdown(
    """
<style>
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard-dynamic-subset.css');
@import url('https://fonts.googleapis.com/css2?family=Gowun+Batang:wght@400;700&display=swap');
 
:root{
  --paper:#FBFAF7; --ink:#1C232B; --ink-soft:#5A6470;
  --rule:#E2DED4; --pen:#B3372C; --seal:#1F3A5F; --hi:#FFF0A8;
  --serif:'Gowun Batang','Nanum Myeongjo','Apple SD Gothic Neo',Batang,serif;
}
html, body, [class*="css"]{
  font-family:'Pretendard','Apple SD Gothic Neo','Malgun Gothic',sans-serif;
}
.stApp{ background:var(--paper); }
.block-container{ padding-top:3rem; padding-bottom:4rem; max-width:52rem; }
 
/* ── 상단 머리띠 (모든 화면) ── */
.topbar{
  display:flex; justify-content:space-between; align-items:center;
  border-bottom:1px solid var(--rule); padding-bottom:.45rem; margin-bottom:1.6rem;
}
.topbar .school{
  font-family:var(--serif); font-size:1rem; font-weight:700; color:var(--ink);
  letter-spacing:.02em;
}
.topbar .brand{
  font-family:var(--serif); font-size:.95rem; color:var(--pen);
  border:1px solid var(--pen); border-radius:2px; padding:.08rem .5rem;
}
 
/* ── 표지 ── */
.eyebrow{
  font-size:1.44rem; letter-spacing:.12em; color:var(--ink-soft);
  font-weight:600; margin-bottom:.5rem; line-height:1.3;
}
.masthead{
  font-family:var(--serif); font-weight:700;
  font-size:2.9rem; line-height:1.15; color:var(--ink); margin:0 0 .45rem 0;
}
.masthead .no{ color:var(--pen); }
.subhead{ color:var(--ink-soft); font-size:.9rem; margin-bottom:1.1rem; }
.rule{ border:0; border-top:1.5px solid var(--ink); margin:.2rem 0 1.4rem 0; }
.rule-thin{ border:0; border-top:1px solid var(--rule); margin:1.5rem 0 1rem 0; }
 
/* ── 세트 머리 ── */
.setline{ display:flex; align-items:baseline; gap:.6rem; margin:.2rem 0 .45rem 0; }
.setno{
  font-variant-numeric:tabular-nums; font-size:.78rem; font-weight:700;
  color:var(--pen); border:1px solid var(--pen); border-radius:2px;
  padding:.05rem .35rem; white-space:nowrap;
}
.settitle{ font-family:var(--serif); font-size:1.02rem; color:var(--ink); }
.areatag{
  font-size:.75rem; letter-spacing:.18em; color:var(--ink-soft);
  border-bottom:1px solid var(--rule); display:block;
  padding-bottom:.3rem; margin:1.5rem 0 .9rem 0;
}
 
/* ── 번호 버튼 ── */
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
 
/* ── 문항 머리 ── */
.crumb{ font-size:.8rem; color:var(--ink-soft); margin-bottom:.25rem; }
.qhead{ display:flex; align-items:center; gap:.75rem; flex-wrap:wrap;
  margin:.2rem 0 .1rem 0; }
.qno{
  font-family:var(--serif); font-size:2.6rem; font-weight:700;
  line-height:1; color:var(--pen); font-variant-numeric:tabular-nums;
}
.ansbadge{
  display:inline-flex; align-items:center; gap:.45rem;
  border:1.5px solid var(--pen); border-radius:3px; padding:.18rem .7rem;
  background:#fff;
}
.ansbadge .lab{ font-size:.7rem; letter-spacing:.15em; color:var(--ink-soft); }
.ansbadge .val{ font-family:var(--serif); font-size:1.35rem; color:var(--pen);
  line-height:1; }
.qtype{ font-size:.92rem; color:var(--ink-soft); }
.qprompt{
  font-family:var(--serif); font-size:1.12rem; line-height:1.65;
  color:var(--ink); border-left:3px solid var(--ink); padding:.55rem 0 .55rem .85rem;
  margin:.9rem 0 1.1rem 0; background:#fff;
}
 
/* ── 섹션 표제 ── */
.sect{
  font-size:.78rem; letter-spacing:.2em; color:var(--ink-soft);
  border-bottom:1px solid var(--rule); padding-bottom:.28rem;
  margin:1.6rem 0 .8rem 0;
}
 
/* ── 함정 한 줄 요약 ── */
.trap{ display:flex; flex-wrap:wrap; gap:.45rem; margin:.2rem 0 .3rem 0; }
.trap .item{
  background:#fff; border:1px solid var(--rule); border-radius:3px;
  padding:.35rem .6rem; font-size:.85rem; color:var(--ink); flex:1 1 30%;
}
.trap .k{ display:block; font-size:.66rem; letter-spacing:.12em;
  color:var(--ink-soft); margin-bottom:.15rem; }
.chips{ margin:.3rem 0 .1rem 0; font-size:.85rem; color:var(--ink-soft); }
.chip{
  display:inline-block; border:1px solid var(--rule); background:#fff;
  border-radius:999px; padding:.1rem .55rem; margin:.15rem .25rem .15rem 0;
  font-size:.8rem; color:var(--ink);
}
 
/* ── 지문 원문 ── */
.psg{ background:#fff; border:1px solid var(--rule); border-radius:3px;
  padding:.9rem 1.05rem; }
.psg .part{ font-family:var(--serif); font-weight:700; color:var(--seal);
  font-size:.95rem; margin:.5rem 0 .35rem 0; }
.psg .para{ display:flex; gap:.7rem; margin:.5rem 0; }
.psg .pn{
  flex:0 0 1.6rem; text-align:right; font-variant-numeric:tabular-nums;
  font-size:.78rem; color:var(--ink-soft); padding-top:.22rem;
}
.psg .pt{ font-size:.94rem; line-height:1.85; color:var(--ink); }
.psg .cited{ border-left:3px solid var(--pen); padding-left:.6rem;
  margin-left:-.6rem; }
.psg .who{ font-size:.72rem; color:var(--pen); margin-left:.35rem;
  white-space:nowrap; }
.psg .dim .pt{ color:#8B939C; }
.psg mark{ background:var(--hi); padding:0 .12em; }
.psg-empty{
  border:1px dashed var(--rule); border-radius:3px; padding:.75rem 1rem;
  font-size:.85rem; color:var(--ink-soft); background:#fff;
}
 
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
.exp table{ border-collapse:collapse; width:100%; margin:.7rem 0;
  font-size:.86rem; background:#fff; }
.exp th, .exp td{ border:1px solid var(--rule); padding:.42rem .6rem;
  vertical-align:top; text-align:left; }
.exp th{ background:#F3F0E9; font-weight:600; }
.exp mark{ background:var(--hi); padding:0 .12em; }
.exp u{ text-decoration:underline; text-underline-offset:3px; }
.exp hr{ border:0; border-top:1px solid var(--rule); margin:1rem 0; }
 
/* ── 등급을 올리는 노하우 ── */
.tip{
  background:#fff; border:1px solid var(--rule); border-left:3px solid var(--pen);
  border-radius:3px; padding:.7rem .95rem; margin:.55rem 0; font-size:.92rem;
  line-height:1.7;
}
.tip .tno{ font-variant-numeric:tabular-nums; color:var(--pen);
  font-weight:700; margin-right:.4rem; }
.tip .tt{ font-family:var(--serif); font-weight:700; color:var(--ink); }
.tip .tb{ display:block; margin-top:.3rem; color:#333B44; }
.tip mark{ background:var(--hi); padding:0 .12em; }
 
div[data-testid="stExpander"]{ border-color:var(--rule); background:#fff; }
</style>
""",
    unsafe_allow_html=True,
)
 
 
def render_html(fragment: str, cls: str = "exp"):
    block = f'<div class="{cls}">{fragment}</div>'
    if hasattr(st, "html"):
        st.html(block)
    else:
        st.markdown(block, unsafe_allow_html=True)
 
 
def raw(fragment: str):
    """마크다운 해석 없이 그대로 출력 (지문 원문처럼 기호가 섞인 글용)."""
    if hasattr(st, "html"):
        st.html(fragment)
    else:
        st.markdown(fragment, unsafe_allow_html=True)
 
 
def topbar():
    st.markdown(
        f'<div class="topbar"><span class="school">{SCHOOL}</span>'
        f'<span class="brand">{BRAND}</span></div>',
        unsafe_allow_html=True,
    )
 
 
# ──────────────────────────────────────────────────────────────
# 지문 원문 하이라이트
# ──────────────────────────────────────────────────────────────
_WS = re.compile(r"\s+")
 
 
def _strip_map(text):
    """공백을 뺀 문자열과, 그 위치 → 원문 위치 대응표."""
    buf, idx = [], []
    for i, ch in enumerate(text):
        if not ch.isspace():
            buf.append(ch)
            idx.append(i)
    return "".join(buf), idx
 
 
def highlight(text, quotes):
    """해설이 인용한 원문 문장을 찾아 형광펜(<mark>)을 칠한다."""
    flat, idx = _strip_map(text)
    spans = []
    for q in quotes:
        key = _WS.sub("", q).strip("…·~")
        if len(key) < 2:
            continue
        start = 0
        while True:
            pos = flat.find(key, start)
            if pos < 0:
                break
            spans.append((idx[pos], idx[pos + len(key) - 1] + 1))
            start = pos + 1
    if not spans:
        return _html.escape(text)
 
    spans.sort()
    merged = [list(spans[0])]
    for a, b in spans[1:]:
        if a <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], b)
        else:
            merged.append([a, b])
 
    out, cur = [], 0
    for a, b in merged:
        out.append(_html.escape(text[cur:a]))
        out.append(f"<mark>{_html.escape(text[a:b])}</mark>")
        cur = b
    out.append(_html.escape(text[cur:]))
    return "".join(out)
 
 
def passage_block(q, set_id, only_cited=True):
    """근거 문단을 원문 그대로 띄우고 인용 문장에 형광펜을 칠한 HTML."""
    psg = PASSAGES.get(set_id)
    if not psg or not any(p.get("paras") for p in psg.get("parts", [])):
        return None
 
    cited = {}          # (label, 문단번호) → 선지 목록
    quotes = []
    for ev in q.get("evidence", []):
        quotes += ev.get("quotes", [])
        for loc in ev.get("locs", []):
            key = (loc.get("part", ""), loc["para"])
            cited.setdefault(key, [])
            if ev.get("choice") and ev["choice"] not in cited[key]:
                cited[key].append(ev["choice"])
 
    def is_cited(label, n):
        return (label, n) in cited or ("", n) in cited
 
    def who(label, n):
        return cited.get((label, n)) or cited.get(("", n)) or []
 
    parts_html = []
    for part in psg.get("parts", []):
        label = part.get("label", "")
        rows = []
        for n, para in enumerate(part.get("paras", []), 1):
            hit = is_cited(label, n)
            if only_cited and not hit:
                continue
            marks = who(label, n)
            tag = (f'<span class="who">{"·".join(marks)}의 근거</span>'
                   if marks else "")
            body = highlight(para, quotes) if hit else _html.escape(para)
            klass = "para cited" if hit else "para dim"
            rows.append(
                f'<div class="{klass}"><div class="pn">{n}</div>'
                f'<div class="pt">{body}{tag}</div></div>'
            )
        if rows:
            head = f'<div class="part">{label}</div>' if label else ""
            parts_html.append(head + "".join(rows))
 
    if not parts_html:
        return ""       # 지문은 있으나 이 문항에 표시할 근거 문단이 없음
    return f'<div class="psg">{"".join(parts_html)}</div>'
 
 
# ──────────────────────────────────────────────────────────────
# 상태
# ──────────────────────────────────────────────────────────────
st.session_state.setdefault("current", None)
st.session_state.setdefault("done", set())
 
 
def go(num):
    st.session_state.current = num
 
 
def home():
    st.session_state.current = None
 
 
# ──────────────────────────────────────────────────────────────
# 사이드바
# ──────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"### {SCHOOL}")
    st.caption(f"{BRAND} · EBS 2027 수능완성 국어영역 실전 모의고사 4회")
    st.divider()
 
    st.markdown("**문항 바로가기**")
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
    st.checkbox("지문 전체 보기", value=False, key="full_passage",
                help="끄면 그 문항의 근거 문단만 보입니다.")
 
 
# ──────────────────────────────────────────────────────────────
# 메인 화면
# ──────────────────────────────────────────────────────────────
def render_home():
    topbar()
    st.markdown(
        '<div class="eyebrow">EBS 2027 수능완성 국어영역</div>'
        f'<h1 class="masthead"><span class="no">4회</span> 모의고사 (화법과 작문)</h1>'
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
        st.markdown(f'<div class="areatag">{area} · {first:02d}–{last:02d}번</div>',
                    unsafe_allow_html=True)
        for s in sets:
            st.markdown(
                f'<div class="setline"><span class="setno">{s["label"]}</span>'
                f'<span class="settitle">{s["title"]}</span></div>',
                unsafe_allow_html=True,
            )
            cols = st.columns(GRID)
            for i, n in enumerate(s["questions"]):
                with cols[i % GRID]:
                    st.button(f"{n:02d}", key=f"btn{n}",
                              type="primary" if n in st.session_state.done
                              else "secondary",
                              on_click=go, args=(n,))
            st.write("")
 
    st.markdown('<hr class="rule-thin">', unsafe_allow_html=True)
    st.caption("빨간색으로 채워진 번호는 학습 완료로 체크한 문항입니다.")
 
 
# ──────────────────────────────────────────────────────────────
# 문항 화면
# ──────────────────────────────────────────────────────────────
def render_question(num):
    q = QMAP[num]
    s = SMAP[q["set_id"]]
    idx = NUMS.index(num)
 
    topbar()
 
    nav = st.columns([1.3, 1, 1, 3])
    with nav[0]:
        st.button("← 전체 목록", key="back", on_click=home)
    with nav[1]:
        st.button("‹ 이전", key="prev", disabled=idx == 0, on_click=go,
                  args=(NUMS[max(idx - 1, 0)],))
    with nav[2]:
        st.button("다음 ›", key="next", disabled=idx == len(NUMS) - 1, on_click=go,
                  args=(NUMS[min(idx + 1, len(NUMS) - 1)],))
 
    st.markdown('<hr class="rule-thin">', unsafe_allow_html=True)
    st.markdown(
        f'<div class="crumb">{q["area"]} · {s["label"]} {s["title"]}</div>'
        f'<div class="qhead"><span class="qno">{num:02d}</span>'
        f'<span class="ansbadge"><span class="lab">정답</span>'
        f'<span class="val">{q["answer"]}</span></span>'
        f'<span class="qtype">{q["type"]}</span></div>',
        unsafe_allow_html=True,
    )
 
    if q["prompt"]:
        st.markdown(f'<div class="qprompt">{q["prompt"]}</div>',
                    unsafe_allow_html=True)
 
    # 함정 한 줄 요약
    if q.get("trap"):
        items = "".join(
            f'<div class="item"><span class="k">{lab}</span>{cell}</div>'
            for lab, cell in zip(q["trap"]["labels"], q["trap"]["cells"])
        )
        st.markdown('<div class="sect">이 문항의 함정</div>', unsafe_allow_html=True)
        render_html(items, cls="trap")
 
    if q.get("procs"):
        chips = "".join(f'<span class="chip">{p}</span>' for p in q["procs"])
        st.markdown(f'<div class="chips">적용할 풀이 절차 {chips}</div>',
                    unsafe_allow_html=True)
 
    # 지문 원문 · 근거 문단
    block = passage_block(q, q["set_id"],
                          only_cited=not st.session_state.get("full_passage"))
    st.markdown('<div class="sect">지문 원문 · 근거 문단</div>',
                unsafe_allow_html=True)
    if block:
        raw(block)
    elif block == "":
        st.markdown(
            '<div class="psg-empty">이 문항의 해설에는 특정 문단을 지목한 '
            "근거 표시가 없습니다. 왼쪽에서 ‘지문 전체 보기’를 켜면 지문 전문이 "
            "나옵니다.</div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="psg-empty">이 세트의 지문 원문이 아직 등록되지 않았습니다. '
            "<code>passages.json</code> 에 지문을 넣으면 근거 문단이 여기에 그대로 "
            "뜨고, 해설이 인용한 문장에 형광펜이 칠해집니다.</div>",
            unsafe_allow_html=True,
        )
 
    # 해설
    st.markdown('<div class="sect">선지별 해설</div>', unsafe_allow_html=True)
    render_html(q["html"])
 
    # 등급을 올리는 노하우
    if q.get("tips"):
        st.markdown('<div class="sect">등급을 올리는 노하우</div>',
                    unsafe_allow_html=True)
        for t in q["tips"]:
            st.markdown(
                f'<div class="tip"><span class="tno">{t["no"]}</span>'
                f'<span class="tt">{t["title"]}</span>'
                f'<span class="tb">{t["body"]}</span></div>',
                unsafe_allow_html=True,
            )
 
    st.markdown('<hr class="rule-thin">', unsafe_allow_html=True)
    if st.checkbox("이 문항 학습 완료", value=num in st.session_state.done,
                   key=f"done{num}"):
        st.session_state.done.add(num)
    else:
        st.session_state.done.discard(num)
 
 
# ──────────────────────────────────────────────────────────────
if st.session_state.current is None:
    render_home()
else:
    render_question(st.session_state.current)
 
