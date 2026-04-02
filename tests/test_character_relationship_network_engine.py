"""Unit tests for CharacterRelationshipNetworkEngine."""

import pytest
from chai.models import Character, CharacterRole, CharacterRelationship
from chai.engines import CharacterRelationshipNetworkEngine


def create_test_character(
    char_id: str,
    name: str,
    role: str,
    relationships: list[CharacterRelationship] = None,
) -> Character:
    """Create a test character."""
    return Character(
        id=char_id,
        name=name,
        role=role,
        relationships=relationships or [],
    )


def create_test_relationship(
    target_id: str,
    target_name: str,
    rel_type: str,
    description: str = "",
    dynamics: str = "",
) -> CharacterRelationship:
    """Create a test relationship with required fields."""
    return CharacterRelationship(
        character_id=target_id,
        character_name=target_name,
        relationship_type=rel_type,
        description=description or f"{rel_type} relationship",
        dynamics=dynamics or f"Typical {rel_type} interaction",
    )


class TestCharacterRelationshipNetworkModels:
    """Test the network data models."""

    def test_character_node_creation(self):
        """Test CharacterNode creation."""
        from chai.models import CharacterNode

        node = CharacterNode(
            character_id="char_1",
            character_name="Test Character",
            role="protagonist",
            importance=0.8,
            degree=5,
        )

        assert node.character_id == "char_1"
        assert node.character_name == "Test Character"
        assert node.role == "protagonist"
        assert node.importance == 0.8
        assert node.degree == 5

    def test_relationship_edge_creation(self):
        """Test RelationshipEdge creation."""
        from chai.models import RelationshipEdge, RelationshipStrength, RelationshipDirection

        edge = RelationshipEdge(
            source_id="char_1",
            target_id="char_2",
            relationship_type="friend",
            strength=RelationshipStrength.STRONG,
            direction=RelationshipDirection.BIDIRECTIONAL,
            weight=1.5,
        )

        assert edge.source_id == "char_1"
        assert edge.target_id == "char_2"
        assert edge.relationship_type == "friend"
        assert edge.strength == RelationshipStrength.STRONG
        assert edge.weight == 1.5

    def test_network_creation(self):
        """Test CharacterRelationshipNetwork creation."""
        from chai.models import CharacterRelationshipNetwork, CharacterNode, RelationshipEdge

        network = CharacterRelationshipNetwork(
            name="Test Network",
            genre="fantasy",
            theme="hero's journey",
            total_characters=2,
            total_relationships=1,
            nodes=[
                CharacterNode(
                    character_id="char_1",
                    character_name="Hero",
                    role="protagonist",
                ),
            ],
            edges=[
                RelationshipEdge(
                    source_id="char_1",
                    target_id="char_2",
                    relationship_type="friend",
                ),
            ],
        )

        assert network.name == "Test Network"
        assert network.genre == "fantasy"
        assert network.total_characters == 2
        assert network.total_relationships == 1


class TestBuildNetwork:
    """Test building networks from characters."""

    def test_build_empty_network(self):
        """Test building network with no characters."""
        engine = CharacterRelationshipNetworkEngine()
        network = engine.build_network([])

        assert network.total_characters == 0
        assert network.total_relationships == 0
        assert len(network.nodes) == 0
        assert len(network.edges) == 0

    def test_build_single_character_network(self):
        """Test building network with single character."""
        engine = CharacterRelationshipNetworkEngine()
        char = create_test_character("char_1", "Lone Hero", "protagonist")
        network = engine.build_network([char])

        assert network.total_characters == 1
        assert network.total_relationships == 0
        assert len(network.nodes) == 1
        assert len(network.edges) == 0

    def test_build_network_with_relationships(self):
        """Test building network with relationships between characters."""
        engine = CharacterRelationshipNetworkEngine()

        # Character 1 with relationship to character 2
        rel = create_test_relationship("char_2", "Friend", "friend", "Close friends")
        char1 = create_test_character("char_1", "Hero", "protagonist", [rel])
        char2 = create_test_character("char_2", "Friend", "supporting")

        network = engine.build_network([char1, char2])

        assert network.total_characters == 2
        assert network.total_relationships == 1
        assert len(network.nodes) == 2
        assert len(network.edges) == 1

        # Verify edge
        edge = network.edges[0]
        assert edge.source_id == "char_1"
        assert edge.target_id == "char_2"
        assert edge.relationship_type == "friend"

    def test_build_network_identifies_protagonist(self):
        """Test that protagonist is correctly identified."""
        engine = CharacterRelationshipNetworkEngine()

        char1 = create_test_character("char_1", "Hero", "protagonist")
        char2 = create_test_character("char_2", "Villain", "antagonist")

        network = engine.build_network([char1, char2])

        assert network.protagonist_id == "char_1"
        assert "char_2" in network.antagonist_ids

    def test_build_network_calculates_degree(self):
        """Test that degree is correctly calculated."""
        engine = CharacterRelationshipNetworkEngine()

        # char1 knows char2 and char3
        rel1 = create_test_relationship("char_2", "Friend1", "friend")
        rel2 = create_test_relationship("char_3", "Friend2", "friend")
        char1 = create_test_character("char_1", "Hub", "protagonist", [rel1, rel2])

        # char2 knows char1 only
        rel3 = create_test_relationship("char_1", "Hub", "friend")
        char2 = create_test_character("char_2", "Friend1", "supporting", [rel3])

        # char3 knows char1 only
        rel4 = create_test_relationship("char_1", "Hub", "friend")
        char3 = create_test_character("char_3", "Friend2", "supporting", [rel4])

        network = engine.build_network([char1, char2, char3])

        # Find the hub node
        hub_node = next(n for n in network.nodes if n.character_id == "char_1")
        assert hub_node.degree == 2

    def test_build_network_avoids_duplicate_edges(self):
        """Test that duplicate edges are not created."""
        engine = CharacterRelationshipNetworkEngine()

        # char1 knows char2
        rel1 = create_test_relationship("char_2", "Friend", "friend")
        char1 = create_test_character("char_1", "Hero", "protagonist", [rel1])

        # char2 also knows char1 (bidirectional)
        rel2 = create_test_relationship("char_1", "Hero", "friend")
        char2 = create_test_character("char_2", "Friend", "supporting", [rel2])

        network = engine.build_network([char1, char2])

        # Should only have one edge, not two
        assert network.total_relationships == 1


