"""Main story structure engine for narrative framework implementation."""

from datetime import datetime
from typing import Optional
import uuid

from chai.models.main_story_structure import (
    MainStoryStructure,
    MainStoryStructureType,
    StoryBeat,
    StoryBeatType,
    StoryBeatStatus,
    ActStructure,
    StructureAnalysis,
)
from chai.models.character_growth_arc import CharacterGrowthArcSystem
from chai.services import AIService


# Three-Act Structure Template (24 chapters: 6-12-6 split)
THREE_ACT_TEMPLATE = {
    "name": "三幕式结构",
    "acts": [
        {
            "id": "act1",
            "number": 1,
            "name": "建置",
            "description": "介绍世界、角色和冲突",
            "start_chapter": 1,
            "end_chapter": 6,
            "purpose": "建立故事基础，介绍主要角色和世界",
            "key_conflict": "日常世界的冲突",
            "thematic_focus": "主角现状",
        },
        {
            "id": "act2",
            "number": 2,
            "name": "对抗",
            "description": "主角面对冲突，克服障碍",
            "start_chapter": 7,
            "end_chapter": 18,
            "purpose": "展现主角成长，对抗核心冲突",
            "key_conflict": "核心冲突的升级",
            "thematic_focus": "挑战与成长",
        },
        {
            "id": "act3",
            "number": 3,
            "name": "解决",
            "description": "高潮对决，问题解决",
            "start_chapter": 19,
            "end_chapter": 24,
            "purpose": "解决核心冲突，展现改变",
            "key_conflict": "最终对决",
            "thematic_focus": "新常态",
        },
    ],
    "beats": [
        # Act 1 - Setup
        {"type": StoryBeatType.EXPOSITION, "name": "建置-世界", "order": 1, "act": 1, "start": 1, "end": 2, "purpose": "介绍故事世界", "tension": "low"},
        {"type": StoryBeatType.EXPOSITION, "name": "建置-角色", "order": 2, "act": 1, "start": 2, "end": 3, "purpose": "介绍主要角色", "tension": "low"},
        {"type": StoryBeatType.INCITING_INCIDENT, "name": "催化事件", "order": 3, "act": 1, "start": 3, "end": 4, "purpose": "打破平衡的事件", "tension": "moderate"},
        {"type": StoryBeatType.RISING_ACTION, "name": "反应", "order": 4, "act": 1, "start": 4, "end": 5, "purpose": "角色对事件的反应", "tension": "moderate"},
        {"type": StoryBeatType.RISING_ACTION, "name": "跨越门槛", "order": 5, "act": 1, "start": 5, "end": 6, "purpose": "正式进入新世界", "tension": "high"},
        # Act 2 - Confrontation
        {"type": StoryBeatType.RISING_ACTION, "name": "新世界", "order": 6, "act": 2, "start": 7, "end": 8, "purpose": "适应新环境", "tension": "moderate"},
        {"type": StoryBeatType.RISING_ACTION, "name": "试炼开始", "order": 7, "act": 2, "start": 8, "end": 10, "purpose": "面对第一个考验", "tension": "high"},
        {"type": StoryBeatType.RISING_ACTION, "name": "盟友与敌人", "order": 8, "act": 2, "start": 10, "end": 12, "purpose": "结交盟友，识别敌人", "tension": "moderate"},
        {"type": StoryBeatType.MIDPOINT, "name": "中点转折", "order": 9, "act": 2, "start": 12, "end": 14, "purpose": "重大发现或转折", "tension": "high"},
        {"type": StoryBeatType.RISING_ACTION, "name": "虚假胜利", "order": 10, "act": 2, "start": 14, "end": 15, "purpose": "看似成功实则危机", "tension": "moderate"},
        {"type": StoryBeatType.RISING_ACTION, "name": "全面压迫", "order": 11, "act": 2, "start": 15, "end": 17, "purpose": "冲突全面升级", "tension": "high"},
        {"type": StoryBeatType.CRISIS, "name": "最低点", "order": 12, "act": 2, "start": 17, "end": 18, "purpose": "主角跌入谷底", "tension": "high"},
        # Act 3 - Resolution
        {"type": StoryBeatType.RISING_ACTION, "name": "重新发现", "order": 13, "act": 3, "start": 19, "end": 20, "purpose": "找到新方向", "tension": "moderate"},
        {"type": StoryBeatType.RISING_ACTION, "name": "最终计划", "order": 14, "act": 3, "start": 20, "end": 21, "purpose": "制定最终方案", "tension": "moderate"},
        {"type": StoryBeatType.CLIMAX, "name": "高潮对决", "order": 15, "act": 3, "start": 21, "end": 22, "purpose": "决定性对决", "tension": "climax"},
        {"type": StoryBeatType.FALLING_ACTION, "name": "余波", "order": 16, "act": 3, "start": 22, "end": 23, "purpose": "冲突后的影响", "tension": "moderate"},
        {"type": StoryBeatType.RESOLUTION, "name": "收尾", "order": 17, "act": 3, "start": 23, "end": 24, "purpose": "问题解决，新常态", "tension": "low"},
    ],
}

