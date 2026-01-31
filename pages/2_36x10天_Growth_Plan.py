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

def _norm(s: str) -> str:
    return (s or "").strip()

def sprints_ready() -> bool:
    sps = get_sprints() or []
    return isinstance(sps, list) and len(sps) >= 36

def ensure_state():
    if "current_cycle_no" not in st.session_state:
        st.session_state["current_cycle_no"] = 1
    if "show_cycle_detail" not in st.session_state:
        st.session_state["show_cycle_detail"] = False
    if "jump_cycle_no_state" not in st.session_state:
        st.session_state["jump_cycle_no_state"] = int(st.session_state["current_cycle_no"])

    # clamp
    try:
        st.session_state["current_cycle_no"] = int(st.session_state["current_cycle_no"])
    except Exception:
        st.session_state["current_cycle_no"] = 1
    st.session_state["current_cycle_no"] = max(1, min(36, st.session_state["current_cycle_no"]))

    try:
        st.session_state["jump_cycle_no_state"] = int(st.session_state["jump_cycle_no_state"])
    except Exception:
        st.session_state["jump_cycle_no_state"] = int(st.session_state["current_cycle_no"])
    st.session_state["jump_cycle_no_state"] = max(1, min(36, st.session_state["jump_cycle_no_state"]))

ensure_state()

# -----------------------
# 样式
# -----------------------
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

