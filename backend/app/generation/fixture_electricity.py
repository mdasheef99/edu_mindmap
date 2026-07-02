"""Deterministic Electricity generation fixture for M4."""

from __future__ import annotations

from app.generation.provider import GeneratedNode

PROMPT_VERSION = "fixture-electricity-v1"
MODEL_ID = "fixture"


class ElectricityFixtureProvider:
    """Student-safe fixture provider for Class 10 CBSE Science - Electricity."""

    _nodes: dict[str, tuple[str, str]] = {
        "overview": (
            "Electricity - chapter overview",
            "Electricity studies how charges move through circuits and how that movement powers devices.",
        ),
        "electric-current": (
            "Electric current",
            "Electric current is the rate at which electric charge flows through a conductor.",
        ),
        "potential-difference": (
            "Potential difference",
            "Potential difference is the push that moves charge between two points in a circuit.",
        ),
        "ohms-law": (
            "Ohm's law",
            "Ohm's law connects voltage, current, and resistance through V = IR.",
        ),
        "resistance": (
            "Resistance",
            "Resistance opposes current and depends on the material and shape of the conductor.",
        ),
        "factors-affecting-resistance": (
            "Factors affecting resistance",
            "Resistance changes with length, area, material, and temperature.",
        ),
        "series-combination": (
            "Series combination",
            "In a series circuit, components share one path and resistances add together.",
        ),
        "parallel-combination": (
            "Parallel combination",
            "In a parallel circuit, components have separate paths and the equivalent resistance decreases.",
        ),
        "heating-effect": (
            "Heating effect of electric current",
            "Current can produce heat when electrical energy is converted into thermal energy.",
        ),
        "electric-power": (
            "Electric power",
            "Electric power measures how quickly electrical energy is used or converted.",
        ),
    }

    def node_keys(self) -> list[str]:
        return list(self._nodes)

    def root(self) -> GeneratedNode:
        return self._node("overview", kind="generated")

    def child_for_choice(self, *, source_key: str, selected_option_text: str) -> GeneratedNode:
        next_key = _next_key(source_key, selected_option_text, self.node_keys())
        kind = "generated" if source_key in self._nodes else "fallback"
        return self._node(
            next_key,
            kind=kind,
            edge_label=selected_option_text,
            is_terminal=source_key == self.node_keys()[-1],
        )

    def _node(
        self,
        key: str,
        *,
        kind: str,
        edge_label: str | None = None,
        is_terminal: bool = False,
    ) -> GeneratedNode:
        title, body = self._nodes[key]
        return GeneratedNode(
            kind=kind,
            node_key=key,
            node_title=title,
            node_body=body,
            edge_label=edge_label,
            is_terminal=is_terminal,
            prompt_version=PROMPT_VERSION,
            model_id=MODEL_ID,
            lineage={
                "provider": "fixture_electricity_v1",
                "source": "m4_seed",
                "node_key": key,
                "completion_state": "terminal" if is_terminal else "in_progress",
            },
        )


def _next_key(source_key: str, selected_option_text: str, keys: list[str]) -> str:
    if source_key not in keys:
        return "overview"
    current_index = keys.index(source_key)
    if current_index + 1 < len(keys):
        return keys[current_index + 1]
    normalized = selected_option_text.strip().lower()
    for key in keys:
        if key.replace("-", " ") in normalized:
            return key
    return keys[-1]