# Hero's Journey Template (17 stages, mapped to ~24 chapters)
HEROS_JOURNEY_TEMPLATE = {
    "name": "英雄之旅",
    "acts": [
        {
            "id": "act1",
            "number": 1,
            "name": "出发",
            "description": "英雄收到召唤，离开普通世界",
            "start_chapter": 1,
            "end_chapter": 6,
            "purpose": "建立英雄和普通世界",
            "key_conflict": "是否接受召唤",
            "thematic_focus": "现状与改变的矛盾",
        },
        {
            "id": "act2",
            "number": 2,
            "name": "考验",
            "description": "英雄在特殊世界中面对考验",
            "start_chapter": 7,
            "end_chapter": 18,
            "purpose": "英雄成长，获得盟友",
            "key_conflict": "与敌人的冲突",
            "thematic_focus": "成长与牺牲",
        },
        {
            "id": "act3",
            "number": 3,
            "name": "回归",
            "description": "英雄带着收获回归",
            "start_chapter": 19,
            "end_chapter": 24,
            "purpose": "最终胜利，英雄蜕变",
            "key_conflict": "最终考验",
            "thematic_focus": "改变与传承",
        },
    ],
    "beats": [
        # Act 1 - Departure
        {"type": StoryBeatType.ORDINARY_WORLD, "name": "普通世界", "order": 1, "act": 1, "start": 1, "end": 2, "purpose": "展示英雄平凡的生活", "tension": "low"},
        {"type": StoryBeatType.CALL_TO_ADVENTURE, "name": "冒险召唤", "order": 2, "act": 1, "start": 3, "end": 4, "purpose": "收到改变命运的召唤", "tension": "moderate"},
        {"type": StoryBeatType.REFUSAL_OF_CALL, "name": "拒绝召唤", "order": 3, "act": 1, "start": 4, "end": 5, "purpose": "英雄犹豫或拒绝", "tension": "moderate"},
        {"type": StoryBeatType.MEETING_THE_MENTOR, "name": "遇到导师", "order": 4, "act": 1, "start": 5, "end": 6, "purpose": "获得指引或学习技能", "tension": "moderate"},
        {"type": StoryBeatType.CROSSING_THE_THRESHOLD, "name": "跨越门槛", "order": 5, "act": 1, "start": 6, "end": 7, "purpose": "正式踏上冒险旅程", "tension": "high"},
        # Act 2 - Initiation
        {"type": StoryBeatType.TESTS_ALLIES_ENEMIES, "name": "考验与盟友", "order": 6, "act": 2, "start": 7, "end": 10, "purpose": "面对挑战，结识伙伴", "tension": "high"},
        {"type": StoryBeatType.APPROACH_TO_INMOST_CAVE, "name": "接近洞穴", "order": 7, "act": 2, "start": 10, "end": 12, "purpose": "准备面对最大挑战", "tension": "moderate"},
        {"type": StoryBeatType.ORDEAL, "name": "最深处的考验", "order": 8, "act": 2, "start": 12, "end": 14, "purpose": "面临最大考验", "tension": "high"},
        {"type": StoryBeatType.REWARD, "name": "获得奖励", "order": 9, "act": 2, "start": 14, "end": 16, "purpose": "获得奖励或完成目标", "tension": "moderate"},
        {"type": StoryBeatType.RESURRECTION, "name": "复活", "order": 10, "act": 2, "start": 16, "end": 18, "purpose": "在考验中重生", "tension": "high"},
        # Act 3 - Return
        {"type": StoryBeatType.THE_ROAD_BACK, "name": "回归之路", "order": 11, "act": 3, "start": 19, "end": 20, "purpose": "带着改变回归", "tension": "moderate"},
        {"type": StoryBeatType.RESURRECTION, "name": "最终复活", "order": 12, "act": 3, "start": 20, "end": 22, "purpose": "最终考验中的蜕变", "tension": "climax"},
        {"type": StoryBeatType.RETURN_WITH_ELIXIR, "name": "带着精华回归", "order": 13, "act": 3, "start": 22, "end": 24, "purpose": "带着收获回归，新常态", "tension": "low"},
    ],
}

