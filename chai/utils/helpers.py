"""Helper utilities for CHAI."""

import json
from pathlib import Path
from chai.models import Novel, Chapter, Volume, WorldSetting, Character, PlotOutline


def save_novel(novel: Novel, path: str | Path) -> Path:
    """Save novel to JSON file."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    data = novel.model_dump(mode='json')

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return path


def load_novel(path: str | Path) -> Novel:
    """Load novel from JSON file."""
    path = Path(path)

    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    return Novel.model_validate(data)


def create_sample_novel() -> Novel:
    """Create a sample novel for testing."""
    world = WorldSetting(
        name="测试世界",
        genre="玄幻",
        geography={"continents": ["主大陆"], "countries": ["王国"]},
        politics={"government": "君主制"},
        culture={"religion": "多神教"},
        history={"events": []},
    )

    characters = [
        Character(
            id="char_0",
            name="主角",
            role="protagonist",
            backstory="从小立志成为强者",
            motivation="保护家人",
            goal="成为天下第一",
        ),
    ]

    chapters = [
        Chapter(
            id="ch_1",
            number=1,
            title="第一章：开始",
            summary="故事从这里开始",
            content="这是一个测试章节的内容。",
            word_count=50,
            status="complete",
        ),
    ]

    volume = Volume(
        id="vol_1",
        title="第一卷",
        number=1,
        description="测试卷",
        chapters=chapters,
    )

    novel = Novel(
        id="test_novel",
        title="测试小说",
        genre="玄幻",
        world_setting=world,
        characters=characters,
        volumes=[volume],
        has_prologue=False,
        has_epilogue=False,
    )

    return novel
