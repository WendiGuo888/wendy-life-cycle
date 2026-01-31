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

# -----------------------
# 路由：用 query param ?cycle=xx 做“进入详情页”
# -----------------------
def get_cycle_from_query() -> int | None:
    qp = st.query_params
    raw = qp.get("cycle", None)
    if raw is None or raw == "":
        return None
    try:
        n = int(raw)
        if 1 <= n <= 36:
            return n
    except Exception:
        return None
    return None

def goto_cycle(n: int):
    st.query_params["cycle"] = str(int(n))
    st.rerun()

def goto_overview():
    # 清掉 cycle 参数 -> 回到总览页
    if "cycle" in st.query_params:
        del st.query_params["cycle"]
    st.rerun()

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
</style>
""",
    unsafe_allow_html=True,
)

# -----------------------
# 页面头
# -----------------------
st.title(TT("② 36×10：自我提升计划（10天行动周期）", "② 36×10: Growth Plan (10-day cycles)"))
st.caption(
    TT(
        "体验：总览只看 6×6 卡片；点击「查看」进入周期详情与任务清单。",
        "Experience: Overview shows only 6×6 cards. Click “Open” to enter cycle details & tasks.",
    )
)

# -----------------------
# A | 生成/重建（总览页、详情页都需要）
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
    goto_overview()

st.markdown("</div>", unsafe_allow_html=True)

if not sprints_ready():
    st.stop()

sps = get_sprints()
cycle_q = get_cycle_from_query()

# =====================================================================
# ✅ 页面分支：
# - 没有 ?cycle=xx -> 只显示 B 总览
# - 有 ?cycle=xx -> 只显示 C 详情
# =====================================================================

# -----------------------
# B | 总览（只显示卡片）
# -----------------------
if cycle_q is None:
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

    # 可选：跳转到某个周期
    jump_no = st.number_input(
        TT("跳转到周期编号（1-36）", "Jump to cycle (1-36)"),
        min_value=1, max_value=36, value=1,
        key="jump_cycle_input",
    )
    if st.button(TT("跳转到详情", "Go to details"), key="jump_go_btn"):
        goto_cycle(int(jump_no))

    st.markdown('<div class="hr-soft"></div>', unsafe_allow_html=True)

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

            with cols[col_i]:
                st.markdown(
                    f"""
<div class="cycle-card">
  <div class="cycle-top">
    <div>{TT("周期","Cycle")} {no}</div>
    <div style="color:#777;font-weight:700;font-size:12px;"></div>
  </div>
  <div class="cycle-sub">{start_s} ~ {end_s}</div>
  <div class="cycle-theme">{TT("主题","Theme")}: <span>{theme}</span></div>
  <div class="cycle-progress">{TT("进度","Progress")}: {d}/{t} · {pct}%</div>
</div>
""",
                    unsafe_allow_html=True,
                )
                st.progress(ratio)

                # ✅ 真正“进入详情页”
                if st.button(TT("查看", "Open"), key=f"open_{no}", use_container_width=True):
                    goto_cycle(no)

    st.markdown("</div>", unsafe_allow_html=True)

    st.info(
        TT(
            "提示：点击卡片「查看」进入该周期详情与任务清单。",
            "Tip: Click “Open” on a card to enter details & tasks."
        )
    )
    st.stop()

# -----------------------
# C | 周期详情（只在 ?cycle=xx 时显示）
# -----------------------
no = int(cycle_q)
sp = get_sprint_by_no(no)

st.markdown('<div class="card">', unsafe_allow_html=True)

topL, topR = st.columns([3, 1])
with topL:
    st.subheader(TT(f"C｜周期 {no} 详情", f"C | Cycle {no} Details"))
with topR:
    if st.button(TT("← 返回总览", "← Back"), use_container_width=True, key="back_overview_btn"):
        goto_overview()

if not sp:
    st.error(TT("未找到该周期，请先重建 36×10。", "Cycle not found. Please rebuild 36×10."))
    st.stop()

start_s = sp.get("start_date", "")
end_s = sp.get("end_date", "")
st.caption(TT(f"{start_s} ~ {end_s}", f"{start_s} ~ {end_s}"))

# 顶部导航
nav1, nav2, nav3 = st.columns([1, 2, 1])
with nav1:
    if st.button(TT("← 上一个", "← Prev"), use_container_width=True, key="prev_btn"):
        goto_cycle(max(1, no - 1))
with nav3:
    if st.button(TT("下一个 →", "Next →"), use_container_width=True, key="next_btn"):
        goto_cycle(min(36, no + 1))

# 进度
tasks = list_tasks_for_sprint(no) or []
total = len(tasks)
done = sum(1 for t in tasks if bool(t.get("done", False)))
ratio = _ratio(done, total)

st.markdown(
    f'<span class="badge">{TT("任务","Tasks")}: {total}</span>'
    f'<span class="badge">{TT("完成","Done")}: {done}</span>'
    f'<span class="badge">{TT("完成率","Rate")}: {int(round(ratio*100))}%</span>',
    unsafe_allow_html=True
)
st.progress(ratio)

# 周期内容编辑
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

# 任务清单
st.subheader(TT("任务清单", "Tasks"))

if not tasks:
    st.info(TT("暂无任务。你可以：1）从年度挖掘/CARE 分配；2）在这里新增任务。", "No tasks yet. Assign from Annual/CARE or add below."))
else:
    for tsk in tasks:
        tid = tsk.get("id", "")
        title = tsk.get("title", "")
        done_now = bool(tsk.get("done", False))
        src = _norm(tsk.get("source_care_id", ""))

        left, right = st.columns([4, 2])
        with left:
            new_done = st.checkbox(title, value=done_now, key=f"done_{tid}")
            if new_done != done_now:
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
            if ev != (tsk.get("evidence", "") or ""):
                update_task_evidence(tid, ev)

st.divider()

# 新增任务
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
