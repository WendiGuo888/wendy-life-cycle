# pages/2_36x10天_Growth_Plan.py
# -*- coding: utf-8 -*-

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Dict, List, Optional

import streamlit as st

from i18n import init_i18n, lang_selector
from store import (
    get_sprints,
    regenerate_sprints,
    update_sprint_text,
    list_tasks_for_sprint,
    add_task_to_sprint_unique,
    toggle_task_done,
    update_task_evidence,
)

# -----------------------
# ✅ set_page_config 必须在任何 st.xxx 前
# -----------------------
lang = st.session_state.get("lang", "zh")
st.set_page_config(
    page_title=("② 36×10天" if lang == "zh" else "② 36×10 Growth Plan"),
    page_icon="🌱",
    layout="wide",
)

# -----------------------
# i18n 初始化 + 侧边栏语言
# -----------------------
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
    padding: 16px 16px;
    margin-bottom: 14px;
    border: 1px solid rgba(0,0,0,0.06);
    box-shadow: 0 10px 24px rgba(0,0,0,0.04);
}
.small { color:#666; font-size: 13px; }
.muted { color:#777; font-size: 12px; }
hr { border: none; border-top: 1px solid rgba(0,0,0,0.06); margin: 10px 0; }
</style>
""",
    unsafe_allow_html=True,
)


# -----------------------
# ✅ 兼容层：dict / 对象 统一
# -----------------------
def to_date(x) -> Optional[date]:
    if x is None:
        return None
    if isinstance(x, date) and not isinstance(x, datetime):
        return x
    if isinstance(x, datetime):
        return x.date()
    if isinstance(x, str) and x.strip():
        try:
            return datetime.fromisoformat(x.strip()).date()
        except Exception:
            return None
    return None


def sprint_to_dict(sp) -> Dict[str, Any]:
    """兼容 store 返回 dict / dataclass / ORM 对象，统一转 dict"""
    if sp is None:
        return {}
    if isinstance(sp, dict):
        return sp
    d = {}
    for k in ["sprint_no", "start_date", "end_date", "theme", "objective", "review", "mit", "tasks"]:
        if hasattr(sp, k):
            d[k] = getattr(sp, k)
    return d


def task_to_dict(t) -> Dict[str, Any]:
    if t is None:
        return {}
    if isinstance(t, dict):
        return t
    d = {}
    for k in ["id", "title", "done", "evidence", "source_care_id"]:
        if hasattr(t, k):
            d[k] = getattr(t, k)
    return d


def sprints_ready() -> bool:
    sps = get_sprints()
    return bool(sps) and len(sps) >= 36


def get_sprint_dict_by_no(no: int) -> Dict[str, Any]:
    for sp in get_sprints() or []:
        spd = sprint_to_dict(sp)
        if int(spd.get("sprint_no", -1) or -1) == int(no):
            return spd
    return {}


# -----------------------
# 状态：当前查看哪个周期（1..36），None 表示总览
# -----------------------
if "current_cycle_no" not in st.session_state:
    st.session_state.current_cycle_no = None  # type: ignore


# -----------------------
# 顶部标题
# -----------------------
st.title(TT("② 36×10：自我提升计划（10天行动周期）", "② 36×10: Growth Plan (10-day cycles)"))
st.caption(
    TT(
        "流程：先生成 36 个周期 → 逐个填写主题/交付物 → 添加任务并勾选完成 → 去④导出。",
        "Flow: generate 36 cycles → fill theme/deliverables → add tasks & mark done → export in page ④.",
    )
)


# =========================================================
# A｜生成/重建 36×10
# =========================================================
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader(TT("A｜生成/重建 36×10 周期", "A | Generate / Rebuild 36×10 Cycles"))

if not sprints_ready():
    st.info(TT("还没有生成 36×10 周期。请先生成。", "No 36×10 cycles yet. Please generate first."))
else:
    st.success(TT("已检测到 36×10 周期 ✅", "36×10 cycles detected ✅"))

start_default = date.today()
start_dt = st.date_input(
    TT("选择开始日期（第1周期的第1天）", "Pick start date (Day 1 of Cycle 1)"),
    value=start_default,
    key="gp_start_date",
)

colA, colB = st.columns([1, 2])
with colA:
    gen_btn = st.button(
        TT("🚀 生成/重建 36×10（会清空旧周期与任务）", "🚀 Generate / Rebuild 36×10 (clears old cycles & tasks)"),
        use_container_width=True,
        key="gp_regen_btn",
    )
with colB:
    st.markdown(
        f'<div class="small">{TT("提示：重建会清空所有周期内容与任务。若你想保留，请先去「备份」页导出 JSON。", "Tip: Rebuild clears all cycle texts & tasks. If you want to keep them, export JSON in Backup page first.")}</div>',
        unsafe_allow_html=True,
    )

if gen_btn:
    regenerate_sprints(start_dt)
    st.session_state.current_cycle_no = None
    st.success(TT("已生成 36 个周期 ✅", "Generated 36 cycles ✅"))
    st.rerun()

st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
# B｜总览（36格）
# =========================================================
def render_overview():
    sps = [sprint_to_dict(x) for x in (get_sprints() or [])]
    if not sps:
        st.warning(TT("请先在上方生成 36×10 周期。", "Please generate 36×10 cycles above first."))
        return

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader(TT("B｜总览（点击进入某个周期）", "B | Overview (click a cycle to edit)"))
    st.caption(
        TT(
            "每格：周期号 + 日期范围 + 主题（若已填写）。",
            "Each tile shows: cycle no + date range + theme (if filled).",
        )
    )

    cols = st.columns(6)
    for i in range(36):
        sp = sps[i] if i < len(sps) else {}
        no = int(sp.get("sprint_no", i + 1) or (i + 1))
        sd = to_date(sp.get("start_date"))
        ed = to_date(sp.get("end_date"))
        theme = (sp.get("theme") or "").strip()

        date_str = ""
        if sd and ed:
            date_str = f"{sd.strftime('%Y/%m/%d')} - {ed.strftime('%m/%d')}"
        else:
            date_str = TT("（未设置日期）", "(date missing)")

        title = f"{TT('第', 'Cycle ')}{no}{TT('周期', '')}"
        subtitle = theme if theme else TT("（未填写主题）", "(theme not set)")

        with cols[i % 6]:
            with st.container(border=True):
                st.markdown(f"**{title}**")
                st.markdown(f"<div class='muted'>{date_str}</div>", unsafe_allow_html=True)
                st.markdown(f"{subtitle}")
                if st.button(TT("编辑", "Edit"), key=f"ov_go_{no}", use_container_width=True):
                    st.session_state.current_cycle_no = no
                    st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
# C｜周期详情
# =========================================================
def render_cycle_detail(cycle_no: int):
    sp = get_sprint_dict_by_no(cycle_no)

    if not sp:
        st.warning(TT("找不到该周期数据。请先生成 36×10。", "Cannot find this cycle. Please generate 36×10 first."))
        return

    sd = to_date(sp.get("start_date"))
    ed = to_date(sp.get("end_date"))

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader(TT(f"C｜第{cycle_no}周期（10天）", f"C | Cycle {cycle_no} (10 days)"))

    # 顶部导航
    nav1, nav2, nav3 = st.columns([1, 1, 1])
    with nav1:
        if st.button(TT("⬅ 返回总览", "⬅ Back to overview"), use_container_width=True, key="btn_back_overview"):
            st.session_state.current_cycle_no = None
            st.rerun()
    with nav2:
        if st.button(TT("⬅ 上一个", "⬅ Prev"), use_container_width=True, key="btn_prev"):
            st.session_state.current_cycle_no = max(1, cycle_no - 1)
            st.rerun()
    with nav3:
        if st.button(TT("下一个 ➡", "Next ➡"), use_container_width=True, key="btn_next"):
            st.session_state.current_cycle_no = min(36, cycle_no + 1)
            st.rerun()

    st.markdown("<hr/>", unsafe_allow_html=True)

    # 日期显示
    if sd and ed:
        st.caption(TT("周期日期：", "Cycle dates: ") + f"{sd.strftime('%Y/%m/%d')} - {ed.strftime('%Y/%m/%d')}")
    else:
        st.caption(TT("周期日期：未设置（请重建 36×10）", "Cycle dates: missing (please rebuild 36×10)"))

    # 主题 / 交付物 / 复盘
    theme_key = f"theme_{cycle_no}"
    obj_key = f"obj_{cycle_no}"
    review_key = f"review_{cycle_no}"

    theme = st.text_input(
        TT("主题（Theme）", "Theme"),
        value=(sp.get("theme") or ""),
        key=theme_key,
        placeholder=TT("例如：论文冲刺 / 体能训练 / IP增长", "e.g., Paper sprint / Fitness / Content growth"),
    )

    objective = st.text_area(
        TT("交付物/成果（Deliverables）", "Deliverables"),
        value=(sp.get("objective") or ""),
        key=obj_key,
        height=120,
        placeholder=TT("写清楚10天后你要交付什么：可衡量、可验证。", "Define what you will deliver in 10 days. Measurable and verifiable."),
    )

    review = st.text_area(
        TT("复盘（Review）", "Review"),
        value=(sp.get("review") or ""),
        key=review_key,
        height=110,
        placeholder=TT("完成了什么？证据是什么？下轮要怎么改？", "What was done? Evidence? What to improve next cycle?"),
    )

    save_col, _ = st.columns([1, 2])
    with save_col:
        if st.button(TT("💾 保存本周期", "💾 Save this cycle"), use_container_width=True, key=f"save_cycle_{cycle_no}"):
            update_sprint_text(cycle_no, theme=theme, objective=objective, review=review)
            st.success(TT("已保存 ✅", "Saved ✅"))
            st.rerun()

    st.markdown("<hr/>", unsafe_allow_html=True)

    # 任务区
    st.subheader(TT("任务清单（Tasks）", "Tasks"))

    add_title = st.text_input(
        TT("新增任务（回车或点击添加）", "Add a task (press Enter or click Add)"),
        value="",
        key=f"new_task_{cycle_no}",
        placeholder=TT("例如：每天写作30分钟 / 完成实验数据整理", "e.g., Write 30 mins/day / Clean experiment data"),
    )
    add_btn = st.button(TT("➕ 添加任务", "➕ Add task"), key=f"btn_add_task_{cycle_no}")

    if add_btn:
        add_task_to_sprint_unique(cycle_no, add_title.strip(), source_care_id=None)
        st.rerun()

    tasks_raw = list_tasks_for_sprint(cycle_no) or []
    tasks = [task_to_dict(x) for x in tasks_raw]

    if not tasks:
        st.info(TT("还没有任务。先添加一条吧。", "No tasks yet. Add one above."))
    else:
        for idx, t in enumerate(tasks):
            tid = str(t.get("id", f"{cycle_no}_{idx}"))
            title = (t.get("title") or "").strip()
            done = bool(t.get("done", False))
            evidence = t.get("evidence") or ""

            with st.container(border=True):
                c1, c2 = st.columns([1, 6])
                with c1:
                    new_done = st.checkbox(TT("完成", "Done"), value=done, key=f"done_{tid}")
                    if new_done != done:
                        toggle_task_done(tid, new_done)
                        st.rerun()

                with c2:
                    st.markdown(f"**{title}**")
                    ev = st.text_area(
                        TT("证据/备注（可选）", "Evidence/Notes (optional)"),
                        value=evidence,
                        key=f"ev_{tid}",
                        height=80,
                        placeholder=TT("例如：截图链接 / 文档链接 / 里程碑说明", "e.g., screenshot link / doc link / milestone notes"),
                    )
                    if ev != evidence:
                        update_task_evidence(tid, ev)

    st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
# 渲染入口：总览 或 详情
# =========================================================
if st.session_state.current_cycle_no is None:
    render_overview()
else:
    try:
        no = int(st.session_state.current_cycle_no)
        no = max(1, min(36, no))
    except Exception:
        no = 1
    render_cycle_detail(no)


# =========================================================
# 底部提示
# =========================================================
st.info(
    TT(
        "提示：如果你想让粉丝/朋友内测且不串数据，当前 store 版已是「每个访问者独立 Session」。想长期保存，建议在「备份」页让用户导出 JSON 自己存。",
        "Tip: For beta testing without data leakage, this store version is session-isolated per visitor. For long-term saving, provide JSON export in Backup page.",
    )
)
