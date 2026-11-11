import dataclasses

import httpx
import pytest

from runbookops.models import Model, ModelError


async def test_paid_model_is_rejected_before_inference(settings, monkeypatch):
    calls = []

    def endpoint(request):
        calls.append(request.method)
        return httpx.Response(
            200,
            json={
                "data": [
                    {
                        "id": "example/paid",
                        "pricing": {"prompt": "0.01", "completion": "0.02"},
                        "supported_parameters": ["tools", "tool_choice"],
                    }
                ]
            },
        )

    original = httpx.AsyncClient
    monkeypatch.setattr(
        httpx, "AsyncClient", lambda **kwargs: original(transport=httpx.MockTransport(endpoint), **kwargs)
    )
    model = Model(
        dataclasses.replace(
            settings, mode="openrouter", model="example/paid", api_key="example-key-test-only"
        )
    )
    with pytest.raises(ModelError, match="Free-only"):
        await model.complete([{"role": "user", "content": "hello"}])
    assert calls == ["GET"]


async def test_provider_timeout_is_visible_without_fallback(settings, monkeypatch):
    def endpoint(request):
        raise httpx.ReadTimeout("simulated provider timeout", request=request)

    original = httpx.AsyncClient
    monkeypatch.setattr(
        httpx, "AsyncClient", lambda **kwargs: original(transport=httpx.MockTransport(endpoint), **kwargs)
    )
    model = Model(
        dataclasses.replace(
            settings, mode="openrouter", model="example/free:free", api_key="example-key-test-only"
        )
    )
    model.verified.add("example/free:free")
    with pytest.raises(ModelError, match="No fallback"):
        await model.complete([{"role": "user", "content": "hello"}])


async def test_prompt_redaction_and_version_metadata(settings, monkeypatch):
    model = Model(settings)

    async def inspect(messages, tools, task):
        assert "should-not-leak" not in str(messages)
        assert "[redacted]" in str(messages)
        return {"role": "assistant", "content": "test response"}, {"mode": "test"}

    monkeypatch.setattr(model, "_complete", inspect)
    _, metadata = await model.complete(
        [
            {"role": "system", "content": "Use evidence."},
            {"role": "user", "content": "API_KEY=sk-or-v1-should-not-leak-checkout"},
        ]
    )
    assert len(metadata["prompt_version"]) == 12
    assert metadata["duration_ms"] >= 0


def test_task_router_is_explicit(settings, monkeypatch):
    monkeypatch.setenv("OPENROUTER_SMALL_MODEL", "example/small:free")
    model = Model(dataclasses.replace(settings, mode="openrouter", model="example/main:free"))
    assert model.route("summarize") == "example/small:free"
    assert model.route("diagnose") == "example/main:free"
