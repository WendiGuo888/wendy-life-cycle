# -*- coding: utf-8 -*-
"""
Created on Mon Jan 26 16:36:32 2026

@author: wengu476
"""

from __future__ import annotations
from typing import List, Tuple
import re


def parse_keywords(raw: str) -> List[str]:
    if not raw:
        return []
    parts = re.split(r"[，,、;；\n]+", raw)
    return [p.strip() for p in parts if p.strip()]


def build_mission_statement(responsibility: str, talent: str, dream: str, vow: str) -> str:
    # 简单模板（MVP 不接外部 LLM）
    return (
        f"我将以【{talent.strip() or '我的天赋'}】为杠杆，"
        f"承担【{responsibility.strip() or '我应承担的责任'}】，"
        f"朝向【{dream.strip() or '我的梦想'}】前进，"
        f"用行动兑现【{vow.strip() or '我的愿力/使命'}】。"
    )


def generate_goals(vow: str, keywords: List[str]) -> List[dict]:
    # 生成 3~7 个目标（MVP：基于关键词 + 通用结构）
    base = []
    for k in keywords[:7]:
        base.append({"title": f"围绕「{k}」打造可复用成果", "metric": "产出≥1个可展示作品/案例"})
    # 补齐到至少 3 个
    while len(base) < 3:
        idx = len(base) + 1
        base.append({"title": f"年度关键目标 {idx}（对齐愿力）", "metric": "每季度有可衡量进展"})
    # 若关键词太多，截断到 7
    return base[:7]


def generate_backlog(goals: List[dict], keywords: List[str]) -> List[dict]:
    # 生成 10~30 条落地清单（项目/习惯/能力混合）
    items = []

    # 项目：每个目标给 2 个项目
    for g in goals:
        items.append({"title": f"{g['title']}：做一个作品/项目Demo", "category": "项目", "linked_goal": g["title"]})
        items.append({"title": f"{g['title']}：输出一篇总结/分享", "category": "项目", "linked_goal": g["title"]})

    # 习惯：通用 4 条
    habits = [
        "每10天做一次复盘（得失/调整/下一步）",
        "每周至少1次公开表达（写作/分享/讲解）",
        "每天1个最小行动（MIT相关）",
        "每10天整理一次 CARE 灵感并转为行动",
    ]
    for h in habits:
        items.append({"title": h, "category": "习惯", "linked_goal": ""})

    # 能力：根据关键词生成
    for k in keywords[:6]:
        items.append({"title": f"能力提升：围绕「{k}」系统学习并做练习", "category": "能力", "linked_goal": ""})

    # 控制数量 10~30
    if len(items) < 10:
        # 补齐
        while len(items) < 10:
            items.append({"title": "补充事项：对齐愿力的一个可执行动作", "category": "项目", "linked_goal": ""})
    return items[:30]