# Seven-Point Story Structure Template
SEVEN_POINT_TEMPLATE = {
    "name": "七点结构",
    "acts": [
        {
            "id": "act1",
            "number": 1,
            "name": "起点",
            "description": "建立故事世界和平衡",
            "start_chapter": 1,
            "end_chapter": 6,
            "purpose": "吸引读者，建立平衡",
            "key_conflict": "表面平静下的暗流",
            "thematic_focus": "现状",
        },
        {
            "id": "act2",
            "number": 2,
            "name": "对抗",
            "description": "主角面对并对抗冲突",
            "start_chapter": 7,
            "end_chapter": 18,
            "purpose": "展现冲突的升级",
            "key_conflict": "核心冲突",
            "thematic_focus": "挣扎与成长",
        },
        {
            "id": "act3",
            "number": 3,
            "name": "解决",
            "description": "最终对决，问题解决",
            "start_chapter": 19,
            "end_chapter": 24,
            "purpose": "解决冲突，建立新平衡",
            "key_conflict": "最终对决",
            "thematic_focus": "改变与新常态",
        },
    ],
    "beats": [
        {"type": StoryBeatType.HOOK, "name": "钩子", "order": 1, "act": 1, "start": 1, "end": 2, "purpose": "吸引读者的开场", "tension": "moderate"},
        {"type": StoryBeatType.FIRST_TURN, "name": "第一转折", "order": 2, "act": 1, "start": 2, "end": 4, "purpose": "打破平衡的事件", "tension": "moderate"},
        {"type": StoryBeatType.PINCER_ONE, "name": "第一次夹钳", "order": 3, "act": 1, "start": 4, "end": 6, "purpose": "主角看似成功", "tension": "high"},
        {"type": StoryBeatType.FIRST_TURNING_POINT, "name": "第一转折点", "order": 4, "act": 1, "start": 6, "end": 8, "purpose": "新局势形成", "tension": "high"},
        {"type": StoryBeatType.MIDPOINT, "name": "中点", "order": 5, "act": 2, "start": 8, "end": 12, "purpose": "重大发现或转折", "tension": "high"},
        {"type": StoryBeatType.SECOND_TURN, "name": "第二转折", "order": 6, "act": 2, "start": 12, "end": 14, "purpose": "局势再次变化", "tension": "moderate"},
        {"type": StoryBeatType.ALL_IS_LOST, "name": "全失时刻", "order": 7, "act": 2, "start": 14, "end": 16, "purpose": "最低谷时刻", "tension": "high"},
        {"type": StoryBeatType.DARK_MOMENT, "name": "黑暗时刻", "order": 8, "act": 2, "start": 16, "end": 18, "purpose": "看似无望", "tension": "high"},
        {"type": StoryBeatType.SECOND_TURNING_POINT, "name": "第二转折点", "order": 9, "act": 3, "start": 18, "end": 20, "purpose": "找到新方向", "tension": "moderate"},
        {"type": StoryBeatType.THIRD_TURNING_POINT, "name": "第三转折点", "order": 10, "act": 3, "start": 20, "end": 22, "purpose": "最终对决", "tension": "climax"},
        {"type": StoryBeatType.RESOLUTION, "name": "结局", "order": 11, "act": 3, "start": 22, "end": 24, "purpose": "解决与收尾", "tension": "low"},
    ],
}

# Save the Cat Template (Blake Snyder's 15 beats)
SAVE_THE_CAT_TEMPLATE = {
    "name": "救猫咪",
    "acts": [
        {
            "id": "act1",
            "number": 1,
            "name": "第一幕",
            "description": "建立世界，催化剂事件",
            "start_chapter": 1,
            "end_chapter": 6,
            "purpose": "建立故事世界",
            "key_conflict": "是否行动",
            "thematic_focus": "现状",
        },
        {
            "id": "act2a",
            "number": 2,
            "name": "第二幕前半",
            "description": "新世界中的探索",
            "start_chapter": 7,
            "end_chapter": 12,
            "purpose": "适应新环境",
            "key_conflict": "应对挑战",
            "thematic_focus": "成长",
        },
        {
            "id": "act2b",
            "number": 3,
            "name": "第二幕后半",
            "description": "冲突全面升级",
            "start_chapter": 13,
            "end_chapter": 18,
            "purpose": "面对核心冲突",
            "key_conflict": "核心冲突升级",
            "thematic_focus": "牺牲",
        },
        {
            "id": "act3",
            "number": 4,
            "name": "第三幕",
            "description": "最终对决，问题解决",
            "start_chapter": 19,
            "end_chapter": 24,
            "purpose": "解决冲突",
            "key_conflict": "最终对决",
            "thematic_focus": "改变",
        },
    ],
    "beats": [
        {"type": StoryBeatType.OPENING_IMAGE, "name": "开场画面", "order": 1, "act": 1, "start": 1, "end": 2, "purpose": "建立调性，展现主题", "tension": "low"},
        {"type": StoryBeatType.THEME_STATED, "name": "主题呈现", "order": 2, "act": 1, "start": 2, "end": 3, "purpose": "提出故事主题", "tension": "low"},
        {"type": StoryBeatType.SETUP, "name": "开场设定", "order": 3, "act": 1, "start": 3, "end": 5, "purpose": "建立世界与角色", "tension": "moderate"},
        {"type": StoryBeatType.CATALYST, "name": "催化剂", "order": 4, "act": 1, "start": 5, "end": 6, "purpose": "改变一切的事件", "tension": "high"},
        {"type": StoryBeatType.DEBATE, "name": "争论", "order": 5, "act": 1, "start": 6, "end": 7, "purpose": "主角抵抗改变", "tension": "moderate"},
        {"type": StoryBeatType.BREAK_INTO_TWO, "name": "进入第二幕", "order": 6, "act": 2, "start": 7, "end": 8, "purpose": "正式进入新世界", "tension": "high"},
        {"type": StoryBeatType.B_STORY, "name": "B故事", "order": 7, "act": 2, "start": 8, "end": 10, "purpose": "引入次要情节线", "tension": "moderate"},
        {"type": StoryBeatType.FUN_AND_GAMES, "name": "游戏时间", "order": 8, "act": 2, "start": 10, "end": 12, "purpose": "中间段，尝试新道路", "tension": "moderate"},
        {"type": StoryBeatType.MIDPOINT, "name": "中点", "order": 9, "act": 2, "start": 12, "end": 14, "purpose": "重大转折", "tension": "high"},
        {"type": StoryBeatType.BAD_GUYS_CLOSE_IN, "name": "坏人逼近", "order": 10, "act": 3, "start": 14, "end": 16, "purpose": "冲突全面升级", "tension": "high"},
        {"type": StoryBeatType.ALL_IS_LOST, "name": "全失时刻", "order": 11, "act": 3, "start": 16, "end": 17, "purpose": "最黑暗时刻", "tension": "high"},
        {"type": StoryBeatType.DARK_NIGHT_OF_SOUL, "name": "灵魂黑夜", "order": 12, "act": 3, "start": 17, "end": 18, "purpose": "跌至谷底", "tension": "high"},
        {"type": StoryBeatType.BREAK_INTO_THREE, "name": "进入第三幕", "order": 13, "act": 4, "start": 19, "end": 20, "purpose": "找到解决方案", "tension": "moderate"},
        {"type": StoryBeatType.FINALE, "name": "结局", "order": 14, "act": 4, "start": 20, "end": 23, "purpose": "最终对决，问题解决", "tension": "climax"},
        {"type": StoryBeatType.FINAL_IMAGE, "name": "最终画面", "order": 15, "act": 4, "start": 23, "end": 24, "purpose": "问题解决，新常态", "tension": "low"},
    ],
}

