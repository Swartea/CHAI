"""AI service for content generation using Claude."""

import os
from typing import Optional
from dataclasses import dataclass

import anthropic


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
