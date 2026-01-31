import streamlit as st

from i18n import init_i18n, lang_selector, t

# 必须最先执行：设置首页 Tab 名（不会显示 Streamlit）

st.set_page_config(page_title="Home | Wendy · Bright Future", page_icon="🌱", layout="centered")



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