# Freytag's Pyramid Template
FREYTAGS_PYRAMID_TEMPLATE = {
    "name": "弗莱塔格金字塔",
    "acts": [
        {
            "id": "act1",
            "number": 1,
            "name": "上升动作",
            "description": "建立冲突， tension 上升",
            "start_chapter": 1,
            "end_chapter": 12,
            "purpose": "建立冲突基础",
            "key_conflict": "冲突的出现",
            "thematic_focus": "现状到冲突",
        },
        {
            "id": "act2",
            "number": 2,
            "name": "高潮",
            "description": "故事的最高点",
            "start_chapter": 13,
            "end_chapter": 14,
            "purpose": "故事的最高潮",
            "key_conflict": "核心冲突的爆发",
            "thematic_focus": "转变点",
        },
        {
            "id": "act3",
            "number": 3,
            "name": "下降动作",
            "description": "冲突解决， tension 下降",
            "start_chapter": 15,
            "end_chapter": 24,
            "purpose": "解决冲突",
            "key_conflict": "冲突的解决",
            "thematic_focus": "新常态",
        },
    ],
    "beats": [
        {"type": StoryBeatType.EXPOSITION, "name": " expositions", "order": 1, "act": 1, "start": 1, "end": 3, "purpose": "介绍背景和人物", "tension": "low"},
        {"type": StoryBeatType.RISING_ACTION, "name": "上升动作开始", "order": 2, "act": 1, "start": 3, "end": 6, "purpose": "冲突开始出现", "tension": "moderate"},
        {"type": StoryBeatType.RISING_ACTION, "name": "上升动作发展", "order": 3, "act": 1, "start": 6, "end": 10, "purpose": "冲突升级", "tension": "high"},
        {"type": StoryBeatType.MIDPOINT, "name": "高潮前奏", "order": 4, "act": 1, "start": 10, "end": 12, "purpose": "为高潮做准备", "tension": "high"},
        {"type": StoryBeatType.CLIMAX, "name": "高潮", "order": 5, "act": 2, "start": 12, "end": 14, "purpose": "故事最高点", "tension": "climax"},
        {"type": StoryBeatType.FALLING_ACTION, "name": "下降动作开始", "order": 6, "act": 3, "start": 14, "end": 17, "purpose": "高潮后的影响", "tension": "moderate"},
        {"type": StoryBeatType.FALLING_ACTION, "name": "下降动作发展", "order": 7, "act": 3, "start": 17, "end": 20, "purpose": "冲突解决", "tension": "moderate"},
        {"type": StoryBeatType.RESOLUTION, "name": "结局", "order": 8, "act": 3, "start": 20, "end": 24, "purpose": "恢复正常或新常态", "tension": "low"},
    ],
}

