# store.py
# -*- coding: utf-8 -*-
"""
Session-only 数据层：每个用户的数据只存在 st.session_state，不会互相串。
适合 Streamlit Cloud 大规模内测阶段。
"""

from __future__ import annotations
import uuid
import json
from dataclasses import dataclass, asdict
from datetime import date, timedelta
from typing import Any, Dict, List, Optional

import streamlit as st


# -----------------------
# 基础：确保每个访问者都有自己的 user_key
# -----------------------
def _ensure_user_key() -> str:
    if "user_key" not in st.session_state:
        st.session_state["user_key"] = str(uuid.uuid4())
    return st.session_state["user_key"]


def _ensure_store():
    _ensure_user_key()
    if "STORE" not in st.session_state:
        st.session_state["STORE"] = {}

    store = st.session_state["STORE"]

    # 初始化核心结构
    store.setdefault("annual_dig", {
        "talent": {},
        "responsibility": {},
        "dream": {},
        "intersections": {"center": [], "resp_dream": [], "resp_talent": [], "dream_talent": [], "_meta": {"name": ""}},
    })
    store.setdefault("profile", {
        "name": "",
        "vow": "",
        "vow_keywords": [],
        "mission_statement": "",
    })
    store.setdefault("sprints", [])  # List[dict] len=36
    store.setdefault("care_records", [])  # List[dict]
    return store


# -----------------------
# AnnualDig（模拟你原来的 AnnualDig 行为）
# -----------------------
@dataclass
class _AnnualDigObj:
    id: int = 1
    talent_json: str = "{}"
    responsibility_json: str = "{}"
    dream_json: str = "{}"
    intersections_json: str = "{}"


def get_or_create_annual_dig() -> _AnnualDigObj:
    store = _ensure_store()
    ad = store["annual_dig"]
    obj = _AnnualDigObj(
        id=1,
        talent_json=json.dumps(ad.get("talent", {}) or {}, ensure_ascii=False),
        responsibility_json=json.dumps(ad.get("responsibility", {}) or {}, ensure_ascii=False),
        dream_json=json.dumps(ad.get("dream", {}) or {}, ensure_ascii=False),
        intersections_json=json.dumps(ad.get("intersections", {}) or {}, ensure_ascii=False),
    )
    return obj


def update_annual_dig(talent: dict, responsibility: dict, dream: dict, intersections: dict):
    store = _ensure_store()
    store["annual_dig"] = {
        "talent": talent or {},
        "responsibility": responsibility or {},
        "dream": dream or {},
        "intersections": intersections or {},
    }


# -----------------------
# 36×10（自我提升计划）Sprint + Task
# -----------------------
def regenerate_sprints(start: date):
    """
    生成 36 个 10天周期（Session 内）。会清空旧 sprints 和 tasks。
    """
    store = _ensure_store()
    sprints = []
    cur = start
    for i in range(1, 37):
        sprints.append({
            "sprint_no": i,
            "start_date": cur.isoformat(),
            "end_date": (cur + timedelta(days=9)).isoformat(),
            "theme": "",
            "objective": "",
            "review": "",
            "tasks": [],  # list of dict
        })
        cur = cur + timedelta(days=10)
    store["sprints"] = sprints


def get_sprints() -> List[dict]:
    store = _ensure_store()
    return store.get("sprints", [])


def get_sprint_by_no(sprint_no: int) -> Optional[dict]:
    for sp in get_sprints():
        if sp.get("sprint_no") == sprint_no:
            return sp
    return None


def update_sprint_text(sprint_no: int, theme: str, objective: str, review: str):
    sp = get_sprint_by_no(sprint_no)
    if not sp:
        return
    sp["theme"] = theme or ""
    sp["objective"] = objective or ""
    sp["review"] = review or ""


def _task_exists(sp: dict, title: str) -> bool:
    title = (title or "").strip()
    if not title:
        return True
    for t in sp.get("tasks", []):
        if (t.get("title") or "").strip() == title:
            return True
    return False


def add_task_to_sprint_unique(sprint_no: int, title: str, source_care_id: Optional[str] = None):
    sp = get_sprint_by_no(sprint_no)
    if not sp:
        return
    title = (title or "").strip()
    if not title:
        return
    if _task_exists(sp, title):
        return
    sp["tasks"].append({
        "id": str(uuid.uuid4()),
        "title": title,
        "done": False,
        "evidence": "",
        "source_care_id": source_care_id,
    })


def list_tasks_for_sprint(sprint_no: int) -> List[dict]:
    sp = get_sprint_by_no(sprint_no)
    if not sp:
        return []
    return sp.get("tasks", [])


def toggle_task_done(task_id: str, done: bool):
    store = _ensure_store()
    for sp in store.get("sprints", []):
        for t in sp.get("tasks", []):
            if t.get("id") == task_id:
                t["done"] = bool(done)
                return


def update_task_evidence(task_id: str, evidence: str):
    store = _ensure_store()
    for sp in store.get("sprints", []):
        for t in sp.get("tasks", []):
            if t.get("id") == task_id:
                t["evidence"] = evidence or ""
                return


# -----------------------
# CARE（Session 内记录）
# -----------------------
def list_care_records() -> List[dict]:
    store = _ensure_store()
    return list(store.get("care_records", []))


def add_care_record(
    capture_source: str,
    cognition: str,
    action: str,
    relationship: str,
    ego_drive: str,
    vow_tag: str,
    relevance_score: int,
    tags: str = "",
):
    store = _ensure_store()
    store["care_records"].insert(0, {
        "id": str(uuid.uuid4()),
        "capture_source": capture_source or "",
        "cognition": cognition or "",
        "action": action or "",
        "relationship": relationship or "",
        "ego_drive": ego_drive or "",
        "vow_tag": vow_tag or "",
        "relevance_score": int(relevance_score),
        "tags": tags or "",
        "created_at": date.today().isoformat(),
    })


def delete_care_record(care_id: str):
    store = _ensure_store()
    store["care_records"] = [r for r in store.get("care_records", []) if r.get("id") != care_id]


def update_care_record(care_id: str, **kwargs):
    store = _ensure_store()
    for r in store.get("care_records", []):
        if r.get("id") == care_id:
            for k, v in kwargs.items():
                r[k] = v
            return


# -----------------------
# JSON 导入/导出（让用户保存自己的数据）
# -----------------------
def export_user_json() -> bytes:
    store = _ensure_store()
    payload = {
        "user_key": st.session_state.get("user_key"),
        "STORE": store,
    }
    return json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")


def import_user_json(file_bytes: bytes):
    data = json.loads(file_bytes.decode("utf-8"))
    if "STORE" in data and isinstance(data["STORE"], dict):
        st.session_state["STORE"] = data["STORE"]
    # 保留当前浏览器的 user_key，不强制覆盖
    _ensure_user_key()