.cycle-card{
  border:1px solid rgba(0,0,0,0.06);
  border-radius:14px;
  padding:12px 12px;
  background:#fff;
  box-shadow:0 8px 18px rgba(0,0,0,0.03);
  min-height: 138px;
}
.cycle-top{
  display:flex; align-items:center; justify-content:space-between;
  font-weight: 850; font-size: 14px;
}
.cycle-sub{ color:#666; font-size: 12px; margin-top: 4px; }
.cycle-theme{ font-size: 13px; margin-top: 8px; font-weight: 700; }
.cycle-theme span{ font-weight: 500; color:#444; }
.cycle-progress{ margin-top: 8px; font-size: 12px; color:#444; }
.hr-soft{ margin: 10px 0 12px 0; border-top: 1px solid rgba(0,0,0,0.06); }

.anchor {
  display:block;
  position:relative;
  top:-72px;
  visibility:hidden;
}
</style>
""",
    unsafe_allow_html=True,
)

def _progress_for_sp(sp: dict) -> tuple[int, int]:
    tasks = sp.get("tasks", []) or []
    total = len(tasks)
    done = sum(1 for t in tasks if bool(t.get("done", False)))
    return done, total

def _ratio(done: int, total: int) -> float:
    if total <= 0:
        return 0.0
    return max(0.0, min(1.0, done / total))

def _theme_preview(sp: dict) -> str:
    t = _norm(sp.get("theme", ""))
    if not t:
        return TT("未填写主题", "No theme yet")
    return t[:22] + ("…" if len(t) > 22 else "")

def open_cycle(no: int):
    """✅ 不要写 widget 的 key（jump_cycle_no），只写纯状态 key"""
    st.session_state["current_cycle_no"] = int(no)
    st.session_state["show_cycle_detail"] = True
    st.session_state["jump_cycle_no_state"] = int(no)  # 纯状态，不是 widget key

# -----------------------
# 页面头
# -----------------------
st.title(TT("② 36×10：自我提升计划（10天行动周期）", "② 36×10: Growth Plan (10-day cycles)"))
st.caption(
    TT(
        "流程：先生成 36 个周期 → 编辑主题/交付物 → 添加任务并勾选完成 → 去④导出。",
        "Flow: Generate 36 cycles → Edit theme/deliverables → Add tasks & mark done → Export in page ④.",
    )
)

# -----------------------
# A | 生成/重建
# -----------------------
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader(TT("A｜生成/重建 36×10 周期", "A | Generate / Rebuild 36×10"))

if not sprints_ready():
    st.warning(TT("你还没有生成 36×10 周期。请选择开始日期并生成。", "No cycles yet. Pick a start date and generate."))
else:
    st.info(
        TT("已生成 36×10 周期。如需重新开始，可重建（会清空旧周期主题与任务）。",
           "Cycles generated. You can rebuild (will clear existing themes & tasks).")
    )

start = st.date_input(TT("请选择开始日期", "Pick a start date"), value=date.today(), key="gp_start_date")

if st.button(
    TT("🚀 生成/重建 36×10（会清空旧周期与任务）", "🚀 Generate/Rebuild 36×10 (clears old data)"),
    use_container_width=True,
    key="gp_rebuild_btn",
):
    regenerate_sprints(start)
    st.success(TT("已生成 36 个周期 ✅", "Generated 36 cycles ✅"))
    st.session_state["current_cycle_no"] = 1
    st.session_state["jump_cycle_no_state"] = 1
    st.session_state["show_cycle_detail"] = False
    st.rerun()

st.markdown("</div>", unsafe_allow_html=True)

if not sprints_ready():
    st.stop()

sps = get_sprints()

# -----------------------
# B | 总览 + 6×6 小卡片（带进度条）
# -----------------------
task_cnt = 0
done_cnt = 0
for sp in sps:
    d, t = _progress_for_sp(sp)
    done_cnt += d
    task_cnt += t

st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader(TT("B｜总览（小卡片 6×6）", "B | Overview (6×6 cards)"))

st.markdown(
    f'<span class="badge">{TT("周期数","Cycles")}: 36</span>'
    f'<span class="badge">{TT("任务","Tasks")}: {task_cnt}</span>'
    f'<span class="badge">{TT("完成","Done")}: {done_cnt}</span>',
    unsafe_allow_html=True
)

# ✅ number_input 的 key 用 jump_cycle_no（widget key），它的值来自 jump_cycle_no_state（纯状态）
jump_no = st.number_input(
    TT("跳转到周期编号（1-36）", "Jump to cycle (1-36)"),
    min_value=1, max_value=36,
    value=int(st.session_state.get("jump_cycle_no_state", 1)),
    key="jump_cycle_no",  # widget key
)
if st.button(TT("跳转", "Go"), key="jump_go"):
    open_cycle(int(jump_no))
    st.rerun()

st.markdown('<div class="hr-soft"></div>', unsafe_allow_html=True)

# 6×6
for row in range(6):
    cols = st.columns(6, gap="small")
    for col_i in range(6):
        idx = row * 6 + col_i
        sp = sps[idx]
        no = int(sp.get("sprint_no", idx + 1))
        start_s = sp.get("start_date", "")
        end_s = sp.get("end_date", "")
        theme = _theme_preview(sp)

        d, t = _progress_for_sp(sp)
        ratio = _ratio(d, t)
        pct = int(round(ratio * 100))

        is_active = (no == int(st.session_state.get("current_cycle_no", 1)))
        header_right = TT("当前", "Current") if is_active else ""

        with cols[col_i]:
            st.markdown(
                f"""
<div class="cycle-card">
  <div class="cycle-top">
    <div>{TT("周期","Cycle")} {no}</div>
    <div style="color:#777;font-weight:700;font-size:12px;">{header_right}</div>
  </div>
  <div class="cycle-sub">{start_s} ~ {end_s}</div>
  <div class="cycle-theme">{TT("主题","Theme")}: <span>{theme}</span></div>
  <div class="cycle-progress">{TT("进度","Progress")}: {d}/{t} · {pct}%</div>
</div>
""",
                unsafe_allow_html=True,
            )

            st.progress(ratio)

            if st.button(TT("查看", "Open"), key=f"open_cycle_{no}", use_container_width=True):
                open_cycle(no)
                st.rerun()

st.markdown("</div>", unsafe_allow_html=True)

# -----------------------
# C | 单周期详情（只有点击“查看/跳转”后才出现）
# -----------------------
if not st.session_state.get("show_cycle_detail", False):
    st.info(
        TT("点击任意卡片的「查看」后，会在下方打开该周期详情。", 
           "Click “Open” on any card to show cycle details below.")
    )
    st.stop()

st.markdown('<span class="anchor" id="cycle_detail"></span>', unsafe_allow_html=True)

no = int(st.session_state.get("current_cycle_no", 1))
sp = get_sprint_by_no(no)

st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader(TT(f"C｜周期 {no} 详情", f"C | Cycle {no} Details"))

if not sp:
    st.error(TT("未找到该周期，请先重建 36×10。", "Cycle not found. Please rebuild 36×10."))
    st.stop()

start_s = sp.get("start_date", "")
end_s = sp.get("end_date", "")
st.caption(TT(f"{start_s} ~ {end_s}", f"{start_s} ~ {end_s}"))

d, t = _progress_for_sp(sp)
ratio = _ratio(d, t)
st.markdown(
    f'<span class="badge">{TT("任务","Tasks")}: {t}</span>'
    f'<span class="badge">{TT("完成","Done")}: {d}</span>'
    f'<span class="badge">{TT("完成率","Rate")}: {int(round(ratio*100))}%</span>',
    unsafe_allow_html=True
)
st.progress(ratio)

cnav1, cnav2, cnav3 = st.columns([1, 2, 1])
with cnav1:
    if st.button(TT("← 上一个", "← Prev"), use_container_width=True, key="prev_btn"):
        open_cycle(max(1, no - 1))
        st.rerun()
with cnav3:
    if st.button(TT("下一个 →", "Next →"), use_container_width=True, key="next_btn"):
        open_cycle(min(36, no + 1))
        st.rerun()

with st.form(f"cycle_text_form_{no}"):
    theme = st.text_input(TT("主题（Theme）", "Theme"), value=sp.get("theme", ""), key=f"theme_{no}")
    objective = st.text_area(
        TT("交付物/目标（Objective）", "Objective / Deliverables"),
        value=sp.get("objective", ""), height=110, key=f"obj_{no}"
    )
    review = st.text_area(
        TT("复盘（Review）", "Review"),
        value=sp.get("review", ""), height=110, key=f"rev_{no}"
    )
    saved = st.form_submit_button(TT("💾 保存本周期内容", "💾 Save cycle"))
if saved:
    update_sprint_text(no, theme, objective, review)
    st.success(TT("已保存 ✅", "Saved ✅"))
    st.rerun()

st.divider()

st.subheader(TT("任务清单", "Tasks"))
tasks = list_tasks_for_sprint(no) or []

if not tasks:
    st.info(TT("暂无任务。你可以：1）从年度挖掘/CARE 分配；2）在这里新增任务。", "No tasks yet. Assign from Annual/CARE or add below."))
else:
    for tsk in tasks:
        tid = tsk.get("id", "")
        title = tsk.get("title", "")
        done = bool(tsk.get("done", False))
        src = _norm(tsk.get("source_care_id", ""))

        left, right = st.columns([4, 2])
        with left:
            new_done = st.checkbox(title, value=done, key=f"done_{tid}")
            if new_done != done:
                toggle_task_done(tid, new_done)
                st.rerun()
            if src:
                st.markdown(
                    f'<span class="badge">from CARE</span><span class="badge">care_id={src}</span>',
                    unsafe_allow_html=True
                )
        with right:
            ev = st.text_input(TT("证据/备注", "Evidence/Notes"),
                               value=tsk.get("evidence", ""), key=f"ev_{tid}")
            if ev != (tsk.get("evidence","") or ""):
                update_task_evidence(tid, ev)

st.divider()

with st.form(f"add_task_form_{no}"):
    new_title = st.text_input(
        TT("新增任务（建议一句话动词开头）", "New task (verb-first)"),
        key=f"new_task_{no}"
    )
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
    TT(
        "提示：内测版数据保存在浏览器会话中。建议在「备份」下载 JSON，或使用完马上导出海报/Excel，以防会话丢失。",
        "Tip (Beta): Data is stored in your browser session. Download JSON backup or export poster/Excel after use."
    )
)
