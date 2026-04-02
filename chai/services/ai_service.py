"""AI service for content generation using Claude."""

import os
from typing import Optional
from dataclasses import dataclass

import anthropic

from chai.models import MagicSystem, SocialStructure


@dataclass
class AIConfig:
    """AI service configuration."""
    api_key: Optional[str] = None
    model: str = "claude-sonnet-4-20250514"
    max_tokens: int = 8192
    temperature: float = 0.7


class AIService:
    """AI service for generating novel content using Claude."""

    def __init__(self, config: Optional[AIConfig] = None):
        """Initialize AI service with configuration."""
        self.config = config or AIConfig()
        api_key = self.config.api_key or os.environ.get("ANTHROPIC_API_KEY")

        if not api_key:
            raise ValueError("API key not provided. Set ANTHROPIC_API_KEY environment variable.")

        self.client = anthropic.Anthropic(api_key=api_key)

    async def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> str:
        """Generate content using AI."""
        response = self.client.messages.create(
            model=self.config.model,
            max_tokens=max_tokens or self.config.max_tokens,
            temperature=temperature if temperature is not None else self.config.temperature,
            system=system or self._default_system(),
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text

    def _default_system(self) -> str:
        """Default system prompt for novel writing."""
        return """You are CHAI, an expert AI novel writing assistant. You help create engaging
novels with rich world-building, compelling characters, and captivating plots.
You write in Chinese and specialize in various novel genres including fantasy,
sci-fi, urban, mystery, and romance. Always maintain consistency in character
voice, narrative style, and plot coherence."""

    async def generate_world_setting(self, genre: str, theme: str) -> dict:
        """Generate world setting for a novel."""
        prompt = f"""为{genre}类型小说生成完整的世界观设定。

主题：{theme}

请生成包含以下方面的详细世界观：
1. 地理环境（大陆、国家、城市、地标）
2. 政治结构（政府、势力、联盟）
3. 文化元素（宗教、语言、传统习俗）
4. 历史背景（重要历史事件）

以JSON格式输出，包含字段：name, genre, geography, politics, culture, history"""
        result = await self.generate(prompt)
        return self._parse_json(result)

    async def generate_geography(
        self,
        genre: str,
        theme: str,
        base_geography: Optional[dict] = None,
        expand: bool = False,
    ) -> dict:
        """Generate detailed geography for a world.

        Args:
            genre: Novel genre
            theme: Central theme
            base_geography: Existing geography data to expand on
            expand: If True, expand the existing geography instead of creating new

        Returns:
            Geography dict with continents, countries, cities, landmarks, etc.
        """
        base_info = f"基础地理：{base_geography}" if base_geography else ""
        expand_instruction = "请扩展现有地理设定，添加更多地区、地点和细节。" if expand else "请生成全新的详细地理设定。"

        prompt = f"""为{genre}类型小说生成详细的地理环境设定。

主题：{theme}
{base_info}
{expand_instruction}

请生成包含以下方面的详细地理设定，以JSON格式输出：
{{
  "continents": [
    {{
      "name": "大陆名称",
      "climate": "气候描述",
      "terrain": "地形特征",
      "major_regions": ["主要区域列表"],
      "description": "整体描述"
    }}
  ],
  "countries": [
    {{
      "name": "国家/势力名称",
      "capital": "首都",
      "territory": "领土范围",
      "neighbors": ["邻国列表"],
      "description": "国家描述"
    }}
  ],
  "cities": [
    {{
      "name": "城市名称",
      "country": "所属国家",
      "population": "人口规模",
      "industry": "主要产业",
      "notable_features": ["著名地标/特色"],
      "description": "城市描述"
    }}
  ],
  "landmarks": [
    {{
      "name": "地标名称",
      "location": "所在位置",
      "type": "类型（山脉/河流/建筑等）",
      "significance": "重要程度和意义",
      "description": "描述"
    }}
  ],
  "geopolitical_regions": ["地缘政治区域列表"]
}}"""
        result = await self.generate(prompt)
        return self._parse_json(result)

    async def generate_politics(
        self,
        genre: str,
        theme: str,
        geography: Optional[dict] = None,
        expand: bool = False,
    ) -> dict:
        """Generate detailed political structures for a world.

        Args:
            genre: Novel genre
            theme: Central theme
            geography: Geography data to base politics on
            expand: If True, expand existing politics

        Returns:
            Politics dict with governments, factions, alliances, etc.
        """
        geo_info = f"地理背景：{geography}" if geography else ""
        expand_instruction = "请扩展现有政治设定，添加更多派系、冲突和细节。" if expand else "请生成全新的详细政治结构设定。"

        prompt = f"""为{genre}类型小说生成详细的政治结构设定。

主题：{theme}
{geo_info}
{expand_instruction}

请生成包含以下方面的详细政治设定，以JSON格式输出：
{{
  "governments": [
    {{
      "name": "政府/政权名称",
      "type": "政体类型（君主制/共和制/神权制等）",
      "leader": "最高领导者",
      "structure": "政府结构",
      "territory": "控制区域",
      "description": "描述"
    }}
  ],
  "factions": [
    {{
      "name": "势力/组织名称",
      "type": "类型（门派/家族/公会/秘密组织等）",
      "leader": "首领",
      "members": "成员规模",
      "goals": ["主要目标"],
      "ideology": "意识形态",
      "relationships": ["与其他势力的关系"],
      "description": "描述"
    }}
  ],
  "alliances": [
    {{
      "name": "联盟名称",
      "members": ["成员势力"],
      "purpose": "联盟目的",
      "leader": "主导势力",
      "duration": "持续时间"
    }}
  ],
  "conflicts": [
    {{
      "name": "冲突名称",
      "parties": ["参与方"],
      "cause": "起因",
      "status": "状态（进行中/结束/酝酿中）",
      "description": "描述"
    }}
  ],
  "laws_and_rules": ["重要法律/规则列表"],
  "power_distribution": {{"权力分布描述": "具体说明"}}
}}"""
        result = await self.generate(prompt)
        return self._parse_json(result)

    async def generate_culture(
        self,
        genre: str,
        theme: str,
        geography: Optional[dict] = None,
        politics: Optional[dict] = None,
        expand: bool = False,
    ) -> dict:
        """Generate detailed cultural elements for a world.

        Args:
            genre: Novel genre
            theme: Central theme
            geography: Geography data
            politics: Politics data
            expand: If True, expand existing culture

        Returns:
            Culture dict with religions, languages, traditions, etc.
        """
        context = ""
        if geography:
            context += f"地理背景：{geography}\n"
        if politics:
            context += f"政治背景：{politics}\n"
        expand_instruction = "请扩展现有文化设定，添加更多细节。" if expand else "请生成全新的详细文化元素设定。"

        prompt = f"""为{genre}类型小说生成详细的文化元素设定。

主题：{theme}
{context}
{expand_instruction}

请生成包含以下方面的详细文化设定，以JSON格式输出：
{{
  "religions": [
    {{
      "name": "宗教/信仰名称",
      "type": "类型（多神教/一神教/自然崇拜等）",
      "deities": ["主要神祇列表"],
      "practices": ["主要仪式/习俗"],
      "holy_places": ["圣地"],
      "clergy": "神职人员",
      "influence": "对社会的影响",
      "description": "描述"
    }}
  ],
  "languages": [
    {{
      "name": "语言名称",
      "speakers": "使用地区/人群",
      "script": "书写系统",
      "official_status": "官方地位",
      "description": "特点描述"
    }}
  ],
  "traditions": [
    {{
      "name": "传统节日/习俗名称",
      "origin": "起源",
      "celebration": "庆祝方式",
      "significance": "意义",
      "associated_regions": ["关联地区"]
    }}
  ],
  "arts": ["主要艺术形式列表"],
  "cuisines": ["特色饮食列表"],
  "customs": ["社会习俗列表"],
  "values": ["核心价值观列表"],
  "taboos": ["禁忌列表"],
  "education_system": "教育体系描述",
  "entertainment": ["娱乐方式列表"]
}}"""
        result = await self.generate(prompt)
        return self._parse_json(result)

    async def generate_history(
        self,
        genre: str,
        theme: str,
        geography: Optional[dict] = None,
        politics: Optional[dict] = None,
        culture: Optional[dict] = None,
        expand: bool = False,
    ) -> dict:
        """Generate detailed history and timeline for a world.

        Args:
            genre: Novel genre
            theme: Central theme
            geography: Geography data
            politics: Politics data
            culture: Culture data
            expand: If True, expand existing history

        Returns:
            History dict with eras, events, timeline, etc.
        """
        context = ""
        if geography:
            context += f"地理背景：{geography}\n"
        if politics:
            context += f"政治背景：{politics}\n"
        if culture:
            context += f"文化背景：{culture}\n"
        expand_instruction = "请扩展现有历史设定，添加更多时代、事件和细节。" if expand else "请生成全新的详细历史设定。"

        prompt = f"""为{genre}类型小说生成详细的历史背景设定。

主题：{theme}
{context}
{expand_instruction}

请生成包含以下方面的详细历史设定，以JSON格式输出：
{{
  "eras": [
    {{
      "name": "时代名称",
      "time_period": "时间跨度",
      "start_event": "开端事件",
      "end_event": "结束事件",
      "major_changes": ["主要变化"],
      "description": "时代描述"
    }}
  ],
  "major_events": [
    {{
      "name": "事件名称",
      "year": "发生年代",
      "location": "发生地点",
      "parties_involved": ["参与方"],
      "cause": "起因",
      "course": "经过",
      "result": "结果",
      "significance": "历史意义"
    }}
  ],
  "historical_figures": [
    {{
      "name": "历史人物名称",
      "title": "头衔/称号",
      "era": "所属时代",
      "achievements": ["主要成就"],
      "legacy": "历史遗产",
      "description": "描述"
    }}
  ],
  "myths_and_legends": [
    {{
      "name": "传说/神话名称",
      "origin": "起源",
      "content": "内容概要",
      "cultural_significance": "文化意义",
      "characters": ["涉及人物"]
    }}
  ],
  "historical_conflicts": [
    {{
      "name": "历史战争/冲突名称",
      "period": "时期",
      "sides": ["参战方"],
      "cause": "起因",
      "outcome": "结局",
      "impact": "影响"
    }}
  ],
  "timeline_summary": "整体时间线概要"
}}"""
        result = await self.generate(prompt)
        return self._parse_json(result)

    async def generate_magic_system(
        self,
        genre: str,
        theme: str,
        world_context: Optional[dict] = None,
    ) -> "MagicSystem":
        """Generate a magic/tech/superpower system.

        Args:
            genre: Novel genre
            theme: Central theme
            world_context: Context about the world (geography, politics, culture)

        Returns:
            MagicSystem object
        """
        context = ""
        if world_context:
            context = f"世界观背景：{world_context}\n"

        prompt = f"""为{genre}类型小说生成详细的魔法/科技/异能系统设定。

主题：{theme}
{context}
请生成完整的系统设定，以JSON格式输出：
{{
  "name": "系统名称",
  "system_type": "系统类型（magic=魔法/technology=科技/superpower=异能/mixed=混合）",
  "rules": [
    "规则1：系统运作的基本原理",
    "规则2：魔法的使用条件",
    "规则3：能量来源",
    "规则4：施展方式"
  ],
  "limitations": [
    "限制1：使用代价或副作用",
    "限制2：使用条件限制",
    "限制3：地理/时间限制",
    "限制4：其他限制"
  ],
  "levels": [
    "初级：基础能力描述",
    "中级：进阶能力描述",
    "高级：高级能力描述",
    "大师：最高境界描述"
  ],
  "schools_or_types": [
    {{
      "name": "流派/类别名称",
      "description": "描述",
      "typical_users": ["典型使用者"],
      "strengths": ["优势"],
      "weaknesses": ["劣势"]
    }}
  ],
  "source_of_power": "力量来源描述",
  "world_influence": "对社会/世界的影响"
}}"""
        result = await self.generate(prompt)
        data = self._parse_json(result)
        return MagicSystem(
            name=data.get("name", "未知系统"),
            system_type=data.get("system_type", "mixed"),
            rules=data.get("rules", []),
            limitations=data.get("limitations", []),
            levels=data.get("levels", []),
        )

    async def expand_magic_system(
        self,
        existing_magic: dict,
        world_context: Optional[dict] = None,
    ) -> dict:
        """Expand an existing magic system.

        Args:
            existing_magic: Existing magic system data
            world_context: Context about the world

        Returns:
            Expanded magic system dict
        """
        context = f"世界观背景：{world_context}" if world_context else ""
        prompt = f"""请扩展以下现有的魔法/异能系统，添加更多细节。

现有系统：{existing_magic}
{context}

请添加：
1. 更多流派/类型
2. 更多规则和限制
3. 更多能力等级
4. 与其他世界元素的互动

以JSON格式输出完整扩展后的系统。"""
        result = await self.generate(prompt)
        return self._parse_json(result)

    async def generate_social_structure(
        self,
        genre: str,
        theme: str,
        geography: Optional[dict] = None,
        politics: Optional[dict] = None,
        culture: Optional[dict] = None,
        magic_system: Optional["MagicSystem"] = None,
        expand: bool = False,
    ) -> "SocialStructure":
        """Generate social structure for a world.

        Args:
            genre: Novel genre
            theme: Central theme
            geography: Geography data
            politics: Politics data
            culture: Culture data
            magic_system: Magic system data
            expand: If True, expand existing social structure

        Returns:
            SocialStructure object
        """
        context = ""
        if geography:
            context += f"地理背景：{geography}\n"
        if politics:
            context += f"政治背景：{politics}\n"
        if culture:
            context += f"文化背景：{culture}\n"
        if magic_system:
            context += f"异能/魔法系统：{magic_system}\n"
        expand_instruction = "请扩展现有社会结构，添加更多阶层、势力和细节。" if expand else "请生成全新的详细社会结构设定。"

        prompt = f"""为{genre}类型小说生成详细的社会结构设定。

主题：{theme}
{context}
{expand_instruction}

请生成包含以下方面的详细社会结构设定，以JSON格式输出：
{{
  "classes": [
    {{
      "name": "阶层名称",
      "description": "描述",
      "typical_members": ["典型成员"],
      "lifestyle": "生活方式",
      "rights": ["享有的权利"],
      "obligations": ["承担的义务"],
      "relationship_with_other_classes": ["与其他阶层的关系"]
    }}
  ],
  "factions": [
    {{
      "name": "势力名称",
      "type": "类型",
      "leader": "领导者",
      "membership": "成员规模",
      "goals": ["目标"],
      "resources": ["资源"],
      "influence": "影响力",
      "description": "描述"
    }}
  ],
  "power_distribution": {{
    "military": "军事力量分布",
    "economic": "经济力量分布",
    "political": "政治力量分布",
    "magical": "魔法力量分布（如适用）",
    "information": "信息/知识力量分布"
  }},
  "social_mobility": "社会流动性描述",
  "family_structures": ["主要家庭结构类型"],
  "profession_distribution": ["主要职业分布"],
  "wealth_distribution": "财富分布描述",
  "conflict_lines": ["社会冲突的主要分界线"]
}}"""
        result = await self.generate(prompt)
        data = self._parse_json(result)
        return SocialStructure(
            classes=data.get("classes", []),
            factions=data.get("factions", []),
            power_distribution=data.get("power_distribution", {}),
        )

    async def generate_characters(
        self,
        world_setting: dict,
        genre: str,
        count: int = 5,
    ) -> list[dict]:
        """Generate characters for the novel."""
        prompt = f"""基于以下世界观设定，生成{count}个角色：

世界观：{world_setting.get('name', '未知')}
类型：{genre}

请为主要角色生成详细信息，包括：
- 姓名、年龄、外貌
- 性格特点、优点、缺点
- 背景故事、动机、目标
- 与其他角色的关系

以JSON数组格式输出。"""
        result = await self.generate(prompt)
        return self._parse_json_array(result)

    async def generate_plot_outline(
        self,
        world_setting: dict,
        characters: list[dict],
        genre: str,
    ) -> dict:
        """Generate plot outline for the novel."""
        prompt = f"""为{genre}小说生成详细的故事大纲。

世界观：{world_setting.get('name', '未知')}
主要角色：{[c.get('name', '') for c in characters]}

请生成包含以下内容的大纲：
1. 主线剧情结构（三幕式）
2. 各章节概要
3. 支线剧情设计
4. 高潮与结局安排
5. 伏笔与呼应设计

以JSON格式输出，包含字段：structure_type, theme, plot_arcs, subplots, foreshadowing_plan"""
        result = await self.generate(prompt)
        return self._parse_json(result)

    async def generate_chapter(
        self,
        chapter_outline: dict,
        world_setting: dict,
        characters: list[dict],
        previous_chapter_summary: Optional[str] = None,
    ) -> str:
        """Generate chapter content."""
        prompt = f"""根据以下大纲生成第{chapter_outline.get('number', '?')}章内容：

章节标题：{chapter_outline.get('title', '')}
章节概要：{chapter_outline.get('summary', '')}
涉及角色：{chapter_outline.get('characters_involved', [])}

世界观背景：{world_setting.get('name', '')}"""
        if previous_chapter_summary:
            prompt += f"\n\n前章概要：{previous_chapter_summary}"

        prompt += f"""

要求：
- 字数目标：2000-4000字
- 场景描写生动，有画面感
- 对话符合角色性格
- 情节推进自然流畅
- 使用中文写作"""

        return await self.generate(prompt, temperature=0.75)

    async def proofread_chapter(self, chapter_content: str) -> str:
        """Proofread and polish chapter content."""
        prompt = f"""请对以下章节内容进行校对和润色：

{chapter_content}

校对项目：
1. 语法错误
2. 错别字
3. 病句与冗余
4. 对话标签规范化
5. 标点符号规范化
6. 风格一致性

保持原意，优化表达。"""
        return await self.generate(prompt, temperature=0.3)

    def _parse_json(self, text: str) -> dict:
        """Parse JSON from text response."""
        import json
        import re

        json_match = re.search(r'\{[\s\S]*\}', text)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass

        return {"raw": text}

    def _parse_json_array(self, text: str) -> list:
        """Parse JSON array from text response."""
        import json
        import re

        json_match = re.search(r'\[[\s\S]*\]', text)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass

        return [{"raw": text}]

    # --- Book Deconstruction Methods ---

    async def deconstruct_book(
        self,
        book_title: str,
        book_synopsis: str,
        genre: str,
        chapter_samples: Optional[list[str]] = None,
    ) -> dict:
        """Deconstruct a book and extract reusable templates.

        Args:
            book_title: Title of the book
            book_synopsis: Book synopsis/description
            genre: Book genre
            chapter_samples: Optional list of chapter content samples

        Returns:
            Dict containing character_templates, plot_patterns, world_template, analysis
        """
        prompt = f"""请对以下小说进行深度拆解，提取可复用的模板和模式。

小说名称：{book_title}
类型：{genre}
简介：{book_synopsis}
{f'样章内容：\n' + '\\n---\\n'.join(chapter_samples) if chapter_samples else ''}

请以JSON格式返回完整的拆解结果，包含以下部分：

{{
  "character_templates": [
    {{
      "name": "模板名称（如：草根逆袭型男主）",
      "template_type": "protagonist|antagonist|supporting|mentor|love_interest|sidekick",
      "age_range": "年龄范围",
      "background_template": "背景模板描述",
      "personality_traits": ["性格特点列表"],
      "strengths": ["优点列表"],
      "weaknesses": ["缺点列表"],
      "speech_pattern": "说话风格描述",
      "growth_arc_template": "成长弧线模板"
    }}
  ],
  "plot_patterns": [
    {{
      "name": "模式名称（如：逆境崛起）",
      "pattern_type": "heros_journey|three_act|save_the_cat|seven_point|mythic|subversion",
      "description": "模式描述",
      "structure_summary": "结构概要",
      "key_beat_templates": ["关键情节点模板"],
      "pacing_notes": "节奏特点",
      "tension_curve": ["张力曲线描述"]
    }}
  ],
  "world_template": {{
    "name": "世界观模板名称",
    "template_type": "fantasy|sci-fi|urban|historical|modern|post_apocalyptic",
    "world_summary": "世界观概述",
    "geography_template": {{"地理设置": "描述"}},
    "political_template": {{"政治结构": "描述"}},
    "cultural_template": {{"文化元素": "描述"}},
    "magic_system_template": {{"魔法/异能系统": "描述"}},
    "recurring_locations": ["典型地点"],
    "typical_conflicts": ["典型冲突"]
  }},
  "genre_classification": "最终类型判定",
  "tone_and_style": "文风语调特点",
  "target_audience": "目标读者"
}}"""
        result = await self.generate(prompt)
        return self._parse_json(result)

    async def extract_character_templates(
        self,
        book_content: str,
        genre: str,
    ) -> list[dict]:
        """Extract character templates from book content."""
        prompt = f"""从以下小说内容中提取角色模板。

类型：{genre}
内容：
{book_content[:5000]}

请提取主要角色模板，以JSON数组格式返回。每个模板应包含：
- name: 模板名称
- template_type: 角色类型 (protagonist/antagonist/supporting/mentor/love_interest/sidekick)
- age_range: 年龄范围
- background_template: 背景模板
- personality_traits: 性格特点列表
- strengths: 优点列表
- weaknesses: 缺点列表
- speech_pattern: 说话风格
- growth_arc_template: 成长弧线

以JSON数组格式输出。"""
        result = await self.generate(prompt)
        return self._parse_json_array(result)

    async def extract_plot_patterns(
        self,
        book_outline: str,
        genre: str,
    ) -> list[dict]:
        """Extract plot patterns from book outline or content."""
        prompt = f"""从以下小说大纲中提取情节模式。

类型：{genre}
大纲：
{book_outline[:5000]}

请提取主要情节模式，以JSON数组格式返回。每个模式应包含：
- name: 模式名称
- pattern_type: 模式类型 (heros_journey/three_act/save_the_cat/seven_point/mythic/subversion)
- description: 模式描述
- structure_summary: 结构概要
- key_beat_templates: 关键情节点模板列表
- pacing_notes: 节奏特点
- tension_curve: 张力曲线描述

以JSON数组格式输出。"""
        result = await self.generate(prompt)
        return self._parse_json_array(result)

    async def extract_world_template(
        self,
        world_description: str,
        genre: str,
    ) -> dict:
        """Extract world setting template from world description."""
        prompt = f"""从以下世界观描述中提取可复用的模板。

类型：{genre}
世界观：
{world_description[:3000]}

请提取世界观模板，以JSON格式返回，包含：
- name: 模板名称
- template_type: 世界类型 (fantasy/sci-fi/urban/historical/modern/post_apocalyptic)
- world_summary: 世界观概述
- geography_template: 地理模板
- political_template: 政治结构模板
- cultural_template: 文化元素模板
- magic_system_template: 魔法/科技系统模板（如适用）
- recurring_locations: 典型地点列表
- typical_conflicts: 典型冲突列表

以JSON格式输出。"""
        result = await self.generate(prompt)
        return self._parse_json(result)

    async def generate_outline_from_templates(
        self,
        genre: str,
        theme: str,
        character_templates: list[dict],
        plot_patterns: list[dict],
        world_template: Optional[dict] = None,
    ) -> dict:
        """Generate a novel outline using deconstructed templates.

        Args:
            genre: Novel genre
            theme: Central theme
            character_templates: Character templates to use
            plot_patterns: Plot patterns to apply
            world_template: World setting template (optional)

        Returns:
            Novel outline dict with world, characters, and plot structure
        """
        char_names = [c.get("name", "") for c in character_templates[:5]]
        plot_names = [p.get("name", "") for p in plot_patterns[:3]]
        world_name = world_template.get("name", "") if world_template else ""

        prompt = f"""基于以下模板，生成小说大纲。

类型：{genre}
主题：{theme}

使用的人物模板：
{chr(10).join(f"- {n}" for n in char_names)}

使用的情节模式：
{chr(10).join(f"- {n}" for n in plot_names)}

世界观模板：{world_name}

请生成完整的小说大纲，包含：
1. 世界观设定（基于模板调整）
2. 主要角色设定（基于模板）
3. 主线剧情结构（基于情节模式）
4. 章节安排

以JSON格式输出，包含字段：
- world_setting: 世界观设定
- characters: 角色列表
- plot_outline: 情节大纲
- structure_type: 结构类型
- theme: 主题

以JSON格式输出。"""
        result = await self.generate(prompt)
        return self._parse_json(result)
