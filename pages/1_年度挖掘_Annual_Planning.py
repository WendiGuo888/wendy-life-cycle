# pages/1_年度挖掘.py
# -*- coding: utf-8 -*-

import io
import json
import textwrap
from typing import Dict, List
from datetime import date


import streamlit as st

# ✅ Matplotlib 在 Cloud 上建议用 Agg
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle


from i18n import init_i18n, lang_selector
from store import (
    get_or_create_annual_dig,
    update_annual_dig,
    get_sprints,
    regenerate_sprints,          # ✅ 新增
    add_task_to_sprint_unique,
)

# -----------------------
# ✅ set_page_config 必须在任何 st.xxx 前
# -----------------------
lang = st.session_state.get("lang", "zh")
st.set_page_config(
    page_title=("① 年度挖掘" if lang == "zh" else "① Annual Planning"),
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
</style>
""",
    unsafe_allow_html=True,
)

# -----------------------
# 工具函数
# -----------------------
def safe_load_json(s: str) -> dict:
    try:
        return json.loads(s) if s else {}
    except Exception:
        return {}

def lines_to_list(text: str) -> List[str]:
    out = []
    seen = set()
    for line in (text or "").splitlines():
        x = str(line).strip()
        if not x:
            continue
        if x not in seen:
            out.append(x)
            seen.add(x)
    return out

def dict_to_text(d: Dict[str, List[str]], zh_key: str, en_key: str) -> str:
    arr = d.get(zh_key) or d.get(en_key) or []
    if not isinstance(arr, list):
        arr = []
    return "\n".join([str(x) for x in arr if str(x).strip()])

def build_items_from_quadrants(d: Dict[str, List[str]]) -> List[str]:
    keys = ["学业","事业","成长","身体","study","career","growth","health"]
    out, seen = [], set()
    for k in keys:
        v = d.get(k, [])
        if not isinstance(v, list):
            continue
        for x in v:
            x = str(x).strip()
            if not x:
                continue
            if x not in seen:
                out.append(x)
                seen.add(x)
    return out

def clamp_list(items: List[str], n: int):
    items = [str(x).strip() for x in (items or []) if str(x).strip()]
    if len(items) <= n:
        return items, 0
    return items[:n], len(items) - n

def one_line(s: str, width: int) -> str:
    wrapped = textwrap.wrap(str(s), width=width)
    return wrapped[0] if wrapped else str(s)

def safe_radius(items, base=2.25, scale=0.03):
    n = len([x for x in (items or []) if str(x).strip()])
    return max(base, base + n * scale)

def _pick_intersection_list(intersections: dict, keys: List[str]) -> List[str]:
    for k in keys:
        v = intersections.get(k)
        if isinstance(v, list) and v:
            return v
    v0 = intersections.get(keys[0], [])
    return v0 if isinstance(v0, list) else []

# -----------------------
# ✅ 关键：Cloud 中文字体修复
# -----------------------
def _mpl_font_setup():
    """
    让 Matplotlib 在 Streamlit Cloud 也能显示中文：
    - 尝试从仓库里注册 NotoSansSC-Regular.ttf
    - 再设置 rcParams 的 sans-serif 优先级
    """
    import matplotlib as mpl
    from pathlib import Path
    from matplotlib import font_manager as fm

    # 常见放置位置：仓库根目录 / assets / fonts
    root = Path(__file__).resolve().parents[1]  # .../wendy-life-cycle
    candidates = [
        root / "NotoSansSC-Regular.ttf",
        root / "assets" / "NotoSansSC-Regular.ttf",
        root / "fonts" / "NotoSansSC-Regular.ttf",
        root / "assets" / "fonts" / "NotoSansSC-Regular.ttf",
    ]

    font_name = None
    for p in candidates:
        if p.exists():
            try:
                fm.fontManager.addfont(str(p))
                # 取出字体的 family 名称
                prop = fm.FontProperties(fname=str(p))
                font_name = prop.get_name()
                break
            except Exception:
                pass

    # 设置字体优先级：先用我们注册的 Noto Sans SC
    # 再兜底常见中文字体
    if font_name:
        mpl.rcParams["font.sans-serif"] = [
            font_name, "Noto Sans CJK SC", "Source Han Sans SC",
            "Microsoft YaHei", "SimHei", "Arial Unicode MS", "DejaVu Sans"
        ]
    else:
        mpl.rcParams["font.sans-serif"] = [
            "Noto Sans CJK SC", "Source Han Sans SC",
            "Microsoft YaHei", "SimHei", "Arial Unicode MS", "DejaVu Sans"
        ]

    mpl.rcParams["axes.unicode_minus"] = False


def draw_auto_title(ax, main_title: str, subtitle: str, signature: str, y_top: float, is_english: bool, mode: str):
    if mode == "share":
        main_fs, sub_fs, sig_fs = 26, 16, 12
    else:
        main_fs, sub_fs, sig_fs = 24, 16, 12

    lines = []
    if is_english:
        words = main_title.split(" ")
        cur = ""
        for w in words:
            if len(cur) + len(w) + (1 if cur else 0) <= 18:
                cur = f"{cur} {w}".strip()
            else:
                if cur:
                    lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
        if len(lines) > 2:
            lines = [" ".join(lines[:-1]), lines[-1]]
    else:
        lines = [main_title]

    y = y_top - 0.70
    for line in lines:
        ax.text(0, y, line, ha="center", va="center", fontsize=main_fs, fontweight="bold")
        y -= 0.80
    ax.text(0, y - 0.10, subtitle, ha="center", va="center", fontsize=sub_fs, fontweight="bold")
    ax.text(0, y - 0.80, signature, ha="center", va="center", fontsize=sig_fs, color="#555", alpha=0.60)


def render_life_circle_preview_png(
    name: str,
    dream_items: List[str],
    resp_items: List[str],
    talent_items: List[str],
    intersections: dict,
    mode: str = "full",  # share/full
) -> bytes:
    _mpl_font_setup()
    is_en = st.session_state.get("lang", "zh") == "en"

    blue = "#4DA3FF"
    purple = "#7E57FF"
    green = "#42C77A"

    dpi = 170
    fig = plt.figure(figsize=(10.5, 7.5), dpi=dpi)
    ax = plt.gca()
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_position([0, 0, 1, 1])

    x_min, x_max = -6.6, 6.6
    y_min, y_max = -5.3, 7.6
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)

    Dream_xy = (-1.85, -1.15)
    Talent_xy = (1.85, -1.15)
    Resp_xy = (0.0, 1.65)

    r_dream = max(2.35, safe_radius(dream_items))
    r_talent = max(2.35, safe_radius(talent_items))
    r_resp = max(2.35, safe_radius(resp_items))

    alpha_circle = 0.22 if mode == "share" else 0.26

    # 圈：紫→蓝/绿（让左右圈更显眼）
    ax.add_patch(Circle(Resp_xy, r_resp, color=purple, alpha=alpha_circle, lw=2, zorder=1))
    ax.add_patch(Circle(Dream_xy, r_dream, color=blue, alpha=alpha_circle, lw=2, zorder=2))
    ax.add_patch(Circle(Talent_xy, r_talent, color=green, alpha=alpha_circle, lw=2, zorder=2))

    if is_en:
        title_main = "Find Your 2026 Breakthrough"
        dream_label, talent_label, resp_label = "Dream", "Talent", "Responsibility"
        center_title = "Breakthrough (Center)"
    else:
        title_main = "找到2026年人生突破点"
        dream_label, talent_label, resp_label = "梦想", "天赋", "责任"
        center_title = "三者交汇（突破点）"

    signature = f"{(name or 'YourName')} · 2026 · Life Circle"
    draw_auto_title(ax, title_main, "Life Circle", signature, y_top=y_max, is_english=is_en, mode=mode)

    # 底部标签（梦想/天赋）
    label_fs = 18
    bottom_label_y = Dream_xy[1] - r_dream - 0.55
    ax.text(Dream_xy[0], bottom_label_y, dream_label, ha="center", va="center", fontsize=label_fs, fontweight="bold")
    ax.text(Talent_xy[0], bottom_label_y, talent_label, ha="center", va="center", fontsize=label_fs, fontweight="bold")

    # 责任标签：紫圈右侧（英文竖排）
    resp_y = Resp_xy[1] + 0.10
    ideal_x = Resp_xy[0] + r_resp + 0.55
    if is_en:
        resp_x = min(ideal_x, x_max - 0.35)
        ax.text(resp_x, resp_y, resp_label, ha="center", va="center", fontsize=label_fs, fontweight="bold", rotation=90)
    else:
        resp_x = min(ideal_x, x_max - 1.2)
        ax.text(resp_x, resp_y, resp_label, ha="left", va="center", fontsize=label_fs, fontweight="bold")

    # slogan
    ax.text(0, y_min + 0.20, "Mission → Action → Reality", ha="center", va="center", fontsize=13, color="#666", alpha=0.55)

    # center
    center = intersections.get("center", []) or intersections.get("中心", []) or []
    show_center, more_center = clamp_list(center, 6 if mode == "share" else 10)
    center_lines = [f"• {one_line(x, 18)}" for x in show_center]
    if more_center > 0:
        center_lines.append(f"… {more_center} more" if is_en else f"… 还有 {more_center} 条")
    center_text = center_title + "\n" + ("\n".join(center_lines) if center_lines else ("(empty)" if is_en else "（空）"))

    ax.text(
        0.0, 0.20,
        center_text,
        ha="center", va="center",
        fontsize=13 if mode == "share" else 12,
        fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.55,rounding_size=0.15", facecolor="white", edgecolor="#333", linewidth=1.1, alpha=0.84),
        zorder=6
    )

    # Full：三清单 + 三交集
    if mode == "full":
        def _list_block(title, items, x, y):
            show, more = clamp_list(items, 7)
            lines = [f"• {one_line(s, 18)}" for s in show]
            if more > 0:
                lines.append(f"… {more} more" if is_en else f"… 还有 {more} 条")
            txt = title + "\n" + ("\n".join(lines) if lines else ("(empty)" if is_en else "（空）"))
            ax.text(
                x, y, txt,
                ha="center", va="center",
                fontsize=10,
                bbox=dict(boxstyle="round,pad=0.30,rounding_size=0.12", facecolor="white", edgecolor="#999", linewidth=0.8, alpha=0.55),
                zorder=5
            )

        _list_block("Responsibility List" if is_en else "责任清单", resp_items, Resp_xy[0], Resp_xy[1] + 0.75)
        _list_block("Dream List" if is_en else "梦想清单", dream_items, Dream_xy[0] - 0.25, Dream_xy[1] + 0.15)
        _list_block("Talent List" if is_en else "天赋清单", talent_items, Talent_xy[0] + 0.25, Talent_xy[1] + 0.15)

        resp_dream = _pick_intersection_list(intersections, ["resp_dream", "责任∩梦想", "rd"])
        resp_talent = _pick_intersection_list(intersections, ["resp_talent", "责任∩天赋", "rt"])
        dream_talent = _pick_intersection_list(intersections, ["dream_talent", "梦想∩天赋", "dt"])

        def _fmt_block(title, items, max_n=4):
            show, more = clamp_list(items, max_n)
            lines = [f"• {one_line(x, 14)}" for x in show]
            if more > 0:
                lines.append(f"… {more} more" if is_en else f"… 还有 {more} 条")
            return title + "\n" + ("\n".join(lines) if lines else ("(empty)" if is_en else "（空）"))

        ax.text(
            -3.10, 0.95,
            _fmt_block("Resp ∩ Dream" if is_en else "责任 ∩ 梦想", resp_dream),
            ha="center", va="center",
            fontsize=9,
            bbox=dict(boxstyle="round,pad=0.25", facecolor="white", edgecolor="#AAA", alpha=0.60),
            zorder=7
        )
        ax.text(
            3.10, 0.95,
            _fmt_block("Resp ∩ Talent" if is_en else "责任 ∩ 天赋", resp_talent),
            ha="center", va="center",
            fontsize=9,
            bbox=dict(boxstyle="round,pad=0.25", facecolor="white", edgecolor="#AAA", alpha=0.60),
            zorder=7
        )
        ax.text(
            0.0, -2.75,
            _fmt_block("Dream ∩ Talent" if is_en else "梦想 ∩ 天赋", dream_talent),
            ha="center", va="center",
            fontsize=9,
            bbox=dict(boxstyle="round,pad=0.25", facecolor="white", edgecolor="#AAA", alpha=0.60),
            zorder=7
        )

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=dpi, facecolor="white", bbox_inches="tight")
    b = buf.getvalue()
    buf.close()
    plt.close(fig)
    return b


def ensure_sprints_ready() -> bool:
    sprints = get_sprints()
    return bool(sprints) and len(sprints) >= 36

def assign_list_to_sprints(items: List[str], start_no: int, end_no: int):
    if not items:
        return 0
    n_slots = end_no - start_no + 1
    to_assign = items[:n_slots]
    count = 0
    for i, title in enumerate(to_assign):
        sprint_no = start_no + i
        add_task_to_sprint_unique(sprint_no, title, source_care_id=None)
        count += 1
    return count

def ensure_sprints_ready() -> bool:
    sprints = get_sprints()
    return bool(sprints) and len(sprints) >= 36


# -----------------------
# 读 DB
# -----------------------
dig = get_or_create_annual_dig()
talent = safe_load_json(dig.talent_json)
resp = safe_load_json(dig.responsibility_json)
dream = safe_load_json(dig.dream_json)
inter = safe_load_json(dig.intersections_json)

meta = inter.get("_meta", {}) if isinstance(inter.get("_meta", {}), dict) else {}
default_name = (meta.get("name", "") or "").strip()


# -----------------------
# 页面
# -----------------------
st.title(TT("① 年度挖掘：四象限 + 交集（生命之轮）", "① Annual Planning: Quadrants + Intersections (Life Circle)"))
st.caption(
    TT(
        "每个输入框支持多条：每行一条。保存后，导出中心会生成海报与 6×6 Excel。",
        "Each box supports multi-line lists (one item per line). After saving, Export Hub can generate poster + 6×6 Excel.",
    )
)

# A 基本信息
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader(TT("A｜基本信息", "A | Basic Info"))
name = st.text_input(TT("你的名字（用于海报署名）", "Your name (for poster signature)"), value=default_name, key="annual_name")
st.markdown("</div>", unsafe_allow_html=True)

# B 四象限
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader(TT("B｜四象限（多条清单）", "B | Quadrants (multi-line lists)"))
tabs = st.tabs([TT("天赋", "Talent"), TT("责任", "Responsibility"), TT("梦想", "Dream")])

quad_defs = [
    (TT("学业", "Study"), "学业", "study"),
    (TT("事业", "Career"), "事业", "career"),
    (TT("成长", "Growth"), "成长", "growth"),
    (TT("身体", "Health"), "身体", "health"),
]

def render_quadrants(store_dict: dict, key_prefix: str) -> dict:
    """✅ 关键：给每个 text_area 稳定 key，避免 DuplicateElementId"""
    updated = dict(store_dict) if isinstance(store_dict, dict) else {}
    c1, c2 = st.columns(2)

    with c1:
        label, zh_k, en_k = quad_defs[0]
        txt = st.text_area(label, value=dict_to_text(updated, zh_k, en_k), height=110, key=f"{key_prefix}_{en_k}_1")
        arr = lines_to_list(txt)
        updated[zh_k] = arr
        updated[en_k] = arr

        label, zh_k, en_k = quad_defs[1]
        txt = st.text_area(label, value=dict_to_text(updated, zh_k, en_k), height=110, key=f"{key_prefix}_{en_k}_2")
        arr = lines_to_list(txt)
        updated[zh_k] = arr
        updated[en_k] = arr

    with c2:
        label, zh_k, en_k = quad_defs[2]
        txt = st.text_area(label, value=dict_to_text(updated, zh_k, en_k), height=110, key=f"{key_prefix}_{en_k}_3")
        arr = lines_to_list(txt)
        updated[zh_k] = arr
        updated[en_k] = arr

        label, zh_k, en_k = quad_defs[3]
        txt = st.text_area(label, value=dict_to_text(updated, zh_k, en_k), height=110, key=f"{key_prefix}_{en_k}_4")
        arr = lines_to_list(txt)
        updated[zh_k] = arr
        updated[en_k] = arr

    return updated

with tabs[0]:
    st.caption(TT("把你拥有的能力/优势拆成四象限。", "Break down your talents into 4 quadrants."))
    talent = render_quadrants(talent, key_prefix="talent")

with tabs[1]:
    st.caption(TT("把你今年必须承担/必须完成的责任拆成四象限。", "Break down your responsibilities into 4 quadrants."))
    resp = render_quadrants(resp, key_prefix="resp")

with tabs[2]:
    st.caption(TT("把你想实现的愿景/梦想拆成四象限。", "Break down your dreams into 4 quadrants."))
    dream = render_quadrants(dream, key_prefix="dream")

st.markdown("</div>", unsafe_allow_html=True)

# C 交集
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader(TT("C｜突破点与交集清单", "C | Breakthrough Lists (Intersections)"))
st.caption(
    TT(
        "中心交汇 + 三个两两交集（每行一条），会出现在导出海报里。",
        "Center + three pairwise intersections (one per line), will be shown on poster.",
    )
)

center_default = "\n".join(inter.get("center", inter.get("中心", [])) or [])
rd_default = "\n".join(inter.get("resp_dream", inter.get("责任∩梦想", inter.get("rd", []))) or [])
rt_default = "\n".join(inter.get("resp_talent", inter.get("责任∩天赋", inter.get("rt", []))) or [])
dt_default = "\n".join(inter.get("dream_talent", inter.get("梦想∩天赋", inter.get("dt", []))) or [])

center_text = st.text_area(
    TT("中心交汇（突破点）清单（每行一条）", "Center intersection (Breakthrough) list (one per line)"),
    value=center_default,
    height=120,
    key="inter_center",
)

colA, colB = st.columns(2)
with colA:
    rd_text = st.text_area(TT("责任 ∩ 梦想（每行一条）", "Responsibility ∩ Dream (one per line)"), value=rd_default, height=110, key="inter_rd")
    dt_text = st.text_area(TT("梦想 ∩ 天赋（每行一条）", "Dream ∩ Talent (one per line)"), value=dt_default, height=110, key="inter_dt")
with colB:
    rt_text = st.text_area(TT("责任 ∩ 天赋（每行一条）", "Responsibility ∩ Talent (one per line)"), value=rt_default, height=110, key="inter_rt")
    st.markdown(
        TT(
            '<div class="small">不确定两两交集也没关系，先填中心突破点，后续再补。</div>',
            '<div class="small">Not sure about pairwise intersections? Fill the center list first and refine later.</div>',
        ),
        unsafe_allow_html=True,
    )

save_ok = st.button(TT("💾 保存四象限 + 交集", "💾 Save quadrants + intersections"), use_container_width=True, key="save_all")
if save_ok:
    intersections = {
        "center": lines_to_list(center_text),
        "resp_dream": lines_to_list(rd_text),
        "resp_talent": lines_to_list(rt_text),
        "dream_talent": lines_to_list(dt_text),
        "_meta": {"name": (name or "").strip()},
    }
    update_annual_dig(talent=talent, responsibility=resp, dream=dream, intersections=intersections)
    st.success(TT("已保存 ✅", "Saved ✅"))
    st.rerun()

st.markdown("</div>", unsafe_allow_html=True)

# Life Circle 预览
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader(TT("Life Circle 预览", "Life Circle Preview"))
st.caption(TT("分享版更干净；完整版会显示三清单 + 三个两两交集。", "Share is clean; Full shows lists + pairwise intersections."))

mode_ui = st.radio(
    TT("预览模式", "Preview mode"),
    [TT("分享版（干净）", "Share (clean)"), TT("完整版（信息更多）", "Full (more info)")],
    horizontal=True,
    index=1,
    key="preview_mode",
)
mode_key = "share" if ("分享" in mode_ui or "Share" in mode_ui) else "full"

dream_items = build_items_from_quadrants(dream)
resp_items = build_items_from_quadrants(resp)
talent_items = build_items_from_quadrants(talent)

preview_png = render_life_circle_preview_png(
    name=(name or "").strip(),
    dream_items=dream_items,
    resp_items=resp_items,
    talent_items=talent_items,
    intersections={
        "center": lines_to_list(center_text),
        "resp_dream": lines_to_list(rd_text),
        "resp_talent": lines_to_list(rt_text),
        "dream_talent": lines_to_list(dt_text),
        "_meta": {"name": (name or "").strip()},
    },
    mode=mode_key,
)

st.image(preview_png, width=1100)
st.markdown("</div>", unsafe_allow_html=True)

# D 分配到 36×10
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader(TT("D｜一键分配到 36×10（与②页面联动）", "D | Assign to 36×10 (sync with page ②)"))
st.caption(
    TT(
        "规则：责任→Sprint 1..N；天赋→Sprint 7..18；梦想→Sprint 19..36。每个 Sprint 默认写入 1 条任务。",
        "Rule: Responsibility→Sprint 1..N; Talent→Sprint 7..18; Dream→Sprint 19..36. One task per sprint by default.",
    )
)
st.write(TT(f"当前：责任 {len(resp_items)} 条｜天赋 {len(talent_items)} 条｜梦想 {len(dream_items)} 条",
            f"Now: Responsibility {len(resp_items)} | Talent {len(talent_items)} | Dream {len(dream_items)}"))

if not ensure_sprints_ready():
    st.warning(
        TT("还没有生成 36×10 周期。你可以在这里一键生成，然后再分配任务。",
           "No 36×10 cycles yet. Generate them here first, then assign tasks.")
    )
    start = st.date_input(TT("选择你的 36×10 开始日期", "Pick your 36×10 start date"), value=date.today(), key="gen_start_date")
    if st.button(TT("🚀 立刻生成 36×10 周期", "🚀 Generate 36×10 cycles now"), use_container_width=True, key="gen_now"):
        regenerate_sprints(start)
        st.success(TT("已生成 36 个周期 ✅ 现在可以分配任务了", "Generated 36 cycles ✅ Now you can assign tasks"))
        st.rerun()
else:
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button(TT("🚀 分配责任 → 周期 1..N", "🚀 Assign Responsibility → Cycle 1..N"), use_container_width=True, key="assign_resp"):
            n = assign_list_to_sprints(resp_items, 1, 36)
            st.success(TT(f"已分配 {n} 条责任到 周期 1..{n}", f"Assigned {n} responsibility items to Cycle 1..{n}"))
            st.rerun()
    with c2:
        if st.button(TT("🚀 分配天赋 → 周期 7..18", "🚀 Assign Talent → Cycle 7..18"), use_container_width=True, key="assign_talent"):
            n = assign_list_to_sprints(talent_items, 7, 18)
            st.success(TT(f"已分配 {n} 条天赋到 周期 7..{min(18, 7+n-1)}",
                          f"Assigned {n} talent items to Cycle 7..{min(18, 7+n-1)}"))
            st.rerun()
    with c3:
        if st.button(TT("🚀 分配梦想 → 周期 19..36", "🚀 Assign Dream → Cycle 19..36"), use_container_width=True, key="assign_dream"):
            n = assign_list_to_sprints(dream_items, 19, 36)
            st.success(TT(f"已分配 {n} 条梦想到 周期 19..{min(36, 19+n-1)}",
                          f"Assigned {n} dream items to Cycle 19..{min(36, 19+n-1)}"))
            st.rerun()


st.markdown("</div>", unsafe_allow_html=True)

st.info(
    TT(
        "下一步：去「② 36×10」编辑每个周期的主题/交付物，并勾选任务完成；最后去「④ 导出中心」导出海报与 6×6 Excel。",
        "Next: go to page ② to edit each cycle's theme/deliverables and mark tasks done; finally go to ④ Export Hub to export poster and 6×6 Excel.",
    )
)
