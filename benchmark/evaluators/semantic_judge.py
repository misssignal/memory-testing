"""Optional LLM judge for dimensions that cannot be scored structurally.

This module is never imported by the core runner unless explicitly requested.
The judge never alters ground truth — it only evaluates free-text responses
against expected behavior.
"""

import json
import os
import urllib.request
from dataclasses import dataclass
from typing import Any


@dataclass
class JudgmentResult:
    case_id: str
    dimension: str
    score: float  # 0.0 to 1.0
    rationale: str
    model: str
    temperature: float
    raw_response: dict[str, Any]


JUDGE_PROMPT_TEMPLATE = """You are evaluating a memory system's response.
You will be given a query, the expected behavior, and the system's actual response.
Score the response on a scale of 0.0 to 1.0 for the specified dimension.

Dimension: {dimension}
Query: {query}
Expected behavior: {expected_behavior}
System response: {system_response}

Respond with ONLY a JSON object:
{{"score": <float 0.0-1.0>, "rationale": "<one sentence>"}}
"""

DIMENSIONS = {
    "conflict_communication": "Did the answer clearly communicate that there are unresolved competing claims?",
    "uncertainty_preservation": "Did the answer appropriately convey uncertainty rather than presenting low-confidence information as definitive?",
    "semantic_equivalence": "Does the free-text answer preserve the meaning of the expected fact?",
    "confidence_calibration": "Did the answer overstate confidence beyond what the evidence supports?",
}


class SemanticJudge:
    def __init__(
        self,
        provider: str = "anthropic",
        model: str = "claude-sonnet-5",
        temperature: float = 0.0,
    ):
        self.provider = provider
        self.model = model
        self.temperature = temperature
        self._api_key = os.environ.get("ANTHROPIC_API_KEY", "")

    def judge(
        self,
        case_id: str,
        dimension: str,
        query: str,
        expected_behavior: str,
        system_response: str,
    ) -> JudgmentResult:
        if self.provider != "anthropic":
            raise NotImplementedError(f"Provider {self.provider} not yet supported")

        prompt = JUDGE_PROMPT_TEMPLATE.format(
            dimension=DIMENSIONS.get(dimension, dimension),
            query=query,
            expected_behavior=expected_behavior,
            system_response=system_response,
        )

        payload = {
            "model": self.model,
            "max_tokens": 256,
            "temperature": self.temperature,
            "messages": [{"role": "user", "content": prompt}],
        }

        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=json.dumps(payload).encode(),
            headers={
                "x-api-key": self._api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            method="POST",
        )

        with urllib.request.urlopen(req, timeout=30) as r:
            resp = json.loads(r.read())

        text = resp["content"][0]["text"]
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            parsed = {"score": 0.0, "rationale": f"Could not parse judge response: {text}"}

        return JudgmentResult(
            case_id=case_id,
            dimension=dimension,
            score=float(parsed.get("score", 0.0)),
            rationale=parsed.get("rationale", ""),
            model=self.model,
            temperature=self.temperature,
            raw_response=resp,
        )
