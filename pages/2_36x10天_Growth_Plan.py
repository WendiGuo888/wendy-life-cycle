# pages/2_36x10天_Growth_Plan.py
# -*- coding: utf-8 -*-

import streamlit as st
from datetime import date

from i18n import init_i18n, lang_selector
from store import (
    get_sprints,
    regenerate_sprints,
    get_sprint_by_no,
    update_sprint_text,
    list_tasks_for_sprint,
    add_task_to_sprint_unique,
    toggle_task_done,
    update_task_evidence,
)

# -----------------------
# set_page_config（必须在 st.xxx 前）
# -----------------------
lang = st.session_state.get("lang", "zh")
st.set_page_config(
    page_title=("② 36×10天" if lang == "zh" else "② 36×10"),
    page_icon="🗓️",
    layout="wide",
)

init_i18n(default="zh")
lang_selector()

def TT(zh: str, en: str) -> str:
    return zh if st.session_state.get("lang", "zh") == "zh" else en

st.markdown(
    """
<style>
.block-container { padding-top: 1.2rem; padding-bottom: 2.0rem; max-width: 1180px; }
.card {
  background:#fff; border-radius:16px; padding:18px 18px; margin-bottom:14px;
  border:1px solid rgba(0,0,0,0.06); box-shadow:0 10px 24px rgba(0,0,0,0.04);
}
.small{color:#666;font-size:13px;}
.badge{
  display:inline-block;padding:2px 10px;border-radius:999px;
  border:1px solid rgba(0,0,0,0.08);background:rgba(0,0,0,0.03);
  font-size:12px;margin-right:8px;margin-bottom:6px;
}
</style>
""",
    unsafe_allow_html=True,
)

def _norm(s: str) -> str:
    return (s or "").strip()

def sprints_ready() -> bool:
    sps = get_sprints() or []
    return isinstance(sps, list) and len(sps) >= 36

def ensure_current_cycle():
    if "current_cycle_no" not in st.session_state:
        st.session_state["current_cycle_no"] = 1
    try:
        st.session_state["current_cycle_no"] = int(st.session_state["current_cycle_no"])
    except Exception:
        st.session_state["current_cycle_no"] = 1
    if st.session_state["current_cycle_no"] < 1:
        st.session_state["current_cycle_no"] = 1
    if st.session_state["current_cycle_no"] > 36:
        st.session_state["current_cycle_no"] = 36

ensure_current_cycle()

st.title(TT("② 36×10：自我提升计划（10天行动周期）", "② 36×10: Growth Plan (10-day cycles)"))
st.caption(
    TT(
        "流程：先生成 36 个周期 → 编辑周期主题/交付物 → 添加任务并勾选完成 → 去④导出。",
        "Flow: Generate 36 cycles → Edit theme/deliverables → Add tasks & mark done → Export in page ④.",
    )
)

# -----------------------
# A | 生成/重建
# -----------------------
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader(TT("A｜生成/重建 36×10 周期", "A | Generate / Rebuild 36×10"))

if not sprints_ready():
    st.warning(
        TT("你还没有生成 36×10 周期。请选择开始日期并生成。", "No cycles yet. Pick a start date and generate.")
    )
else:
    st.info(
        TT("已生成 36×10 周期。如需重新开始，可重建（会清空旧周期主题与任务）。",
           "Cycles generated. You can rebuild (will clear existing themes & tasks).")
    )

start = st.date_input(TT("请选择开始日期", "Pick a start date"), value=date.today(), key="gp_start_date")

col1, col2 = st.columns(2)
with col1:
    if st.button(TT("🚀 生成/重建 36×10（会清空旧周期与任务）", "🚀 Generate/Rebuild 36×10 (clears old data)"),
                 use_container_width=True, key="gp_rebuild_btn"):
        regenerate_sprints(start)
        st.success(TT("已生成 36 个周期 ✅", "Generated 36 cycles ✅"))
        st.session_state["current_cycle_no"] = 1
        st.rerun()

with col2:
    st.markdown('<div class="small">', unsafe_allow_html=True)
    st.write(TT("提示：生成后，你可以从年度挖掘或 CARE 一键分配任务到某个周期。",
                "Tip: After generating, you can assign tasks from Annual Planning or CARE into cycles."))
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

if not sprints_ready():
    st.stop()

# -----------------------
# B | Overview
# -----------------------
sps = get_sprints()
done_cnt = 0
task_cnt = 0
for sp in sps:
    tasks = sp.get("tasks", []) or []
    task_cnt += len(tasks)
    done_cnt += sum(1 for t in tasks if bool(t.get("done", False)))

