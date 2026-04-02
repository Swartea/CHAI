"""Scene description models for environment, atmosphere, and visual details."""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class EnvironmentType(str, Enum):
    """Type of environment/setting."""
    INDOOR = "indoor"           # Inside a building
    OUTDOOR = "outdoor"         # Open air
    NATURAL = "natural"         # Forests, mountains, beaches
    URBAN = "urban"             # City streets, buildings
    RURAL = "rural"             # Countryside, villages
    FANTASY = "fantasy"         # Magical or fictional
    SCI_FI = "sci_fi"          # Sci-fi settings
    MYSTERIOUS = "mysterious"  # Ominous or unknown


class LightingCondition(str, Enum):
    """Lighting conditions in a scene."""
    BRIGHT = "bright"           # Full daylight, clear sun
    DIM = "dim"                 # Low light, overcast
    DARK = "dark"               # Night, deep shadow
    DRAMATIC = "dramatic"       # Strong contrast, chiaroscuro
    SOFT = "soft"               # Diffused, gentle
    ARTIFICIAL = "artificial"   # Lamplight, candles, neon
    MOONLIGHT = "moonlight"     # Night with moon
    SUNSET = "sunset"           # Golden hour
    DAWN = "dawn"               # Early morning
    FOGGY = "foggy"             # Mist, fog


class WeatherCondition(str, Enum):
    """Weather conditions."""
    CLEAR = "clear"
    CLOUDY = "cloudy"
    RAINY = "rainy"
    STORMY = "stormy"
    SNOWY = "snowy"
    WINDY = "windy"
    FOGGY = "foggy"
    HOT = "hot"
    COLD = "cold"
    HUMID = "humid"
    DRY = "dry"


class TimeOfDay(str, Enum):
    """Time of day."""
    DAWN = "dawn"               # 5-7 AM
    MORNING = "morning"         # 7-12 PM
    NOON = "noon"               # 12-2 PM
    AFTERNOON = "afternoon"    # 2-6 PM
    EVENING = "evening"         # 6-9 PM
    NIGHT = "night"             # 9 PM-5 AM
    MIDNIGHT = "midnight"       # 12 AM


class AtmosphereType(str, Enum):
    """Atmosphere/mood types."""
    NEUTRAL = "neutral"         # Neutral, balanced
    TENSE = "tense"             # Nervous, suspenseful
    PEACEFUL = "peaceful"       # Calm, serene
    MYSTERIOUS = "mysterious"   # Unknown, intriguing
    OMINOUS = "ominous"         # foreboding, threatening
    JOYFUL = "joyful"           # Happy, celebratory
    SAD = "sad"                 # Melancholic, grieving
    ROMANTIC = "romantic"        # Loving, intimate
    DANGEROUS = "dangerous"     # Threatening, risky
    EPIC = "epic"               # Grand, heroic
    LYRICAL = "lyrical"         # Poetic, beautiful
    GRIM = "grim"               # Dark, bleak
    HOPEFUL = "hopeful"          # Optimistic, uplifting
    NOSTALGIC = "nostalgic"     # Reminiscent, wistful
    EERIE = "eerie"              # Uncanny, unsettling
    COMIC = "comic"             # Humorous, light
    DRAMATIC = "dramatic"       # Intense, emotional


class VisualDetailType(str, Enum):
    """Types of visual details to include."""
    COLOR = "color"             # Color palette
    TEXTURE = "texture"         # Surface qualities
    SHAPE = "shape"             # Object shapes
    SIZE = "size"               # Scale and proportion
    MOVEMENT = "movement"       # Motion descriptions
    LIGHT = "light"             # How light interacts
    SHADOW = "shadow"           # Shadow patterns
    SPACE = "space"             # Spatial relationships
    DETAIL = "detail"           # Small details


class SensoryDetailType(str, Enum):
    """Sensory detail types beyond visual."""
    SOUND = "sound"             # Auditory details
    SMELL = "smell"             # Olfactory details
    TOUCH = "touch"             # Tactile details
    TASTE = "taste"             # Gustatory details
    TEMPERATURE = "temperature" # Heat/cold sensations


