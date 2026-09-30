import unittest

from ai_layer import InferenceRequest, SnapdragonProvider, get_provider


class ProviderSelectionTests(unittest.TestCase):
    def setUp(self):
        self.request = InferenceRequest(
            question="What is the main idea?",
            document_text="The main idea is an example study passage.",
            filename="notes.txt",
        )

    def test_local_provider_is_snapdragon_provider(self):
        provider = get_provider("local")
        self.assertIsInstance(provider, SnapdragonProvider)

    def test_snapdragon_provider_is_explicitly_a_mock(self):
        result = SnapdragonProvider().infer(self.request)
        self.assertEqual(result.provider, "local")
        self.assertEqual(result.metadata["execution"], "mock")
        self.assertFalse(result.metadata["hardware_execution"])
        self.assertIn("No Snapdragon model is loaded", result.answer)

    def test_cloud_alias_selects_cloud_provider_without_calling_network(self):
        provider = get_provider("gemini")
        self.assertEqual(provider.provider_id, "cloud")

    def test_unknown_provider_is_rejected(self):
        with self.assertRaises(ValueError):
            get_provider("unknown")


if __name__ == "__main__":
    unittest.main()
