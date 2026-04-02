"""Magic/Technology/Superpower system engine for comprehensive power rules."""

from typing import Optional, Any
from chai.models import (
    MagicSystem,
    PowerTechnique,
    PowerConflict,
    WorldSetting,
)
from chai.services import AIService


class MagicSystemEngine:
    """Engine for managing magic, technology, and superpower systems.

    Provides comprehensive rule definition, technique generation,
    consistency analysis, and conflict creation for power systems.
    """

    def __init__(self, ai_service: AIService):
        """Initialize magic system engine with AI service."""
        self.ai_service = ai_service

    async def build_power_system(
        self,
        genre: str,
        theme: str,
        system_type: str = "mixed",
        world_context: Optional[dict] = None,
    ) -> MagicSystem:
        """Build a complete power system from scratch.

        Args:
            genre: Novel genre
            theme: Central theme
            system_type: Type of system (magic, technology, superpower, mixed)
            world_context: Optional world context (geography, politics, culture)

        Returns:
            Complete MagicSystem with all rules and components
        """
        context = ""
        if world_context:
            context = f"世界观背景：{world_context}\n"

        prompt = f"""为{genre}类型小说生成完整的{system_type}系统设定。

主题：{theme}
{context}

请生成极其详细的{system_type}系统设定，以JSON格式输出：

{{
  "name": "系统名称",
  "system_type": "{system_type}",
  "source_of_power": "力量来源详细描述",
  "power_origin_story": "系统起源与历史背景",

  "rules": [
    "规则1：详细的系统运作原理",
    "规则2：能量的获取与消耗机制",
    "规则3：使用条件与触发方式",
    "规则4：系统内的等级划分依据",
    "规则5：与其他系统的区别特征"
  ],

  "limitations": [
    "限制1：使用代价（体力、寿命、资源等）",
    "限制2：环境条件限制",
    "限制3：身体/精神负荷",
    "限制4：技术/知识门槛",
    "限制5：社会/法律限制"
  ],

  "levels": [
    "初级：入门者能做什么",
    "中级：熟练者的能力范围",
    "高级：精英所掌握的力量",
    "大师：登峰造极的境界描述",
    "传说/神话级：（如有）超越人类极限的表现"
  ],

  "schools_or_types": [
    {{
      "name": "流派名称",
      "description": "此流派的特点与专长",
      "typical_users": ["典型使用者类型"],
      "strengths": ["此流派优势"],
      "weaknesses": ["此流派劣势"],
      "core_techniques": ["核心技能"]
    }}
  ],

  "training_methods": [
    {{
      "name": "修炼方法名称",
      "description": "方法描述",
      "requirements": ["前提条件"],
      "duration": "所需时间",
      "effects": ["效果"]
    }}
  ],

  "typical_training_duration": "从入门到精通的典型时间跨度",

  "artifacts": [
    {{
      "name": "神器/重要物品名称",
      "description": "描述与来历",
      "power_level": "威力等级",
      "requirements": "使用条件",
      "limitations": "已知缺陷"
    }}
  ],

  "consumables": [
    "丹药/药剂/能量块等消耗品名称及效果"
  ],

  "organizations": [
    {{
      "name": "组织名称",
      "type": "类型（门派/学院/公司/公会等）",
      "leader": "领导者",
      "size": "规模",
      "goals": ["主要目标"],
      "ideology": "核心理念",
      "relationship_with_system": "与此系统的关系"
    }}
  ],

  "power_interactions": [
    "不同力量相遇时的相互作用规则",
    "组合技的原理与限制"
  ],

  "weaknesses": [
    "已知弱点1",
    "已知弱点2",
    "力量失控的风险"
  ],

  "world_influence": "此系统对世界（政治、经济、文化）的影响",

  "social_acceptance": "社会接受度（被广泛接受/被管制/被禁止/神秘等）",

  "history": [
    {{
      "era": "时代/时期",
      "event": "重大事件",
      "impact": "对系统的影响"
    }}
  ],

  "forbidden_techniques": [
    {{
      "name": "禁术名称",
      "description": "为何被禁止",
      "original_purpose": "原本目的",
      "consequences": "使用后果"
    }}
  ],

  "associated_phenomena": [
    "使用时会伴随出现的现象（如魔法阵、光芒等）"
  ]
}}"""
        result = await self.ai_service.generate(prompt)
        data = self.ai_service._parse_json(result)

        return MagicSystem(
            name=data.get("name", "未知系统"),
            system_type=data.get("system_type", system_type),
            rules=data.get("rules", []),
            limitations=data.get("limitations", []),
            levels=data.get("levels", []),
            source_of_power=data.get("source_of_power", ""),
            power_origin_story=data.get("power_origin_story", ""),
            schools_or_types=data.get("schools_or_types", []),
            training_methods=data.get("training_methods", []),
            typical_training_duration=data.get("typical_training_duration", ""),
            artifacts=data.get("artifacts", []),
            consumables=data.get("consumables", []),
            organizations=data.get("organizations", []),
            power_interactions=data.get("power_interactions", []),
            weaknesses=data.get("weaknesses", []),
            world_influence=data.get("world_influence", ""),
            social_acceptance=data.get("social_acceptance", ""),
            history=data.get("history", []),
            forbidden_techniques=data.get("forbidden_techniques", []),
            associated_phenomena=data.get("associated_phenomena", []),
        )

    async def generate_technique(
        self,
        magic_system: MagicSystem,
        technique_type: str = "attack",
        power_level: int = 1,
        school: Optional[str] = None,
    ) -> PowerTechnique:
        """Generate a specific technique for a magic system.

        Args:
            magic_system: The parent magic system
            technique_type: Type (attack, defense, support, utility, healing)
            power_level: Desired power level (1-10)
            school: Optional specific school/style

        Returns:
            PowerTechnique object
        """
        school_filter = f"限定流派：{school}" if school else "不限定流派"

        prompt = f"""基于以下{magic_system.system_type}系统，生成一个{technique_type}类型的技能/法术/能力。

系统名称：{magic_system.name}
系统类型：{magic_system.system_type}
力量来源：{magic_system.source_of_power}
{school_filter}

已有等级体系：
{chr(10).join(f"- {lvl}" for lvl in magic_system.levels[:3])}

生成一个{power_level}级（1-10级）的{technique_type}技能，以JSON格式输出：

{{
  "name": "技能名称",
  "description": "技能描述",
  "school": "所属流派（可从系统已有流派选择或新建）",
  "type": "{technique_type}",
  "power_level": {power_level},
  "mastery_level": "所需掌握级别（beginner/intermediate/advanced/master）",
  "energy_cost": "能量消耗",
  "cooldown": "冷却时间",
  "conditions": ["使用条件1", "使用条件2"],
  "primary_effect": "主要效果描述",
  "secondary_effects": ["附加效果1", "附加效果2"],
  "side_effects": ["副作用1", "副作用2"],
  "countermeasures": ["破解/防御方法1", "破解/防御方法2"],
  "manifestation": "施展时的表现形式"
}}"""
        result = await self.ai_service.generate(prompt)
        data = self.ai_service._parse_json(result)

        return PowerTechnique(
            name=data.get("name", "未知技能"),
            description=data.get("description", ""),
            school=data.get("school", school or ""),
            type=data.get("type", technique_type),
            power_level=data.get("power_level", power_level),
            mastery_level=data.get("mastery_level", "beginner"),
            energy_cost=data.get("energy_cost", ""),
            cooldown=data.get("cooldown", ""),
            conditions=data.get("conditions", []),
            primary_effect=data.get("primary_effect", ""),
            secondary_effects=data.get("secondary_effects", []),
            side_effects=data.get("side_effects", []),
            countermeasures=data.get("countermeasures", []),
            manifestation=data.get("manifestation", ""),
        )

    async def generate_techniques_batch(
        self,
        magic_system: MagicSystem,
        count: int = 10,
        technique_types: Optional[list[str]] = None,
    ) -> list[PowerTechnique]:
        """Generate multiple techniques at once.

        Args:
            magic_system: The parent magic system
            count: Number of techniques to generate
            technique_types: List of types to include (attack, defense, support, utility, healing)

        Returns:
            List of PowerTechnique objects
        """
        types_str = technique_types or ["attack", "defense", "support", "utility", "healing"]
        types_json = '", "'.join(types_str)

        prompt = f"""基于以下{magic_system.system_type}系统，批量生成{count}个多样化的技能/法术/能力。

系统名称：{magic_system.name}
系统类型：{magic_system.system_type}
力量来源：{magic_system.source_of_power}

已有流派：
{chr(10).join(f"- {s.get('name', '')}: {s.get('description', '')[:50]}" for s in magic_system.schools_or_types[:5])}

请生成{count}个涵盖以下类型的技能（JSON数组格式）：
["{types_json}"]

每个技能需要包含：
- name: 技能名称
- description: 描述
- school: 所属流派
- type: 类型
- power_level: 威力等级(1-10)
- mastery_level: 所需级别
- energy_cost: 能量消耗
- cooldown: 冷却时间
- conditions: 使用条件
- primary_effect: 主要效果
- secondary_effects: 附加效果
- side_effects: 副作用
- countermeasures: 克制方法
- manifestation: 表现形式

以JSON数组格式输出完整列表。"""
        result = await self.ai_service.generate(prompt)
        data = self.ai_service._parse_json_array(result)

        techniques = []
        for item in data:
            if isinstance(item, dict):
                techniques.append(PowerTechnique(
                    name=item.get("name", "未知"),
                    description=item.get("description", ""),
                    school=item.get("school", ""),
                    type=item.get("type", "utility"),
                    power_level=item.get("power_level", 5),
                    mastery_level=item.get("mastery_level", "intermediate"),
                    energy_cost=item.get("energy_cost", ""),
                    cooldown=item.get("cooldown", ""),
                    conditions=item.get("conditions", []),
                    primary_effect=item.get("primary_effect", ""),
                    secondary_effects=item.get("secondary_effects", []),
                    side_effects=item.get("side_effects", []),
                    countermeasures=item.get("countermeasures", []),
                    manifestation=item.get("manifestation", ""),
                ))
        return techniques

    async def create_system_conflict(
        self,
        magic_system: MagicSystem,
        world_setting: Optional[WorldSetting] = None,
    ) -> PowerConflict:
        """Generate a conflict centered around this power system.

        Args:
            magic_system: The magic system
            world_setting: Optional world context

        Returns:
            PowerConflict object
        """
        context = ""
        if world_setting:
            context = f"世界背景：{world_setting.name}\n"
            if world_setting.politics:
                context += f"政治势力：{[f.get('name', '') for f in world_setting.politics.get('factions', [])][:5]}\n"
            if world_setting.social_structure:
                context += f"社会势力：{[f.get('name', '') for f in world_setting.social_structure.factions[:5]]}\n"

        prompt = f"""基于以下{magic_system.system_type}系统，生成一个围绕此系统的重大冲突/纷争。

系统名称：{magic_system.name}
{context}

请生成一个详细的冲突设定，以JSON格式输出：

{{
  "name": "冲突名称",
  "description": "冲突概述",
  "parties_involved": ["参与方1", "参与方2", "参与方3"],
  "cause": "根本原因",
  "current_status": "当前状态（酝酿中/进行中/冻结/即将爆发）",
  "key_battles": [
    {{
      "name": "战役名称",
      "description": "描述",
      "result": "结果"
    }}
  ],
  "stakes": "冲突的赌注和意义",
  "potential_resolution": ["可能的解决方式1", "可能的解决方式2"]
}}"""
        result = await self.ai_service.generate(prompt)
        data = self.ai_service._parse_json(result)

        return PowerConflict(
            name=data.get("name", "未知冲突"),
            description=data.get("description", ""),
            parties_involved=data.get("parties_involved", []),
            cause=data.get("cause", ""),
            current_status=data.get("current_status", "active"),
            key_battles=data.get("key_battles", []),
            stakes=data.get("stakes", ""),
            potential_resolution=data.get("potential_resolution", []),
        )

    def analyze_system_consistency(
        self,
        magic_system: MagicSystem,
    ) -> dict[str, Any]:
        """Analyze a magic system for logical consistency.

        Checks for contradictions, gaps, and balance issues.

        Args:
            magic_system: The magic system to analyze

        Returns:
            Dict with analysis results
        """
        issues = []
        warnings = []
        suggestions = []

        # Check basic completeness
        if not magic_system.name:
            issues.append("系统名称为空")

        if not magic_system.source_of_power:
            warnings.append("缺少力量来源描述")

        if not magic_system.rules:
            issues.append("系统缺少基本规则")
        elif len(magic_system.rules) < 3:
            warnings.append("系统规则较少，可能过于简单")

        if not magic_system.limitations:
            warnings.append("系统缺少限制描述，可能导致力量过于强大")

        if not magic_system.levels:
            warnings.append("系统缺少等级划分")

        # Check schools consistency
        if magic_system.schools_or_types:
            for school in magic_system.schools_or_types:
                if isinstance(school, dict):
                    name = school.get("name", "")
                    if not school.get("strengths"):
                        warnings.append(f"流派「{name}」缺少优势描述")
                    if not school.get("weaknesses"):
                        warnings.append(f"流派「{name}」缺少劣势描述")

        # Check organizations
        if magic_system.organizations:
            org_names = [o.get("name", "") if isinstance(o, dict) else str(o) for o in magic_system.organizations]
            if len(org_names) != len(set(org_names)):
                warnings.append("存在同名组织，可能需要区分")

        # Check forbidden techniques vs levels
        if magic_system.forbidden_techniques and magic_system.levels:
            # If there are forbidden techniques but no clear power progression, suggest improvement
            if len(magic_system.levels) < 3:
                suggestions.append("有禁术设定但等级较少，建议增加等级以体现禁术的危险性")

        # Check artifacts vs power source
        if magic_system.artifacts and not magic_system.source_of_power:
            warnings.append("系统有神器设定但未说明力量来源")

        # Balance check
        if len(magic_system.limitations) < 2 and len(magic_system.rules) > 5:
            suggestions.append("系统规则较多但限制较少，可能存在平衡问题")

        return {
            "issues": issues,
            "warnings": warnings,
            "suggestions": suggestions,
            "status": "consistent" if not issues else "needs_review",
            "completeness_score": self._calculate_completeness(magic_system),
        }

    def _calculate_completeness(self, magic_system: MagicSystem) -> float:
        """Calculate how complete the magic system is (0.0 - 1.0)."""
        score = 0.0
        total = 12.0

        if magic_system.name:
            score += 0.5
        if magic_system.source_of_power:
            score += 1.0
        if magic_system.rules:
            score += min(1.0, len(magic_system.rules) / 5)
        if magic_system.limitations:
            score += min(1.0, len(magic_system.limitations) / 4)
        if magic_system.levels:
            score += min(1.0, len(magic_system.levels) / 4)
        if magic_system.schools_or_types:
            score += min(1.0, len(magic_system.schools_or_types) / 3)
        if magic_system.training_methods:
            score += 0.5
        if magic_system.artifacts:
            score += 0.5
        if magic_system.organizations:
            score += 0.5
        if magic_system.weaknesses:
            score += 0.5
        if magic_system.world_influence:
            score += 0.5
        if magic_system.history:
            score += 0.5

        return round(score / total, 2)

    def validate_power_levels(
        self,
        magic_system: MagicSystem,
    ) -> dict[str, Any]:
        """Validate power level progression makes sense.

        Args:
            magic_system: The magic system

        Returns:
            Dict with validation results
        """
        issues = []

        if not magic_system.levels:
            return {
                "valid": False,
                "issues": ["没有定义等级体系"],
                "levels": [],
            }

        levels = magic_system.levels
        if len(levels) < 2:
            issues.append("等级数量过少，建议至少3个级别")

        # Check for ascending progression
        power_keywords = ["初级", "入门", "中级", "进阶", "高级", "精英", "大师", "传说"]
        found_keywords = [kw for kw in power_keywords if any(kw in lvl for lvl in levels)]

        if len(found_keywords) < 2:
            issues.append("等级命名可能缺乏渐进性，难以区分层次")

        # Check consistency with limitations
        if magic_system.limitations and levels:
            if len(levels) > 5 and len(magic_system.limitations) < 2:
                issues.append("等级很多但限制很少，可能导致力量膨胀")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "levels": levels,
            "level_count": len(levels),
        }

    def get_system_summary(
        self,
        magic_system: MagicSystem,
    ) -> str:
        """Get a human-readable summary of the magic system.

        Args:
            magic_system: The magic system

        Returns:
            Formatted string summary
        """
        lines = [
            f"=== {magic_system.name} ===",
            f"类型: {magic_system.system_type}",
            "",
        ]

        if magic_system.source_of_power:
            lines.append(f"【力量来源】{magic_system.source_of_power}")

        if magic_system.power_origin_story:
            lines.extend(["", "【起源】"])
            lines.append(f"  {magic_system.power_origin_story}")

        if magic_system.rules:
            lines.extend(["", "【核心规则】"])
            for i, rule in enumerate(magic_system.rules, 1):
                lines.append(f"  {i}. {rule}")

        if magic_system.limitations:
            lines.extend(["", "【限制与代价】"])
            for i, limit in enumerate(magic_system.limitations, 1):
                lines.append(f"  {i}. {limit}")

        if magic_system.levels:
            lines.extend(["", "【等级体系】"])
            for i, level in enumerate(magic_system.levels, 1):
                lines.append(f"  {i}. {level}")

        if magic_system.schools_or_types:
            lines.extend(["", "【流派分支】"])
            for school in magic_system.schools_or_types:
                if isinstance(school, dict):
                    lines.append(f"  • {school.get('name', '未知')}: {school.get('description', '')[:50]}")

        if magic_system.training_methods:
            lines.extend(["", "【修炼方式】"])
            for method in magic_system.training_methods[:3]:
                if isinstance(method, dict):
                    lines.append(f"  • {method.get('name', '未知')}")

        if magic_system.organizations:
            lines.extend(["", "【相关组织】"])
            for org in magic_system.organizations:
                if isinstance(org, dict):
                    lines.append(f"  • {org.get('name', '未知')} ({org.get('type', '')})")

        if magic_system.artifacts:
            lines.extend(["", "【神器/秘宝】"])
            for artifact in magic_system.artifacts[:3]:
                if isinstance(artifact, dict):
                    lines.append(f"  • {artifact.get('name', '未知')}")

        if magic_system.forbidden_techniques:
            lines.extend(["", "【禁术】"])
            for technique in magic_system.forbidden_techniques:
                if isinstance(technique, dict):
                    lines.append(f"  • {technique.get('name', '未知')}: {technique.get('consequences', '')[:30]}")

        if magic_system.weaknesses:
            lines.extend(["", "【弱点】"])
            for weakness in magic_system.weaknesses:
                lines.append(f"  • {weakness}")

        if magic_system.world_influence:
            lines.extend(["", "【世界影响】"])
            lines.append(f"  {magic_system.world_influence}")

        if magic_system.social_acceptance:
            lines.extend(["", "【社会态度】"])
            lines.append(f"  {magic_system.social_acceptance}")

        return "\n".join(lines)

    def export_power_system(
        self,
        magic_system: MagicSystem,
        include_analysis: bool = True,
    ) -> dict[str, Any]:
        """Export magic system as a complete document.

        Args:
            magic_system: The magic system to export
            include_analysis: Whether to include consistency analysis

        Returns:
            Complete export dict
        """
        export_data = {
            "magic_system": magic_system.model_dump(),
            "summary": self.get_system_summary(magic_system),
        }

        if include_analysis:
            export_data["analysis"] = self.analyze_system_consistency(magic_system)
            export_data["power_level_validation"] = self.validate_power_levels(magic_system)

        return export_data

    async def expand_magic_system(
        self,
        magic_system: MagicSystem,
        expansion_type: str,
        world_context: Optional[dict] = None,
    ) -> MagicSystem:
        """Expand an existing magic system with new content.

        Args:
            magic_system: Existing magic system
            expansion_type: What to expand (schools, artifacts, organizations, history, techniques)
            world_context: Optional world context

        Returns:
            Updated MagicSystem with new content added
        """
        context = ""
        if world_context:
            context = f"世界观背景：{world_context}\n"

        if expansion_type == "schools":
            prompt = f"""请为以下{magic_system.system_type}系统添加更多流派/类型。

现有系统：{magic_system.name}
已有流派数量：{len(magic_system.schools_or_types)}
{context}

请生成3-5个新的流派补充，以JSON数组格式输出：

[
  {{
    "name": "新流派名称",
    "description": "描述",
    "typical_users": ["典型使用者"],
    "strengths": ["优势"],
    "weaknesses": ["劣势"],
    "core_techniques": ["核心技能"]
  }}
]"""
            result = await self.ai_service.generate(prompt)
            data = self.ai_service._parse_json_array(result)
            existing_names = {s.get("name", "") if isinstance(s, dict) else "" for s in magic_system.schools_or_types}
            for item in data:
                if isinstance(item, dict) and item.get("name", "") not in existing_names:
                    magic_system.schools_or_types.append(item)

        elif expansion_type == "artifacts":
            prompt = f"""请为以下{magic_system.system_type}系统添加更多神器/秘宝。

现有系统：{magic_system.name}
已有神器数量：{len(magic_system.artifacts)}
{context}

请生成3-5个新的神器补充，以JSON数组格式输出：

[
  {{
    "name": "神器名称",
    "description": "描述与来历",
    "power_level": "威力等级",
    "requirements": "使用条件",
    "limitations": "已知缺陷"
  }}
]"""
            result = await self.ai_service.generate(prompt)
            data = self.ai_service._parse_json_array(result)
            existing_names = {a.get("name", "") if isinstance(a, dict) else "" for a in magic_system.artifacts}
            for item in data:
                if isinstance(item, dict) and item.get("name", "") not in existing_names:
                    magic_system.artifacts.append(item)

        elif expansion_type == "organizations":
            prompt = f"""请为以下{magic_system.system_type}系统添加更多相关组织。

现有系统：{magic_system.name}
已有组织数量：{len(magic_system.organizations)}
{context}

请生成3-5个新的组织补充，以JSON数组格式输出：

[
  {{
    "name": "组织名称",
    "type": "类型",
    "leader": "领导者",
    "size": "规模",
    "goals": ["主要目标"],
    "ideology": "核心理念",
    "relationship_with_system": "与此系统的关系"
  }}
]"""
            result = await self.ai_service.generate(prompt)
            data = self.ai_service._parse_json_array(result)
            existing_names = {o.get("name", "") if isinstance(o, dict) else "" for o in magic_system.organizations}
            for item in data:
                if isinstance(item, dict) and item.get("name", "") not in existing_names:
                    magic_system.organizations.append(item)

        elif expansion_type == "history":
            prompt = f"""请为以下{magic_system.system_type}系统添加更多历史。

现有系统：{magic_system.name}
已有历史事件：{len(magic_system.history)}
{context}

请生成3-5个新的历史事件补充，以JSON数组格式输出：

[
  {{
    "era": "时代/时期",
    "event": "重大事件",
    "impact": "对系统的影响"
  }}
]"""
            result = await self.ai_service.generate(prompt)
            data = self.ai_service._parse_json_array(result)
            for item in data:
                if isinstance(item, dict):
                    magic_system.history.append(item)

        elif expansion_type == "forbidden":
            prompt = f"""请为以下{magic_system.system_type}系统添加更多禁术/禁忌。

现有系统：{magic_system.name}
已有禁术数量：{len(magic_system.forbidden_techniques)}
{context}

请生成2-4个新的禁术补充，以JSON数组格式输出：

[
  {{
    "name": "禁术名称",
    "description": "为何被禁止",
    "original_purpose": "原本目的",
    "consequences": "使用后果"
  }}
]"""
            result = await self.ai_service.generate(prompt)
            data = self.ai_service._parse_json_array(result)
            existing_names = {f.get("name", "") if isinstance(f, dict) else "" for f in magic_system.forbidden_techniques}
            for item in data:
                if isinstance(item, dict) and item.get("name", "") not in existing_names:
                    magic_system.forbidden_techniques.append(item)

        return magic_system
