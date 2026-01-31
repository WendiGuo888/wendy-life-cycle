# pages/3_CARE四宫格_CARE_Grid.py
# -*- coding: utf-8 -*-

import streamlit as st
from datetime import date

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
)

# -----------------------
# ✅ set_page_config（必须在 st.xxx 前）
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
# ✅ 通用小工具（兼容 dict / ORM / dataclass）
# -----------------------
def _is_dict(x):
    return isinstance(x, dict)


def _get(obj, key, default=None):
    if _is_dict(obj):
        return obj.get(key, default)
    return getattr(obj, key, default)


def _norm(s: str) -> str:
    return (s or "").strip()


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
# ✅ Vow Tag：本页自增长（不依赖年度挖掘）
# -----------------------
def _ensure_vow_store():
    if "vow_tags" not in st.session_state:
        st.session_state["vow_tags"] = []  # List[str]


def _add_tag_if_new(tag: str):
    _ensure_vow_store()
    tag = _norm(tag)
    if not tag:
        return
    if tag not in st.session_state["vow_tags"]:
        # 新的放最前面，让用户立刻看到“系统在跟随我”
        st.session_state["vow_tags"].insert(0, tag)


def _rebuild_tags_from_history():
    """从历史记录里回填候选标签（vow_tag + tags 的短词）"""
    _ensure_vow_store()
    for r in (list_care_records() or []):
        vt = _norm(_get(r, "vow_tag", ""))
        if vt:
            _add_tag_if_new(vt)

        tg = _norm(_get(r, "tags", ""))
        if tg:
            for x in [t.strip() for t in tg.split(",") if t.strip()]:
                if 1 <= len(x) <= 10:  # 控制噪声
                    _add_tag_if_new(x)


# -----------------------
# ✅ 36×10：查 “这条 CARE 是否已被分配为任务” + 完成状态
# -----------------------
def find_assignment_by_care_id(care_id: str):
    """
    返回 (sprint_no, done, title) 或 None
    兼容：store dict / ORM / dataclass
    """
    sprints = get_sprints() or []
    if not sprints:
        return None

    care_id_str = str(care_id)

    for sp in sprints:
        sp_no = _get(sp, "sprint_no", None)
        if sp_no is None:
            continue

        tasks = list_tasks_for_sprint(int(sp_no)) or []
        for t in tasks:
            source_id = _get(t, "source_care_id", "")
            if str(source_id) == care_id_str:
                done = bool(_get(t, "done", False))
                title = _get(t, "title", "") or ""
                return (int(sp_no), done, title)

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


def _vow_none_label():
    return TT("（不设置）", "(None)")


def _vow_all_label():
    return TT("（全部）", "(All)")


def _no_tag_label():
    return TT("（无标签）", "(no tag)")


# -----------------------
# A | 新增
# -----------------------
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader(TT("新增 CARE 记录", "Add a CARE Record"))

vow_pool = st.session_state.get("vow_tags", []) or []
vow_options_add = [_vow_none_label()] + vow_pool

with st.form("care_add_form", clear_on_submit=True):
    capture = st.text_area(
        TT("Capture/Source（必填：原文/链接）", "Capture/Source (required: text/link)"),
        height=80,
        key="add_capture",
    )
    cognition = st.text_area(
        TT("Cognition（认知/启发）", "Cognition (insight)"),
        height=80,
        key="add_cognition",
    )
    action = st.text_area(
        TT("Action（必填：下一步最小可执行行动）", "Action (required: next smallest doable step)"),
        height=80,
        key="add_action",
    )

    c1, c2 = st.columns(2)
    with c1:
        relationship = st.text_input(
            TT("Relationship（相关的人/协作）", "Relationship (people/collab)"),
            key="add_relationship",
        )
    with c2:
        ego_drive = st.text_input(
            TT("Ego drive（内在驱动力）", "Ego drive (inner motivation)"),
            key="add_ego",
        )

    st.markdown("**" + TT("Vow Tag（愿力关键词）", "Vow Tag") + "**")
    colA, colB = st.columns([2, 3])
    with colA:
        vow_pick = st.selectbox(
            TT("从已有标签选择（可选）", "Pick an existing tag (optional)"),
            options=vow_options_add,
            index=0,
            key="add_vow_pick",
        )
    with colB:
        vow_new = st.text_input(
            TT("或手动输入新标签（推荐）", "Or type a new one (recommended)"),
            placeholder=TT("例如：勇气 / 自律 / 影响力 / 科研突破", "e.g., Courage / Discipline / Impact"),
            key="add_vow_new",
        )

    score = st.slider(
        TT("Relevance Score（0-5，必填）", "Relevance Score (0-5, required)"),
        0, 5, 4,
        key="add_score",
    )
    tags = st.text_input(
        TT("Tags（可选，逗号分隔）", "Tags (optional, comma separated)"),
        key="add_tags",
    )

    submitted = st.form_submit_button(TT("➕ 添加 CARE", "➕ Add CARE"))