class TestRelationshipTypeClassification:
    """Test relationship type classification."""

    def test_conflict_relationship_detection(self):
        """Test conflict relationships are detected."""
        engine = CharacterRelationshipNetworkEngine()

        rel = create_test_relationship("char_2", "Enemy", "enemy", "Sworn enemies")
        char1 = create_test_character("char_1", "Hero", "protagonist", [rel])
        char2 = create_test_character("char_2", "Enemy", "antagonist")

        network = engine.build_network([char1, char2])

        assert network.conflict_count >= 1
        assert network.edges[0].is_conflict

    def test_romantic_relationship_detection(self):
        """Test romantic relationships are detected."""
        engine = CharacterRelationshipNetworkEngine()

        rel = create_test_relationship("char_2", "Lover", "lover", "Deeply in love")
        char1 = create_test_character("char_1", "Hero", "protagonist", [rel])
        char2 = create_test_character("char_2", "Lover", "supporting")

        network = engine.build_network([char1, char2])

        assert network.romantic_count >= 1
        assert network.edges[0].is_romantic

    def test_family_relationship_detection(self):
        """Test family relationships are detected."""
        engine = CharacterRelationshipNetworkEngine()

        rel = create_test_relationship("char_2", "Sister", "sibling", "Close sisters")
        char1 = create_test_character("char_1", "Hero", "protagonist", [rel])
        char2 = create_test_character("char_2", "Sister", "supporting")

        network = engine.build_network([char1, char2])

        assert network.family_count >= 1
        assert network.edges[0].is_family


class TestShortestPath:
    """Test shortest path finding."""

    def test_shortest_path_exists(self):
        """Test finding path between connected characters."""
        engine = CharacterRelationshipNetworkEngine()

        # char1 -> char2 -> char3
        rel1 = create_test_relationship("char_2", "Friend2", "friend")
        rel2 = create_test_relationship("char_3", "Friend3", "friend")
        char1 = create_test_character("char_1", "A", "protagonist", [rel1])
        char2 = create_test_character("char_2", "B", "supporting", [rel2])
        char3 = create_test_character("char_3", "C", "supporting")

        network = engine.build_network([char1, char2, char3])

        result = engine.find_shortest_path(network, "char_1", "char_3")

        assert result.exists
        assert result.length == 2  # A -> B -> C
        assert len(result.path) == 3
        assert result.path == ["char_1", "char_2", "char_3"]

    def test_shortest_path_no_connection(self):
        """Test path not found for isolated characters."""
        engine = CharacterRelationshipNetworkEngine()

        char1 = create_test_character("char_1", "Lone Hero", "protagonist")
        char2 = create_test_character("char_2", "Isolated", "supporting")

        network = engine.build_network([char1, char2])

        result = engine.find_shortest_path(network, "char_1", "char_2")

        assert not result.exists
        assert result.length == -1

    def test_shortest_path_direct_connection(self):
        """Test direct path between characters."""
        engine = CharacterRelationshipNetworkEngine()

        rel = create_test_relationship("char_2", "Friend", "friend")
        char1 = create_test_character("char_1", "A", "protagonist", [rel])
        char2 = create_test_character("char_2", "B", "supporting")

        network = engine.build_network([char1, char2])

        result = engine.find_shortest_path(network, "char_1", "char_2")

        assert result.exists
        assert result.length == 1  # Direct connection


