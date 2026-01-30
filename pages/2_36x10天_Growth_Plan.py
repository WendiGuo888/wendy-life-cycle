# pages/2_36x10天_Growth_Plan.py
# -*- coding: utf-8 -*-

from datetime import date
import streamlit as st

from i18n import init_i18n, lang_selector

# ✅ Session-only 数据层（不会串数据）
from store import (
    regenerate_sprints,
    get_sprints,
    get_sprint_by_no,
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
    page_title=("② 36×10 自我提升计划" if lang == "zh" else "② 36×10 Growth Plan"),
    page_icon="📆",
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
# 样式（扁平化卡片）
# -----------------------
st.markdown(
    """
<style>
.block-container { padding-top: 1.2rem; padding-bottom: 2.0rem; max-width: 1180px; }
.card {
    background: #fff;
    border-radius: 16px;
    padding: 14px 14px;
    margin-bottom: 12px;
    border: 1px solid rgba(0,0,0,0.06);
    box-shadow: 0 10px 24px rgba(0,0,0,0.04);
}
.small { color:#666; font-size: 13px; }
.kpi { font-size: 12px; color:#666; }
</style>
""",
    unsafe_allow_html=True,
)

# -----------------------
# 页面标题
# -----------------------
st.title(TT("② 36×10：自我提升计划（10天一个周期）", "② 36×10 Growth Plan (10-day cycles)"))
st.caption(
    TT(
        "你可以生成 36 个「10天周期」，每个周期填写：主题、交付物（Objective）、复盘、任务清单。",
        "Generate 36 '10-day cycles'. Each cycle has: Theme, Deliverables (Objective), Review, and Tasks.",
    )
)

# -----------------------
# 状态：当前查看的周期
# -----------------------
if "current_cycle_no" not in st.session_state:
    st.session_state.current_cycle_no = None


# -----------------------
# 周期生成（首次使用）
# -----------------------
with st.expander(TT("首次使用：生成 36 个 10天周期（建议只做一次）", "First time: Generate 36 cycles (recommended once)"), expanded=False):
    start = st.date_input(TT("请选择开始日期", "Pick a start date"), value=date.today())
    if st.button(TT("🚀 生成/重建 36×10（会清空旧周期与任务）", "🚀 Generate/Rebuild 36×10 (will clear existing cycles & tasks)"), use_container_width=True):
        regenerate_sprints(start)
        st.success(TT("已生成 36 个周期 ✅", "Generated 36 cycles ✅"))
        st.session_state.current_cycle_no = 1
        st.rerun()

cycles = get_sprints()
if not cycles:
    st.info(TT("还没有周期。请先在上面生成 36×10。", "No cycles yet. Please generate 36×10 first."))
    st.stop()


# -----------------------
# 详情视图
# -----------------------
def render_cycle_detail(cycle_no: int):
    sp = get_sprint_by_no(cycle_no)
    if not sp:
        st.error(TT("找不到该周期", "Cycle not found"))
        return

    # sp 是 dict：start_date/end_date 是 iso str
    start_date = sp.get("start_date", "")
    end_date = sp.get("end_date", "")

    st.markdown(f"## {TT('第', 'Cycle ')}{cycle_no}{TT('个10天周期', '')}")
    st.write(TT(f"日期：{start_date} ~ {end_date}", f"Dates: {start_date} ~ {end_date}"))

    # 编辑区（主题/交付物/复盘）
    with st.form(f"cycle_edit_{cycle_no}"):
        theme = st.text_input(TT("主题（Theme）", "Theme"), value=sp.get("theme", ""))
        objective = st.text_area(
            TT("交付物 / 目标（Objective）", "Deliverables / Objective"),
            value=sp.get("objective", ""),
            height=120,
            placeholder=TT("例如：完成一份可发布的 Life Circle 海报 + 计划表", "e.g. finish a publishable Life Circle poster + plan sheet"),
        )
        review = st.text_area(
            TT("复盘（Review）", "Review"),
            value=sp.get("review", ""),
            height=120,
            placeholder=TT("记录：做得好/需要改进/下一周期怎么调整", "Write: what worked / what to improve / how to adjust next cycle"),
        )
        ok = st.form_submit_button(TT("💾 保存本周期内容", "💾 Save cycle"), use_container_width=True)

    if ok:
        update_sprint_text(cycle_no, theme, objective, review)
        st.success(TT("已保存 ✅", "Saved ✅"))
        st.rerun()

    st.markdown("---")
    st.subheader(TT("任务清单", "Task List"))

    tasks = list_tasks_for_sprint(cycle_no)

    # 新增任务
    with st.form(f"add_task_{cycle_no}"):
        new_title = st.text_area(
            TT("新增任务（支持多行：每行一个）", "Add tasks (multi-line: one per line)"),
            value="",
            height=90,
            placeholder=TT("例如：\n- 完成海报英文版\n- 录制30秒演示视频", "e.g.\n- Finish English poster\n- Record a 30s demo video"),
        )
        add = st.form_submit_button(TT("➕ 添加任务", "➕ Add tasks"), use_container_width=True)

    if add:
        if new_title.strip():
            for line in new_title.splitlines():
                line = line.strip().lstrip("-").strip()
                if line:
                    add_task_to_sprint_unique(cycle_no, line, source_care_id=None)
            st.success(TT("已添加 ✅", "Added ✅"))
            st.rerun()

    if not tasks:
        st.info(TT("该周期还没有任务。你可以从年度挖掘分配，或在这里新增。", "No tasks yet. Assign from Annual Planning or add here."))
        return

    # 任务展示（卡片）
    done_cnt = sum(1 for t in tasks if t.get("done"))
    st.caption(TT(f"完成进度：{done_cnt}/{len(tasks)}", f"Progress: {done_cnt}/{len(tasks)}"))

    for t in tasks:
        tid = t.get("id")
        title = t.get("title", "")
        done = bool(t.get("done", False))
        evidence = t.get("evidence", "") or ""

        st.markdown('<div class="card">', unsafe_allow_html=True)
        c1, c2 = st.columns([1, 4], vertical_alignment="top")

        with c1:
            checked = st.checkbox(TT("完成", "Done"), value=done, key=f"done_{tid}")
            if checked != done:
                toggle_task_done(tid, checked)
                st.rerun()

        with c2:
            st.write(f"**{title}**")
            ev = st.text_area(
                TT("证据/记录（可选）", "Evidence/Notes (optional)"),
                value=evidence,
                height=70,
                key=f"ev_{tid}",
            )
            if ev != evidence:
                update_task_evidence(tid, ev)

        st.markdown("</div>", unsafe_allow_html=True)


# -----------------------
# 顶部导航：返回/上一周期/下一周期
# -----------------------
top = st.columns([1, 2, 1])
with top[0]:
    if st.session_state.current_cycle_no is not None:
        if st.button(TT("⬅ 返回总览", "⬅ Back to overview"), use_container_width=True):
            st.session_state.current_cycle_no = None
            st.rerun()

with top[2]:
    if st.session_state.current_cycle_no is not None:
        cur = int(st.session_state.current_cycle_no)
        prev_ok = st.button(TT("← 上一个", "← Prev"), use_container_width=True)
        next_ok = st.button(TT("下一个 →", "Next →"), use_container_width=True)
        if prev_ok:
            st.session_state.current_cycle_no = max(1, cur - 1)
            st.rerun()
        if next_ok:
            st.session_state.current_cycle_no = min(36, cur + 1)
            st.rerun()


# -----------------------
# 渲染：总览 or 详情
# -----------------------
if st.session_state.current_cycle_no is not None:
    render_cycle_detail(int(st.session_state.current_cycle_no))
    st.stop()

st.markdown("## " + TT("36 个 10天周期总览（点击进入）", "36 cycles overview (click to open)"))
st.caption(
    TT(
        "提示：你在「① 年度挖掘」里一键分配后，这里每个周期会自动出现任务。",
        "Tip: After auto-assigning from page ①, tasks will appear here automatically.",
    )
)

cols = st.columns(3)
for idx, sp in enumerate(cycles):
    with cols[idx % 3]:
        cycle_no = sp.get("sprint_no")
        start_date = sp.get("start_date", "")
        end_date = sp.get("end_date", "")
        theme = (sp.get("theme", "") or "").strip()
        objective = (sp.get("objective", "") or "").strip()

        tasks = list_tasks_for_sprint(cycle_no)
        done_cnt = sum(1 for t in tasks if t.get("done"))
        total_cnt = len(tasks)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.write(f"**{TT('周期', 'Cycle')} {cycle_no}**")
        st.write(f"{start_date} ~ {end_date}")

        if theme:
            st.caption(f"{TT('主题', 'Theme')}：{theme}")
        if objective:
            st.caption(f"{TT('交付物', 'Objective')}：{objective[:60]}{'…' if len(objective) > 60 else ''}")

        st.caption(TT(f"任务：{done_cnt}/{total_cnt} 完成", f"Tasks: {done_cnt}/{total_cnt} done"))

        if st.button(TT("进入编辑", "Open"), key=f"enter_{cycle_no}", use_container_width=True):
            st.session_state.current_cycle_no = cycle_no
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

st.info(
    TT(
        "建议流程：①年度挖掘填写并分配 → ②这里逐个周期写主题/交付物并执行 → ④导出海报 + 6×6 Excel。",
        "Suggested flow: ① Fill & assign → ② Edit each cycle and execute → ④ Export poster + 6×6 Excel.",
    )
)
