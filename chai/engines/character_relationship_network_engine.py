"""Character relationship network engine for building and analyzing character relationship graphs."""

from collections import defaultdict
from datetime import datetime
from typing import Optional, Any
from chai.models import Character
from chai.models.character_relationship_network import (
    CharacterNode,
    CharacterRelationshipNetwork,
    RelationshipEdge,
    RelationshipStrength,
    RelationshipDirection,
    NetworkMetricType,
    CommunityDetectionMethod,
    NetworkAnalysisResult,
    ShortestPathResult,
    CommunityResult,
)
from chai.services import AIService


class CharacterRelationshipNetworkEngine:
    """Engine for building and analyzing character relationship networks.

    Provides methods to construct relationship networks from characters,
    analyze network properties, detect communities, find paths, and
    generate visualization data.
    """

    def __init__(self, ai_service: Optional[AIService] = None):
        """Initialize the network engine.

        Args:
            ai_service: Optional AI service for enhanced analysis
        """
        self.ai_service = ai_service

    def build_network(
        self,
        characters: list[Character],
        name: str = "",
        genre: str = "",
        theme: str = "",
    ) -> CharacterRelationshipNetwork:
        """Build a character relationship network from a list of characters.

        Args:
            characters: List of Character objects
            name: Network name
            genre: Genre for context
            theme: Theme for context

        Returns:
            CharacterRelationshipNetwork with nodes and edges
        """
        network = CharacterRelationshipNetwork(
            name=name or "Character Relationship Network",
            genre=genre,
            theme=theme,
            created_at=datetime.now().isoformat(),
            total_characters=len(characters),
        )

        # Build adjacency list for analysis
        adjacency: dict[str, set[str]] = defaultdict(set)
        char_map: dict[str, Character] = {c.id: c for c in characters}
        edge_map: dict[tuple[str, str], RelationshipEdge] = {}

        # Process relationships from each character
        for char in characters:
            for rel in char.relationships:
                if rel.character_id and rel.character_id in char_map:
                    source_id = char.id
                    target_id = rel.character_id

                    # Determine edge properties
                    is_conflict = self._is_conflict_relationship(rel.relationship_type)
                    is_romantic = self._is_romantic_relationship(rel.relationship_type)
                    is_family = self._is_family_relationship(rel.relationship_type)
                    strength = self._determine_strength(rel)
                    direction = RelationshipDirection.BIDIRECTIONAL

                    # Create edge
                    edge = RelationshipEdge(
                        source_id=source_id,
                        target_id=target_id,
                        relationship_type=rel.relationship_type,
                        strength=strength,
                        direction=direction,
                        weight=self._strength_to_weight(strength),
                        description=rel.description,
                        dynamics=rel.dynamics,
                        history=rel.history,
                        current_status=rel.current_status,
                        key_events=rel.key_events,
                        is_conflict=is_conflict,
                        is_romantic=is_romantic,
                        is_family=is_family,
                    )

                    # Store edge (avoid duplicates)
                    edge_key = tuple(sorted([source_id, target_id]))
                    if edge_key not in edge_map:
                        edge_map[edge_key] = edge
                        network.edges.append(edge)
                        adjacency[source_id].add(target_id)
                        adjacency[target_id].add(source_id)

        # Build nodes with degree information
        for char in characters:
            degree = len(adjacency[char.id])
            node = CharacterNode(
                character_id=char.id,
                character_name=char.name,
                role=char.role.value if hasattr(char.role, 'value') else str(char.role),
                importance=self._calculate_importance(char, degree, len(characters)),
                degree=degree,
            )
            network.nodes.append(node)

        # Calculate network statistics
        network.total_relationships = len(network.edges)
        network.average_degree = (
            sum(n.degree for n in network.nodes) / len(network.nodes)
            if network.nodes else 0.0
        )
        network.network_density = self._calculate_density(network)
        network.clustering_coefficient = self._calculate_clustering_coefficient(adjacency)

        # Count relationship types
        for edge in network.edges:
            rel_type = edge.relationship_type
            network.relationship_type_counts[rel_type] = (
                network.relationship_type_counts.get(rel_type, 0) + 1
            )
            if edge.is_conflict:
                network.conflict_count += 1
            if edge.is_romantic:
                network.romantic_count += 1
            if edge.is_family:
                network.family_count += 1

        # Identify special characters
        self._identify_special_characters(network, characters)

        # Calculate centrality metrics
        self._calculate_centrality_metrics(network, adjacency)

        # Detect communities
        self._detect_communities(network, adjacency)

        # Identify bridges and isolated characters
        self._identify_bridges_and_isolated(network, adjacency)

        # Generate visualization data
        network.visualization_data = self._generate_visualization_data(network)

        return network

    def _is_conflict_relationship(self, rel_type: str) -> bool:
        """Check if relationship type is a conflict type."""
        conflict_types = {"enemy", "rival", "nemesis", "antagonist"}
        return rel_type.lower() in conflict_types

    def _is_romantic_relationship(self, rel_type: str) -> bool:
        """Check if relationship type is romantic."""
        romantic_types = {"lover", "love_interest", "romantic", "partner", "spouse", "dating"}
        return rel_type.lower() in romantic_types

    def _is_family_relationship(self, rel_type: str) -> bool:
        """Check if relationship type is family."""
        family_types = {"family", "parent", "child", "sibling", "relative", "cousin", "spouse", "parent-child", "sibling"}
        return rel_type.lower() in family_types

    def _determine_strength(self, rel) -> RelationshipStrength:
        """Determine relationship strength from description."""
        desc = (rel.description or "").lower()
        dyn = (rel.dynamics or "").lower()

        text = f"{desc} {dyn}"

        strong_indicators = ["deep", "strong", "lifelong", "eternal", "intense", "bonded"]
        weak_indicators = ["weak", "distant", "superficial", "new", "estranged"]

        strong_count = sum(1 for w in strong_indicators if w in text)
        weak_count = sum(1 for w in weak_indicators if w in text)

        if strong_count > weak_count:
            return RelationshipStrength.STRONG
        elif weak_count > strong_count:
            return RelationshipStrength.WEAK
        return RelationshipStrength.MEDIUM

    def _strength_to_weight(self, strength: RelationshipStrength) -> float:
        """Convert strength to edge weight."""
        weights = {
            RelationshipStrength.VERY_WEAK: 0.3,
            RelationshipStrength.WEAK: 0.5,
            RelationshipStrength.MEDIUM: 1.0,
            RelationshipStrength.STRONG: 1.5,
            RelationshipStrength.VERY_STRONG: 2.0,
        }
        return weights.get(strength, 1.0)

    def _calculate_importance(
        self,
        char: Character,
        degree: int,
        total_chars: int,
    ) -> float:
        """Calculate character importance score (0.0-1.0)."""
        score = 0.5  # Base score

        # Role-based importance
        role = char.role.value if hasattr(char.role, 'value') else str(char.role)
        if role == "protagonist":
            score += 0.3
        elif role == "antagonist":
            score += 0.25
        elif role == "deuteragonist":
            score += 0.15

        # Connection-based
        if total_chars > 0:
            connection_ratio = degree / (total_chars - 1) if total_chars > 1 else 0
            score += min(0.2, connection_ratio * 0.5)

        return min(1.0, score)

    def _calculate_density(self, network: CharacterRelationshipNetwork) -> float:
        """Calculate network density (actual edges / possible edges)."""
        n = network.total_characters
        if n <= 1:
            return 0.0

        possible_edges = n * (n - 1) / 2
        actual_edges = len(network.edges)
        return actual_edges / possible_edges if possible_edges > 0 else 0.0

    def _calculate_clustering_coefficient(
        self,
        adjacency: dict[str, set[str]],
    ) -> float:
        """Calculate global clustering coefficient."""
        if not adjacency:
            return 0.0

        triangles = 0
        triplets = 0

        for node in adjacency:
            neighbors = adjacency[node]
            k = len(neighbors)
            if k >= 2:
                # Count connected triples
                triplets += k * (k - 1) / 2
                # Count triangles
                for i, n1 in enumerate(neighbors):
                    for n2 in list(neighbors)[i + 1:]:
                        if n1 in adjacency and n2 in adjacency[n1]:
                            triangles += 1

        return triangles / triplets if triplets > 0 else 0.0

    def _identify_special_characters(
        self,
        network: CharacterRelationshipNetwork,
        characters: list[Character],
    ):
        """Identify protagonist, antagonists, and key characters."""
        for char in characters:
            role = char.role.value if hasattr(char.role, 'value') else str(char.role)

            if role == "protagonist":
                network.protagonist_id = char.id

            if role == "antagonist":
                network.antagonist_ids.append(char.id)

        # Key characters are those with high degree (many connections)
        if network.nodes:
            sorted_nodes = sorted(
                network.nodes,
                key=lambda n: n.degree,
                reverse=True,
            )
            # Top 20% or at least main characters
            key_count = max(1, len(sorted_nodes) // 5)
            for node in sorted_nodes[:key_count]:
                if node.role not in ["minor"]:
                    node.is_key_character = True
                    network.key_character_ids.append(node.character_id)

    def _calculate_centrality_metrics(
        self,
        network: CharacterRelationshipNetwork,
        adjacency: dict[str, set[str]],
    ):
        """Calculate various centrality metrics for each node."""
        if not network.nodes or not adjacency:
            return

        n = len(adjacency)

        # Degree centrality
        max_degree = max(len(adjacency[node]) for node in adjacency) if adjacency else 1
        for node in network.nodes:
            degree = len(adjacency.get(node.character_id, set()))
            node.centrality_scores["degree_centrality"] = degree / max_degree if max_degree > 0 else 0

        # Betweenness centrality (approximation)
        betweenness = self._calculate_betweenness_centrality(adjacency)
        max_betweenness = max(betweenness.values()) if betweenness else 1
        for node in network.nodes:
            btwn = betweenness.get(node.character_id, 0)
            node.centrality_scores["betweenness_centrality"] = (
                btwn / max_betweenness if max_betweenness > 0 else 0
            )

        # Closeness centrality
        closeness = self._calculate_closeness_centrality(adjacency)
        max_closeness = max(closeness.values()) if closeness else 1
        for node in network.nodes:
            clsn = closeness.get(node.character_id, 0)
            node.centrality_scores["closeness_centrality"] = (
                clsn / max_closeness if max_closeness > 0 else 0
            )

    def _calculate_betweenness_centrality(
        self,
        adjacency: dict[str, set[str]],
    ) -> dict[str, float]:
        """Calculate betweenness centrality for all nodes."""
        betweenness: dict[str, float] = defaultdict(float)
        nodes = list(adjacency.keys())

        for source in nodes:
            # BFS to find shortest paths
            distances = {source: 0}
            parents: dict[str, list[str]] = defaultdict(list)
            queue = [source]

            while queue:
                current = queue.pop(0)
                for neighbor in adjacency.get(current, set()):
                    if neighbor not in distances:
                        distances[neighbor] = distances[current] + 1
                        queue.append(neighbor)
                    if distances[neighbor] == distances[current] + 1:
                        parents[neighbor].append(current)

            # Count shortest paths through each node
            for target in nodes:
                if source != target:
                    count = 1
                    stack = [[target]]
                    paths = []
                    while stack:
                        path = stack.pop(0)
                        if path[-1] == source:
                            paths.append(path)
                        else:
                            for parent in parents.get(path[-1], []):
                                stack.append(path + [parent])

                    for path in paths:
                        for i in path[1:-1]:
                            betweenness[i] += 1

        return dict(betweenness)

    def _calculate_closeness_centrality(
        self,
        adjacency: dict[str, set[str]],
    ) -> dict[str, float]:
        """Calculate closeness centrality for all nodes."""
        closeness: dict[str, float] = {}
        nodes = list(adjacency.keys())

        for source in nodes:
            # BFS to find distances
            distances: dict[str, int] = {source: 0}
            queue = [source]

            while queue:
                current = queue.pop(0)
                for neighbor in adjacency.get(current, set()):
                    if neighbor not in distances:
                        distances[neighbor] = distances[current] + 1
                        queue.append(neighbor)

            # Calculate harmonic centrality
            total_distance = sum(distances.values())
            n = len(distances) - 1
            if n > 0:
                closeness[source] = sum(
                    (n - distances.get(node, 0)) / n
                    for node in distances
                    if node != source
                ) / n
            else:
                closeness[source] = 0

        return closeness

    def _detect_communities(
        self,
        network: CharacterRelationshipNetwork,
        adjacency: dict[str, set[str]],
    ):
        """Detect communities using label propagation."""
        if not adjacency:
            return

        nodes = list(adjacency.keys())
        labels = {node: i for i, node in enumerate(nodes)}

        # Label propagation iterations
        for _ in range(10):
            changed = False
            for node in nodes:
                neighbors = adjacency.get(node, set())
                if not neighbors:
                    continue

                # Get most common label among neighbors
                neighbor_labels = [labels[n] for n in neighbors]
                if neighbor_labels:
                    most_common = max(set(neighbor_labels), key=neighbor_labels.count)
                    if most_common != labels[node]:
                        labels[node] = most_common
                        changed = True

            if not changed:
                break

        # Group by label
        communities: dict[int, list[str]] = defaultdict(list)
        for node, label in labels.items():
            communities[label].append(node)

        # Assign community IDs to nodes
        for node in network.nodes:
            node.community_id = labels.get(node.character_id, 0)

        network.community_count = len(communities)

    def _identify_bridges_and_isolated(
        self,
        network: CharacterRelationshipNetwork,
        adjacency: dict[str, set[str]],
    ):
        """Identify bridge characters and isolated characters."""
        # Isolated characters (no connections)
        for node in network.nodes:
            if node.degree == 0:
                node.is_isolated = True
                network.isolated_character_ids.append(node.character_id)

        # Bridge characters (high betweenness centrality)
        betweenness = {
            node.character_id: node.centrality_scores.get("betweenness_centrality", 0)
            for node in network.nodes
        }

        if betweenness:
            max_betweenness = max(betweenness.values())
            if max_betweenness > 0:
                threshold = max_betweenness * 0.3
                for node in network.nodes:
                    if betweenness.get(node.character_id, 0) >= threshold:
                        node.is_bridge = True
                        network.bridge_character_ids.append(node.character_id)

    def _generate_visualization_data(
        self,
        network: CharacterRelationshipNetwork,
    ) -> dict[str, Any]:
        """Generate data formatted for graph visualization."""
        # Format nodes for visualization
        viz_nodes = []
        for node in network.nodes:
            # Determine node size based on importance and centrality
            base_size = 20
            importance_size = node.importance * 30
            centrality_size = node.centrality_scores.get("degree_centrality", 0) * 20
            node_size = base_size + importance_size + centrality_size

            viz_nodes.append({
                "id": node.character_id,
                "label": node.character_name,
                "role": node.role,
                "size": node_size,
                "color": self._get_node_color(node.role),
                "x": None,  # Layout algorithm will set
                "y": None,
                "community": node.community_id,
                "is_key": node.is_key_character,
                "is_bridge": node.is_bridge,
                "is_isolated": node.is_isolated,
            })

        # Format edges for visualization
        viz_edges = []
        for edge in network.edges:
            viz_edges.append({
                "source": edge.source_id,
                "target": edge.target_id,
                "relationship": edge.relationship_type,
                "weight": edge.weight,
                "strength": edge.strength.value,
                "color": self._get_edge_color(edge),
                "width": edge.weight * 2,
                "is_conflict": edge.is_conflict,
                "is_romantic": edge.is_romantic,
                "is_family": edge.is_family,
            })

        return {
            "nodes": viz_nodes,
            "edges": viz_edges,
            "metadata": {
                "total_characters": network.total_characters,
                "total_relationships": network.total_relationships,
                "network_density": network.network_density,
                "clustering_coefficient": network.clustering_coefficient,
                "community_count": network.community_count,
            },
        }

    def _get_node_color(self, role: str) -> str:
        """Get color for node based on role."""
        colors = {
            "protagonist": "#FF6B6B",
            "antagonist": "#4ECDC4",
            "deuteragonist": "#45B7D1",
            "supporting": "#96CEB4",
            "minor": "#DDA0DD",
            "mentor": "#9B59B6",
            "love_interest": "#E91E63",
            "sidekick": "#3498DB",
        }
        return colors.get(role.lower(), "#95A5A6")

    def _get_edge_color(self, edge: RelationshipEdge) -> str:
        """Get color for edge based on relationship type."""
        if edge.is_conflict:
            return "#E74C3C"  # Red for conflict
        if edge.is_romantic:
            return "#E91E63"  # Pink for romantic
        if edge.is_family:
            return "#3498DB"  # Blue for family
        return "#95A5A6"  # Gray for others

    def find_shortest_path(
        self,
        network: CharacterRelationshipNetwork,
        source_id: str,
        target_id: str,
    ) -> ShortestPathResult:
        """Find shortest path between two characters.

        Args:
            network: Character relationship network
            source_id: Source character ID
            target_id: Target character ID

        Returns:
            ShortestPathResult with path information
        """
        # Build adjacency from edges
        adjacency: dict[str, list[tuple[str, str]]] = defaultdict(list)
        edge_map: dict[tuple[str, str], RelationshipEdge] = {}

        for edge in network.edges:
            adjacency[edge.source_id].append((edge.target_id, edge.relationship_type))
            adjacency[edge.target_id].append((edge.source_id, edge.relationship_type))
            edge_key = tuple(sorted([edge.source_id, edge.target_id]))
            edge_map[edge_key] = edge

        # BFS for shortest path
        if source_id not in adjacency or target_id not in adjacency:
            return ShortestPathResult(
                source_id=source_id,
                target_id=target_id,
                path=[],
                path_names=[],
                path_relationships=[],
                length=-1,
                exists=False,
            )

        visited = {source_id}
        queue = [(source_id, [source_id], [])]

        while queue:
            current, path, relationships = queue.pop(0)

            if current == target_id:
                # Get character names
                node_map = {n.character_id: n.character_name for n in network.nodes}
                return ShortestPathResult(
                    source_id=source_id,
                    target_id=target_id,
                    path=path,
                    path_names=[node_map.get(p, p) for p in path],
                    path_relationships=relationships,
                    length=len(path) - 1,
                    exists=True,
                )

            for neighbor, rel_type in adjacency.get(current, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    edge_key = tuple(sorted([current, neighbor]))
                    edge = edge_map.get(edge_key)
                    rel_desc = edge.relationship_type if edge else rel_type
                    queue.append((neighbor, path + [neighbor], relationships + [rel_desc]))

        return ShortestPathResult(
            source_id=source_id,
            target_id=target_id,
            path=[],
            path_names=[],
            path_relationships=[],
            length=-1,
            exists=False,
        )

    def analyze_network(
        self,
        network: CharacterRelationshipNetwork,
    ) -> NetworkAnalysisResult:
        """Perform comprehensive network analysis.

        Args:
            network: Character relationship network to analyze

        Returns:
            NetworkAnalysisResult with findings and recommendations
        """
        findings = []
        recommendations = []
        metrics: dict[str, Any] = {}

        # Analyze network density
        if network.network_density < 0.1:
            findings.append(f"Network density is low ({network.network_density:.2f}), characters may not be well connected")
            recommendations.append("Consider adding more relationships between characters")
        elif network.network_density > 0.5:
            findings.append(f"Network density is high ({network.network_density:.2f}), densely connected story")

        # Analyze protagonist connectivity
        if network.protagonist_id:
            protagonist_node = next(
                (n for n in network.nodes if n.character_id == network.protagonist_id),
                None,
            )
            if protagonist_node:
                if protagonist_node.degree < 2:
                    findings.append("Protagonist has few connections, may feel isolated")
                    recommendations.append("Ensure protagonist has meaningful interactions with other characters")
                metrics["protagonist_degree"] = protagonist_node.degree
                metrics["protagonist_centrality"] = protagonist_node.centrality_scores.get("degree_centrality", 0)

        # Analyze antagonist presence
        if not network.antagonist_ids:
            findings.append("No antagonist identified in the network")
        else:
            metrics["antagonist_count"] = len(network.antagonist_ids)

        # Analyze community structure
        if network.community_count > 1:
            findings.append(f"Network has {network.community_count} distinct communities")
            if len(network.bridge_character_ids) < 2:
                recommendations.append("Consider adding characters that bridge different communities")

        # Analyze isolated characters
        if network.isolated_character_ids:
            findings.append(f"{len(network.isolated_character_ids)} characters are isolated (no relationships)")
            recommendations.append("Integrate isolated characters into the story or remove them")

        # Analyze relationship balance
        if network.conflict_count > network.total_relationships * 0.7:
            findings.append("Story has many conflict relationships, ensure balance with alliances")
        if network.romantic_count > 0:
            metrics["has_romantic_relationships"] = True

        metrics["network_density"] = network.network_density
        metrics["average_degree"] = network.average_degree
        metrics["clustering_coefficient"] = network.clustering_coefficient
        metrics["total_characters"] = network.total_characters
        metrics["total_relationships"] = network.total_relationships

        return NetworkAnalysisResult(
            analysis_type="comprehensive_network_analysis",
            summary=self._generate_analysis_summary(network, findings),
            findings=findings,
            metrics=metrics,
            recommendations=recommendations,
        )

    def _generate_analysis_summary(
        self,
        network: CharacterRelationshipNetwork,
        findings: list[str],
    ) -> str:
        """Generate a human-readable analysis summary."""
        lines = [
            f"=== Character Relationship Network Analysis ===",
            f"",
            f"Network: {network.name or 'Unnamed'}",
            f"Genre: {network.genre or 'Not specified'}",
            f"Theme: {network.theme or 'Not specified'}",
            f"",
            f"Statistics:",
            f"  Total Characters: {network.total_characters}",
            f"  Total Relationships: {network.total_relationships}",
            f"  Average Degree: {network.average_degree:.2f}",
            f"  Network Density: {network.network_density:.2%}",
            f"  Clustering Coefficient: {network.clustering_coefficient:.2f}",
            f"  Communities Detected: {network.community_count}",
            f"",
            f"Relationship Types:",
        ]

        for rel_type, count in sorted(network.relationship_type_counts.items()):
            lines.append(f"  {rel_type}: {count}")

        if findings:
            lines.extend(["", "Key Findings:"])
            for finding in findings[:5]:
                lines.append(f"  - {finding}")

        return "\n".join(lines)

    def detect_communities_detailed(
        self,
        network: CharacterRelationshipNetwork,
        method: CommunityDetectionMethod = CommunityDetectionMethod.LABEL_PROPAGATION,
    ) -> CommunityResult:
        """Detect communities in the network with detailed output.

        Args:
            network: Character relationship network
            method: Detection method to use

        Returns:
            CommunityResult with community information
        """
        adjacency: dict[str, set[str]] = defaultdict(set)
        for edge in network.edges:
            adjacency[edge.source_id].add(edge.target_id)
            adjacency[edge.target_id].add(edge.source_id)

        # Get node assignments from network
        community_map: dict[int, list[str]] = defaultdict(list)
        for node in network.nodes:
            if node.community_id is not None:
                community_map[node.community_id].append(node.character_id)

        # Build communities list
        communities = []
        for comm_id, members in community_map.items():
            node_map = {n.character_id: n.character_name for n in network.nodes}
            communities.append({
                "id": comm_id,
                "member_ids": members,
                "member_names": [node_map.get(m, m) for m in members],
                "size": len(members),
            })

        # Calculate modularity (simplified)
        m = len(network.edges)
        if m > 0:
            modularity = sum(
                1.0 / m
                for comm in communities
                for i, member_i in enumerate(comm["member_ids"])
                for member_j in comm["member_ids"][i + 1:]
                if any(
                    e.source_id == member_i and e.target_id == member_j
                    or e.target_id == member_i and e.source_id == member_j
                    for e in network.edges
                )
            )
            modularity = max(0, modularity - 0.5)
        else:
            modularity = 0.0

        return CommunityResult(
            method=method.value,
            communities=communities,
            modularity=modularity,
            community_count=len(communities),
        )

    def get_network_summary(
        self,
        network: CharacterRelationshipNetwork,
    ) -> str:
        """Get a human-readable summary of the network.

        Args:
            network: Character relationship network

        Returns:
            Formatted string summary
        """
        lines = [
            f"=== {network.name or 'Character Relationship Network'} ===",
            f"",
            f"Overview:",
            f"  Characters: {network.total_characters}",
            f"  Relationships: {network.total_relationships}",
            f"  Density: {network.network_density:.2%}",
            f"",
        ]

        if network.protagonist_id:
            protag = next(
                (n for n in network.nodes if n.character_id == network.protagonist_id),
                None,
            )
            if protag:
                lines.append(f"Protagonist: {protag.character_name}")

        if network.antagonist_ids:
            lines.append(f"Antagonists: {len(network.antagonist_ids)}")

        if network.key_character_ids:
            lines.append(f"Key Characters: {len(network.key_character_ids)}")
            names = [
                n.character_name
                for n in network.nodes
                if n.character_id in network.key_character_ids
            ]
            lines.append(f"  {', '.join(names[:5])}")

        if network.bridge_character_ids:
            lines.append(f"Bridge Characters: {len(network.bridge_character_ids)}")

        if network.isolated_character_ids:
            lines.append(f"Isolated Characters: {len(network.isolated_character_ids)}")

        lines.extend(["", "Relationship Distribution:"])
        for rel_type, count in sorted(
            network.relationship_type_counts.items(),
            key=lambda x: x[1],
            reverse=True,
        ):
            lines.append(f"  {rel_type}: {count}")

        lines.extend(["", "Community Structure:"])
        lines.append(f"  Communities: {network.community_count}")

        return "\n".join(lines)

    def export_network(
        self,
        network: CharacterRelationshipNetwork,
        include_analysis: bool = True,
    ) -> dict[str, Any]:
        """Export network as a complete document.

        Args:
            network: Character relationship network to export
            include_analysis: Whether to include network analysis

        Returns:
            Complete export dict
        """
        export_data = {
            "network": network.model_dump(),
            "summary": self.get_network_summary(network),
            "visualization_data": network.visualization_data,
        }

        if include_analysis:
            export_data["analysis"] = self.analyze_network(network).model_dump()

        return export_data

    async def generate_network_insights(
        self,
        network: CharacterRelationshipNetwork,
    ) -> str:
        """Generate AI-powered insights about the network.

        Args:
            network: Character relationship network

        Returns:
            AI-generated insights as string
        """
        if not self.ai_service:
            return "AI service not available for insights generation"

        prompt = f"""分析以下角色关系网络的结构和特点：

角色数量：{network.total_characters}
关系数量：{network.total_relationships}
网络密度：{network.network_density:.2%}
聚类系数：{network.clustering_coefficient:.2f}
社区数量：{network.community_count}

关键角色：{', '.join(network.key_character_ids[:5]) if network.key_character_ids else '无'}
孤立角色：{len(network.isolated_character_ids)}

关系类型分布：
{chr(10).join(f"- {k}: {v}" for k, v in network.relationship_type_counts.items())}

请分析：
1. 网络结构的特点和潜在问题
2. 角色关系的模式和动态
3. 故事叙事的优势和劣势
4. 改进建议

请用中文回答。"""

        result = await self.ai_service.generate(prompt)
        return result
