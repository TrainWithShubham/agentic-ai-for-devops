import dataclasses
import json
from unittest.mock import Mock

import boto3
import httpx
import pytest
from botocore.stub import Stubber

from runbookops.models import Model, ModelError, tool_call
from runbookops.tools import SCHEMAS


@pytest.mark.parametrize(
    "case",
    [
        "missing-key",
        "missing-model",
        "no-tools",
        "inference-http",
        "inference-error",
        "no-choices",
        "success",
        "paid-allowed",
        "groq",
        "empty-content",
    ],
)
async def test_http_provider_contract(settings, monkeypatch, case):
    requests = []

    def endpoint(request):
        requests.append(request)
        if request.url.path.endswith("/models"):
            return httpx.Response(
                200,
                json={
                    "data": [
                        {
                            "id": "test/model:free",
                            "pricing": {"prompt": "0", "completion": "0"},
                            "supported_parameters": [] if case == "no-tools" else ["tools", "tool_choice"],
                        }
                    ]
                },
            )
        payload = json.loads(request.content)
        assert payload["max_tokens"] == settings.max_tokens
        assert payload["messages"][0]["content"] == "Hello"
        if case == "inference-http":
            return httpx.Response(429, json={"error": "password=private-provider-body"})
        if case == "inference-error":
            return httpx.Response(200, json={"error": "private-provider-body"})
        if case == "no-choices":
            return httpx.Response(200, json={"choices": []})
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "content": None
                            if case == "empty-content"
                            else "API_KEY=sk-or-v1-example-private-secret",
                        }
                    }
                ],
                "usage": {
                    "prompt_tokens": 10,
                    "completion_tokens": 3,
                    "total_tokens": 13,
                    "cost": 0,
                    "private": "not-exported",
                },
            },
        )

    original = httpx.AsyncClient
    monkeypatch.setattr(
        httpx, "AsyncClient", lambda **kw: original(transport=httpx.MockTransport(endpoint), **kw)
    )
    config = dataclasses.replace(
        settings,
        mode="groq" if case == "groq" else "openrouter",
        model="" if case == "missing-model" else "test/model:free",
        api_key="" if case == "missing-key" else "test-key",
        free_only=case != "paid-allowed",
    )
    model = Model(config)
    if case in (
        "missing-key",
        "missing-model",
        "no-tools",
        "inference-http",
        "inference-error",
        "no-choices",
    ):
        with pytest.raises(ModelError) as failure:
            await model.complete([{"role": "user", "content": "Hello"}], SCHEMAS)
        assert "private-provider-body" not in str(failure.value)
        if case.startswith("missing"):
            assert not requests
    else:
        message, meta = await model.complete([{"role": "user", "content": "Hello"}], SCHEMAS)
        assert message["content"] is None if case == "empty-content" else "[redacted]" in message["content"]
        assert meta["usage"]["total_tokens"] == 13 and "private" not in meta["usage"]
        assert len(requests) == (1 if case in ("paid-allowed", "groq") else 2)


@pytest.mark.parametrize("failure", [httpx.ConnectTimeout, httpx.ConnectError, httpx.ReadTimeout])
async def test_network_failure_is_safe_and_does_not_fallback(settings, monkeypatch, failure):
    def endpoint(request):
        raise failure("secret-request-detail", request=request)

    original = httpx.AsyncClient
    monkeypatch.setattr(
        httpx, "AsyncClient", lambda **kw: original(transport=httpx.MockTransport(endpoint), **kw)
    )
    model = Model(dataclasses.replace(settings, mode="openrouter", model="test:free", api_key="test-key"))
    with pytest.raises(ModelError, match="No fallback") as error:
        await model.complete([{"role": "user", "content": "Hello"}])
    assert "secret-request-detail" not in str(error.value)


async def test_catalog_http_error_is_distinct(settings, monkeypatch):
    original = httpx.AsyncClient
    monkeypatch.setattr(
        httpx,
        "AsyncClient",
        lambda **kw: original(transport=httpx.MockTransport(lambda r: httpx.Response(503)), **kw),
    )
    with pytest.raises(ModelError, match="catalog returned HTTP 503"):
        await Model(
            dataclasses.replace(settings, mode="openrouter", model="test:free", api_key="test-key")
        ).complete([])


async def test_offline_reply_without_tools_and_after_tools(settings):
    model = Model(settings)
    message, meta = await model.complete([{"role": "user", "content": "hello"}])
    assert "Offline practice" in message["content"] and meta["mode"] == "offline"
    history = [{"role": "assistant", "tool_calls": [tool_call("prepare_change", {}, 1)]}]
    assert "awaits Jethalal" in model.offline(history, SCHEMAS)["content"]


def test_bedrock_refuses_implicit_billed_inference(settings):
    with pytest.raises(ModelError, match="FREE_ONLY=false"):
        Model(settings).converse([], None, "answer")


async def test_bedrock_converse_conversion_and_usage(settings, monkeypatch):
    client = boto3.client(
        "bedrock-runtime",
        region_name="us-east-1",
        aws_access_key_id="testing",
        aws_secret_access_key="testing",
    )
    factory = Mock(return_value=client)
    monkeypatch.setattr(boto3, "client", factory)
    model = Model(dataclasses.replace(settings, mode="bedrock", model="test-bedrock", free_only=False))
    messages = [
        {"role": "system", "content": "Use tools."},
        {"role": "user", "content": "Check checkout"},
        {
            "role": "assistant",
            "content": None,
            "tool_calls": [
                {
                    "id": "call-1",
                    "function": {"name": "get_service_health", "arguments": '{"service":"checkout"}'},
                }
            ],
        },
        {"role": "tool", "tool_call_id": "call-1", "content": '{"http_status":503}'},
        {"role": "tool", "tool_call_id": "call-2", "content": '{"lines":[]}'},
    ]
    response = {
        "output": {
            "message": {
                "role": "assistant",
                "content": [
                    {"text": "Checking notes."},
                    {
                        "toolUse": {
                            "toolUseId": "call-3",
                            "name": "search_runbooks",
                            "input": {"query": "checkout"},
                        }
                    },
                ],
            }
        },
        "stopReason": "tool_use",
        "usage": {"inputTokens": 20, "outputTokens": 10, "totalTokens": 30},
        "metrics": {"latencyMs": 5},
    }
    with Stubber(client) as stub:
        stub.add_response("converse", response)
        stub.add_response(
            "converse",
            {
                **response,
                "output": {"message": {"role": "assistant", "content": [{"text": "Done"}]}},
                "stopReason": "end_turn",
            },
        )
        message, meta = await model.complete(messages, SCHEMAS)
        assert message["tool_calls"][0]["id"] == "call-3"
        assert meta["usage"] == {"prompt_tokens": 20, "completion_tokens": 10}
        final, _ = await model.complete([{"role": "user", "content": "hello"}])
        assert final["content"] == "Done" and "tool_calls" not in final
        stub.assert_no_pending_responses()
    factory.assert_called_once()
