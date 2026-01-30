# -*- coding: utf-8 -*-
"""
Created on Mon Jan 26 16:35:27 2026

@author: wengu476
"""


from __future__ import annotations

import json

from datetime import date
from typing import List, Optional

from sqlalchemy import (
    create_engine, Column, Integer, String, Text, Date, Boolean, ForeignKey
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship


DB_URL = "sqlite:///app.db"

engine = create_engine(DB_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base = declarative_base()


# -------------------------
# ORM Models
# -------------------------

# -------------------------
# 年度挖掘（结构化）表：四象限 + 交集清单
# -------------------------
class AnnualDig(Base):
    __tablename__ = "annual_dig"

    id = Column(Integer, primary_key=True)  # 固定使用 1
    talent_json = Column(Text, default="{}")
    responsibility_json = Column(Text, default="{}")
    dream_json = Column(Text, default="{}")
    intersections_json = Column(Text, default="{}")  # 中心/两两交集/单圈清单



class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True)
    responsibility = Column(Text, default="")
    talent = Column(Text, default="")
    dream = Column(Text, default="")
    vow = Column(Text, default="")
    vow_keywords = Column(Text, default="")  # 用逗号分隔保存
    mission_statement = Column(Text, default="")

    goals = relationship("Goal", back_populates="profile", cascade="all, delete-orphan")
    backlog_items = relationship("BacklogItem", back_populates="profile", cascade="all, delete-orphan")


class Goal(Base):
    __tablename__ = "goals"

    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey("profiles.id"))
    title = Column(String(255), nullable=False)
    metric = Column(String(255), default="")

    profile = relationship("Profile", back_populates="goals")


class BacklogItem(Base):
    __tablename__ = "backlog_items"

    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey("profiles.id"))
    title = Column(String(255), nullable=False)
    category = Column(String(50), default="项目")  # 项目/习惯/能力
    linked_goal = Column(String(255), default="")
    sprint_no = Column(Integer, nullable=True)  # 1~36

    profile = relationship("Profile", back_populates="backlog_items")


class Sprint(Base):
    __tablename__ = "sprints"

    id = Column(Integer, primary_key=True)
    sprint_no = Column(Integer, nullable=False, unique=True)  # 1~36
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)

    theme = Column(String(255), default="")
    objective = Column(Text, default="")
    review = Column(Text, default="")
    mit = Column(String(255), default="")  # Most Important Thing

    tasks = relationship("SprintTask", back_populates="sprint", cascade="all, delete-orphan")


class SprintTask(Base):
    __tablename__ = "sprint_tasks"

    id = Column(Integer, primary_key=True)
    sprint_id = Column(Integer, ForeignKey("sprints.id"))
    title = Column(String(255), nullable=False)
    done = Column(Boolean, default=False)
    evidence = Column(Text, default="")
    source_care_id = Column(Integer, nullable=True)  # 来自 CARE 的记录 id

    sprint = relationship("Sprint", back_populates="tasks")


class CareRecord(Base):
    __tablename__ = "care_records"

    id = Column(Integer, primary_key=True)
    capture_source = Column(Text, nullable=False)  # inspiration 原文/链接
    cognition = Column(Text, default="")
    action = Column(Text, nullable=False)
    relationship = Column(Text, default="")
    ego_drive = Column(Text, default="")
    vow_tag = Column(String(255), default="")
    relevance_score = Column(Integer, nullable=False, default=0)  # 0~5
    tags = Column(String(255), default="")  # 逗号分隔
    linked_goal = Column(String(255), default="")

    created_at = Column(Date, default=date.today)


# -------------------------
# DB Helpers
# -------------------------
def init_db() -> None:
    Base.metadata.create_all(bind=engine)


def get_session():
    return SessionLocal()



def update_profile(
    responsibility: str,
    talent: str,
    dream: str,
    vow: str,
    vow_keywords: str,
    mission_statement: str,
):
    db = get_session()
    try:
        prof = db.query(Profile).filter(Profile.id == 1).first()
        if not prof:
            prof = Profile(id=1)
            db.add(prof)

        prof.responsibility = responsibility
        prof.talent = talent
        prof.dream = dream
        prof.vow = vow
        prof.vow_keywords = vow_keywords
        prof.mission_statement = mission_statement

        db.commit()
    finally:
        db.close()


def replace_goals(goals: List[dict]):
    db = get_session()
    try:
        prof = db.query(Profile).filter(Profile.id == 1).first()
        if not prof:
            prof = Profile(id=1)
            db.add(prof)
            db.commit()
            db.refresh(prof)

        # 清空旧 goals
        db.query(Goal).filter(Goal.profile_id == 1).delete()
        db.commit()

        for g in goals:
            db.add(Goal(profile_id=1, title=g["title"], metric=g.get("metric", "")))
        db.commit()
    finally:
        db.close()


