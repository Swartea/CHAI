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
