# pages/3_CARE四宫格_CARE_Grid.py
# -*- coding: utf-8 -*-

import streamlit as st
from datetime import date

from i18n import init_i18n, lang_selector
from store import (
    list_care_records,
    add_care_record,
    delete_care_record,
)

# -----------------------
# set_page_config（必须在 st.xxx 前）
# -----------------------
lang = st.session_state.get("lang", "zh")
st.set_page_config(
    page_title=("③ CARE 四宫格" if lang == "zh" else "③ CARE Grid"),
    page_icon="🧩",
    layout="wide",
)

init_i18n(default="zh")
lang_selector()


def TT(zh: str, en: str) -> str:
    return zh if st.session_state.get("lang", "zh") == "zh" else en


# -----------------------
# 样式
# -----------------------
st.markdown(
    """
<style>
.block-container { padding-top: 1.2rem; padding-bottom: 2.0rem; max-width: 1180px; }
.card {
    background: #fff;
    border-radius: 16px;
    padding: 18px 18px;
    margin-bottom: 14px;
    border: 1px solid rgba(0,0,0,0.06);
    box-shadow: 0 10px 24px rgba(0,0,0,0.04);
}
.small { color:#666; font-size: 13px; }
</style>
""",
    unsafe_allow_html=True,
)

# -----------------------
# Session 内的 Vow Tag 管理（不依赖年度挖掘）
# -----------------------
def ensure_vow_store():
    if "vow_tags" not in st.session_state:
        st.session_state["vow_tags"] = []  # List[str]

def norm_tag(x: str) -> str:
    return (x or "").strip()

def add_tag_if_new(tag: str):
    ensure_vow_store()
    tag = norm_tag(tag)
    if not tag:
        return
    if tag not in st.session_state["vow_tags"]:
        st.session_state["vow_tags"].insert(0, tag)  # 新的放前面


# -----------------------
# 顶部
# -----------------------
st.title(TT("③ CARE 记录", "③ CARE Records"))
st.caption(
    TT(
        "把灵感转成可执行行动，并用「愿力关键词」串起来，方便后续复盘与规划。",
        "Turn inspiration into an action. Use a Vow Tag to connect your records for review & planning.",
    )
)

# -----------------------
# A | 新增 CARE
# -----------------------
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader(TT("新增 CARE 记录", "Add a CARE Record"))

ensure_vow_store()

# 自动从历史记录里“反哺”出 vow tag（如果用户已经用过）
# 这样不用年度挖掘也能越来越聪明
existing = list_care_records() or []
for r in existing:
    vt = norm_tag(r.get("vow_tag", ""))
    if vt:
        add_tag_if_new(vt)

# 下拉选项
vow_options = st.session_state.get("vow_tags", [])
if not vow_options:
    vow_options = [TT("（还没有标签，建议先手动输入一个）", "(No tags yet — type one below)")]
    has_real_tags = False
else:
    has_real_tags = True

with st.form("care_form", clear_on_submit=True):
    capture = st.text_area(
        TT("Capture/Source（必填：原文/链接）", "Capture/Source (required: text/link)"),
        height=80,
    )
    cognition = st.text_area(TT("Cognition（认知/启发）", "Cognition (insight)"), height=80)
    action = st.text_area(
        TT("Action（必填：下一步最小可执行行动）", "Action (required: next smallest doable step)"),
        height=80,
    )

    c1, c2 = st.columns(2)
    with c1:
        relationship = st.text_input(TT("Relationship（相关的人/协作）", "Relationship (people/collab)"))
    with c2:
        ego_drive = st.text_input(TT("Ego drive（内在驱动力）", "Ego drive (inner motivation)"))

    # --- Vow Tag：下拉 + 手动输入 ---
    st.markdown("**" + TT("Vow Tag（愿力关键词）", "Vow Tag") + "**")
    colA, colB = st.columns([2, 3])
    with colA:
        vow_pick = st.selectbox(
            TT("从已有标签选择（可选）", "Pick an existing tag (optional)"),
            options=vow_options,
            index=0,
            disabled=(not has_real_tags),
        )
    with colB:
        vow_new = st.text_input(
            TT("或手动输入新标签（推荐）", "Or type a new one (recommended)"),
            placeholder=TT("例如：勇气 / 自律 / 影响力 / 科研突破", "e.g., Courage / Discipline / Impact"),
        )

    score = st.slider(TT("Relevance Score（0-5，必填）", "Relevance Score (0-5, required)"), 0, 5, 4)
    tags = st.text_input(TT("Tags（可选，逗号分隔）", "Tags (optional, comma separated)"))

    submitted = st.form_submit_button(TT("➕ 添加 CARE", "➕ Add CARE"))