if submitted:
    if not _norm(capture):
        st.warning(TT("请填写 Capture/Source。", "Please fill in Capture/Source."))
    elif not _norm(action):
        st.warning(TT("请填写 Action。", "Please fill in Action."))
    else:
        final_vow = _norm(vow_new) if _norm(vow_new) else ("" if vow_pick == _vow_none_label() else _norm(vow_pick))
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
# B | 列表 + 可编辑 + 分配到 36×10
# -----------------------
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader(TT("记录列表", "Records"))

filter_strong = st.checkbox(
    TT("默认只看强相关（评分 ≥ 4）", "Show only high relevance (score ≥ 4)"),
    value=True,
    key="filter_strong",
)
kw = st.text_input(
    TT("关键词搜索", "Keyword search"),
    placeholder=TT("输入任意关键词…", "Type any keyword..."),
    key="kw_search",
)

vow_pool_now = st.session_state.get("vow_tags", []) or []
vow_filter = st.selectbox(
    TT("Vow Tag 筛选", "Filter by Vow Tag"),
    options=[_vow_all_label()] + vow_pool_now,
    index=0,
    key="vow_filter",
)

records = list_care_records() or []


def _blob(r) -> str:
    parts = [
        str(_get(r, "capture_source", "")),
        str(_get(r, "cognition", "")),
        str(_get(r, "action", "")),
        str(_get(r, "relationship", "")),
        str(_get(r, "ego_drive", "")),
        str(_get(r, "vow_tag", "")),
        str(_get(r, "tags", "")),
    ]
    return " ".join(parts).lower()


def match(r) -> bool:
    rs = int(_get(r, "relevance_score", 0) or 0)
    if filter_strong and rs < 4:
        return False

    if vow_filter != _vow_all_label():
        if _norm(_get(r, "vow_tag", "")) != _norm(vow_filter):
            return False

    if _norm(kw):
        if kw.strip().lower() not in _blob(r):
            return False

    return True


records_show = [r for r in records if match(r)]

if not records_show:
    st.info(TT("暂无记录。你可以先添加一条 CARE。", "No records yet. Add your first CARE above."))