class TestNetworkAnalysis:
    """Test network analysis."""

    def test_analyze_empty_network(self):
        """Test analysis of empty network."""
        engine = CharacterRelationshipNetworkEngine()
        network = engine.build_network([])

        result = engine.analyze_network(network)

        assert result.analysis_type == "comprehensive_network_analysis"
        assert len(result.findings) >= 0

    def test_analyze_low_density_network(self):
        """Test analysis detects low density or isolated characters."""
        engine = CharacterRelationshipNetworkEngine()

        # Only one relationship among many characters
        rel = create_test_relationship("char_2", "Friend", "friend")
        char1 = create_test_character("char_1", "A", "protagonist", [rel])
        char2 = create_test_character("char_2", "B", "supporting")
        char3 = create_test_character("char_3", "C", "supporting")
        char4 = create_test_character("char_4", "D", "supporting")

        network = engine.build_network([char1, char2, char3, char4])

        result = engine.analyze_network(network)

        # Should detect low density OR isolated characters
        findings_lower = [f.lower() for f in result.findings]
        has_low_density = any("density" in f for f in findings_lower)
        has_isolated = any("isolated" in f for f in findings_lower)
        assert has_low_density or has_isolated

    def test_analyze_metrics(self):
        """Test that metrics are populated."""
        engine = CharacterRelationshipNetworkEngine()

        rel = create_test_relationship("char_2", "Friend", "friend")
        char1 = create_test_character("char_1", "A", "protagonist", [rel])
        char2 = create_test_character("char_2", "B", "supporting")

        network = engine.build_network([char1, char2])

        result = engine.analyze_network(network)

        assert "network_density" in result.metrics
        assert "average_degree" in result.metrics
        assert "total_characters" in result.metrics


class TestCommunityDetection:
    """Test community detection."""

    def test_detect_communities(self):
        """Test community detection on network."""
        engine = CharacterRelationshipNetworkEngine()

        # Create two clusters: (A, B) and (C, D)
        # Cluster 1: A <-> B
        rel_ab = create_test_relationship("char_2", "B", "friend")
        char_a = create_test_character("char_1", "A", "protagonist", [rel_ab])
        char_b = create_test_character("char_2", "B", "supporting", [rel_ab])

        # Cluster 2: C <-> D
        rel_cd = create_test_relationship("char_4", "D", "friend")
        char_c = create_test_character("char_3", "C", "supporting", [rel_cd])
        char_d = create_test_character("char_4", "D", "supporting", [rel_cd])

        network = engine.build_network([char_a, char_b, char_c, char_d])

        assert network.community_count >= 1

        result = engine.detect_communities_detailed(network)
        assert result.community_count >= 1
        assert len(result.communities) >= 1

    def test_detect_communities_single_cluster(self):
        """Test community detection on fully connected network."""
        engine = CharacterRelationshipNetworkEngine()

        # All characters connected
        rel1 = create_test_relationship("char_2", "B", "friend")
        rel2 = create_test_relationship("char_3", "C", "friend")
        char1 = create_test_character("char_1", "A", "protagonist", [rel1, rel2])
        char2 = create_test_character("char_2", "B", "supporting", [])
        char3 = create_test_character("char_3", "C", "supporting", [])

        network = engine.build_network([char1, char2, char3])

        # Dense network should have fewer communities
        result = engine.detect_communities_detailed(network)
        assert result.community_count >= 1


class TestVisualizationData:
    """Test visualization data generation."""

    def test_visualization_data_format(self):
        """Test visualization data is correctly formatted."""
        engine = CharacterRelationshipNetworkEngine()

        rel = create_test_relationship("char_2", "Friend", "friend")
        char1 = create_test_character("char_1", "Hero", "protagonist", [rel])
        char2 = create_test_character("char_2", "Friend", "supporting")

        network = engine.build_network([char1, char2])

        viz = network.visualization_data

        assert "nodes" in viz
        assert "edges" in viz
        assert "metadata" in viz
        assert len(viz["nodes"]) == 2
        assert len(viz["edges"]) == 1

    def test_node_visualization_properties(self):
        """Test node visualization properties."""
        engine = CharacterRelationshipNetworkEngine()

        char = create_test_character("char_1", "Hero", "protagonist")

        network = engine.build_network([char])

        viz = network.visualization_data
        node = viz["nodes"][0]

        assert node["id"] == "char_1"
        assert node["label"] == "Hero"
        assert node["role"] == "protagonist"
        assert "size" in node
        assert "color" in node

    def test_edge_visualization_properties(self):
        """Test edge visualization properties."""
        engine = CharacterRelationshipNetworkEngine()

        rel = create_test_relationship("char_2", "Friend", "friend")
        char1 = create_test_character("char_1", "A", "protagonist", [rel])
        char2 = create_test_character("char_2", "B", "supporting")

        network = engine.build_network([char1, char2])

        viz = network.visualization_data
        edge = viz["edges"][0]

        assert edge["source"] == "char_1"
        assert edge["target"] == "char_2"
        assert edge["relationship"] == "friend"
        assert "weight" in edge
        assert "color" in edge


