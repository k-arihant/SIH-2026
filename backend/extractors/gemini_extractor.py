"""
Gemini Semantic Extractor.
Uses strictly gemini-3.6-flash via the official google-genai SDK for structured semantic extraction.
"""

import os
import json
import logging
from typing import Dict, Any, Union
from google import genai
from google.genai import types

from backend.extractors.prompt import EXTRACTION_SYSTEM_INSTRUCTION, build_user_prompt

logger = logging.getLogger(__name__)


class GeminiSemanticExtractor:
    def __init__(self, api_key: str = None):
        raw_key = api_key or os.getenv("GEMINI_API_KEY", "")
        self.api_key = raw_key.strip().strip('"').strip("'") if raw_key else ""
        self.model_name = "gemini-3.6-flash"
        self._client = None

    @property
    def client(self) -> genai.Client:
        if self._client is None:
            if not self.api_key:
                raise ValueError("GEMINI_API_KEY is not set. Please provide a valid Gemini API key.")
            self._client = genai.Client(api_key=self.api_key)
        return self._client

    def extract(self, ocr_data: Union[Dict[str, Any], Any]) -> Dict[str, Any]:
        """
        Extracts structured product declarations using ONLY gemini-3.6-flash.
        """
        if hasattr(ocr_data, "model_dump"):
            ocr_dict = ocr_data.model_dump()
        else:
            ocr_dict = ocr_data

        user_content = build_user_prompt(ocr_dict)

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=user_content,
                config=types.GenerateContentConfig(
                    system_instruction=EXTRACTION_SYSTEM_INSTRUCTION,
                    response_mime_type="application/json",
                    temperature=0.0,
                ),
            )
            response_text = response.text.strip()
            return json.loads(response_text)

        except Exception as e:
            err_msg = str(e)
            # Never retry if quota is exhausted
            if "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg:
                raise e
            # Check if Interactions API is recommended
            if "Interactions API" in err_msg and hasattr(self.client, "interactions"):
                logger.info("Attempting extraction via Interactions API...")
                interaction = self.client.interactions.create(
                    model=self.model_name,
                    input=f"{EXTRACTION_SYSTEM_INSTRUCTION}\n\n{user_content}"
                )
                output_text = getattr(interaction, "output_text", str(interaction))
                return json.loads(output_text)
            raise e