class SpatialLayout(str, Enum):
    """Spatial arrangement of a scene."""
    CRAMPED = "cramped"         # Small, tight space
    SPACIOUS = "spacious"       # Open, roomy
    VERTICAL = "vertical"       # Towering, high ceilings
    HORIZONTAL = "horizontal"  # Wide, sprawling
    COMPLEX = "complex"         # Multi-level, labyrinthine
    SIMPLE = "simple"           # Straightforward layout
    ORGANIZED = "organized"     # Neat, arranged
    CHAOTIC = "chaotic"         # Messy, disordered


class EnvironmentDetail(BaseModel):
    """Detailed environment/setting description."""
    environment_type: EnvironmentType = Field(
        default=EnvironmentType.INDOOR,
        description="Type of environment"
    )
    location_name: str = Field(
        default="",
        description="Specific location name"
    )
    architecture_style: Optional[str] = Field(
        default=None,
        description="Architectural style (e.g., gothic, minimalist, baroque)"
    )
    main_features: list[str] = Field(
        default_factory=list,
        description="Key features of the location"
    )
    decorative_elements: list[str] = Field(
        default_factory=list,
        description="Decorative items present"
    )
    spatial_layout: SpatialLayout = Field(
        default=SpatialLayout.SIMPLE,
        description="Spatial arrangement"
    )
    spatial_details: Optional[str] = Field(
        default=None,
        description="Description of space dimensions and layout"
    )
    props: list[str] = Field(
        default_factory=list,
        description="Important props/objects in scene"
    )


class LightingDetail(BaseModel):
    """Lighting conditions and effects."""
    condition: LightingCondition = Field(
        default=LightingCondition.DIM,
        description="Overall lighting condition"
    )
    light_source: Optional[str] = Field(
        default=None,
        description="Where the light comes from"
    )
    light_color: Optional[str] = Field(
        default=None,
        description="Color tint of light"
    )
    shadow_intensity: str = Field(
        default="medium",
        description="Shadow presence: none, low, medium, high, extreme"
    )
    shadow_pattern: Optional[str] = Field(
        default=None,
        description="How shadows fall in the scene"
    )
    light_effects: list[str] = Field(
        default_factory=list,
        description="Special light effects (glow, rays, etc.)"
    )


class WeatherDetail(BaseModel):
    """Weather conditions."""
    condition: WeatherCondition = Field(
        default=WeatherCondition.CLEAR,
        description="Weather condition"
    )
    temperature: Optional[str] = Field(
        default=None,
        description="Temperature description"
    )
    humidity: Optional[str] = Field(
        default=None,
        description="Humidity level"
    )
    wind: Optional[str] = Field(
        default=None,
        description="Wind conditions"
    )
    visibility: Optional[str] = Field(
        default=None,
        description="How far can be seen"
    )
    weather_effects: list[str] = Field(
        default_factory=list,
        description="Weather-related phenomena"
    )


class VisualDetail(BaseModel):
    """Visual detail specifications."""
    detail_types: list[VisualDetailType] = Field(
        default_factory=list,
        description="Types of visual details to emphasize"
    )
    color_palette: list[str] = Field(
        default_factory=list,
        description="Dominant colors in scene"
    )
    texture_descriptions: list[str] = Field(
        default_factory=list,
        description="Texture qualities to describe"
    )
    focal_point: Optional[str] = Field(
        default=None,
        description="What the eye is drawn to"
    )
    visual_contrasts: list[str] = Field(
        default_factory=list,
        description="Contrasting elements"
    )
    visual_highlights: list[str] = Field(
        default_factory=list,
        description="Notable visual features"
    )


class SensoryDetail(BaseModel):
    """Sensory detail specifications."""
    detail_types: list[SensoryDetailType] = Field(
        default_factory=list,
        description="Sensory details to include"
    )
    sound_descriptions: list[str] = Field(
        default_factory=list,
        description="Sounds to describe"
    )
    smell_descriptions: list[str] = Field(
        default_factory=list,
        description="Smells to describe"
    )
    touch_descriptions: list[str] = Field(
        default_factory=list,
        description="Tactile sensations"
    )
    temperature_sensation: Optional[str] = Field(
        default=None,
        description="How temperature feels"
    )
    taste_descriptions: list[str] = Field(
        default_factory=list,
        description="Taste sensations"
    )