class TestNetworkSummary:
    """Test network summary generation."""

    def test_get_network_summary(self):
        """Test network summary generation."""
        engine = CharacterRelationshipNetworkEngine()

        rel = create_test_relationship("char_2", "Friend", "friend")
        char1 = create_test_character("char_1", "Hero", "protagonist", [rel])
        char2 = create_test_character("char_2", "Friend", "supporting")

        network = engine.build_network([char1, char2])
        summary = engine.get_network_summary(network)

        assert "Hero" in summary
        assert "protagonist" in summary.lower()
        assert "2" in summary  # Total characters
        assert "Relationships" in summary

    def test_export_network(self):
        """Test network export."""
        engine = CharacterRelationshipNetworkEngine()

        char = create_test_character("char_1", "Hero", "protagonist")
        network = engine.build_network([char], name="Test Network")

        export = engine.export_network(network, include_analysis=True)

        assert "network" in export
        assert "summary" in export
        assert "analysis" in export
        assert "visualization_data" in export


class TestSpecialCharacterIdentification:
    """Test identification of special characters."""

    def test_identify_key_characters(self):
        """Test that key characters are identified."""
        engine = CharacterRelationshipNetworkEngine()

        # Create a hub character with many connections
        rels = [
            create_test_relationship(f"char_{i}", f"Friend{i}", "friend")
            for i in range(2, 6)
        ]
        hub = create_test_character("char_1", "Hub", "protagonist", rels)

        # Create leaf characters with only one connection each
        others = [
            create_test_character(f"char_{i}", f"Friend{i-1}", "supporting", [
                create_test_relationship("char_1", "Hub", "friend")
            ])
            for i in range(2, 6)
        ]

        network = engine.build_network([hub] + others)

        assert len(network.key_character_ids) >= 1
        assert "char_1" in network.key_character_ids

    def test_identify_isolated_characters(self):
        """Test that isolated characters are identified."""
        engine = CharacterRelationshipNetworkEngine()

        char1 = create_test_character("char_1", "Connected", "protagonist", [
            create_test_relationship("char_2", "Friend", "friend")
        ])
        char2 = create_test_character("char_2", "Friend", "supporting", [])
        char3 = create_test_character("char_3", "Isolated", "supporting", [])  # No relationships

        network = engine.build_network([char1, char2, char3])

        assert "char_3" in network.isolated_character_ids


class TestEdgeCases:
    """Test edge cases."""

    def test_self_referential_relationship(self):
        """Test handling of self-referential relationships."""
        engine = CharacterRelationshipNetworkEngine()

        # Character with relationship to self (should be ignored)
        rel = create_test_relationship("char_1", "Self", "self")
        char = create_test_character("char_1", "Self Aware", "protagonist", [rel])

        network = engine.build_network([char])

        # Should not crash and should not create invalid edges
        assert network.total_characters == 1

    def test_relationship_to_nonexistent_character(self):
        """Test handling of relationships to non-existent characters."""
        engine = CharacterRelationshipNetworkEngine()

        rel = create_test_relationship("nonexistent", "Ghost", "friend")
        char = create_test_character("char_1", "Real", "protagonist", [rel])

        network = engine.build_network([char])

        # Should not create edges to non-existent characters
        assert network.total_relationships == 0

    def test_network_with_many_relationship_types(self):
        """Test network with various relationship types."""
        engine = CharacterRelationshipNetworkEngine()

        rels = [
            create_test_relationship("char_2", "Enemy", "enemy"),
            create_test_relationship("char_3", "Lover", "lover"),
            create_test_relationship("char_4", "Mentor", "mentor"),
        ]
        char1 = create_test_character("char_1", "Hero", "protagonist", rels)

        others = [
            create_test_character(f"char_{i}", f"Char{i}", "supporting")
            for i in range(2, 5)
        ]

        network = engine.build_network([char1] + others)

        assert network.total_relationships == 3
        assert network.conflict_count >= 1
        assert network.romantic_count >= 1
        assert len(network.relationship_type_counts) >= 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
