# pages/3_CARE四宫格_CARE_Grid.py
# -*- coding: utf-8 -*-

import streamlit as st

from i18n import init_i18n, lang_selector
from store import (
    list_care_records,
    add_care_record,
    update_care_record,
    delete_care_record,
    # 36×10 联动
    get_sprints,
    list_tasks_for_sprint,
    add_task_to_sprint_unique,
    toggle_task_done_by_source,
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


def _norm(s: str) -> str:
    return (s or "").strip()


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
.badge {
    display:inline-block;
    padding: 2px 10px;
    border-radius: 999px;
    border: 1px solid rgba(0,0,0,0.08);
    background: rgba(0,0,0,0.03);
    font-size: 12px;
    margin-right: 8px;
    margin-bottom: 6px;
}
</style>
""",
    unsafe_allow_html=True,
)

# -----------------------
# Vow Tag：本页自增长
# -----------------------
def _ensure_vow_store():
    if "vow_tags" not in st.session_state:
        st.session_state["vow_tags"] = []


def _add_tag_if_new(tag: str):
    _ensure_vow_store()
    tag = _norm(tag)
    if tag and tag not in st.session_state["vow_tags"]:
        st.session_state["vow_tags"].insert(0, tag)


def _rebuild_tags_from_history():
    _ensure_vow_store()
    for r in (list_care_records() or []):
        vt = _norm(r.get("vow_tag", ""))
        if vt:
            _add_tag_if_new(vt)
        tg = _norm(r.get("tags", ""))
        if tg:
            for x in [t.strip() for t in tg.split(",") if t.strip()]:
                if 1 <= len(x) <= 10:
                    _add_tag_if_new(x)


def find_assignment_by_care_id(care_id: str):
    sprints = get_sprints() or []
    if not sprints:
        return None

    care_id_str = str(care_id)
    for sp in sprints:
        sp_no = sp.get("sprint_no")
        if not sp_no:
            continue
        tasks = list_tasks_for_sprint(int(sp_no)) or []
        for t in tasks:
            if str(t.get("source_care_id", "")) == care_id_str:
                return (int(sp_no), bool(t.get("done", False)), t.get("title", ""))
    return None


# -----------------------
# 页面头
# -----------------------
st.title(TT("③ CARE 记录", "③ CARE Records"))
st.caption(
    TT(
        "把灵感转成可执行行动，并用「愿力关键词」把行动串成长期主题。",
        "Turn inspiration into action. Use a Vow Tag to connect records into long-term themes.",
    )
)

_rebuild_tags_from_history()
vow_pool = st.session_state.get("vow_tags", []) or []
vow_none = TT("（不设置）", "(None)")
vow_all = TT("（全部）", "(All)")


# -----------------------
# A | 新增
# -----------------------
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader(TT("新增 CARE 记录", "Add a CARE Record"))

with st.form("care_add_form", clear_on_submit=True):
    capture = st.text_area(TT("Capture/Source（必填：原文/链接）", "Capture/Source (required: text/link)"), height=80)
    cognition = st.text_area(TT("Cognition（认知/启发）", "Cognition (insight)"), height=80)
    action = st.text_area(TT("Action（必填：下一步最小可执行行动）", "Action (required: next smallest doable step)"), height=80)

    c1, c2 = st.columns(2)
    with c1:
        relationship = st.text_input(TT("Relationship（相关的人/协作）", "Relationship (people/collab)"))
    with c2:
        ego_drive = st.text_input(TT("Ego drive（内在驱动力）", "Ego drive (inner motivation)"))

    st.markdown("**" + TT("Vow Tag（愿力关键词）", "Vow Tag") + "**")
    colA, colB = st.columns([2, 3])
    with colA:
        vow_pick = st.selectbox(TT("从已有标签选择（可选）", "Pick an existing tag (optional)"),
                                options=[vow_none] + vow_pool, index=0)
    with colB:
        vow_new = st.text_input(TT("或手动输入新标签（推荐）", "Or type a new one (recommended)"),
                                placeholder=TT("例如：勇气 / 自律 / 影响力 / 科研突破", "e.g., Courage / Discipline / Impact"))

    score = st.slider(TT("Relevance Score（0-5，必填）", "Relevance Score (0-5, required)"), 0, 5, 4)
    tags = st.text_input(TT("Tags（可选，逗号分隔）", "Tags (optional, comma separated)"))

    submitted = st.form_submit_button(TT("➕ 添加 CARE", "➕ Add CARE"))

if submitted:
    if not _norm(capture):
        st.warning(TT("请填写 Capture/Source。", "Please fill in Capture/Source."))
    elif not _norm(action):
        st.warning(TT("请填写 Action。", "Please fill in Action."))
    else:
        final_vow = _norm(vow_new) if _norm(vow_new) else ("" if vow_pick == vow_none else _norm(vow_pick))
        if final_vow:
            _add_tag_if_new(final_vow)

        add_care_record(
            capture_source=_norm(capture),
            cognition=_norm(cognition),
            action=_norm(action),
            relationship=_norm(relationship),
            ego_drive=_norm(ego_drive),
            vow_tag=final_vow,
            relevance_score=int(score),
            tags=_norm(tags),
        )
        st.success(TT("已添加 ✅", "Added ✅"))
        st.rerun()

st.markdown("</div>", unsafe_allow_html=True)


# -----------------------
# B | 列表 + 编辑 + 分配到 36×10 + 同步完成状态
# -----------------------
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader(TT("记录列表", "Records"))

filter_strong = st.checkbox(TT("默认只看强相关（评分 ≥ 4）", "Show only high relevance (score ≥ 4)"), value=True)
kw = st.text_input(TT("关键词搜索", "Keyword search"), placeholder=TT("输入任意关键词…", "Type any keyword..."))
vow_filter = st.selectbox(TT("Vow Tag 筛选", "Filter by Vow Tag"),
                          options=[vow_all] + (st.session_state.get("vow_tags", []) or []), index=0)

records = list_care_records() or []

def match(r: dict) -> bool:
    if filter_strong and int(r.get("relevance_score", 0)) < 4:
        return False
    if vow_filter != vow_all:
        if _norm(r.get("vow_tag", "")) != _norm(vow_filter):
            return False
    if _norm(kw):
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
sprints_exist = bool(get_sprints())

if not records_show:
    st.info(TT("暂无记录。你可以先添加一条 CARE。", "No records yet. Add your first CARE above."))
else:
    for r in records_show:
        care_id = str(r.get("id"))
        vt = _norm(r.get("vow_tag", "")) or TT("（无标签）", "(no tag)")
        score = int(r.get("relevance_score", 0))

        assign_info = find_assignment_by_care_id(care_id)
        if assign_info:
            sp_no, done, _ = assign_info
            badge = f"{TT('已分配','Assigned')} · {TT('周期','Cycle')} {sp_no} · {'✅' if done else '⬜'}"
        else:
            badge = TT("未分配到 36×10", "Not assigned to 36×10")

        st.markdown(
            f'<span class="badge">⭐ {score}</span>'
            f'<span class="badge">{vt}</span>'
            f'<span class="badge">{badge}</span>',
            unsafe_allow_html=True
        )

        st.write(r.get("action", ""))

        with st.expander(TT("展开详情 / 编辑 / 分配", "Details / Edit / Assign"), expanded=False):

            # ✅ 若已分配：允许直接勾选完成（同步 36×10）
            if assign_info:
                sp_no, done, _ = assign_info
                new_done = st.checkbox(
                    TT(f"本行动已加入 周期 {sp_no} 的任务：完成了吗？", f"Assigned to Cycle {sp_no}: Mark done?"),
                    value=bool(done),
                    key=f"done_sync_{care_id}",
                )
                if new_done != bool(done):
                    toggle_task_done_by_source(sp_no, care_id, new_done)
                    st.success(TT("已同步到 36×10 ✅", "Synced to 36×10 ✅"))
                    st.rerun()

            # 编辑
            with st.form(f"edit_{care_id}"):
                cap_e = st.text_area("Capture/Source", value=r.get("capture_source",""), height=70)
                cog_e = st.text_area("Cognition", value=r.get("cognition",""), height=70)
                act_e = st.text_area("Action", value=r.get("action",""), height=70)

                c1, c2 = st.columns(2)
                with c1:
                    rel_e = st.text_input("Relationship", value=r.get("relationship",""))
                with c2:
                    ego_e = st.text_input("Ego drive", value=r.get("ego_drive",""))

                st.markdown("**Vow Tag**")
                colA, colB = st.columns([2, 3])
                with colA:
                    vow_opts_now = [vow_none] + (st.session_state.get("vow_tags", []) or [])
                    cur_v = _norm(r.get("vow_tag",""))
                    idx = vow_opts_now.index(cur_v) if (cur_v and cur_v in vow_opts_now) else 0
                    vow_pick_e = st.selectbox("Pick", vow_opts_now, index=idx, key=f"pick_{care_id}")
                with colB:
                    vow_new_e = st.text_input(TT("输入新标签（可选）","New tag (optional)"), key=f"new_{care_id}")

                score_e = st.slider("Relevance Score", 0, 5, int(r.get("relevance_score",0)), key=f"sc_{care_id}")
                tags_e = st.text_input("Tags", value=r.get("tags",""), key=f"tg_{care_id}")
                save_edit = st.form_submit_button(TT("保存修改", "Save changes"))

            if save_edit:
                final_v = _norm(vow_new_e) if _norm(vow_new_e) else ("" if vow_pick_e == vow_none else _norm(vow_pick_e))
                if final_v:
                    _add_tag_if_new(final_v)

                update_care_record(
                    care_id,
                    capture_source=_norm(cap_e),
                    cognition=_norm(cog_e),
                    action=_norm(act_e),
                    relationship=_norm(rel_e),
                    ego_drive=_norm(ego_e),
                    vow_tag=final_v,
                    relevance_score=int(score_e),
                    tags=_norm(tags_e),
                )
                st.success(TT("已保存 ✅", "Saved ✅"))
                st.rerun()

            st.divider()

            # 分配到 36×10
            if not sprints_exist:
                st.info(TT("还没有生成 36×10 周期。请先去「36×10天」页面生成周期。",
                           "No 36×10 cycles yet. Please generate them first."))
            else:
                st.markdown("**" + TT("把这条行动分配到 36×10", "Assign this action to 36×10") + "**")
                colX, colY = st.columns([2, 1])
                with colX:
                    sp_no_sel = st.selectbox(TT("选择周期", "Select cycle"), options=list(range(1, 37)), index=0, key=f"sp_{care_id}")
                with colY:
                    assign_btn = st.button(TT("一键分配", "Assign"), key=f"as_{care_id}")

                if assign_btn:
                    title = _norm(r.get("action",""))
                    if not title:
                        st.warning(TT("这条记录的 Action 为空，无法分配。", "Action is empty — cannot assign."))
                    else:
                        add_task_to_sprint_unique(int(sp_no_sel), title, source_care_id=care_id)
                        st.success(TT(f"已分配到 周期 {sp_no_sel}", f"Assigned to Cycle {sp_no_sel}"))
                        st.rerun()

            st.divider()

            # 删除
            if st.button(TT("🗑 删除这条", "🗑 Delete"), key=f"del_{care_id}"):
                delete_care_record(care_id)
                st.success(TT("已删除", "Deleted"))
                st.rerun()

        st.divider()

st.markdown("</div>", unsafe_allow_html=True)
