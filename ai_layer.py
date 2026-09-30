"""Inference providers for StudySnap.

The application talks to this module rather than coupling itself to a specific
cloud SDK or device runtime.  The Snapdragon provider is intentionally a mock
until a compatible device and compiled model are available.
"""

from __future__ import annotations

import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

GEMINI_MODELS = (
    "gemini-3.7-flash",
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-flash-latest",
)
PLACEHOLDER_API_KEY = "YOUR_API_KEY_HERE"


@dataclass(frozen=True)
class InferenceRequest:
    """The provider-neutral input needed to answer a study question."""

    question: str
    document_text: str
    filename: str | None = None


@dataclass(frozen=True)
class InferenceResult:
    """A provider-neutral answer returned to the Flask application."""

    answer: str
    provider: str
    model: str
    metadata: dict[str, Any]


class ProviderError(RuntimeError):
    """Base error raised by an inference provider."""


class InvalidCredentialsError(ProviderError):
    """The configured cloud credentials are missing or invalid."""


class RetryableProviderError(ProviderError):
    """The provider/model is temporarily unavailable or overloaded."""


class InferenceProvider(ABC):
    """Stable application-facing interface for cloud or local inference."""

    provider_id: str

    @abstractmethod
    def infer(self, request: InferenceRequest) -> InferenceResult:
        raise NotImplementedError


def get_gemini_api_key() -> str | None:
    """Return a usable Gemini key without ever exposing it to the client."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or not api_key.strip() or api_key.strip() == PLACEHOLDER_API_KEY:
        return None
    return api_key.strip()


def _error_text(exc: Exception) -> str:
    return str(exc).lower()


def is_invalid_api_key_error(exc: Exception) -> bool:
    markers = (
        "api key not valid",
        "api_key_invalid",
        "invalid api key",
        "api key expired",
        "invalid x-goog-api-key",
        "unauthenticated",
    )
    return any(marker in _error_text(exc) for marker in markers)


def is_retryable_model_error(exc: Exception) -> bool:
    markers = (
        "not_found",
        "not found",
        "no longer available",
        "unavailable",
        "high demand",
        "overloaded",
        "resource exhausted",
        "429",
        "503",
        "404",
    )
    return any(marker in _error_text(exc) for marker in markers)


class GeminiProvider(InferenceProvider):
    """Existing Gemini API path, isolated behind the common provider contract."""

    provider_id = "cloud"

    def infer(self, request: InferenceRequest) -> InferenceResult:
        # Keep the cloud SDK lazy so local/mock deployments do not need the
        # Gemini dependency installed just to use the Snapdragon abstraction.
        from google import genai

        api_key = get_gemini_api_key()
        if not api_key:
            raise InvalidCredentialsError(
                "Gemini API key is missing. Set GEMINI_API_KEY in your local .env file "
                "(do not commit the real key) and restart the Flask server."
            )

        study_context = request.document_text[:400_000]
        prompt = (
            "You are StudySnap, a study assistant. Answer the student's question using only "
            "the provided study material. If the material does not contain the answer, say so "
            "clearly. Be concise and accurate.\n\n"
            f"Study material (filename: {request.filename or 'document'}):\n"
            f"{study_context}\n\n"
            f"Student question:\n{request.question}"
        )

        client = genai.Client(api_key=api_key)
        last_error: Exception | None = None
        response = None
        used_model = None
        for model_name in GEMINI_MODELS:
            try:
                response = client.models.generate_content(model=model_name, contents=prompt)
                used_model = model_name
                break
            except Exception as exc:
                last_error = exc
                if is_invalid_api_key_error(exc):
                    raise InvalidCredentialsError from exc
                if is_retryable_model_error(exc):
                    continue
                raise ProviderError from exc

        if response is None:
            error = last_error or RuntimeError("Gemini returned no response.")
            if is_retryable_model_error(error):
                raise RetryableProviderError from error
            raise ProviderError from error

        answer = (getattr(response, "text", None) or "").strip()
        if not answer:
            raise ProviderError("Gemini returned an empty response. Try a more specific question.")

        return InferenceResult(
            answer=answer,
            provider=self.provider_id,
            model=used_model or "unknown",
            metadata={"execution": "cloud", "credentials": "server-side"},
        )


class SnapdragonProvider(InferenceProvider):
    """Local provider seam; currently returns a transparent, deterministic mock.

    This class deliberately does not claim to execute on a Snapdragon NPU.  A
    future implementation can replace the mock body while preserving the
    InferenceProvider interface used by the application.
    """

    provider_id = "local"
    model_name = "snapdragon-mock-v0"

    def infer(self, request: InferenceRequest) -> InferenceResult:
        # Future Qualcomm deployment boundary:
        # 1. Load a Qualcomm AI Hub-optimized ONNX or equivalent compiled model.
        # 2. Create a Qualcomm AI Runtime/QNN (AI Engine Direct) session.
        # 3. Bind tokenizer/tensors and execute on the Hexagon NPU where supported.
        # The model and runtime must be supplied by the deployment environment;
        # this repository intentionally ships neither hardware bindings nor a model.
        answer = (
            "[Snapdragon local inference mock] No Snapdragon model is loaded in this "
            "environment, so no on-device inference was performed. "
            f"Your question was: {request.question}"
        )
        return InferenceResult(
            answer=answer,
            provider=self.provider_id,
            model=self.model_name,
            metadata={
                "execution": "mock",
                "hardware_execution": False,
                "runtime": "not configured",
                "deployment_note": "Replace SnapdragonProvider.infer with Qualcomm runtime execution.",
            },
        )


def get_provider(provider_name: str | None = None) -> InferenceProvider:
    """Build the configured provider without importing device-specific runtimes."""
    selected = (provider_name or os.getenv("AI_PROVIDER", "cloud")).strip().lower()
    if selected in {"local", "snapdragon", "snapdragon-local"}:
        return SnapdragonProvider()
    if selected in {"cloud", "gemini"}:
        return GeminiProvider()
    raise ValueError(f"Unsupported inference provider: {selected}")
