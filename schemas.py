# -*- coding: utf-8 -*-
"""
Created on Mon Jan 26 16:36:09 2026

@author: wengu476
"""

from pydantic import BaseModel, Field
from typing import Optional


class GoalSchema(BaseModel):
    title: str
    metric: str = ""


class BacklogItemSchema(BaseModel):
    title: str
    category: str = Field(default="项目", pattern="^(项目|习惯|能力)$")
    linked_goal: str = ""
    sprint_no: Optional[int] = None


class CareRecordSchema(BaseModel):
    capture_source: str
    cognition: str = ""
    action: str
    relationship: str = ""
    ego_drive: str = ""
    vow_tag: str = ""
    relevance_score: int = Field(ge=0, le=5)
    tags: str = ""
    linked_goal: str = ""