# Kishotenketsu Template (Four-Act Chinese/Japanese structure)
KISHOTENKETSU_TEMPLATE = {
    "name": "起承转合",
    "acts": [
        {
            "id": "act1",
            "number": 1,
            "name": "起",
            "description": "介绍人物和情境",
            "start_chapter": 1,
            "end_chapter": 6,
            "purpose": "建立故事基础",
            "key_conflict": "引入人物和情境",
            "thematic_focus": "介绍",
        },
        {
            "id": "act2",
            "number": 2,
            "name": "承",
            "description": "发展人物和情境",
            "start_chapter": 7,
            "end_chapter": 14,
            "purpose": "深化故事",
            "key_conflict": "深化人物关系",
            "thematic_focus": "发展",
        },
        {
            "id": "act3",
            "number": 3,
            "name": "转",
            "description": "引入转折或意外",
            "start_chapter": 15,
            "end_chapter": 19,
            "purpose": "制造转折或惊喜",
            "key_conflict": "转折带来的冲突",
            "thematic_focus": "转折",
        },
        {
            "id": "act4",
            "number": 4,
            "name": "合",
            "description": "整合和结局",
            "start_chapter": 20,
            "end_chapter": 24,
            "purpose": "整合所有元素",
            "key_conflict": "冲突的解决",
            "thematic_focus": "整合",
        },
    ],
    "beats": [
        {"type": StoryBeatType.INTRODUCTION, "name": "起-引入", "order": 1, "act": 1, "start": 1, "end": 3, "purpose": "介绍人物和情境", "tension": "low"},
        {"type": StoryBeatType.INTRODUCTION, "name": "起-设定", "order": 2, "act": 1, "start": 3, "end": 6, "purpose": "设定故事背景", "tension": "low"},
        {"type": StoryBeatType.DEVELOPMENT, "name": "承-发展", "order": 3, "act": 2, "start": 7, "end": 10, "purpose": "发展人物关系", "tension": "moderate"},
        {"type": StoryBeatType.DEVELOPMENT, "name": "承-深化", "order": 4, "act": 2, "start": 10, "end": 14, "purpose": "深化冲突和情感", "tension": "moderate"},
        {"type": StoryBeatType.TWIST, "name": "转-转折", "order": 5, "act": 3, "start": 15, "end": 17, "purpose": "引入意外转折", "tension": "high"},
        {"type": StoryBeatType.TWIST, "name": "转-冲突", "order": 6, "act": 3, "start": 17, "end": 19, "purpose": "转折带来的冲突", "tension": "high"},
        {"type": StoryBeatType.CONCLUSION, "name": "合-整合", "order": 7, "act": 4, "start": 20, "end": 22, "purpose": "整合所有元素", "tension": "moderate"},
        {"type": StoryBeatType.CONCLUSION, "name": "合-结局", "order": 8, "act": 4, "start": 22, "end": 24, "purpose": "问题解决，主题升华", "tension": "low"},
    ],
}

STRUCTURE_TEMPLATES = {
    MainStoryStructureType.THREE_ACT: THREE_ACT_TEMPLATE,
    MainStoryStructureType.HEROS_JOURNEY: HEROS_JOURNEY_TEMPLATE,
    MainStoryStructureType.SEVEN_POINT: SEVEN_POINT_TEMPLATE,
    MainStoryStructureType.SAVE_THE_CAT: SAVE_THE_CAT_TEMPLATE,
    MainStoryStructureType.FREYTAGS_PYRAMID: FREYTAGS_PYRAMID_TEMPLATE,
    MainStoryStructureType.KISHOTENKETSU: KISHOTENKETSU_TEMPLATE,
}


