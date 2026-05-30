"""Local prior-art graph and novelty scoring for AFPM design candidates."""

from __future__ import annotations

import re

from pydantic import BaseModel, Field

TOKEN_PATTERN = re.compile(r"[a-z0-9]+")


def _tokens(text: str) -> set[str]:
    return set(TOKEN_PATTERN.findall(text.lower()))


class PriorArtNode(BaseModel):
    """A compact prior-art or patent-family node."""

    node_id: str
    title: str
    assignee: str = ""
    source: str = "local_seed"
    features: list[str] = Field(default_factory=list)

    @property
    def token_set(self) -> set[str]:
        return _tokens(" ".join([self.title, *self.features]))


class NoveltyScore(BaseModel):
    """Novelty scoring result against the local graph."""

    novelty_score: float
    max_overlap: float
    closest_nodes: list[PriorArtNode]
    differentiators: list[str]


class PatentKnowledgeGraph(BaseModel):
    """Small deterministic prior-art graph.

    This is intentionally local and conservative. A live Google Patents/WIPO/USPTO
    ingestion layer can feed this graph later without changing the lab contract.
    """

    nodes: list[PriorArtNode] = Field(default_factory=list)

    @classmethod
    def seed_afpm_baseline(cls) -> PatentKnowledgeGraph:
        return cls(
            nodes=[
                PriorArtNode(
                    node_id="afpm-yasa-baseline",
                    title="Yokeless segmented armature axial flux machine",
                    assignee="YASA family",
                    features=[
                        "yokeless segmented armature",
                        "concentrated tooth coils",
                        "dual rotor axial flux",
                        "high torque density",
                    ],
                ),
                PriorArtNode(
                    node_id="afpm-coreless-pcb",
                    title="Coreless PCB stator axial flux permanent magnet machine",
                    features=[
                        "printed circuit board stator",
                        "coreless winding",
                        "single stator double rotor",
                        "low cogging torque",
                    ],
                ),
                PriorArtNode(
                    node_id="afpm-halbach-coreless",
                    title="Halbach rotor coreless axial flux generator",
                    features=[
                        "halbach permanent magnet array",
                        "reduced back iron",
                        "coreless stator",
                        "air gap flux concentration",
                    ],
                ),
                PriorArtNode(
                    node_id="afpm-wind-open-source",
                    title="Low speed axial flux wind generator with disc rotors",
                    features=[
                        "direct drive wind generator",
                        "surface mounted magnets",
                        "resin cast coils",
                        "manufacturable disc rotor",
                    ],
                ),
            ]
        )

    def score_novelty(self, candidate_features: list[str]) -> NoveltyScore:
        candidate_tokens = _tokens(" ".join(candidate_features))
        if not candidate_tokens:
            return NoveltyScore(
                novelty_score=0.0,
                max_overlap=1.0,
                closest_nodes=[],
                differentiators=[],
            )

        ranked: list[tuple[float, PriorArtNode]] = []
        for node in self.nodes:
            node_tokens = node.token_set
            union = candidate_tokens | node_tokens
            overlap = len(candidate_tokens & node_tokens) / len(union) if union else 0.0
            ranked.append((overlap, node))

        ranked.sort(key=lambda item: item[0], reverse=True)
        max_overlap = ranked[0][0] if ranked else 0.0
        closest = [node for _, node in ranked[:3]]
        known_tokens = set().union(*(node.token_set for node in closest)) if closest else set()
        differentiators = sorted(candidate_tokens - known_tokens)

        return NoveltyScore(
            novelty_score=max(0.0, 1.0 - max_overlap),
            max_overlap=max_overlap,
            closest_nodes=closest,
            differentiators=differentiators[:12],
        )