if submitted:
    # ✅ 必填校验：不要用 if not score（0 会被误判）
    if not (capture or "").strip():
        st.warning(TT("请填写 Capture/Source。", "Please fill in Capture/Source."))
    elif not (action or "").strip():
        st.warning(TT("请填写 Action。", "Please fill in Action."))
    else:
        final_vow = norm_tag(vow_new) if norm_tag(vow_new) else (norm_tag(vow_pick) if has_real_tags else "")
        if final_vow:
            add_tag_if_new(final_vow)

        add_care_record(
            capture_source=capture.strip(),
            cognition=(cognition or "").strip(),
            action=action.strip(),
            relationship=(relationship or "").strip(),
            ego_drive=(ego_drive or "").strip(),
            vow_tag=final_vow,
            relevance_score=int(score),
            tags=(tags or "").strip(),
        )
        st.success(TT("已添加 ✅", "Added ✅"))
        st.rerun()

st.markdown("</div>", unsafe_allow_html=True)


# -----------------------
# B | 列表
# -----------------------
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader(TT("记录列表", "Records"))

filter_strong = st.checkbox(
    TT("默认只看强相关（评分 ≥ 4）", "Show only high relevance (score ≥ 4)"),
    value=True,
)

kw = st.text_input(TT("关键词搜索", "Keyword search"), placeholder=TT("输入任意关键词…", "Type any keyword..."))
vow_filter = st.selectbox(
    TT("Vow Tag 筛选", "Filter by Vow Tag"),
    options=[TT("（全部）", "(All)")] + (st.session_state.get("vow_tags", []) or []),
    index=0,
)

records = list_care_records() or []

def match(r: dict) -> bool:
    if filter_strong and int(r.get("relevance_score", 0)) < 4:
        return False

    if vow_filter not in [TT("（全部）", "(All)")]:
        if norm_tag(r.get("vow_tag", "")) != norm_tag(vow_filter):
            return False

    if kw.strip():
        blob = " ".join([
            str(r.get("capture_source","")),
            str(r.get("cognition","")),
            str(r.get("action","")),
            str(r.get("relationship","")),
            str(r.get("ego_drive","")),
            str(r.get("vow_tag","")),
            str(r.get("tags","")),
        ]).lower()
        if kw.strip().lower() not in blob:
            return False
    return True

records_show = [r for r in records if match(r)]

if not records_show:
    st.info(TT("暂无记录。你可以先添加一条 CARE。", "No records yet. Add your first CARE above."))
else:
    for r in records_show:
        top = f"⭐ {r.get('relevance_score',0)}  ·  {r.get('vow_tag','') or TT('（无标签）','(no tag)')}"
        st.markdown(f"**{top}**")
        st.write(r.get("action",""))
        with st.expander(TT("展开详情", "Details"), expanded=False):
            st.markdown(f"**Capture/Source**\n\n{r.get('capture_source','')}")
            if r.get("cognition"):
                st.markdown(f"**Cognition**\n\n{r.get('cognition','')}")
            cols = st.columns(2)
            with cols[0]:
                st.markdown(f"**Relationship**\n\n{r.get('relationship','')}")
            with cols[1]:
                st.markdown(f"**Ego drive**\n\n{r.get('ego_drive','')}")
            if r.get("tags"):
                st.markdown(f"**Tags**: {r.get('tags')}")

            # 删除按钮
            if st.button(TT("🗑 删除这条", "🗑 Delete"), key=f"del_{r.get('id')}"):
                delete_care_record(r.get("id"))
                st.success(TT("已删除", "Deleted"))
                st.rerun()
        st.divider()

st.markdown("</div>", unsafe_allow_html=True)