def replace_backlog(items: List[dict]):
    db = get_session()
    try:
        prof = db.query(Profile).filter(Profile.id == 1).first()
        if not prof:
            prof = Profile(id=1)
            db.add(prof)
            db.commit()
            db.refresh(prof)

        db.query(BacklogItem).filter(BacklogItem.profile_id == 1).delete()
        db.commit()

        for it in items:
            db.add(
                BacklogItem(
                    profile_id=1,
                    title=it["title"],
                    category=it.get("category", "项目"),
                    linked_goal=it.get("linked_goal", ""),
                    sprint_no=it.get("sprint_no", None),
                )
            )
        db.commit()
    finally:
        db.close()



def assign_backlog_item_to_sprint(item_id: int, sprint_no: Optional[int]):
    db = get_session()
    try:
        item = db.query(BacklogItem).filter(BacklogItem.id == item_id).first()
        if not item:
            return
        item.sprint_no = sprint_no
        db.commit()
    finally:
        db.close()



def get_sprint_by_no(sprint_no: int) -> Optional[Sprint]:
    db = get_session()
    try:
        return db.query(Sprint).filter(Sprint.sprint_no == sprint_no).first()
    finally:
        db.close()


def regenerate_sprints(start: date):
    """生成/重建 36 个 10 天 sprint（会清空旧 sprint 与 tasks）"""
    db = get_session()
    try:
        # 删除旧数据
        db.query(SprintTask).delete()
        db.query(Sprint).delete()
        db.commit()

        # 生成 36 个 sprint
        cur = start
        for i in range(1, 37):
            s = Sprint(
                sprint_no=i,
                start_date=cur,
                end_date=date.fromordinal(cur.toordinal() + 9),
                theme="",
                objective="",
                review="",
                mit="",
            )
            db.add(s)
            cur = date.fromordinal(cur.toordinal() + 10)

        db.commit()
    finally:
        db.close()


def update_sprint_text(sprint_no: int, theme: str, objective: str, review: str, mit: str):
    db = get_session()
    try:
        s = db.query(Sprint).filter(Sprint.sprint_no == sprint_no).first()
        if not s:
            return
        s.theme = theme
        s.objective = objective
        s.review = review
        s.mit = mit
        db.commit()
    finally:
        db.close()


def add_task_to_sprint(sprint_no: int, title: str, source_care_id: Optional[int] = None):
    db = get_session()
    try:
        s = db.query(Sprint).filter(Sprint.sprint_no == sprint_no).first()
        if not s:
            return
        t = SprintTask(sprint_id=s.id, title=title, done=False, evidence="", source_care_id=source_care_id)
        db.add(t)
        db.commit()
    finally:
        db.close()


def toggle_task_done(task_id: int, done: bool):
    db = get_session()
    try:
        t = db.query(SprintTask).filter(SprintTask.id == task_id).first()
        if not t:
            return
        t.done = done
        db.commit()
    finally:
        db.close()


def update_task_evidence(task_id: int, evidence: str):
    db = get_session()
    try:
        t = db.query(SprintTask).filter(SprintTask.id == task_id).first()
        if not t:
            return
        t.evidence = evidence
        db.commit()
    finally:
        db.close()


def list_tasks_for_sprint(sprint_no: int) -> List[SprintTask]:
    db = get_session()
    try:
        s = db.query(Sprint).filter(Sprint.sprint_no == sprint_no).first()
        if not s:
            return []
        return db.query(SprintTask).filter(SprintTask.sprint_id == s.id).order_by(SprintTask.id.asc()).all()
    finally:
        db.close()


def add_care_record(
    capture_source: str,
    cognition: str,
    action: str,
    relationship: str,
    ego_drive: str,
    vow_tag: str,
    relevance_score: int,
    tags: str,
    linked_goal: str,
):
    db = get_session()
    try:
        r = CareRecord(
            capture_source=capture_source,
            cognition=cognition,
            action=action,
            relationship=relationship,
            ego_drive=ego_drive,
            vow_tag=vow_tag,
            relevance_score=relevance_score,
            tags=tags,
            linked_goal=linked_goal,
        )
        db.add(r)
        db.commit()
    finally:
        db.close()

        
def task_exists_in_sprint(sprint_no: int, title: str) -> bool:
    db = get_session()
    try:
        s = db.query(Sprint).filter(Sprint.sprint_no == sprint_no).first()
        if not s:
            return False
        t = (
            db.query(SprintTask)
            .filter(SprintTask.sprint_id == s.id, SprintTask.title == title)
            .first()
        )
        return t is not None
    finally:
        db.close()


def add_task_to_sprint_unique(sprint_no: int, title: str, source_care_id: int | None = None):
    """如果同名任务已存在，则不重复添加（用于从 Backlog 导入、避免重复）"""
    if not title.strip():
        return
    if task_exists_in_sprint(sprint_no, title.strip()):
        return
    add_task_to_sprint(sprint_no, title.strip(), source_care_id=source_care_id)



