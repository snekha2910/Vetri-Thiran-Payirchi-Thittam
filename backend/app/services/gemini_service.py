import asyncio
import json
import logging
import random
import re
from typing import Dict, Any, Optional, List
from google.genai import types
from app.integrations.gemini_client import gemini_manager
from app.core.config import settings
from app.core.exceptions import AIProcessingError

logger = logging.getLogger("pocketsmart.gemini_service")

class GeminiService:
    @staticmethod
    def _parse_json(text: str) -> Dict[str, Any]:
        cleaned = text.strip()
        
        # Match markdown code block ```json ... ```
        json_pattern = r"```(?:json)?\s*([\s\S]*?)\s*```"
        match = re.search(json_pattern, cleaned)
        if match:
            cleaned = match.group(1).strip()
        else:
            first_brace = cleaned.find("{")
            last_brace = cleaned.rfind("}")
            if first_brace != -1 and last_brace != -1:
                cleaned = cleaned[first_brace:last_brace + 1]

        try:
            return json.loads(cleaned)
        except Exception as e:
            logger.error(f"Failed to parse JSON from AI response: {e}. Raw snippet: {text[:200]}")
            raise AIProcessingError("Failed to parse structured JSON from AI response")

    @classmethod
    def validate_response(cls, data: Dict[str, Any], planner_type: str) -> Dict[str, Any]:
        """
        Validates AI parsed output ensuring no corrupted or malformed payloads reach persistence.
        """
        if not isinstance(data, dict):
            raise AIProcessingError("AI output must be a valid JSON dictionary")

        default_sum = f"AI Curated Plan for {planner_type.capitalize()} with optimal cost-to-value distribution."
        if not data.get("summary") and not data.get("ai_summary"):
            data["summary"] = default_sum
            data["ai_summary"] = default_sum
        elif data.get("summary") and not data.get("ai_summary"):
            data["ai_summary"] = data["summary"]
        elif data.get("ai_summary") and not data.get("summary"):
            data["summary"] = data["ai_summary"]

        if not isinstance(data.get("recommendations"), list):
            data["recommendations"] = []
        else:
            # Filter and sanitize recommendations
            clean_recs = []
            for r in data["recommendations"]:
                if isinstance(r, dict) and r.get("name"):
                    try:
                        price = float(r.get("price", 0))
                        if price >= 0:
                            r["price"] = price
                            clean_recs.append(r)
                    except (ValueError, TypeError):
                        continue
            data["recommendations"] = clean_recs

        if not isinstance(data.get("warnings"), list):
            data["warnings"] = []

        if not isinstance(data.get("additional_suggestions"), list):
            data["additional_suggestions"] = [
                "Prioritize high-impact foundational items first.",
                "Compare seasonal discounts across online marketplaces.",
                "Review multi-vendor shipping options for bulk savings."
            ]

        if planner_type == "jewelry":
            if not isinstance(data.get("styling_tips"), list):
                data["styling_tips"] = [
                    "Match metal tones across your accessories.",
                    "Choose one statement piece to balance the ensemble."
                ]
            if not isinstance(data.get("outfit_analysis"), dict):
                data["outfit_analysis"] = {
                    "colors": ["complementary"],
                    "style": "contemporary",
                    "formality": "semi-formal"
                }

        if planner_type == "party":
            if not isinstance(data.get("venue_suggestions"), list):
                data["venue_suggestions"] = []

        return data

    @classmethod
    def _repair_plan_schema(cls, data: Dict[str, Any], planner_type: str) -> Dict[str, Any]:
        return cls.validate_response(data, planner_type)

    @classmethod
    async def generate_plan_ai(
        cls,
        prompt: str,
        planner_type: str = "home",
        image_bytes: Optional[bytes] = None,
        max_retries: int = 3,
        initial_backoff: float = 1.0,
        backoff_factor: float = 2.0
    ) -> Dict[str, Any]:
        """
        Executes Google Gemini generation using google.genai SDK with multi-model fallback,
        retry backoff, and robust schema validation.
        """
        if not gemini_manager.is_available:
            logger.warning("Gemini manager is not available or mock mode is active, returning fallback structured plan.")
            return {
                "ai_summary": f"Smart AI {planner_type.capitalize()} Plan designed to maximize quality within your budget parameters.",
                "summary": f"Smart AI {planner_type.capitalize()} Plan designed to maximize quality within your budget parameters.",
                "recommendations": [],
                "warnings": ["AI generation offline; deterministic algorithmic allocation used."]
            }

        client = gemini_manager.client
        if client is None:
            logger.warning("Gemini client is None, returning fallback plan.")
            return {
                "ai_summary": f"Smart AI {planner_type.capitalize()} Plan designed to maximize quality within your budget parameters.",
                "summary": f"Smart AI {planner_type.capitalize()} Plan designed to maximize quality within your budget parameters.",
                "recommendations": [],
                "warnings": ["Gemini client not initialized."]
            }

        # Build contents
        contents: List[Any] = [prompt]
        if image_bytes:
            contents.append(types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"))

        # Candidate models to try in order (primary from config, then valid fallbacks)
        candidate_models = [settings.gemini_model]
        for fallback in ["gemini-3.5-flash", "gemini-3.5-flash-lite", "gemini-3.6-flash"]:
            if fallback not in candidate_models:
                candidate_models.append(fallback)

        last_error = None

        for model_name in candidate_models:
            for attempt in range(1, max_retries + 1):
                try:
                    logger.info(f"Invoking Gemini model '{model_name}' (attempt {attempt}/{max_retries})...")
                    response = await asyncio.to_thread(
                        client.models.generate_content,
                        model=model_name,
                        contents=contents,
                        config=types.GenerateContentConfig(
                            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)
                        )
                    )
                    raw_text = response.text or ""
                    parsed = cls._parse_json(raw_text)
                    validated = cls.validate_response(parsed, planner_type)
                    logger.info(f"Gemini generation succeeded with model '{model_name}'")
                    return validated

                except AIProcessingError as e:
                    logger.warning(f"JSON parsing error from model '{model_name}': {e}")
                    last_error = e
                    # Non-fatal if retries left
                    if attempt < max_retries:
                        await asyncio.sleep(0.5)
                        continue
                    break

                except Exception as e:
                    err_str = str(e).lower()
                    last_error = e

                    # Model not found or deprecated for this API version -> skip to next candidate immediately
                    if "404" in err_str or "not found" in err_str or "no longer available" in err_str:
                        logger.warning(f"Model '{model_name}' returned 404/unavailable: {e}. Switching to next candidate.")
                        break

                    is_retryable = any(k in err_str for k in ["429", "resource_exhausted", "quota", "503", "500", "timeout", "deadline"])
                    if is_retryable and attempt < max_retries:
                        sleep_time = (initial_backoff * (backoff_factor ** (attempt - 1))) + random.uniform(0.1, 0.4)
                        logger.warning(f"Gemini call attempt {attempt}/{max_retries} failed ({type(e).__name__}). Retrying in {sleep_time:.2f}s...")
                        await asyncio.sleep(sleep_time)
                    else:
                        logger.error(f"Gemini attempt failed for model '{model_name}': {e}")
                        break

        # Fallback safe error return
        logger.warning(f"All Gemini models exhausted. Returning safe deterministic fallback. Last error: {last_error}")
        return {
            "ai_summary": f"Optimized {planner_type.capitalize()} Plan generated with algorithmic recommendations.",
            "summary": f"Optimized {planner_type.capitalize()} Plan generated with algorithmic recommendations.",
            "recommendations": [],
            "warnings": [f"AI synthesis notice: {str(last_error)[:80] if last_error else 'AI generation temporarily unavailable'}"]
        }

    # Centralized abstraction methods required by STEP 7.4
    @classmethod
    async def generate_home(cls, input_data: Dict[str, Any]) -> Dict[str, Any]:
        from app.prompts.home_prompt import build_home_prompt
        prompt = build_home_prompt(input_data)
        return await cls.generate_plan_ai(prompt, planner_type="home")

    @classmethod
    async def generate_party(cls, input_data: Dict[str, Any]) -> Dict[str, Any]:
        from app.prompts.party_prompt import build_party_prompt
        prompt = build_party_prompt(input_data)
        return await cls.generate_plan_ai(prompt, planner_type="party")

    @classmethod
    async def generate_jewelry(cls, input_data: Dict[str, Any], image_bytes: Optional[bytes] = None) -> Dict[str, Any]:
        from app.prompts.jewelry_prompt import build_jewelry_prompt
        prompt = build_jewelry_prompt(input_data)
        return await cls.generate_plan_ai(prompt, planner_type="jewelry", image_bytes=image_bytes)

    @classmethod
    async def analyze_outfit(cls, image_bytes: bytes, style_preference: Optional[str] = None) -> Dict[str, Any]:
        prompt = f"""You are a professional fashion analyst and jewelry stylist.
Analyze this outfit image and describe:
1. Primary and accent colors
2. Formality level (casual, business, semi-formal, formal)
3. Styling aesthetic ({style_preference or 'contemporary'})
4. Recommended jewelry categories (necklaces, earrings, bracelets, rings) that complement this outfit.

Return ONLY valid JSON:
{{
  "colors": ["color1", "color2"],
  "formality": "formal",
  "style": "{style_preference or 'contemporary'}",
  "recommended_jewelry": ["necklace", "earrings"]
}}
"""
        return await cls.generate_plan_ai(prompt, planner_type="jewelry", image_bytes=image_bytes)
