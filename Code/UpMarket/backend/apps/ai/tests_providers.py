"""Switching a capability between our GPU and an API must be a data change."""
from unittest.mock import patch

from django.test import TestCase

from services.ai import factory, providers
from services.ai.ollama import OllamaProvider
from services.ai.openai_compat import OpenAICompatProvider

from .models import ModelProvider


class ResolutionTests(TestCase):
    def test_no_rows_falls_back_to_env_defaults(self):
        chosen = providers.primary(providers.TEXT)
        self.assertIsNotNone(chosen)
        self.assertEqual(chosen.kind, "OLLAMA")
        self.assertTrue(chosen.is_local)

    def test_a_row_overrides_the_default(self):
        ModelProvider.objects.create(
            capability=ModelProvider.Capability.TEXT,
            kind=ModelProvider.Kind.OPENAI,
            name="OpenRouter",
            base_url="https://openrouter.ai/api/v1",
            api_key="sk-test",
            model_name="anthropic/claude-sonnet-4",
        )
        chosen = providers.primary(providers.TEXT)
        self.assertEqual(chosen.kind, "OPENAI")
        self.assertEqual(chosen.model_name, "anthropic/claude-sonnet-4")
        self.assertFalse(chosen.is_local)

    def test_priority_decides_the_order(self):
        ModelProvider.objects.create(
            capability=ModelProvider.Capability.TEXT, kind=ModelProvider.Kind.OPENAI,
            name="پشتیبان", base_url="https://api.example.com/v1",
            model_name="gpt-4o-mini", priority=200,
        )
        ModelProvider.objects.create(
            capability=ModelProvider.Capability.TEXT, kind=ModelProvider.Kind.OLLAMA,
            name="لوکال", model_name="qwq:32b", priority=10,
        )
        order = [p.name for p in providers.candidates(providers.TEXT)]
        self.assertEqual(order, ["لوکال", "پشتیبان"])

    def test_inactive_rows_are_skipped(self):
        ModelProvider.objects.create(
            capability=ModelProvider.Capability.IMAGE, kind=ModelProvider.Kind.OPENAI,
            name="خاموش", base_url="https://api.example.com/v1",
            model_name="dall-e-3", is_active=False,
        )
        chosen = providers.primary(providers.IMAGE)
        self.assertEqual(chosen.kind, "COMFYUI")  # back to the .env default

    def test_uses_own_gpu_reflects_the_choice(self):
        self.assertTrue(providers.uses_own_gpu(providers.VIDEO))
        ModelProvider.objects.create(
            capability=ModelProvider.Capability.VIDEO, kind=ModelProvider.Kind.REPLICATE,
            name="ابری", base_url="https://api.replicate.com/v1/predictions",
            api_key="r8-test", model_name="wan-2.2", priority=1,
        )
        self.assertFalse(providers.uses_own_gpu(providers.VIDEO))

    def test_empty_base_url_inherits_from_env(self):
        ModelProvider.objects.create(
            capability=ModelProvider.Capability.TEXT, kind=ModelProvider.Kind.OLLAMA,
            name="لوکال", model_name="qwq:32b", base_url="",
        )
        chosen = providers.primary(providers.TEXT)
        self.assertTrue(chosen.base_url)  # filled in from settings


class FactoryTests(TestCase):
    def test_ollama_row_builds_the_local_client(self):
        ModelProvider.objects.create(
            capability=ModelProvider.Capability.TEXT, kind=ModelProvider.Kind.OLLAMA,
            name="لوکال", model_name="qwq:32b",
        )
        self.assertIsInstance(factory.text_provider(), OllamaProvider)

    def test_api_row_builds_the_http_client(self):
        ModelProvider.objects.create(
            capability=ModelProvider.Capability.TEXT, kind=ModelProvider.Kind.OPENAI,
            name="ابری", base_url="https://api.example.com/v1",
            api_key="sk-x", model_name="gpt-4o-mini",
        )
        client = factory.text_provider()
        self.assertIsInstance(client, OpenAICompatProvider)
        self.assertEqual(client.model, "gpt-4o-mini")
        self.assertEqual(client.api_key, "sk-x")

    def test_vision_and_text_resolve_independently(self):
        ModelProvider.objects.create(
            capability=ModelProvider.Capability.TEXT, kind=ModelProvider.Kind.OPENAI,
            name="متن ابری", base_url="https://api.example.com/v1", model_name="gpt-4o-mini",
        )
        self.assertIsInstance(factory.text_provider(), OpenAICompatProvider)
        self.assertIsInstance(factory.vision_provider(), OllamaProvider)


class ValidationTests(TestCase):
    def test_external_provider_requires_a_url(self):
        from django.core.exceptions import ValidationError

        row = ModelProvider(
            capability=ModelProvider.Capability.TEXT, kind=ModelProvider.Kind.OPENAI,
            name="بی‌آدرس", model_name="gpt-4o-mini",
        )
        with self.assertRaises(ValidationError):
            row.full_clean()

    def test_comfyui_cannot_serve_text(self):
        from django.core.exceptions import ValidationError

        row = ModelProvider(
            capability=ModelProvider.Capability.TEXT, kind=ModelProvider.Kind.COMFYUI,
            name="غلط", model_name="x",
        )
        with self.assertRaises(ValidationError):
            row.full_clean()


class OpenAICompatTests(TestCase):
    def _reply(self, content):
        class R:
            status_code = 200

            @staticmethod
            def json():
                return {"choices": [{"message": {"content": content}}]}

        return R()

    @patch("services.ai.openai_compat.requests.post")
    def test_generate_returns_text(self, mock_post):
        mock_post.return_value = self._reply("سلام")
        client = OpenAICompatProvider("https://api.example.com/v1", "k", "m")
        self.assertEqual(client.generate("hi"), "سلام")

    @patch("services.ai.openai_compat.requests.post")
    def test_generate_json_parses_a_fenced_block(self, mock_post):
        mock_post.return_value = self._reply('```json\n{"a": 1}\n```')
        client = OpenAICompatProvider("https://api.example.com/v1", "k", "m")
        self.assertEqual(client.generate_json("hi"), {"a": 1})

    @patch("services.ai.openai_compat.requests.post")
    def test_bad_key_is_reported_not_retried(self, mock_post):
        class R:
            status_code = 401
            text = "unauthorized"

        mock_post.return_value = R()
        client = OpenAICompatProvider("https://api.example.com/v1", "bad", "m")
        with self.assertRaises(Exception) as ctx:
            client.generate("hi")
        self.assertIn("۴۰۱", str(ctx.exception))
        self.assertEqual(mock_post.call_count, 1)  # no pointless retries

    def test_missing_url_fails_clearly(self):
        client = OpenAICompatProvider("", "k", "m")
        with self.assertRaises(Exception):
            client.generate("hi")
