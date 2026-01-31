# store.py
# -*- coding: utf-8 -*-
"""
Session-only 数据层：每个访问者的数据只存在 st.session_state，不会互相串。
适合 Streamlit Cloud 大规模内测阶段（不做登录、不做服务器端持久化）。
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any, Dict, List, Optional

import streamlit as st


# ============================================================
# 0) 基础：确保每个访问者都有自己的 user_key + STORE
# ============================================================
def _ensure_user_key() -> str:
    if "user_key" not in st.session_state:
        st.session_state["user_key"] = str(uuid.uuid4())
    return st.session_state["user_key"]


def _ensure_store() -> Dict[str, Any]:
    _ensure_user_key()

    if "STORE" not in st.session_state:
        st.session_state["STORE"] = {}

    store = st.session_state["STORE"]

    # profile（使命/誓言等）
    store.setdefault(
        "profile",
        {
            "name": "",
            "responsibility": "",
            "talent": "",
            "dream": "",
            "vow": "",
            "vow_keywords": [],
            "mission_statement": "",
        },
    )

    # annual dig（四象限 + 交集）
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

    # 36×10 sprints（36个周期）
    store.setdefault("sprints", [])  # List[dict]

    # CARE records
    store.setdefault("care_records", [])  # List[dict]

    return store


# ============================================================
# 1) 兼容 init_db：云端 session-only 不需要 DB，但 app.py 可能会调用
# ============================================================
def init_db() -> None:
    """兼容旧代码：session-only 模式不需要真正 init DB。"""
    _ensure_store()
    return


# ============================================================
# 2) Profile：兼容 db.py 的 get_or_create_profile / update_profile
# ============================================================
@dataclass
class _ProfileObj:
    id: int = 1
    responsibility: str = ""
    talent: str = ""
    dream: str = ""
    vow: str = ""
    vow_keywords: str = ""
    mission_statement: str = ""


def get_or_create_profile() -> _ProfileObj:
    store = _ensure_store()
    p = store["profile"]
    vow_keywords = p.get("vow_keywords", [])
    if isinstance(vow_keywords, list):
        vow_keywords_str = ",".join([str(x) for x in vow_keywords if str(x).strip()])
    else:
        vow_keywords_str = str(vow_keywords or "")

    return _ProfileObj(
        id=1,
        responsibility=str(p.get("responsibility", "") or ""),
        talent=str(p.get("talent", "") or ""),
        dream=str(p.get("dream", "") or ""),
        vow=str(p.get("vow", "") or ""),
        vow_keywords=vow_keywords_str,
        mission_statement=str(p.get("mission_statement", "") or ""),
    )


def update_profile(
    responsibility: str = "",
    talent: str = "",
    dream: str = "",
    vow: str = "",
    vow_keywords: str = "",
    mission_statement: str = "",
) -> None:
    store = _ensure_store()
    kws = [x.strip() for x in (vow_keywords or "").split(",") if x.strip()]
    store["profile"] = {
        "name": store.get("profile", {}).get("name", ""),
        "responsibility": responsibility or "",
        "talent": talent or "",
        "dream": dream or "",
        "vow": vow or "",
        "vow_keywords": kws,
        "mission_statement": mission_statement or "",
    }


# ============================================================
# 3) Annual Dig：兼容 get_or_create_annual_dig / update_annual_dig
# ============================================================
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


def update_annual_dig(talent: dict, responsibility: dict, dream: dict, intersections: dict) -> None:
    store = _ensure_store()
    store["annual_dig"] = {
        "talent": talent or {},
        "responsibility": responsibility or {},
        "dream": dream or {},
        "intersections": intersections or {},
    }


# ============================================================
# 4) 36×10：Sprint / Task 对象（兼容属性访问）
# ============================================================
@dataclass
class _TaskObj:
    id: str
    title: str
    done: bool = False
    evidence: str = ""
    source_care_id: Optional[str] = None


@dataclass
class _SprintObj:
    sprint_no: int
    start_date: date
    end_date: date
    theme: str = ""
    objective: str = ""
    review: str = ""
    mit: str = ""


def regenerate_sprints(start: date) -> None:
    """生成 36 个 10 天周期（会清空旧 sprints 和 tasks）"""
    store = _ensure_store()
    sprints: List[Dict[str, Any]] = []
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
                "mit": "",
                "tasks": [],  # list[dict]
            }
        )
        cur = cur + timedelta(days=10)
    store["sprints"] = sprints


def get_sprints() -> List[dict]:
    store = _ensure_store()
    sprints = store.get("sprints", []) or []

    # ✅ 强制转换：如果有人误把 ORM 对象塞进来了，也变成 dict
    out = []
    for sp in sprints:
        if isinstance(sp, dict):
            out.append(sp)
        else:
            # 尽量从对象上取字段
            out.append({
                "sprint_no": getattr(sp, "sprint_no", None),
                "start_date": getattr(sp, "start_date", ""),
                "end_date": getattr(sp, "end_date", ""),
                "theme": getattr(sp, "theme", ""),
                "objective": getattr(sp, "objective", ""),
                "review": getattr(sp, "review", ""),
                "tasks": getattr(sp, "tasks", []) if hasattr(sp, "tasks") else [],
            })
    store["sprints"] = out
    return out



def get_sprints() -> List[_SprintObj]:
    """返回 Sprint 对象列表（兼容 sp.sprint_no / sp.start_date / sp.end_date）"""
    out: List[_SprintObj] = []
    for sp in _get_sprints_raw():
        try:
            sd = date.fromisoformat(sp.get("start_date"))
            ed = date.fromisoformat(sp.get("end_date"))
        except Exception:
            # 兜底：如果坏数据，跳过
            continue
        out.append(
            _SprintObj(
                sprint_no=int(sp.get("sprint_no", 0)),
                start_date=sd,
                end_date=ed,
                theme=str(sp.get("theme", "") or ""),
                objective=str(sp.get("objective", "") or ""),
                review=str(sp.get("review", "") or ""),
                mit=str(sp.get("mit", "") or ""),
            )
        )
    out.sort(key=lambda x: x.sprint_no)
    return out


def _get_sprint_raw_by_no(sprint_no: int) -> Optional[Dict[str, Any]]:
    for sp in _get_sprints_raw():
        if int(sp.get("sprint_no", 0)) == int(sprint_no):
            return sp
    return None


def update_sprint_text(sprint_no: int, theme: str = "", objective: str = "", review: str = "", mit: str = "") -> None:
    sp = _get_sprint_raw_by_no(sprint_no)
    if not sp:
        return
    sp["theme"] = theme or ""
    sp["objective"] = objective or ""
    sp["review"] = review or ""
    sp["mit"] = mit or ""


def add_task_to_sprint_unique(sprint_no: int, title: str, source_care_id: Optional[str] = None) -> None:
    sp = _get_sprint_raw_by_no(sprint_no)
    if not sp:
        return
    title = (title or "").strip()
    if not title:
        return
    for t in sp.get("tasks", []):
        if (t.get("title") or "").strip() == title:
            return
    sp["tasks"].append(
        {
            "id": str(uuid.uuid4()),
            "title": title,
            "done": False,
            "evidence": "",
            "source_care_id": source_care_id,
        }
    )


def list_tasks_for_sprint(sprint_no: int) -> List[_TaskObj]:
    sp = _get_sprint_raw_by_no(sprint_no)
    if not sp:
        return []
    out: List[_TaskObj] = []
    for t in sp.get("tasks", []) or []:
        out.append(
            _TaskObj(
                id=str(t.get("id", "")),
                title=str(t.get("title", "")),
                done=bool(t.get("done", False)),
                evidence=str(t.get("evidence", "") or ""),
                source_care_id=(t.get("source_care_id") or None),
            )
        )
    return out


def toggle_task_done(task_id: str, done: bool) -> None:
    store = _ensure_store()
    for sp in store.get("sprints", []) or []:
        for t in sp.get("tasks", []) or []:
            if str(t.get("id")) == str(task_id):
                t["done"] = bool(done)
                return


def update_task_evidence(task_id: str, evidence: str) -> None:
    store = _ensure_store()
    for sp in store.get("sprints", []) or []:
        for t in sp.get("tasks", []) or []:
            if str(t.get("id")) == str(task_id):
                t["evidence"] = evidence or ""
                return


# ============================================================
# 5) CARE：兼容 list_care_records / add_care_record / update / delete
# ============================================================
def list_care_records() -> List[Dict[str, Any]]:
    store = _ensure_store()
    return list(store.get("care_records", []) or [])


def add_care_record(
    capture_source: str,
    cognition: str,
    action: str,
    relationship: str,
    ego_drive: str,
    vow_tag: str,
    relevance_score: int,
    tags: str = "",
    linked_goal: str = "",
) -> None:
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
            "linked_goal": linked_goal or "",
            "created_at": date.today().isoformat(),
        },
    )


def update_care_record(care_id: str, **kwargs) -> None:
    store = _ensure_store()
    for r in store.get("care_records", []) or []:
        if str(r.get("id")) == str(care_id):
            for k, v in kwargs.items():
                r[k] = v
            return


def delete_care_record(care_id: str) -> None:
    store = _ensure_store()
    store["care_records"] = [r for r in (store.get("care_records", []) or []) if str(r.get("id")) != str(care_id)]


# ============================================================
# 6) JSON 备份/恢复（你“数据备份页”会用到）
# ============================================================
def export_user_json() -> bytes:
    store = _ensure_store()
    payload = {
        "user_key": st.session_state.get("user_key"),
        "STORE": store,
    }
    return json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")


def import_user_json(file_bytes: bytes) -> None:
    data = json.loads(file_bytes.decode("utf-8"))
    if "STORE" in data and isinstance(data["STORE"], dict):
        st.session_state["STORE"] = data["STORE"]
    # 保留当前浏览器的 user_key，不强制覆盖
    _ensure_user_key()

# ============================
# EXTRA COMPAT: for page ② (36×10)
# ============================

def get_sprint_by_no(sprint_no: int):
    """
    兼容旧代码：返回一个 _SprintObj（属性访问：.theme/.objective/...）
    若不存在返回 None
    """
    for sp in get_sprints():
        if int(sp.sprint_no) == int(sprint_no):
            return sp
    return None


def task_exists_in_sprint(sprint_no: int, title: str) -> bool:
    """兼容旧代码：判断某 sprint 是否已有同名任务"""
    title = (title or "").strip()
    if not title:
        return True
    for t in list_tasks_for_sprint(sprint_no):
        if (t.title or "").strip() == title:
            return True
    return False


def add_task_to_sprint(sprint_no: int, title: str, source_care_id=None):
    """
    兼容旧代码：允许重复插入（旧 db.py 有这个版本）
    但我们仍做最基本的空字符串过滤
    """
    sp = _get_sprint_raw_by_no(sprint_no)
    if not sp:
        return
    title = (title or "").strip()
    if not title:
        return
    sp["tasks"].append(
        {
            "id": str(uuid.uuid4()),
            "title": title,
            "done": False,
            "evidence": "",
            "source_care_id": source_care_id,
        }
    )


def delete_task(task_id: str):
    """如果你的 36×10 页面支持删除任务，补这个"""
    store = _ensure_store()
    for sp in store.get("sprints", []) or []:
        sp["tasks"] = [t for t in (sp.get("tasks", []) or []) if str(t.get("id")) != str(task_id)]


def update_task_title(task_id: str, new_title: str):
    """如果你的 36×10 页面支持编辑任务标题，补这个"""
    new_title = (new_title or "").strip()
    if not new_title:
        return
    store = _ensure_store()
    for sp in store.get("sprints", []) or []:
        for t in sp.get("tasks", []) or []:
            if str(t.get("id")) == str(task_id):
                t["title"] = new_title
                return


def clear_sprint_tasks(sprint_no: int):
    """如果你的 36×10 页面有“一键清空该周期任务”，补这个"""
    sp = _get_sprint_raw_by_no(sprint_no)
    if not sp:
        return
    sp["tasks"] = []