st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader(TT("B｜总览", "B | Overview"))
st.markdown(
    f'<span class="badge">{TT("周期数","Cycles")}: 36</span>'
    f'<span class="badge">{TT("任务","Tasks")}: {task_cnt}</span>'
    f'<span class="badge">{TT("完成","Done")}: {done_cnt}</span>',
    unsafe_allow_html=True
)

# 快速跳转
jump_no = st.number_input(TT("跳转到周期编号（1-36）", "Jump to cycle (1-36)"),
                          min_value=1, max_value=36, value=int(st.session_state["current_cycle_no"]),
                          key="jump_cycle_no")
if st.button(TT("跳转", "Go"), key="jump_go"):
    st.session_state["current_cycle_no"] = int(jump_no)
    st.rerun()

st.markdown("</div>", unsafe_allow_html=True)

# -----------------------
# C | 单周期详情
# -----------------------
ensure_current_cycle()
no = int(st.session_state["current_cycle_no"])
sp = get_sprint_by_no(no)

st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader(TT(f"C｜周期 {no} 详情", f"C | Cycle {no} Details"))

if not sp:
    st.error(TT("未找到该周期，请先重建 36×10。", "Cycle not found. Please rebuild 36×10."))
    st.stop()

st.caption(TT(f"{sp.get('start_date','')} ~ {sp.get('end_date','')}",
              f"{sp.get('start_date','')} ~ {sp.get('end_date','')}"))

# 上一个/下一个
cnav1, cnav2, cnav3 = st.columns([1, 2, 1])
with cnav1:
    if st.button(TT("← 上一个", "← Prev"), use_container_width=True, key="prev_btn"):
        st.session_state["current_cycle_no"] = max(1, no - 1)
        st.rerun()
with cnav3:
    if st.button(TT("下一个 →", "Next →"), use_container_width=True, key="next_btn"):
        st.session_state["current_cycle_no"] = min(36, no + 1)
        st.rerun()

# 编辑主题/目标/复盘
with st.form(f"cycle_text_form_{no}"):
    theme = st.text_input(TT("主题（Theme）", "Theme"), value=sp.get("theme", ""), key=f"theme_{no}")
    objective = st.text_area(TT("交付物/目标（Objective）", "Objective / Deliverables"),
                             value=sp.get("objective", ""), height=110, key=f"obj_{no}")
    review = st.text_area(TT("复盘（Review）", "Review"),
                          value=sp.get("review", ""), height=110, key=f"rev_{no}")
    saved = st.form_submit_button(TT("💾 保存本周期内容", "💾 Save cycle"))
if saved:
    update_sprint_text(no, theme, objective, review)
    st.success(TT("已保存 ✅", "Saved ✅"))
    st.rerun()

st.divider()

# 任务清单
st.subheader(TT("任务清单", "Tasks"))

tasks = list_tasks_for_sprint(no) or []
if not tasks:
    st.info(TT("暂无任务。你可以：1）从年度挖掘/CARE 分配；2）在这里新增任务。", "No tasks yet. Assign from Annual/CARE or add below."))
else:
    for t in tasks:
        tid = t.get("id", "")
        title = t.get("title", "")
        done = bool(t.get("done", False))
        src = (t.get("source_care_id", "") or "").strip()

        left, right = st.columns([4, 2])
        with left:
            new_done = st.checkbox(title, value=done, key=f"done_{tid}")
            if new_done != done:
                toggle_task_done(tid, new_done)
                st.rerun()
            if src:
                st.markdown(f'<span class="badge">from CARE</span><span class="badge">care_id={src}</span>', unsafe_allow_html=True)

        with right:
            ev = st.text_input(TT("证据/备注", "Evidence/Notes"),
                               value=t.get("evidence", ""), key=f"ev_{tid}")
            if ev != (t.get("evidence","") or ""):
                update_task_evidence(tid, ev)

    st.caption(TT("提示：勾选完成会即时保存；证据/备注输入后自动保存。", "Tip: done status saves instantly; notes auto-save."))

st.divider()

# 新增任务
with st.form(f"add_task_form_{no}"):
    new_title = st.text_input(TT("新增任务（建议一句话动词开头）", "New task (verb-first)"), key=f"new_task_{no}")
    add_btn = st.form_submit_button(TT("➕ 添加到本周期", "➕ Add to this cycle"))
if add_btn:
    if not _norm(new_title):
        st.warning(TT("请输入任务标题。", "Please enter a task title."))
    else:
        add_task_to_sprint_unique(no, _norm(new_title), source_care_id="")
        st.success(TT("已添加 ✅", "Added ✅"))
        st.rerun()

st.markdown("</div>", unsafe_allow_html=True)

st.info(
    TT("下一步：去「④ 导出中心」导出海报与 6×6 Excel；也建议在「备份」下载 JSON 以防浏览器会话丢失。",
       "Next: Export poster & 6×6 Excel in page ④; also download JSON backup to avoid session loss.")
)