# -------------------------
# CARE CRUD
# -------------------------
def update_care_record(
    care_id: int,
    capture_source: str,
    cognition: str,
    action: str,
    relationship: str,
    ego_drive: str,
    vow_tag: str,
    relevance_score: int,
    tags: str,
    linked_goal: str,
):
    db = get_session()
    try:
        r = db.query(CareRecord).filter(CareRecord.id == care_id).first()
        if not r:
            return
        r.capture_source = capture_source
        r.cognition = cognition
        r.action = action
        r.relationship = relationship
        r.ego_drive = ego_drive
        r.vow_tag = vow_tag
        r.relevance_score = int(relevance_score)
        r.tags = tags
        r.linked_goal = linked_goal
        db.commit()
    finally:
        db.close()


def delete_care_record(care_id: int):
    db = get_session()
    try:
        r = db.query(CareRecord).filter(CareRecord.id == care_id).first()
        if r:
            db.delete(r)
            db.commit()
    finally:
        db.close()


# -------------------------
# Backlog CRUD
# -------------------------
def add_backlog_item(title: str, category: str = "项目", linked_goal: str = "", sprint_no: int | None = None):
    db = get_session()
    try:
        db.add(
            BacklogItem(
                profile_id=1,
                title=title,
                category=category,
                linked_goal=linked_goal,
                sprint_no=sprint_no,
            )
        )
        db.commit()
    finally:
        db.close()


def update_backlog_item(item_id: int, title: str, category: str, linked_goal: str, sprint_no: int | None):
    db = get_session()
    try:
        it = db.query(BacklogItem).filter(BacklogItem.id == item_id).first()
        if not it:
            return
        it.title = title
        it.category = category
        it.linked_goal = linked_goal
        it.sprint_no = sprint_no
        db.commit()
    finally:
        db.close()


def delete_backlog_item(item_id: int):
    db = get_session()
    try:
        it = db.query(BacklogItem).filter(BacklogItem.id == item_id).first()
        if it:
            db.delete(it)
            db.commit()
    finally:
        db.close()


# -------------------------
# Goal CRUD（用于年度挖掘页可编辑）
# -------------------------
def add_goal(title: str, metric: str = ""):
    db = get_session()
    try:
        db.add(Goal(profile_id=1, title=title, metric=metric))
        db.commit()
    finally:
        db.close()


def update_goal(goal_id: int, title: str, metric: str):
    db = get_session()
    try:
        g = db.query(Goal).filter(Goal.id == goal_id).first()
        if not g:
            return
        g.title = title
        g.metric = metric
        db.commit()
    finally:
        db.close()


def delete_goal(goal_id: int):
    db = get_session()
    try:
        g = db.query(Goal).filter(Goal.id == goal_id).first()
        if g:
            db.delete(g)
            db.commit()
    finally:
        db.close()

# -------------------------
# SAFETY PATCH：如果你之前粘贴时覆盖/丢失了部分函数，这里补回关键查询函数
# -------------------------

def list_care_records():
    db = get_session()
    try:
        return db.query(CareRecord).order_by(CareRecord.id.desc()).all()
    finally:
        db.close()


def list_goals():
    db = get_session()
    try:
        return db.query(Goal).filter(Goal.profile_id == 1).order_by(Goal.id.asc()).all()
    finally:
        db.close()


def list_backlog():
    db = get_session()
    try:
        return db.query(BacklogItem).filter(BacklogItem.profile_id == 1).order_by(BacklogItem.id.asc()).all()
    finally:
        db.close()


def get_sprints():
    db = get_session()
    try:
        return db.query(Sprint).order_by(Sprint.sprint_no.asc()).all()
    finally:
        db.close()


def get_or_create_profile():
    db = get_session()
    try:
        prof = db.query(Profile).filter(Profile.id == 1).first()
        if not prof:
            prof = Profile(id=1)
            db.add(prof)
            db.commit()
            db.refresh(prof)
        return prof
    finally:
        db.close()
        



        
def get_or_create_annual_dig():
    """获取/创建年度挖掘结构化数据（固定 id=1）"""
    db = get_session()
    try:
        row = db.query(AnnualDig).filter(AnnualDig.id == 1).first()
        if not row:
            row = AnnualDig(
                id=1,
                talent_json="{}",
                responsibility_json="{}",
                dream_json="{}",
                intersections_json="{}",
            )
            db.add(row)
            db.commit()
            db.refresh(row)
        return row
    finally:
        db.close()


def update_annual_dig(talent: dict, responsibility: dict, dream: dict, intersections: dict):
    """保存年度挖掘结构化数据（四象限 + 交汇清单）"""
    db = get_session()
    try:
        row = db.query(AnnualDig).filter(AnnualDig.id == 1).first()
        if not row:
            row = AnnualDig(id=1)
            db.add(row)

        row.talent_json = json.dumps(talent or {}, ensure_ascii=False)
        row.responsibility_json = json.dumps(responsibility or {}, ensure_ascii=False)
        row.dream_json = json.dumps(dream or {}, ensure_ascii=False)
        row.intersections_json = json.dumps(intersections or {}, ensure_ascii=False)

        db.commit()
    finally:
        db.close()


