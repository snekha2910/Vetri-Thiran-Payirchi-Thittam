import pytest
from app.services.gemini_service import GeminiService
from app.core.exceptions import AIProcessingError

class TestExtractJson:
    def test_plain_json(self):
        text = '{"summary": "Looks great", "recommendations": []}'
        res = GeminiService._parse_json(text)
        assert res["summary"] == "Looks great"

    def test_json_in_markdown_block(self):
        text = '```json\n{"summary": "Decor plan", "recommendations": []}\n```'
        res = GeminiService._parse_json(text)
        assert res["summary"] == "Decor plan"

    def test_json_in_backtick_block(self):
        text = '```\n{"summary": "Party plan", "recommendations": []}\n```'
        res = GeminiService._parse_json(text)
        assert res["summary"] == "Party plan"

    def test_json_embedded_in_text(self):
        text = 'Here is your plan:\n{"summary": "Jewelry styling", "recommendations": []}\nHope you like it!'
        res = GeminiService._parse_json(text)
        assert res["summary"] == "Jewelry styling"

    def test_invalid_raises(self):
        text = 'This is totally invalid non-json string.'
        with pytest.raises(AIProcessingError):
            GeminiService._parse_json(text)


class TestAttemptRepair:
    def test_missing_summary_gets_default(self):
        data = {"recommendations": []}
        repaired = GeminiService._repair_plan_schema(data, "home")
        assert "summary" in repaired
        assert len(repaired["summary"]) > 0

    def test_missing_recommendations_gets_empty_list(self):
        data = {"summary": "Generated summary"}
        repaired = GeminiService._repair_plan_schema(data, "party")
        assert "recommendations" in repaired
        assert isinstance(repaired["recommendations"], list)

    def test_repair_adds_fallback_warning(self):
        data = {}
        repaired = GeminiService._repair_plan_schema(data, "jewelry")
        assert "warnings" in repaired
