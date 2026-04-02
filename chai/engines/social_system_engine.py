"""Social system engine for comprehensive social structure and faction generation."""

from typing import Optional, Any
from chai.models import (
    SocialStructure,
    SocialClass,
    Faction,
    FactionRelationship,
    Guild,
    CriminalOrganization,
    ReligiousInstitution,
    SecretSociety,
    SocialConflict,
)
from chai.services import AIService


class SocialSystemEngine:
    """Engine for building comprehensive social structures and faction systems.

    Provides methods to generate, analyze, and manage social hierarchies,
    factions, organizations, and social conflicts.
    """

    def __init__(self, ai_service: AIService):
        """Initialize with AI service."""
        self.ai_service = ai_service

    async def build_social_system(
        self,
        genre: str,
        theme: str,
        geography: Optional[dict] = None,
        politics: Optional[dict] = None,
        culture: Optional[dict] = None,
        magic_system: Optional[Any] = None,
    ) -> SocialStructure:
        """Build a complete social system.

        Args:
            genre: Novel genre
            theme: Central theme
            geography: Geography data for context
            politics: Politics data for context
            culture: Culture data for context
            magic_system: Magic/tech system for context

        Returns:
            Complete SocialStructure
        """
        context = self._build_context_string(genre, theme, geography, politics, culture, magic_system)

        prompt = f"""为{genre}类型小说生成详细完整的社会结构设定。

主题：{theme}
{context}

请生成包含以下方面的详细社会结构设定，以JSON格式输出：

{{
  "classes": [
    {{
      "name": "阶层名称",
      "description": "详细描述",
      "typical_members": ["典型成员"],
      "lifestyle": "生活方式",
      "rights": ["享有的权利"],
      "obligations": ["承担的义务"],
      "relationship_with_other_classes": [{{"class": "其他阶层名", "type": "关系类型", "description": "关系描述"}}],
      "economic_base": "经济基础",
      "political_influence": 5,
      "population_percentage": "人口比例"
    }}
  ],
  "social_mobility": "社会流动性描述",
  "family_structures": ["主要家庭结构类型"],
  "wealth_distribution": "财富分布描述",

  "factions": [
    {{
      "name": "势力名称",
      "faction_type": "类型",
      "description": "详细描述",
      "leader": "领导者",
      "leadership_structure": "领导结构",
      "internal_hierarchy": ["层级列表"],
      "membership": "成员规模",
      "recruitment": "招募方式",
      "membership_requirements": ["加入条件"],
      "goals": ["目标"],
      "ideology": "意识形态",
      "values": ["核心价值"],
      "resources": ["资源"],
      "power_level": 5,
      "military_strength": "军事实力",
      "economic_power": "经济实力",
      "political_alignment": "政治立场",
      "territories": ["控制地区"],
      "headquarters": "总部位置",
      "symbol": "标志",
      "founding_story": "创立故事",
      "founding_date": "创立日期",
      "historical_events": [{{"event": "事件", "year": "年份", "impact": "影响"}}],
      "allies": ["盟友势力"],
      "rivals": ["竞争对手"],
      "enemies": ["敌对势力"],
      "notable_members": [{{"name": "姓名", "role": "角色", "description": "描述"}}],
      "current_status": "现状",
      "current_goals": ["当前目标"]
    }}
  ],

  "guilds": [
    {{
      "name": "公会名称",
      "profession": "行业",
      "description": "描述",
      "hierarchy": ["等级列表"],
      "membership_requirements": ["入会条件"],
      "notable_members": ["著名成员"],
      "resources": ["资源"],
      "influence": "影响力",
      "headquarters": "总部位置",
      "allied_factions": ["友好势力"],
      "rival_guilds": ["竞争公会"]
    }}
  ],

  "criminal_organizations": [
    {{
      "name": "组织名称",
      "description": "描述",
      "organizational_structure": "组织结构",
      "leader": "首领",
      "territories": ["控制区域"],
      "illegal_activities": ["非法活动"],
      "legitimate_businesses": ["合法业务"],
      "alliances": ["盟友"],
      "rival_organizations": ["敌对组织"],
      "law_enforcement_relationship": "与执法部门关系",
      "influence": "影响力"
    }}
  ],

  "religious_institutions": [
    {{
      "name": "宗教名称",
      "deity_or_belief": "信仰的神",
      "description": "描述",
      "hierarchy": ["宗教等级"],
      "holy_sites": ["圣地"],
      "practices": ["主要仪式"],
      "political_influence": "政治影响力",
      "factions_within": ["内部派系"],
      "relationship_with_state": "与国家关系",
      "allied_factions": ["友好势力"],
      "rival_religions": ["敌对宗教"]
    }}
  ],

  "secret_societies": [
    {{
      "name": "秘密社团名称",
      "description": "描述",
      "secrecy_level": "保密等级",
      "membership": "成员数量",
      "hierarchy": ["等级结构"],
      "initiation_rituals": ["入会仪式"],
      "goals": ["真正目的"],
      "public_goals": ["公开目的"],
      "headquarters": "隐秘总部",
      "member_identifiers": ["成员标识"],
      "notable_members": ["著名成员"],
      "allied_secret_societies": ["友好社团"],
      "rival_secret_societies": ["敌对社团"]
    }}
  ],

  "faction_relationships": [
    {{
      "faction_a": "势力A",
      "faction_b": "势力B",
      "relationship_type": "关系类型",
      "description": "关系描述",
      "history": "关系历史",
      "current_status": "现状",
      "key_events": ["关键事件"]
    }}
  ],

  "power_distribution": {{
    "military": "军事力量分布",
    "economic": "经济力量分布",
    "political": "政治力量分布",
    "magical": "魔法力量分布",
    "information": "信息/知识力量分布"
  }},

  "economic_system": {{
    "type": "经济类型",
    "major_industries": ["主要产业"],
    "trade_routes": ["主要贸易路线"],
    "currency": "货币",
    "economic_disparity": "经济差距"
  }},

  "social_conflicts": [
    {{
      "name": "冲突名称",
      "description": "描述",
      "parties_involved": ["参与方"],
      "cause": "起因",
      "current_status": "现状",
      "key_battles_or_events": [{{"event": "事件", "year": "年份", "outcome": "结果"}}],
      "stakes": "赌注",
      "potential_resolutions": ["可能的解决方案"],
      "impact_on_society": "对社会影响"
    }}
  ],

  "conflict_lines": ["社会冲突的主要分界线"],

  "social_norms": ["重要社会规范"],
  "taboos": ["主要禁忌"],

  "regional_variations": [
    {{
      "region": "地区名称",
      "class_structure": "阶层结构差异",
      "dominant_factions": ["主导势力"],
      "cultural_differences": "文化差异",
      "economic_differences": "经济差异"
    }}
  ]
}}"""
        result = await self.ai_service.generate(prompt)
        data = self.ai_service._parse_json(result)
        return self._parse_social_structure(data)

    def _parse_social_structure(self, data: dict) -> SocialStructure:
        """Parse raw data into SocialStructure model.

        Args:
            data: Raw social structure data

        Returns:
            SocialStructure instance
        """
        return SocialStructure(
            classes=data.get("classes", []),
            social_mobility=data.get("social_mobility", ""),
            family_structures=data.get("family_structures", []),
            wealth_distribution=data.get("wealth_distribution", ""),
            factions=data.get("factions", []),
            guilds=data.get("guilds", []),
            criminal_organizations=data.get("criminal_organizations", []),
            religious_institutions=data.get("religious_institutions", []),
            secret_societies=data.get("secret_societies", []),
            faction_relationships=data.get("faction_relationships", []),
            power_distribution=data.get("power_distribution", {}),
            economic_system=data.get("economic_system", {}),
            social_conflicts=data.get("social_conflicts", []),
            conflict_lines=data.get("conflict_lines", []),
            social_norms=data.get("social_norms", []),
            taboos=data.get("taboos", []),
            regional_variations=data.get("regional_variations", []),
        )

    async def generate_faction(
        self,
        faction_type: str,
        genre: str,
        theme: str,
        existing_factions: Optional[list[dict]] = None,
    ) -> dict:
        """Generate a specific faction with detailed information.

        Args:
            faction_type: Type of faction to generate
            genre: Novel genre
            theme: Central theme
            existing_factions: List of existing faction names to avoid duplication

        Returns:
            Detailed faction data
        """
        existing_names = ", ".join([f["name"] for f in existing_factions]) if existing_factions else "无"
        prompt = f"""为{genre}类型小说生成一个详细的{faction_type}类型势力。

主题：{theme}
已存在的势力：{existing_names}

请生成包含以下方面的详细设定，以JSON格式输出：
{{
  "name": "势力名称（必须是新的独特名称，不能与已存在的势力重复）",
  "faction_type": "{faction_type}",
  "description": "详细描述",
  "leader": "领导者",
  "leadership_structure": "领导结构",
  "internal_hierarchy": ["层级列表"],
  "membership": "成员规模",
  "recruitment": "招募方式",
  "membership_requirements": ["加入条件"],
  "goals": ["目标"],
  "ideology": "意识形态",
  "values": ["核心价值"],
  "resources": ["资源"],
  "power_level": 5,
  "military_strength": "军事实力",
  "economic_power": "经济实力",
  "political_alignment": "政治立场",
  "territories": ["控制地区"],
  "headquarters": "总部位置",
  "symbol": "标志",
  "founding_story": "创立故事",
  "founding_date": "创立日期",
  "historical_events": [{{"event": "事件", "year": "年份", "impact": "影响"}}],
  "allies": ["盟友势力"],
  "rivals": ["竞争对手"],
  "enemies": ["敌对势力"],
  "notable_members": [{{"name": "姓名", "role": "角色", "description": "描述"}}],
  "current_status": "现状",
  "current_goals": ["当前目标"]
}}"""
        result = await self.ai_service.generate(prompt)
        data = self.ai_service._parse_json(result)
        return data

    async def generate_factions_batch(
        self,
        faction_types: list[str],
        genre: str,
        theme: str,
        existing_factions: Optional[list[dict]] = None,
    ) -> list[dict]:
        """Generate multiple factions at once.

        Args:
            faction_types: List of faction types to generate
            genre: Novel genre
            theme: Central theme
            existing_factions: Existing factions to avoid duplication

        Returns:
            List of faction data dicts
        """
        existing_names = ", ".join([f["name"] for f in existing_factions]) if existing_factions else "无"
        types_str = ", ".join(faction_types)
        prompt = f"""为{genre}类型小说生成{len(faction_types)}个不同类型的势力。

主题：{theme}
势力类型：{types_str}
已存在的势力：{existing_names}

请为每种类型生成一个独特的势力，确保名称和设定不与已存在的势力重复。以JSON数组格式输出：
[
  {{
    "name": "势力名称",
    "faction_type": "类型",
    ...
  }},
  ...
]"""
        result = await self.ai_service.generate(prompt)
        data = self.ai_service._parse_json(result)
        if isinstance(data, list):
            return data
        return [data] if isinstance(data, dict) else []

    def analyze_faction_relationships(
        self,
        factions: list[dict],
    ) -> list[dict]:
        """Analyze relationships between factions.

        Args:
            factions: List of faction data

        Returns:
            List of FactionRelationship dicts
        """
        relationships = []
        faction_names = [f.get("name", "") for f in factions if f.get("name")]

        for faction in factions:
            name = faction.get("name", "")

            # Process explicit allies
            for ally_name in faction.get("allies", []):
                if ally_name in faction_names and ally_name != name:
                    relationships.append({
                        "faction_a": name,
                        "faction_b": ally_name,
                        "relationship_type": "alliance",
                        "description": f"{name}与{ally_name}结为盟友",
                        "current_status": "stable",
                    })

            # Process explicit rivals
            for rival_name in faction.get("rivals", []):
                if rival_name in faction_names and rival_name != name:
                    relationships.append({
                        "faction_a": name,
                        "faction_b": rival_name,
                        "relationship_type": "rivalry",
                        "description": f"{name}与{rival_name}存在竞争关系",
                        "current_status": "tense",
                    })

            # Process explicit enemies
            for enemy_name in faction.get("enemies", []):
                if enemy_name in faction_names and enemy_name != name:
                    relationships.append({
                        "faction_a": name,
                        "faction_b": enemy_name,
                        "relationship_type": "hostile",
                        "description": f"{name}与{enemy_name}处于敌对状态",
                        "current_status": "active_conflict",
                    })

        # Deduplicate
        seen = set()
        unique_rels = []
        for rel in relationships:
            key = tuple(sorted([rel["faction_a"], rel["faction_b"]]))
            if key not in seen:
                seen.add(key)
                unique_rels.append(rel)

        return unique_rels

    def analyze_social_consistency(
        self,
        social_structure: SocialStructure,
    ) -> dict[str, Any]:
        """Analyze social structure for logical consistency.

        Args:
            social_structure: SocialStructure to analyze

        Returns:
            Analysis results with issues and recommendations
        """
        issues = []
        recommendations = []

        # Check class count
        if len(social_structure.classes) < 2:
            issues.append("社会阶层数量过少，建议至少2个阶层以形成对比")

        # Check faction count
        total_factions = (
            len(social_structure.factions)
            + len(social_structure.guilds)
            + len(social_structure.criminal_organizations)
            + len(social_structure.religious_institutions)
        )
        if total_factions < 3:
            issues.append("势力数量过少，建议增加更多势力以丰富世界")

        # Check for faction-territory alignment
        for faction in social_structure.factions:
            territories = faction.get("territories", [])
            if not territories and faction.get("faction_type") not in ["secret", "hidden"]:
                recommendations.append(f"势力'{faction.get('name')}'没有控制领土，考虑添加地理控制区域")

        # Check leadership distribution
        factions_without_leaders = [
            f.get("name") for f in social_structure.factions
            if not f.get("leader") and f.get("faction_type") not in ["secret", "hidden"]
        ]
        if factions_without_leaders:
            recommendations.append(f"以下势力缺少领导者：{', '.join(factions_without_leaders)}")

        # Check for faction relationships
        if len(social_structure.faction_relationships) == 0 and len(social_structure.factions) > 1:
            recommendations.append("考虑为势力之间添加正式的关系描述")

        # Check economic system
        if not social_structure.economic_system:
            recommendations.append("考虑添加详细的经济系统设定")

        # Check social conflicts
        if len(social_structure.social_conflicts) == 0 and len(social_structure.classes) > 1:
            recommendations.append("考虑添加社会冲突以增加戏剧性")

        # Check power distribution
        if not social_structure.power_distribution:
            recommendations.append("考虑详细描述权力分布情况")

        return {
            "issues": issues,
            "recommendations": recommendations,
            "status": "consistent" if len(issues) == 0 else "needs_review",
            "stats": {
                "class_count": len(social_structure.classes),
                "faction_count": len(social_structure.factions),
                "guild_count": len(social_structure.guilds),
                "criminal_org_count": len(social_structure.criminal_organizations),
                "religious_count": len(social_structure.religious_institutions),
                "secret_society_count": len(social_structure.secret_societies),
                "conflict_count": len(social_structure.social_conflicts),
            },
        }

    def get_social_summary(
        self,
        social_structure: SocialStructure,
    ) -> str:
        """Get human-readable summary of social structure.

        Args:
            social_structure: SocialStructure to summarize

        Returns:
            Formatted summary string
        """
        lines = ["=== 社会结构概要 ===", ""]

        # Classes
        lines.append(f"【社会阶层】共{len(social_structure.classes)}个阶层")
        for cls in social_structure.classes[:5]:
            name = cls.get("name", "未知")
            influence = cls.get("political_influence", "?")
            lines.append(f"  - {name} (政治影响力: {influence})")
        if len(social_structure.classes) > 5:
            lines.append(f"  ... 还有{len(social_structure.classes) - 5}个阶层")

        # Factions
        total_factions = len(social_structure.factions)
        lines.append(f"\n【主要势力】共{total_factions}个")
        for faction in social_structure.factions[:5]:
            name = faction.get("name", "未知")
            ftype = faction.get("faction_type", "")
            power = faction.get("power_level", "?")
            lines.append(f"  - {name} ({ftype}) [ power: {power} ]")
        if total_factions > 5:
            lines.append(f"  ... 还有{total_factions - 5}个势力")

        # Organizations
        if social_structure.guilds:
            lines.append(f"\n【公会组织】共{len(social_structure.guilds)}个")
        if social_structure.criminal_organizations:
            lines.append(f"【地下组织】共{len(social_structure.criminal_organizations)}个")
        if social_structure.religious_institutions:
            lines.append(f"【宗教势力】共{len(social_structure.religious_institutions)}个")
        if social_structure.secret_societies:
            lines.append(f"【秘密社团】共{len(social_structure.secret_societies)}个")

        # Conflicts
        if social_structure.social_conflicts:
            lines.append(f"\n【社会冲突】共{len(social_structure.social_conflicts)}起")
            for conflict in social_structure.social_conflicts[:3]:
                status = conflict.get("current_status", "")
                lines.append(f"  - {conflict.get('name')} ({status})")

        # Social mobility
        if social_structure.social_mobility:
            lines.append(f"\n【社会流动性】{social_structure.social_mobility}")

        return "\n".join(lines)

    def export_social_system(
        self,
        social_structure: SocialStructure,
        include_analysis: bool = True,
    ) -> dict[str, Any]:
        """Export social system as complete document.

        Args:
            social_structure: SocialStructure to export
            include_analysis: Whether to include consistency analysis

        Returns:
            Complete social system data
        """
        export_data = {
            "social_structure": social_structure.model_dump(),
            "summary": self.get_social_summary(social_structure),
        }

        if include_analysis:
            export_data["analysis"] = self.analyze_social_consistency(social_structure)

        return export_data

    async def expand_social_system(
        self,
        social_structure: SocialStructure,
        expansion_type: str,
        genre: str = "玄幻",
        theme: str = "",
    ) -> SocialStructure:
        """Expand an existing social structure.

        Args:
            social_structure: Existing social structure
            expansion_type: Type of expansion: factions, guilds, criminal, religious, secret, conflicts
            genre: Novel genre
            theme: Central theme

        Returns:
            Updated SocialStructure
        """
        if expansion_type == "factions":
            existing_factions = social_structure.factions
            new_factions = await self.generate_factions_batch(
                ["royal", "military", "political"],
                genre=genre,
                theme=theme,
                existing_factions=existing_factions,
            )
            social_structure.factions = existing_factions + new_factions

        elif expansion_type == "guilds":
            existing_factions = social_structure.factions + social_structure.guilds
            new_guilds = await self.generate_factions_batch(
                ["merchant", "craft", "scholarly"],
                genre=genre,
                theme=theme,
                existing_factions=existing_factions,
            )
            social_structure.guilds = social_structure.guilds + new_guilds

        elif expansion_type == "criminal":
            new_orgs = await self.generate_factions_batch(
                ["criminal"],
                genre=genre,
                theme=theme,
                existing_factions=social_structure.factions,
            )
            social_structure.criminal_organizations = (
                social_structure.criminal_organizations + new_orgs
            )

        elif expansion_type == "religious":
            new_religions = await self.generate_factions_batch(
                ["religious"],
                genre=genre,
                theme=theme,
                existing_factions=social_structure.factions,
            )
            social_structure.religious_institutions = (
                social_structure.religious_institutions + new_religions
            )

        elif expansion_type == "secret":
            new_secrets = await self.generate_factions_batch(
                ["secret"],
                genre=genre,
                theme=theme,
                existing_factions=social_structure.factions,
            )
            social_structure.secret_societies = (
                social_structure.secret_societies + new_secrets
            )

        elif expansion_type == "conflicts":
            prompt = f"""基于现有的社会结构，生成一个新的社会冲突。

现有势力：{[f.get('name') for f in social_structure.factions]}
现有阶层：{[c.get('name') for c in social_structure.classes]}

请生成一个新的社会冲突，以JSON格式输出：
{{
  "name": "冲突名称",
  "description": "描述",
  "parties_involved": ["参与方"],
  "cause": "起因",
  "current_status": "现状",
  "key_battles_or_events": [{{"event": "事件", "year": "年份", "outcome": "结果"}}],
  "stakes": "赌注",
  "potential_resolutions": ["可能的解决方案"],
  "impact_on_society": "对社会影响"
}}"""
            result = await self.ai_service.generate(prompt)
            data = self.ai_service._parse_json(result)
            social_structure.social_conflicts = social_structure.social_conflicts + [data]

        # Recalculate faction relationships
        if expansion_type in ["factions", "guilds", "criminal", "religious", "secret"]:
            all_factions = (
                social_structure.factions
                + social_structure.guilds
                + social_structure.criminal_organizations
                + social_structure.religious_institutions
            )
            social_structure.faction_relationships = self.analyze_faction_relationships(all_factions)

        return social_structure

    def _build_context_string(
        self,
        genre: str,
        theme: str,
        geography: Optional[dict],
        politics: Optional[dict],
        culture: Optional[dict],
        magic_system: Optional[Any],
    ) -> str:
        """Build context string for prompts."""
        context_parts = []

        if geography:
            countries = geography.get("countries", [])
            if countries:
                country_names = ", ".join([c.get("name", "") for c in countries[:5]])
                context_parts.append(f"地理背景：已知国家/地区包括 {country_names}")
            cities = geography.get("cities", [])
            if cities:
                city_names = ", ".join([c.get("name", "") for c in cities[:5]])
                context_parts.append(f"主要城市：{city_names}")

        if politics:
            governments = politics.get("governments", [])
            if governments:
                gov_names = ", ".join([g.get("name", "") for g in governments[:3]])
                context_parts.append(f"政治体制：{gov_names}")
            factions = politics.get("factions", [])
            if factions:
                faction_names = ", ".join([f.get("name", "") for f in factions[:5]])
                context_parts.append(f"政治势力：{faction_names}")

        if culture:
            religions = culture.get("religions", [])
            if religions:
                rel_names = ", ".join([r.get("name", "") for r in religions[:3]])
                context_parts.append(f"宗教信仰：{rel_names}")
            traditions = culture.get("traditions", [])
            if traditions:
                context_parts.append(f"文化传统：存在{len(traditions)}项主要传统")

        if magic_system:
            ms_name = getattr(magic_system, "name", "未知魔法系统")
            ms_type = getattr(magic_system, "system_type", "")
            context_parts.append(f"异能/魔法系统：{ms_name} ({ms_type})")

        if context_parts:
            return "背景信息：\n" + "\n".join(f"- {c}" for c in context_parts) + "\n"
        return ""
