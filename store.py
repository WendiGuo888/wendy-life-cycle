# store.py
# -*- coding: utf-8 -*-
"""
Session-only 数据层：每个访问者数据只存在 st.session_state，不会互相串。
适合 Streamlit Cloud 内测阶段。
"""

from __future__ import annotations

import uuid
import json
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Dict, List, Optional, Any

import streamlit as st


# -----------------------
# 基础：每个访问者唯一 user_key
# -----------------------
def _ensure_user_key() -> str:
    if "user_key" not in st.session_state:
        st.session_state["user_key"] = str(uuid.uuid4())
    return st.session_state["user_key"]


def _ensure_store() -> Dict[str, Any]:
    _ensure_user_key()
    if "STORE" not in st.session_state:
        st.session_state["STORE"] = {}

    store = st.session_state["STORE"]

    store.setdefault(
        "annual_dig",
        {
            "talent": {},
            "responsibility": {},
            "dream": {},
            "intersections": {
                "center": [],
                "resp_dream": [],
                "resp_talent": [],
                "dream_talent": [],
                "_meta": {"name": ""},
            },
        },
    )

    store.setdefault(
        "profile",
        {
            "name": "",
            "vow": "",
            "vow_keywords": [],
            "mission_statement": "",
        },
    )

    store.setdefault("sprints", [])       # List[dict] len=36
    store.setdefault("care_records", [])  # List[dict]
    return store


# -----------------------
# AnnualDig（模拟 DB 行对象）
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
    return _AnnualDigObj(
        id=1,
        talent_json=json.dumps(ad.get("talent", {}) or {}, ensure_ascii=False),
        responsibility_json=json.dumps(ad.get("responsibility", {}) or {}, ensure_ascii=False),
        dream_json=json.dumps(ad.get("dream", {}) or {}, ensure_ascii=False),
        intersections_json=json.dumps(ad.get("intersections", {}) or {}, ensure_ascii=False),
    )


def update_annual_dig(talent: dict, responsibility: dict, dream: dict, intersections: dict):
    store = _ensure_store()
    store["annual_dig"] = {
        "talent": talent or {},
        "responsibility": responsibility or {},
        "dream": dream or {},
        "intersections": intersections or {},
    }


# -----------------------
# 36×10 Sprint + Task（dict）
# -----------------------
def regenerate_sprints(start: date):
    """生成 36 个 10天周期（会清空旧 sprints 和 tasks）"""
    store = _ensure_store()
    sprints: List[dict] = []
    cur = start
    for i in range(1, 37):
        sprints.append(
            {
                "sprint_no": i,
                "start_date": cur.isoformat(),
                "end_date": (cur + timedelta(days=9)).isoformat(),
                "theme": "",
                "objective": "",
                "review": "",
                "tasks": [],  # List[dict]
            }
        )
        cur = cur + timedelta(days=10)
    store["sprints"] = sprints


def get_sprints() -> List[dict]:
    store = _ensure_store()
    sps = store.get("sprints", [])
    return sps if isinstance(sps, list) else []


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


def list_tasks_for_sprint(sprint_no: int) -> List[dict]:
    sp = get_sprint_by_no(sprint_no)
    if not sp:
        return []
    tasks = sp.get("tasks", [])
    return tasks if isinstance(tasks, list) else []


def _task_exists(sp: dict, title: str) -> bool:
    title = (title or "").strip()
    if not title:
        return True
    for t in sp.get("tasks", []):
        if (t.get("title") or "").strip() == title:
            return True
    return False


def add_task_to_sprint_unique(sprint_no: int, title: str, source_care_id: Optional[str] = None):
    sp = get_sprint_by_no(int(sprint_no))
    if not sp:
        return
    title = (title or "").strip()
    if not title:
        return
    if _task_exists(sp, title):
        return
    sp["tasks"].append(
        {
            "id": str(uuid.uuid4()),
            "title": title,
            "done": False,
            "evidence": "",
            "source_care_id": str(source_care_id) if source_care_id is not None else "",
        }
    )


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


def find_task_by_source(sprint_no: int, source_care_id: str) -> Optional[dict]:
    source_care_id = str(source_care_id)
    for t in list_tasks_for_sprint(int(sprint_no)):
        if str(t.get("source_care_id", "")) == source_care_id:
            return t
    return None


def toggle_task_done_by_source(sprint_no: int, source_care_id: str, done: bool) -> bool:
    t = find_task_by_source(int(sprint_no), str(source_care_id))
    if not t:
        return False
    t["done"] = bool(done)
    return True


# -----------------------
# CARE（Session 内记录）
# -----------------------
def list_care_records() -> List[dict]:
    store = _ensure_store()
    recs = store.get("care_records", [])
    return list(recs) if isinstance(recs, list) else []


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
    store["care_records"].insert(
        0,
        {
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
        },
    )


def update_care_record(care_id: str, **kwargs):
    store = _ensure_store()
    care_id = str(care_id)
    for r in store.get("care_records", []):
        if str(r.get("id")) == care_id:
            for k, v in kwargs.items():
                r[k] = v
            return


def delete_care_record(care_id: str):
    store = _ensure_store()
    care_id = str(care_id)
    store["care_records"] = [r for r in store.get("care_records", []) if str(r.get("id")) != care_id]


# -----------------------
# JSON 备份/恢复
# -----------------------
def export_user_json() -> bytes:
    store = _ensure_store()
    payload = {"user_key": st.session_state.get("user_key"), "STORE": store}
    return json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")


def import_user_json(file_bytes: bytes):
    data = json.loads(file_bytes.decode("utf-8"))
    if "STORE" in data and isinstance(data["STORE"], dict):
        st.session_state["STORE"] = data["STORE"]
    _ensure_user_key()
