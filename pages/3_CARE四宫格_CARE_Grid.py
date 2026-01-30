import streamlit as st
# ✅ 必须在任何 st.xxx 之前
lang = st.session_state.get("lang", "zh")
st.set_page_config(
    page_title=("③ CARE 四宫格" if lang == "zh" else "③ CARE Grid"),
    page_icon="🌱",
    layout="wide",
)


from i18n import init_i18n, lang_selector, t

from store import (
    get_or_create_profile,
    list_care_records,
    add_care_record,
    update_care_record,
    delete_care_record,
    get_sprints,
    add_task_to_sprint_unique,
)

init_i18n(default="zh")
lang_selector()

st.markdown(
    """
<style>
.block-container { padding-top: 1.4rem; padding-bottom: 2.0rem; max-width: 1180px; }
.card {
    background: #fff;
    border-radius: 16px;
    padding: 14px 14px;
    margin-bottom: 12px;
    border: 1px solid rgba(0,0,0,0.06);
    box-shadow: 0 10px 24px rgba(0,0,0,0.04);
}
.small { color:#666; font-size: 13px; }
</style>
""",
    unsafe_allow_html=True,
)

st.title(t("page_care_title"))
st.caption(t("page_care_caption"))

prof = get_or_create_profile()
vow_keywords = [x.strip() for x in (prof.vow_keywords or "").split(",") if x.strip()]

st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader(t("care_add_title"))

with st.form("care_add_form"):
    capture = st.text_area(t("care_capture"), height=80)
    cognition = st.text_area(t("care_cognition"), height=80)
    action = st.text_area(t("care_action"), height=80)

    c1, c2 = st.columns(2)
    with c1:
        relationship = st.text_area(t("care_relationship"), height=80)
        vow_tag = st.selectbox(t("care_vow_tag"), options=([""] + vow_keywords) if vow_keywords else [""], index=0)
    with c2:
        ego = st.text_area(t("care_ego"), height=80)
        relevance = st.slider(t("care_relevance"), min_value=0, max_value=5, value=4, step=1)

    tags = st.text_input(t("care_tags"), value="")

    add_btn = st.form_submit_button(t("care_add_btn"), use_container_width=True)

if add_btn:
    if not capture.strip():
        st.error("Capture/Source is required." if st.session_state.lang == "en" else "Capture/Source 必填。")
    elif not action.strip():
        st.error("Action is required." if st.session_state.lang == "en" else "Action 必填。")
    else:
        add_care_record(
            capture_source=capture.strip(),
            cognition=cognition.strip(),
            action=action.strip(),
            relationship=relationship.strip(),
            ego_drive=ego.strip(),
            vow_tag=vow_tag.strip(),
            relevance_score=int(relevance),
            tags=tags.strip(),
            linked_goal="",
        )
        st.success("Added ✅" if st.session_state.lang == "en" else "已添加 ✅")
        st.rerun()

st.markdown("</div>", unsafe_allow_html=True)

st.divider()

# Filters
st.markdown("### " + ("Records" if st.session_state.lang == "en" else "记录列表"))
strong_only = st.checkbox(t("care_filter_strong"), value=True)
search = st.text_input(t("care_search"), value="")

tag_filter = st.selectbox(
    t("care_vow_tag"),
    options=(["(All)"] if st.session_state.lang == "en" else ["（全部）"]) + (vow_keywords if vow_keywords else []),
    index=0
)

records = list_care_records()

def match(r):
    if strong_only and int(getattr(r, "relevance_score", 0)) < 4:
        return False
    if tag_filter not in ["(All)", "（全部）"] and (getattr(r, "vow_tag", "") or "") != tag_filter:
        return False
    if search.strip():
        s = search.strip().lower()
        blob = " ".join([
            getattr(r, "capture_source", "") or "",
            getattr(r, "cognition", "") or "",
            getattr(r, "action", "") or "",
            getattr(r, "relationship", "") or "",
            getattr(r, "ego_drive", "") or "",
            getattr(r, "vow_tag", "") or "",
            getattr(r, "tags", "") or "",
        ]).lower()
        return s in blob
    return True