class MainStoryStructureEngine:
    """Engine for generating main story structures using various narrative frameworks."""

    def __init__(self, ai_service: AIService):
        """Initialize main story structure engine with AI service."""
        self.ai_service = ai_service

    async def generate_structure(
        self,
        genre: str,
        theme: str,
        main_characters: list[dict],
        structure_type: MainStoryStructureType = MainStoryStructureType.THREE_ACT,
        target_chapters: int = 24,
        target_word_count: int = 80000,
        antagonist: Optional[dict] = None,
        growth_arcs: Optional[CharacterGrowthArcSystem] = None,
    ) -> MainStoryStructure:
        """Generate a main story structure.

        Args:
            genre: Novel genre
            theme: Central theme
            main_characters: List of main character dicts
            structure_type: Story structure framework to use
            target_chapters: Target number of chapters
            target_word_count: Target word count
            antagonist: Optional antagonist dict
            growth_arcs: Optional character growth arc system

        Returns:
            MainStoryStructure object
        """
        structure_id = f"structure_{uuid.uuid4().hex[:8]}"

        # Get structure template
        template = STRUCTURE_TEMPLATES.get(structure_type, THREE_ACT_TEMPLATE)

        # Generate AI-assisted story elements
        ai_story_data = await self._generate_story_elements(
            genre=genre,
            theme=theme,
            main_characters=main_characters,
            structure_type=structure_type,
        )

        # Build acts
        acts = self._build_acts(structure_id, template, target_chapters)

        # Build beats
        beats = self._build_beats(
            structure_id=structure_id,
            template=template,
            ai_data=ai_story_data,
            main_characters=main_characters,
            target_chapters=target_chapters,
        )

        # Build structure
        structure = MainStoryStructure(
            id=structure_id,
            title=ai_story_data.get("title", f"{theme}：故事主线"),
            genre=genre,
            theme=theme,
            structure_type=structure_type,
            target_chapters=target_chapters,
            target_word_count=target_word_count,
            acts=acts,
            beats=beats,
            main_character_ids=[c.get("id", f"char_{i}") for i, c in enumerate(main_characters)],
            antagonist_id=antagonist.get("id") if antagonist else None,
            core_conflict=ai_story_data.get("core_conflict", f"{theme}的核心冲突"),
            central_question=ai_story_data.get("central_question", f"故事探讨的核心问题"),
            thematic_statement=ai_story_data.get("thematic_statement", f"关于{theme}的主题陈述"),
            status=StoryBeatStatus.COMPLETE,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
        )

        return structure

    async def _generate_story_elements(
        self,
        genre: str,
        theme: str,
        main_characters: list[dict],
        structure_type: MainStoryStructureType,
    ) -> dict:
        """Generate story elements using AI."""
        char_names = [c.get("name", f"角色{i}") for i, c in enumerate(main_characters)]

        prompt = f"""为{genre}类型小说生成主线故事结构元素。

主题：{theme}
主要角色：{', '.join(char_names)}
结构框架：{structure_type.value}

请以JSON格式生成：
{{
  "title": "故事标题",
  "core_conflict": "核心冲突描述",
  "central_question": "故事探讨的核心问题",
  "thematic_statement": "主题陈述",
  "beat_details": {{
    "关键转折点详情": ["转折1", "转折2", ...]
  }},
  "character_involvement": {{
    "角色名": ["参与的关键事件"]
  }}
}}"""
        result = await self.ai_service.generate(prompt)
        return self.ai_service._parse_json(result)

    def _build_acts(
        self,
        structure_id: str,
        template: dict,
        target_chapters: int,
    ) -> list[ActStructure]:
        """Build act structures from template."""
        acts = []
        template_acts = template.get("acts", [])

        # Calculate chapter distribution if needed
        total_chapters = sum(a.get("end_chapter", 0) - a.get("start_chapter", 0) + 1 for a in template_acts)
        if total_chapters != target_chapters:
            scale_factor = target_chapters / max(total_chapters, 1)

        for i, act_template in enumerate(template_acts):
            start = act_template.get("start_chapter", i * 8 + 1)
            end = act_template.get("end_chapter", min((i + 1) * 8, target_chapters))

            # Scale if needed
            if total_chapters != target_chapters:
                start = max(1, int((start - 1) * scale_factor) + 1)
                end = min(target_chapters, int(end * scale_factor))

            act = ActStructure(
                id=f"{structure_id}_act_{i + 1}",
                number=i + 1,
                name=act_template.get("name", f"第{i + 1}幕"),
                description=act_template.get("description", ""),
                start_chapter=start,
                end_chapter=end,
                beats=[],
                purpose=act_template.get("purpose", ""),
                key_conflict=act_template.get("key_conflict", ""),
                thematic_focus=act_template.get("thematic_focus", ""),
            )
            acts.append(act)

        return acts

    def _build_beats(
        self,
        structure_id: str,
        template: dict,
        ai_data: dict,
        main_characters: list[dict],
        target_chapters: int,
    ) -> list[StoryBeat]:
        """Build story beats from template."""
        beats = []
        template_beats = template.get("beats", [])

        # Calculate scaling if needed
        total_beats_chapters = max(
            b.get("end", 1) - b.get("start", 0) + 1 for b in template_beats
        ) * len(template_beats)
        scale_factor = (target_chapters * len(main_characters)) / max(total_beats_chapters, 1)

        for i, beat_template in enumerate(template_beats):
            start = beat_template.get("start", i * 2 + 1)
            end = beat_template.get("end", (i + 1) * 2)

            # Scale chapters if needed
            if scale_factor != 1.0:
                start = max(1, min(target_chapters, int(start * scale_factor)))
                end = max(start, min(target_chapters, int(end * scale_factor)))

            beat = StoryBeat(
                id=f"{structure_id}_beat_{i + 1}",
                beat_type=beat_template.get("type", StoryBeatType.RISING_ACTION),
                name=beat_template.get("name", f"情节点{i + 1}"),
                description=f"描述：{beat_template.get('purpose', '')}",
                order=i + 1,
                act_number=beat_template.get("act"),
                start_chapter=start,
                end_chapter=end,
                purpose=beat_template.get("purpose", ""),
                key_events=self._get_key_events(ai_data, i),
                character_involvement=[
                    c.get("name", f"角色{j}") for j, c in enumerate(main_characters[:3])
                ],
                themes_explored=[ai_data.get("thematic_statement", "")],
                tension_level=beat_template.get("tension", "moderate"),
                status=StoryBeatStatus.PENDING,
            )
            beats.append(beat)

        return beats

    def _get_key_events(self, ai_data: dict, beat_index: int) -> list[str]:
        """Get key events for a beat from AI data."""
        beat_details = ai_data.get("beat_details", {})
        if isinstance(beat_details, dict):
            keys = list(beat_details.keys())
            if beat_index < len(keys):
                detail = beat_details.get(keys[beat_index % len(keys)], [])
                if isinstance(detail, list):
                    return detail[:3]
        return [f"关键事件{beat_index + 1}"]

    async def analyze_structure(
        self,
        structure: MainStoryStructure,
    ) -> StructureAnalysis:
        """Analyze a story structure for quality and consistency.

        Args:
            structure: MainStoryStructure to analyze

        Returns:
            StructureAnalysis with findings
        """
        analysis = StructureAnalysis(structure_id=structure.id)

        # Analyze beat coverage
        required_beats = self._get_required_beats(structure.structure_type)
        existing_beats = {b.beat_type for b in structure.beats}
        analysis.missing_beats = [
            b for b in required_beats if b not in existing_beats
        ]
        analysis.beat_coverage = {
            "required": len(required_beats),
            "present": len(existing_beats),
            "coverage": len(existing_beats) / max(len(required_beats), 1),
        }

        # Analyze pacing
        analysis.pacing_score = self._calculate_pacing_score(structure)

        # Analyze chapter distribution
        analysis.chapter_distribution = self._analyze_chapter_distribution(structure)

        # Analyze tension curve
        analysis.tension_curve = self._analyze_tension_curve(structure)

        # Analyze thematic coherence
        analysis.thematic_coherence = self._calculate_thematic_coherence(structure)

        # Calculate overall scores
        analysis.coherence_score = self._calculate_coherence_score(analysis)
        analysis.completeness_score = self._calculate_completeness_score(
            structure, analysis
        )

        # Identify issues and recommendations
        analysis.structural_issues = self._identify_issues(structure, analysis)
        analysis.recommendations = self._generate_recommendations(structure, analysis)

        return analysis

    def _get_required_beats(self, structure_type: MainStoryStructureType) -> list[str]:
        """Get required beats for a structure type."""
        if structure_type == MainStoryStructureType.THREE_ACT:
            return [b.value for b in [
                StoryBeatType.EXPOSITION, StoryBeatType.INCITING_INCIDENT,
                StoryBeatType.RISING_ACTION, StoryBeatType.MIDPOINT,
                StoryBeatType.CRISIS, StoryBeatType.CLIMAX,
                StoryBeatType.FALLING_ACTION, StoryBeatType.RESOLUTION,
            ]]
        elif structure_type == MainStoryStructureType.HEROS_JOURNEY:
            return [b.value for b in [
                StoryBeatType.ORDINARY_WORLD, StoryBeatType.CALL_TO_ADVENTURE,
                StoryBeatType.REFUSAL_OF_CALL, StoryBeatType.MEETING_THE_MENTOR,
                StoryBeatType.CROSSING_THE_THRESHOLD, StoryBeatType.TESTS_ALLIES_ENEMIES,
                StoryBeatType.ORDEAL, StoryBeatType.REWARD,
                StoryBeatType.RESURRECTION, StoryBeatType.RETURN_WITH_ELIXIR,
            ]]
        elif structure_type == MainStoryStructureType.SEVEN_POINT:
            return [b.value for b in [
                StoryBeatType.HOOK, StoryBeatType.FIRST_TURN,
                StoryBeatType.MIDPOINT, StoryBeatType.ALL_IS_LOST,
                StoryBeatType.DARK_MOMENT, StoryBeatType.RESOLUTION,
            ]]
        elif structure_type == MainStoryStructureType.SAVE_THE_CAT:
            return [b.value for b in [
                StoryBeatType.OPENING_IMAGE, StoryBeatType.CATALYST,
                StoryBeatType.MIDPOINT, StoryBeatType.ALL_IS_LOST,
                StoryBeatType.DARK_NIGHT_OF_SOUL, StoryBeatType.FINALE,
            ]]
        return []

    def _calculate_pacing_score(self, structure: MainStoryStructure) -> float:
        """Calculate pacing score based on beat distribution."""
        if not structure.beats:
            return 0.0

        # Check if beats are reasonably distributed
        beat_chapters = [
            (b.end_chapter - b.start_chapter + 1) for b in structure.beats
        ]
        avg_chapters = sum(beat_chapters) / len(beat_chapters)

        # Ideal: beats are 2-4 chapters each
        ideal_min, ideal_max = 2, 4
        within_ideal = sum(
            1 for c in beat_chapters if ideal_min <= c <= ideal_max
        )

        return within_ideal / max(len(beat_chapters), 1)

    def _analyze_chapter_distribution(self, structure: MainStoryStructure) -> dict:
        """Analyze chapter distribution across acts."""
        if not structure.acts:
            return {}

        distribution = {}
        for act in structure.acts:
            chapters_count = act.end_chapter - act.start_chapter + 1
            distribution[f"act_{act.number}"] = {
                "chapters": chapters_count,
                "percentage": chapters_count / max(structure.target_chapters, 1),
            }

        return distribution

    def _analyze_tension_curve(self, structure: MainStoryStructure) -> list[dict]:
        """Analyze tension curve across beats."""
        tension_curve = []
        for beat in sorted(structure.beats, key=lambda b: b.order):
            tension_curve.append({
                "beat": beat.name,
                "order": beat.order,
                "tension": beat.tension_level,
                "chapter_start": beat.start_chapter,
                "chapter_end": beat.end_chapter,
            })
        return tension_curve

    def _calculate_thematic_coherence(self, structure: MainStoryStructure) -> float:
        """Calculate thematic coherence score."""
        if not structure.beats:
            return 0.0

        # Check if thematic statement is present
        if not structure.thematic_statement:
            return 0.3

        # Check if themes are explored across beats
        beats_with_themes = sum(
            1 for b in structure.beats if b.themes_explored
        )

        return beats_with_themes / max(len(structure.beats), 1)

    def _calculate_coherence_score(self, analysis: StructureAnalysis) -> float:
        """Calculate overall coherence score."""
        score = 1.0

        # Penalize for missing beats
        if analysis.missing_beats:
            score -= 0.1 * len(analysis.missing_beats)

        # Penalize for structural issues
        if analysis.structural_issues:
            score -= 0.05 * len(analysis.structural_issues)

        return max(0.0, min(1.0, score))

    def _calculate_completeness_score(
        self,
        structure: MainStoryStructure,
        analysis: StructureAnalysis,
    ) -> float:
        """Calculate completeness score."""
        score = 0.0
        max_score = 5.0

        # Has title
        if structure.title:
            score += 0.5

        # Has core conflict
        if structure.core_conflict:
            score += 0.5

        # Has beats
        if len(structure.beats) >= 5:
            score += 1.0

        # Has acts
        if len(structure.acts) >= 2:
            score += 1.0

        # Has thematic statement
        if structure.thematic_statement:
            score += 1.0

        # Beat coverage
        coverage = analysis.beat_coverage.get("coverage", 0)
        score += coverage

        return score / max_score

    def _identify_issues(
        self,
        structure: MainStoryStructure,
        analysis: StructureAnalysis,
    ) -> list[str]:
        """Identify structural issues."""
        issues = []

        # Check for missing beats
        if analysis.missing_beats:
            issues.append(f"缺少关键情节点: {', '.join(analysis.missing_beats[:3])}")

        # Check pacing
        if analysis.pacing_score < 0.5:
            issues.append("节奏分布不均匀，部分情节点篇幅过长或过短")

        # Check climax position
        climax_beats = [
            b for b in structure.beats if b.tension_level == "climax"
        ]
        if climax_beats:
            last_chapter = max(b.end_chapter for b in structure.beats)
            for climax in climax_beats:
                if climax.end_chapter < last_chapter * 0.7:
                    issues.append("高潮出现过早，可能导致故事后劲不足")
                    break

        # Check for character involvement
        if structure.main_character_ids:
            avg_involvement = sum(
                len(b.character_involvement) for b in structure.beats
            ) / max(len(structure.beats), 1)
            if avg_involvement < 1.0:
                issues.append("部分情节点缺少角色参与记录")

        return issues

    def _generate_recommendations(
        self,
        structure: MainStoryStructure,
        analysis: StructureAnalysis,
    ) -> list[str]:
        """Generate improvement recommendations."""
        recommendations = []

        # Missing beats
        if analysis.missing_beats:
            recommendations.append(
                f"建议补充缺失的情节点以增强结构完整性"
            )

        # Pacing
        if analysis.pacing_score < 0.7:
            recommendations.append(
                "建议调整情节点篇幅，确保节奏均匀分布"
            )

        # Thematic
        if analysis.thematic_coherence < 0.7:
            recommendations.append(
                "建议在更多情节点中深化主题探索"
            )

        # Character
        if structure.main_character_ids:
            recommendations.append(
                "建议为每个情节点明确角色参与，增强角色驱动感"
            )

        return recommendations

    def get_structure_summary(self, structure: MainStoryStructure) -> str:
        """Get a human-readable summary of the story structure.

        Args:
            structure: MainStoryStructure

        Returns:
            Summary string
        """
        lines = [
            f"《{structure.title}》",
            f"类型：{structure.genre}",
            f"主题：{structure.theme}",
            f"结构框架：{structure.structure_type.value}",
            f"",
            f"核心冲突：{structure.core_conflict}",
            f"核心问题：{structure.central_question}",
            f"",
            f"=== 结构概览 ===",
        ]

        for act in structure.acts:
            lines.append(
                f"第{act.number}幕《{act.name}》"
                f"(第{act.start_chapter}-{act.end_chapter}章)：{act.purpose}"
            )

        lines.extend([
            "",
            "=== 情节点概览 ===",
        ])

        for beat in structure.beats[:8]:  # First 8 beats
            lines.append(
                f"{beat.order}. {beat.name}：{beat.purpose[:40]}..."
                f"(第{beat.start_chapter}-{beat.end_chapter}章)"
            )

        if len(structure.beats) > 8:
            lines.append(f"... 共{len(structure.beats)}个情节点")

        return "\n".join(lines)

    def export_structure(self, structure: MainStoryStructure) -> dict:
        """Export story structure as a dictionary.

        Args:
            structure: MainStoryStructure to export

        Returns:
            Dictionary representation
        """
        return {
            "id": structure.id,
            "title": structure.title,
            "genre": structure.genre,
            "theme": structure.theme,
            "structure_type": structure.structure_type.value,
            "target_chapters": structure.target_chapters,
            "target_word_count": structure.target_word_count,
            "acts": [
                {
                    "id": a.id,
                    "number": a.number,
                    "name": a.name,
                    "chapter_range": f"{a.start_chapter}-{a.end_chapter}",
                    "purpose": a.purpose,
                    "key_conflict": a.key_conflict,
                }
                for a in structure.acts
            ],
            "beats": [
                {
                    "id": b.id,
                    "order": b.order,
                    "name": b.name,
                    "type": b.beat_type.value,
                    "chapter_range": f"{b.start_chapter}-{b.end_chapter}",
                    "purpose": b.purpose,
                    "tension": b.tension_level,
                }
                for b in structure.beats
            ],
            "main_character_ids": structure.main_character_ids,
            "antagonist_id": structure.antagonist_id,
            "core_conflict": structure.core_conflict,
            "central_question": structure.central_question,
            "thematic_statement": structure.thematic_statement,
            "status": structure.status.value,
            "created_at": structure.created_at,
        }