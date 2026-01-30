import streamlit as st

TRANSLATIONS = {
    "zh": {
        "lang_name": "中文",

        # Home
        "app_title": "🌱 Wendy · Bright Future",
        "app_intro_title": "年度使命落地系统（MVP）",
        "app_intro_line1": "年度挖掘 / Life Circle：责任 / 天赋 / 梦想 / 愿力 → 使命宣言与生命之轮海报",
        "app_intro_line2": "36×10 自我提升计划：36 个 10天行动周期，主题/交付物/任务/证据/复盘",
        "app_intro_line3": "CARE 四宫格：记录强相关 inspiration → 一键转为 10天任务",
        "app_intro_line4": "导出中心：海报（多比例）+ Excel（6×6 大表）",
        "nav_tip": "从左侧导航进入：① 年度挖掘 → ② 36×10 → ③ CARE → ④ 导出中心",

        # 36×10
        "page_36_title": "② 36×10：自我提升计划（10天行动周期）",
        "page_36_caption": "主题 + 交付物 → 任务执行 → 证据 → 复盘",
        "export_excel_btn": "⬇️ 导出 Excel（6×6 大表：主题/交付物/任务）",

        # Export hub
        "page_export_title": "④ 导出中心",
        "page_export_caption": "导出 Life Circle 海报（多平台比例）与 36×10 Excel（6×6 大表）",
        "poster_section": "A｜Life Circle 海报导出",
        "excel_section": "B｜36×10 自我提升计划 Excel 导出（6×6大表）",
        "mode_label": "选择导出模式",
        "mode_share": "分享版（干净）",
        "mode_full": "完整版（信息更多）",
        "download_ig_square": "📷 IG 1:1",
        "download_ig_story": "📱 IG Story 9:16",
        "download_xhs_3x4": "📕 小红书 3:4",
        "download_xhs_4x5": "📕 小红书 4:5",
        "download_excel": "⬇️ 导出 Excel（6×6大表）",

        # Annual Dig / Life Circle
        "page_dig_title": "① 年度挖掘：Life Circle",
        "page_dig_caption": "责任 / 天赋 / 梦想 / 愿力 → 使命宣言 → 四象限与交集清单 → 生命之轮海报 → 一键分配到 36×10",
        "save_mission": "💾 保存使命 + 名字",
        "mission_statement": "使命宣言",
        "quadrants": "四象限（多条清单）",
        "tab_talent": "天赋",
        "tab_resp": "责任",
        "tab_dream": "梦想",
        "q_study": "学业",
        "q_career": "事业",
        "q_growth": "成长",
        "q_body": "身体",
        "intersection_title": "本年度一定实现的突破点（交集区）",
        "inter_rd": "责任 ∩ 梦想（多条）",
        "inter_rt": "责任 ∩ 天赋（多条）",
        "inter_dt": "梦想 ∩ 天赋（多条）",
        "inter_center": "三者交汇（今年必须成，多条）",
        "save_dig": "💾 保存四象限 + 交集",
        "preview_title": "Life Circle 预览",
        "preview_mode": "预览模式",
        "assign_title": "年度规划 → 36×10 自动落地（联动）",
        "assign_caption": "规则：责任→周期1-6；天赋→周期7-18；梦想→周期19-36（每个周期默认放1条）。",
        "assign_prefix": "给任务加前缀（更清晰：【责任】/【天赋】/【梦想】）",
        "assign_btn": "🚀 一键分配：责任→1-6 / 天赋→7-18 / 梦想→19-36",

        # CARE
        "page_care_title": "③ CARE 四宫格（强相关 Inspiration）",
        "page_care_caption": "记录与你的愿力强相关的灵感：打分 + 标签 → 一键转为 10天行动任务",
        "care_add_title": "新增 CARE 记录",
        "care_capture": "Capture/Source（必填：原文/链接）",
        "care_cognition": "Cognition（认知/启发）",
        "care_action": "Action（必填：下一步最小可执行行动）",
        "care_relationship": "Relationship（相关的人/协作）",
        "care_ego": "Ego drive（内在驱动力）",
        "care_vow_tag": "Vow Tag（愿力关键词）",
        "care_relevance": "Relevance Score（0~5，必填）",
        "care_tags": "Tags（可选，逗号分隔）",
        "care_add_btn": "➕ 添加 CARE",
        "care_filter_strong": "默认只看强相关（评分≥4）",
        "care_show_all": "显示全部",
        "care_search": "关键词搜索",
        "care_to_task": "一键转为任务",
        "care_choose_sprint": "选择 10天行动周期",
        "care_to_task_btn": "➕ 将 Action 添加为任务",
        "care_delete": "删除",
        "care_update": "保存修改",
    },

    "en": {
        "lang_name": "English",

        # Home
        "app_title": "🌱 Wendy · Bright Future",
        "app_intro_title": "Mission → Action → Reality (MVP)",
        "app_intro_line1": "Annual Dig / Life Circle: Responsibility / Talent / Dream / Vow → mission statement & poster",
        "app_intro_line2": "36×10 Plan: 36 ten-day cycles with Theme/Deliverables/Tasks/Evidence/Review",
        "app_intro_line3": "CARE Grid: capture vow-aligned inspirations → one-click to tasks",
        "app_intro_line4": "Export Hub: Posters (multi ratios) + Excel (6×6 master sheet)",
        "nav_tip": "Use the left sidebar: ① Life Circle → ② 36×10 → ③ CARE → ④ Export Hub",

        # 36×10
        "page_36_title": "② 36×10: Growth Plan (10-Day Cycles)",
        "page_36_caption": "Theme + Deliverables → Execute tasks → Evidence → Review",
        "export_excel_btn": "⬇️ Export Excel (6×6 master sheet)",

        # Export hub
        "page_export_title": "④ Export Hub",
        "page_export_caption": "Export Life Circle posters (multi ratios) and 36×10 Excel (6×6 master sheet)",
        "poster_section": "A | Life Circle Posters",
        "excel_section": "B | 36×10 Excel Export (6×6 master sheet)",
        "mode_label": "Choose mode",
        "mode_share": "Share (clean)",
        "mode_full": "Full (more info)",
        "download_ig_square": "📷 IG 1:1",
        "download_ig_story": "📱 IG Story 9:16",
        "download_xhs_3x4": "🖼 Poster 3:4",
        "download_xhs_4x5": "🖼 Poster 4:5",
        "download_excel": "⬇️ Export Excel (6×6)",

        # Annual Dig
        "page_dig_title": "① Annual Dig: Life Circle",
        "page_dig_caption": "Responsibility / Talent / Dream / Vow → Mission statement → Lists & intersections → Poster → Auto-assign to 36×10",
        "save_mission": "💾 Save mission + name",
        "mission_statement": "Mission statement",
        "quadrants": "Quadrants (multiple items)",
        "tab_talent": "Talent",
        "tab_resp": "Responsibility",
        "tab_dream": "Dream",
        "q_study": "Study",
        "q_career": "Career",
        "q_growth": "Growth",
        "q_body": "Body",
        "intersection_title": "Breakthrough intersections",
        "inter_rd": "Responsibility ∩ Dream",
        "inter_rt": "Responsibility ∩ Talent",
        "inter_dt": "Dream ∩ Talent",
        "inter_center": "Center (must happen this year)",
        "save_dig": "💾 Save quadrants + intersections",
        "preview_title": "Life Circle preview",
        "preview_mode": "Preview mode",
        "assign_title": "Annual plan → 36×10 execution (auto)",
        "assign_caption": "Rule: Responsibility→Cycles 1-6; Talent→7-18; Dream→19-36 (1 item per cycle).",
        "assign_prefix": "Add prefixes for clarity ([R]/[T]/[D])",
        "assign_btn": "🚀 Auto-assign: R→1-6 / T→7-18 / D→19-36",

        # CARE
        "page_care_title": "③ CARE Grid (Vow-aligned inspirations)",
        "page_care_caption": "Capture vow-aligned inspirations: score + tag → one-click to 10-day tasks",
        "care_add_title": "Add a CARE record",
        "care_capture": "Capture/Source (required: text/link)",
        "care_cognition": "Cognition",
        "care_action": "Action (required: smallest next step)",
        "care_relationship": "Relationship",
        "care_ego": "Ego drive",
        "care_vow_tag": "Vow tag",
        "care_relevance": "Relevance score (0~5, required)",
        "care_tags": "Tags (optional, comma-separated)",
        "care_add_btn": "➕ Add CARE",
        "care_filter_strong": "Show strong only (score ≥ 4)",
        "care_show_all": "Show all",
        "care_search": "Search",
        "care_to_task": "One-click to task",
        "care_choose_sprint": "Choose a 10-day cycle",
        "care_to_task_btn": "➕ Add Action as task",
        "care_delete": "Delete",
        "care_update": "Save changes",
    },
}

def init_i18n(default="zh"):
    if "lang" not in st.session_state:
        st.session_state.lang = default

def lang_selector():
    options = {"中文": "zh", "English": "en"}
    current = st.session_state.get("lang", "zh")
    reverse = {v: k for k, v in options.items()}
    label = reverse.get(current, "中文")
    choice = st.sidebar.selectbox("Language / 语言", ["中文", "English"], index=0 if label == "中文" else 1)
    st.session_state.lang = options[choice]

def t(key: str) -> str:
    lang = st.session_state.get("lang", "zh")
    return TRANSLATIONS.get(lang, TRANSLATIONS["zh"]).get(key, key)
