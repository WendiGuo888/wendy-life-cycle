import streamlit as st
from i18n import init_i18n, lang_selector

# 必须最先
lang = st.session_state.get("lang", "zh")
st.set_page_config(
    page_title="💬 Feedback" if lang == "en" else "💬 使用反馈",
    page_icon="💬",
    layout="wide",
)

init_i18n(default="zh")
lang_selector()

def TT(zh, en):
    return zh if st.session_state.get("lang", "zh") == "zh" else en

st.title(TT("💬 使用反馈", "💬 Feedback"))
st.caption(
    TT(
        "你的反馈将直接影响这个产品的下一步迭代，非常感谢参与内测 🙏",
        "Your feedback directly shapes the next iteration. Thank you for joining the beta 🙏",
    )
)

# ====== 你的 Google Form 嵌入链接 ======
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSegYe_ldCenc1il7I4AFTQROkVwe9DdRZPyLbmy4bNCtOAGPQ/viewform?embedded=true"

# ====== 页面说明（产品感） ======
with st.expander(TT("为什么要填写这个？", "Why this feedback matters")):
    st.markdown(
        TT(
            """
- 这是一个 **内测版本（Beta）**
- 所有建议都会被认真阅读和整理
- 你正在参与共创，而不是填问卷
""",
            """
- This is a **beta version**
- Every suggestion will be reviewed
- You are co-creating the product, not just filling a form
""",
        )
    )

# ====== 嵌入 Form（核心） ======
st.components.v1.iframe(
    FORM_URL,
    height=900,
    scrolling=True,
)

st.markdown("---")
st.markdown(
    TT(
        "💚 谢谢你愿意花时间反馈，这对我非常重要。",
        "💚 Thank you for taking the time to share feedback — it means a lot.",
    )
)