class AtmosphereDetail(BaseModel):
    """Atmosphere and mood specifications."""
    atmosphere_type: AtmosphereType = Field(
        default=AtmosphereType.NEUTRAL,
        description="Primary atmosphere type"
    )
    atmosphere_intensity: str = Field(
        default="medium",
        description="Intensity: subtle, mild, moderate, strong, overwhelming"
    )
    emotional_tone: list[str] = Field(
        default_factory=list,
        description="Emotional qualities to convey"
    )
    atmosphere_indicators: list[str] = Field(
        default_factory=list,
        description="Environmental cues that signal the mood"
    )
    pacing_quality: str = Field(
        default="moderate",
        description="Scene pacing feel: slow, moderate, fast"
    )
    tension_level: str = Field(
        default="low",
        description="Narrative tension: none, low, moderate, high, critical"
    )


class SceneDescriptionPlan(BaseModel):
    """Complete scene description plan."""
    scene_id: str = Field(description="Scene identifier")
    scene_location: str = Field(description="Scene location summary")
    time_setting: TimeOfDay = Field(default=TimeOfDay.AFTERNOON)
    environment: EnvironmentDetail = Field(default_factory=EnvironmentDetail)
    lighting: LightingDetail = Field(default_factory=LightingDetail)
    weather: Optional[WeatherDetail] = Field(default=None)
    visual: VisualDetail = Field(default_factory=VisualDetail)
    sensory: SensoryDetail = Field(default_factory=SensoryDetail)
    atmosphere: AtmosphereDetail = Field(default_factory=AtmosphereDetail)

    # Writing guidance
    description_length: str = Field(
        default="medium",
        description="Length: brief (50-100字), short (100-200字), medium (200-400字), long (400-600字)"
    )
    description_focus: list[str] = Field(
        default_factory=list,
        description="What to focus on in description"
    )
    narrative_perspective: str = Field(
        default="third_person",
        description="Perspective for description: third_person, character_centric"
    )


class SceneDescriptionDraft(BaseModel):
    """Generated scene description draft."""
    plan: SceneDescriptionPlan = Field(description="The plan used")
    environment_description: str = Field(
        default="",
        description="Environment/setting description"
    )
    atmosphere_description: str = Field(
        default="",
        description="Atmosphere/mood description"
    )
    visual_details_description: str = Field(
        default="",
        description="Visual detail description"
    )
    sensory_description: str = Field(
        default="",
        description="Sensory detail description"
    )
    combined_description: str = Field(
        default="",
        description="Combined, flowing scene description"
    )
    word_count: int = Field(default=0, description="Total word count")
    status: str = Field(
        default="draft",
        description="Status: draft, revised, finalized"
    )


class SceneDescriptionRevision(BaseModel):
    """Revision details for scene description."""
    original_draft: SceneDescriptionDraft = Field(
        description="Original draft"
    )
    revision_notes: list[str] = Field(
        default_factory=list,
        description="What to revise"
    )
    revised_description: Optional[str] = Field(
        default=None,
        description="Revised combined description"
    )
    quality_score: Optional[float] = Field(
        default=None,
        description="Quality score 0-1"
    )


class SceneDescriptionAnalysis(BaseModel):
    """Analysis of scene description quality."""
    scene_id: str = Field(description="Scene identifier")
    atmosphere_consistency: float = Field(
        default=0.0,
        description="Consistency score 0-1"
    )
    visual_immersion: float = Field(
        default=0.0,
        description="Visual immersion score 0-1"
    )
    sensory_balance: float = Field(
        default=0.0,
        description="Sensory detail balance 0-1"
    )
    descriptive_density: str = Field(
        default="medium",
        description="Density: too_sparse, sparse, medium, rich, too_rich"
    )
    issues: list[str] = Field(
        default_factory=list,
        description="Issues found"
    )
    suggestions: list[str] = Field(
        default_factory=list,
        description="Improvement suggestions"
    )


class SceneDescriptionTemplate(BaseModel):
    """Template for scene description generation."""
    name: str = Field(description="Template name")
    environment_type: EnvironmentType = Field(
        default=EnvironmentType.INDOOR
    )
    atmosphere_type: AtmosphereType = Field(
        default=AtmosphereType.NEUTRAL
    )
    lighting_condition: LightingCondition = Field(
        default=LightingCondition.DIM
    )
    visual_detail_types: list[VisualDetailType] = Field(
        default_factory=list
    )
    sensory_detail_types: list[SensoryDetailType] = Field(
        default_factory=list
    )
    description_length: str = Field(default="medium")
    typical_focus: list[str] = Field(default_factory=list)
