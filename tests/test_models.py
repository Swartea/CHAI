"""Tests for data models."""

import pytest
from chai.models import (
    WorldSetting,
    Character,
    CharacterRole,
    CharacterRelationship,
    PlotOutline,
    PlotArc,
    PlotPoint,
    PlotPointType,
    Novel,
    Volume,
    Chapter,
    Scene,
)


class TestWorldSetting:
    """Tests for WorldSetting model."""

    def test_create_world_setting(self):
        """Test creating a world setting."""
        world = WorldSetting(
            name="测试世界",
            genre="玄幻",
            geography={"continents": ["主大陆"]},
            politics={"government": "君主制"},
        )

        assert world.name == "测试世界"
        assert world.genre == "玄幻"
        assert "主大陆" in world.geography["continents"]

    def test_world_setting_defaults(self):
        """Test world setting default values."""
        world = WorldSetting(name="默认世界", genre="都市")

        assert world.geography == {}
        assert world.politics == {}
        assert world.culture == {}
        assert world.history == {}


class TestCharacter:
    """Tests for Character model."""

    def test_create_character(self):
        """Test creating a character."""
        char = Character(
            id="char_1",
            name="张三",
            role=CharacterRole.PROTAGONIST,
            backstory="从小习武",
            motivation="成为武林盟主",
            goal="统一江湖",
        )

        assert char.id == "char_1"
        assert char.name == "张三"
        assert char.role == CharacterRole.PROTAGONIST

    def test_character_relationships(self):
        """Test character with relationships."""
        rel = CharacterRelationship(
            character_id="char_2",
            relationship_type="friend",
            description="青梅竹马",
            dynamics="相互扶持",
        )

        char = Character(
            id="char_1",
            name="张三",
            role=CharacterRole.PROTAGONIST,
            relationships=[rel],
        )

        assert len(char.relationships) == 1
        assert char.relationships[0].relationship_type == "friend"


class TestPlotOutline:
    """Tests for PlotOutline model."""

    def test_create_plot_outline(self):
        """Test creating a plot outline."""
        plot_point = PlotPoint(
            id="pp_1",
            point_type=PlotPointType.EXPOSITION,
            title="开场",
            description="介绍主角",
            chapter_range=(1, 2),
        )

        arc = PlotArc(
            id="main_arc",
            name="主线",
            arc_type="main",
            plot_points=[plot_point],
        )

        outline = PlotOutline(
            structure_type="three_act",
            genre="玄幻",
            theme=["成长"],
            plot_arcs=[arc],
        )

        assert outline.structure_type == "three_act"
        assert len(outline.plot_arcs) == 1
        assert outline.plot_arcs[0].plot_points[0].title == "开场"


class TestNovel:
    """Tests for Novel model."""

    def test_create_novel(self):
        """Test creating a novel."""
        chapter = Chapter(
            id="ch_1",
            number=1,
            title="第一章",
            content="测试内容",
            word_count=100,
        )

        volume = Volume(
            id="vol_1",
            title="第一卷",
            number=1,
            chapters=[chapter],
        )

        novel = Novel(
            id="novel_1",
            title="测试小说",
            genre="玄幻",
            volumes=[volume],
        )

        assert novel.title == "测试小说"
        assert len(novel.volumes) == 1
        assert novel.volumes[0].chapters[0].number == 1

    def test_novel_word_count(self):
        """Test calculating novel word count."""
        chapters = [
            Chapter(id="ch_1", number=1, title="第一章", word_count=3000),
            Chapter(id="ch_2", number=2, title="第二章", word_count=3500),
        ]

        volume = Volume(
            id="vol_1",
            title="第一卷",
            number=1,
            chapters=chapters,
        )

        novel = Novel(
            id="novel_1",
            title="测试小说",
            genre="玄幻",
            volumes=[volume],
        )

        total = sum(c.word_count for c in volume.chapters)
        assert total == 6500