filtered = [r for r in records if match(r)]
if not filtered:
    st.info("No records yet." if st.session_state.lang == "en" else "暂无记录。")
    st.stop()

# for "one-click to task"
sprints = get_sprints()
sprint_options = [sp.sprint_no for sp in sprints] if sprints else []
default_sprint = sprint_options[0] if sprint_options else 1

for r in filtered:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.write(f"**#{r.id}**  |  {t('care_relevance')}: **{r.relevance_score}**  |  {t('care_vow_tag')}: **{r.vow_tag or '-'}**")
    st.write(f"**{t('care_capture')}**")
    st.write(r.capture_source)

    with st.expander("Edit / 编辑", expanded=False):
        with st.form(f"edit_{r.id}"):
            cap2 = st.text_area(t("care_capture"), value=r.capture_source, height=80)
            cog2 = st.text_area(t("care_cognition"), value=r.cognition or "", height=80)
            act2 = st.text_area(t("care_action"), value=r.action or "", height=80)

            cc1, cc2 = st.columns(2)
            with cc1:
                rel2 = st.text_area(t("care_relationship"), value=r.relationship or "", height=80)
                vow2 = st.selectbox(t("care_vow_tag"), options=([""] + vow_keywords) if vow_keywords else [""],
                                    index=([""] + vow_keywords).index(r.vow_tag) if (vow_keywords and r.vow_tag in vow_keywords) else 0,
                                    key=f"vow_{r.id}")
            with cc2:
                ego2 = st.text_area(t("care_ego"), value=r.ego_drive or "", height=80)
                score2 = st.slider(t("care_relevance"), 0, 5, int(r.relevance_score), 1, key=f"score_{r.id}")

            tags2 = st.text_input(t("care_tags"), value=r.tags or "", key=f"tags_{r.id}")

            cbtn1, cbtn2 = st.columns(2)
            with cbtn1:
                save = st.form_submit_button(t("care_update"), use_container_width=True)
            with cbtn2:
                delete = st.form_submit_button(t("care_delete"), use_container_width=True)

        if save:
            if not cap2.strip():
                st.error("Capture/Source is required." if st.session_state.lang == "en" else "Capture/Source 必填。")
            elif not act2.strip():
                st.error("Action is required." if st.session_state.lang == "en" else "Action 必填。")
            else:
                update_care_record(
                    care_id=r.id,
                    capture_source=cap2.strip(),
                    cognition=cog2.strip(),
                    action=act2.strip(),
                    relationship=rel2.strip(),
                    ego_drive=ego2.strip(),
                    vow_tag=vow2.strip(),
                    relevance_score=int(score2),
                    tags=tags2.strip(),
                    linked_goal="",
                )
                st.success("Saved ✅" if st.session_state.lang == "en" else "已保存 ✅")
                st.rerun()

        if delete:
            delete_care_record(r.id)
            st.success("Deleted ✅" if st.session_state.lang == "en" else "已删除 ✅")
            st.rerun()

    st.markdown("---")
    st.subheader(t("care_to_task"))

    if not sprint_options:
        st.info("Please generate 36×10 cycles first (page ②)." if st.session_state.lang == "en"
                else "请先在「② 36×10」页面生成 36×10 行动周期。")
    else:
        colA, colB = st.columns([2, 1])
        with colA:
            chosen = st.selectbox(t("care_choose_sprint"), options=sprint_options, index=0, key=f"s_{r.id}")
        with colB:
            if st.button(t("care_to_task_btn"), key=f"to_{r.id}", use_container_width=True):
                # 把 action 写入该周期任务，source_care_id 可选（你 db 支持）
                add_task_to_sprint_unique(int(chosen), (r.action or "").strip(), source_care_id=r.id)
                st.success("Added to cycle ✅" if st.session_state.lang == "en" else "已添加到周期 ✅")

    st.markdown("</div>", unsafe_allow_html=True)