else:
    sprints_exist = bool(get_sprints())

    for r in records_show:
        care_id = _get(r, "id", "")
        care_id_str = str(care_id)

        vt_raw = _norm(_get(r, "vow_tag", ""))
        vt = vt_raw if vt_raw else _no_tag_label()

        score = int(_get(r, "relevance_score", 0) or 0)

        assign_info = find_assignment_by_care_id(care_id_str)
        if assign_info:
            sp_no, done, task_title = assign_info
            badge = f"{TT('已分配','Assigned')} · {TT('周期','Cycle')} {sp_no} · {'✅' if done else '⬜'}"
        else:
            badge = TT("未分配到 36×10", "Not assigned to 36×10")

        st.markdown(
            f'<span class="badge">⭐ {score}</span>'
            f'<span class="badge">{vt}</span>'
            f'<span class="badge">{badge}</span>',
            unsafe_allow_html=True
        )

        # ✅ 列表主行：显示 Action（你要的“行动词组”）
        st.write(_get(r, "action", ""))

        with st.expander(TT("展开详情 / 编辑 / 分配", "Details / Edit / Assign"), expanded=False):

            # --------- 编辑区（form）---------
            with st.form(f"edit_form_{care_id_str}"):
                cap_e = st.text_area("Capture/Source", value=_get(r, "capture_source", ""), height=70, key=f"cap_{care_id_str}")
                cog_e = st.text_area("Cognition", value=_get(r, "cognition", ""), height=70, key=f"cog_{care_id_str}")
                act_e = st.text_area("Action", value=_get(r, "action", ""), height=70, key=f"act_{care_id_str}")

                c1, c2 = st.columns(2)
                with c1:
                    rel_e = st.text_input("Relationship", value=_get(r, "relationship", ""), key=f"rel_{care_id_str}")
                with c2:
                    ego_e = st.text_input("Ego drive", value=_get(r, "ego_drive", ""), key=f"ego_{care_id_str}")

                st.markdown("**Vow Tag**")
                colA, colB = st.columns([2, 3])

                with colA:
                    vow_opts_now = [_vow_none_label()] + (st.session_state.get("vow_tags", []) or [])
                    cur_v = _norm(_get(r, "vow_tag", ""))
                    idx = 0
                    if cur_v and cur_v in vow_opts_now:
                        idx = vow_opts_now.index(cur_v)

                    vow_pick_e = st.selectbox("Pick", vow_opts_now, index=idx, key=f"pick_{care_id_str}")

                with colB:
                    vow_new_e = st.text_input(
                        TT("输入新标签（可选）", "New tag (optional)"),
                        placeholder=TT("例如：勇气 / 自律 / 影响力", "e.g., Courage / Discipline / Impact"),
                        key=f"new_{care_id_str}",
                    )

                score_e = st.slider("Relevance Score", 0, 5, int(_get(r, "relevance_score", 0) or 0), key=f"sc_{care_id_str}")
                tags_e = st.text_input("Tags", value=_get(r, "tags", ""), key=f"tg_{care_id_str}")

                save_edit = st.form_submit_button(TT("保存修改", "Save changes"))

            if save_edit:
                if not _norm(cap_e):
                    st.warning(TT("Capture/Source 不能为空。", "Capture/Source cannot be empty."))
                    st.stop()
                if not _norm(act_e):
                    st.warning(TT("Action 不能为空。", "Action cannot be empty."))
                    st.stop()

                final_v = _norm(vow_new_e) if _norm(vow_new_e) else ("" if vow_pick_e == _vow_none_label() else _norm(vow_pick_e))
                if final_v:
                    _add_tag_if_new(final_v)

                update_care_record(
                    care_id_str,
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

            # --------- 分配到 36×10 ---------
            if not sprints_exist:
                st.info(
                    TT("还没有生成 36×10 周期。请先去「36×10天」页面生成周期。",
                       "No 36×10 cycles yet. Please generate them on the 36×10 page first.")
                )
            else:
                st.markdown("**" + TT("把这条行动分配到 36×10", "Assign this action to 36×10") + "**")

                colX, colY = st.columns([2, 1])
                with colX:
                    sp_no_sel = st.selectbox(
                        TT("选择周期", "Select cycle"),
                        options=list(range(1, 37)),
                        index=0,
                        key=f"sp_{care_id_str}",
                    )
                with colY:
                    assign_btn = st.button(TT("一键分配", "Assign"), key=f"as_{care_id_str}")

                if assign_btn:
                    title = _norm(_get(r, "action", ""))
                    if not title:
                        st.warning(TT("这条记录的 Action 为空，无法分配。", "Action is empty — cannot assign."))
                    else:
                        # ✅ 用 CARE 的 id 作为 source_care_id 绑定
                        add_task_to_sprint_unique(int(sp_no_sel), title, source_care_id=care_id_str)
                        st.success(TT(f"已分配到 周期 {sp_no_sel}", f"Assigned to Cycle {sp_no_sel}"))
                        st.rerun()

            st.divider()

            # --------- 删除 ---------
            if st.button(TT("🗑 删除这条", "🗑 Delete"), key=f"del_{care_id_str}"):
                delete_care_record(care_id_str)
                st.success(TT("已删除", "Deleted"))
                st.rerun()

        st.divider()

st.markdown("</div>", unsafe_allow_html=True)
