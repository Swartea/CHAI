"""Character relationship network graph models for visualizing and analyzing character relationships."""

from enum import Enum
from typing import Optional, Any
from pydantic import BaseModel, Field


class RelationshipStrength(str, Enum):
    """Strength of relationship."""
    VERY_WEAK = "very_weak"
    WEAK = "weak"
    MEDIUM = "medium"
    STRONG = "strong"
    VERY_STRONG = "very_strong"


class RelationshipDirection(str, Enum):
    """Direction of relationship."""
    UNIDIRECTIONAL = "unidirectional"  # A -> B
    BIDIRECTIONAL = "bidirectional"   # A <-> B


class NetworkMetricType(str, Enum):
    """Types of network metrics."""
    DEGREE_CENTRALITY = "degree_centrality"
    BETWEENNESS_CENTRALITY = "betweenness_centrality"
    CLOSENESS_CENTRALITY = "closeness_centrality"
    EIGENVECTOR_CENTRALITY = "eigenvector_centrality"
    PAGERANK = "pagerank"


class CommunityDetectionMethod(str, Enum):
    """Methods for detecting communities in network."""
    LABEL_PROPAGATION = "label_propagation"
    LOUVAIN = "louvain"
    GREEDY_MODULARITY = "greedy_modularity"


class CharacterNode(BaseModel):
    """A character as a node in the relationship network."""

    character_id: str = Field(description="Unique character identifier")
    character_name: str = Field(description="Character name for display")
    role: str = Field(description="Character role (protagonist, antagonist, supporting, etc.)")
    importance: float = Field(default=1.0, description="Importance score (0.0-1.0)")
    centrality_scores: dict[str, float] = Field(
        default_factory=dict,
        description="Centrality scores by metric type"
    )
    community_id: Optional[int] = Field(default=None, description="Community ID if detected")
    is_key_character: bool = Field(default=False, description="Whether this is a key character")
    is_bridge: bool = Field(default=False, description="Whether this character bridges communities")
    is_isolated: bool = Field(default=False, description="Whether this character is isolated")
    degree: int = Field(default=0, description="Number of direct connections")
    clustering_coefficient: float = Field(default=0.0, description="Local clustering coefficient")


class RelationshipEdge(BaseModel):
    """A relationship between two characters as an edge in the network."""

    source_id: str = Field(description="Source character ID")
    target_id: str = Field(description="Target character ID")
    relationship_type: str = Field(description="Type: family, friend, enemy, lover, mentor, etc.")
    strength: RelationshipStrength = Field(default=RelationshipStrength.MEDIUM)
    direction: RelationshipDirection = Field(default=RelationshipDirection.BIDIRECTIONAL)
    weight: float = Field(default=1.0, description="Edge weight (0.0-2.0)")
    description: str = Field(default="", description="Relationship description")
    dynamics: str = Field(default="", description="Interaction dynamics")
    history: str = Field(default="", description="Relationship history")
    current_status: str = Field(default="", description="Current relationship status")
    key_events: list[str] = Field(default_factory=list, description="Key events in relationship")
    is_conflict: bool = Field(default=False, description="Whether this is a conflict relationship")
    is_romantic: bool = Field(default=False, description="Whether this is a romantic relationship")
    is_family: bool = Field(default=False, description="Whether this is a family relationship")


class CharacterRelationshipNetwork(BaseModel):
    """Complete character relationship network with nodes, edges, and metadata."""

    # Network metadata
    name: str = Field(default="", description="Network name")
    genre: str = Field(default="", description="Genre for context")
    theme: str = Field(default="", description="Central theme")
    created_at: str = Field(default="", description="Creation timestamp")

    # Network structure
    nodes: list[CharacterNode] = Field(default_factory=list, description="Character nodes")
    edges: list[RelationshipEdge] = Field(default_factory=list, description="Relationship edges")

    # Network statistics
    total_characters: int = Field(default=0, description="Total number of characters")
    total_relationships: int = Field(default=0, description="Total number of relationships")
    average_degree: float = Field(default=0.0, description="Average connections per character")
    network_density: float = Field(default=0.0, description="Network density (0.0-1.0)")
    clustering_coefficient: float = Field(default=0.0, description="Global clustering coefficient")
    community_count: int = Field(default=0, description="Number of detected communities")

    # Key characters identified
    protagonist_id: Optional[str] = Field(default=None, description="Main protagonist character ID")
    antagonist_ids: list[str] = Field(default_factory=list, description="Antagonist character IDs")
    key_character_ids: list[str] = Field(default_factory=list, description="Key character IDs (high centrality)")
    bridge_character_ids: list[str] = Field(default_factory=list, description="Bridge character IDs")
    isolated_character_ids: list[str] = Field(default_factory=list, description="Isolated character IDs")

    # Relationship type distribution
    relationship_type_counts: dict[str, int] = Field(
        default_factory=dict,
        description="Count of relationships by type"
    )
    conflict_count: int = Field(default=0, description="Number of conflict relationships")
    romantic_count: int = Field(default=0, description="Number of romantic relationships")
    family_count: int = Field(default=0, description="Number of family relationships")

    # Visualization data
    visualization_data: dict[str, Any] = Field(
        default_factory=dict,
        description="Data formatted for visualization"
    )


class NetworkAnalysisResult(BaseModel):
    """Result of network analysis."""

    analysis_type: str = Field(description="Type of analysis performed")
    summary: str = Field(description="Human-readable summary")
    findings: list[str] = Field(default_factory=list, description="Key findings")
    metrics: dict[str, Any] = Field(default_factory=dict, description="Analysis metrics")
    recommendations: list[str] = Field(default_factory=list, description="Recommendations")


class ShortestPathResult(BaseModel):
    """Result of shortest path calculation."""

    source_id: str = Field(description="Source character ID")
    target_id: str = Field(description="Target character ID")
    path: list[str] = Field(default_factory=list, description="Character IDs in path")
    path_names: list[str] = Field(default_factory=list, description="Character names in path")
    path_relationships: list[str] = Field(default_factory=list, description="Relationships along path")
    length: int = Field(default=0, description="Path length (number of hops)")
    exists: bool = Field(default=True, description="Whether path exists")


class CommunityResult(BaseModel):
    """Result of community detection."""

    method: str = Field(description="Detection method used")
    communities: list[dict[str, Any]] = Field(
        default_factory=list,
        description="List of communities with character IDs"
    )
    modularity: float = Field(default=0.0, description="Modularity score")
    community_count: int = Field(default=0, description="Number of communities detected")
