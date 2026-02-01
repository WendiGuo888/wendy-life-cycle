import streamlit as st

from i18n import init_i18n, lang_selector, t

# 必须最先执行：设置首页 Tab 名（不会显示 Streamlit）

st.set_page_config(page_title="Home | Wendy · Bright Future", page_icon="🌱", layout="centered")
st.markdown(
    """
    <style>
    /* ===== 基础：字体渲染更清晰 ===== */
    html, body, [class*="css"]  {
        -webkit-text-size-adjust: 100%;
        text-rendering: optimizeLegibility;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }

    .block-container { padding-top: 1.2rem; padding-bottom: 2.0rem; max-width: 980px; }

    /* ====== Light mode：白卡黑字 ====== */
    .card{
        background: #ffffff;
        color: #111111;
        border-radius: 16px;
        padding: 18px 18px;
        margin-top: 12px;
        border: 1px solid rgba(0,0,0,0.06);
        box-shadow: 0 10px 24px rgba(0,0,0,0.04);
    }
    .card *{ color:#111111; }

    /* ====== Dark mode：深卡白字（关键！） ====== */
    @media (prefers-color-scheme: dark) {
        .card{
            background: rgba(255,255,255,0.06) !important;
            color: rgba(255,255,255,0.92) !important;
            border: 1px solid rgba(255,255,255,0.12) !important;
            box-shadow: 0 10px 24px rgba(0,0,0,0.35) !important;
        }
        .card *{
            color: rgba(255,255,255,0.92) !important;
        }
        .small{ color: rgba(255,255,255,0.70) !important; }
        .badge{
            border: 1px solid rgba(255,255,255,0.18) !important;
            background: rgba(255,255,255,0.08) !important;
            color: rgba(255,255,255,0.88) !important;
        }
    }

    /* ===== 平板/手机：字号更大 ===== */
    @media (max-width: 1024px) {
        .block-container { max-width: 100% !important; padding-left: 1rem; padding-right: 1rem; }
        textarea, input, button, select, label { font-size: 18px !important; }
        h1 { font-size: 2.0rem !important; }
        h2 { font-size: 1.55rem !important; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)





init_i18n(default="zh")
lang_selector()

st.markdown(
    """
<style>
.block-container { padding-top: 1.2rem; padding-bottom: 2.0rem; max-width: 1180px; }
h1,h2,h3 { font-weight: 750; }
.card {
    background: #fff;
    border-radius: 16px;
    padding: 18px 18px;
    margin-top: 12px;
    border: 1px solid rgba(0,0,0,0.06);
    box-shadow: 0 10px 24px rgba(0,0,0,0.04);
}
.small { color:#666; font-size: 13px; }
.badge {
    display:inline-block;
    padding: 3px 10px;
    border-radius: 999px;
    border: 1px solid rgba(0,0,0,0.08);
    background: rgba(0,0,0,0.02);
    font-size: 12px;
    margin-right: 8px;
}
</style>
""",
    unsafe_allow_html=True,
)

st.title(t("app_title"))

st.markdown(
    f"""
<div class="card">
<h2>年度使命落地系统（MVP · Beta）</h2>

<ul>
  <li><b>年度挖掘 / Life Circle</b>：责任 / 天赋 / 梦想 / 愿力 → 生成年度使命与生命之轮</li>
  <li><b>36×10 自我提升计划</b>：36 个 10 天行动周期，明确主题 / 交付物 / 复盘 / 任务</li>
  <li><b>CARE 四宫格</b>：把强相关灵感（inspiration）沉淀为行动 → 一键加入 10 天任务</li>
  <li><b>导出中心</b>：一键导出海报+ 6×6 成长表</li>
  <li><b>反馈中心</b>：一起共创「周年可持续使用」的成长系统（匿名、不收集邮箱）</li>
</ul>

</div>
""",
    unsafe_allow_html=True,
)


st.markdown(
    f"""
<div class="card">
<div class="small">
<span class="badge">Mission</span>
<span class="badge">Action</span>
<span class="badge">Reality</span>
</div>

### {t("app_intro_title")}

- {t("app_intro_line1")}
- {t("app_intro_line2")}
- {t("app_intro_line3")}
- {t("app_intro_line4")}

</div>
""",
    unsafe_allow_html=True,
)

st.info(t("nav_tip"))
