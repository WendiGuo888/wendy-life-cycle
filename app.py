import streamlit as st

from i18n import init_i18n, lang_selector, t

# 必须最先执行：设置首页 Tab 名（不会显示 Streamlit）

st.set_page_config(page_title="Home | Wendy · Bright Future", page_icon="🌱", layout="centered")
st.markdown(
    """
    <style>
    /* ========= iPad / 手机：整体可读性增强 ========= */
    html, body, [class*="css"]  {
        -webkit-text-size-adjust: 100%;
        text-rendering: optimizeLegibility;
        font-smooth: always;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }

    /* 基础字号：桌面也更舒服 */
    .block-container {
        max-width: 980px;
        padding-top: 1.2rem;
        padding-bottom: 2rem;
    }

    /* 输入框、按钮字号统一 */
    textarea, input, button, select, label {
        font-size: 16px !important;
        line-height: 1.6 !important;
    }

    /* 标题更清晰 */
    h1 { font-size: 2.0rem !important; line-height: 1.25 !important; }
    h2 { font-size: 1.55rem !important; line-height: 1.3 !important; }
    h3 { font-size: 1.25rem !important; line-height: 1.35 !important; }

    /* ===== 平板/手机：字号再上调一档 ===== */
    @media (max-width: 1024px) {
        .block-container {
            max-width: 100% !important;
            padding-left: 1rem;
            padding-right: 1rem;
        }

        /* 整体字体放大 */
        html, body, [class*="css"]  {
            font-size: 18px !important;
        }

        /* 输入控件更易点 */
        textarea, input, button, select {
            font-size: 18px !important;
        }

        /* 卡片间距更舒服 */
        .card {
            padding: 16px !important;
            border-radius: 14px !important;
        }
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
