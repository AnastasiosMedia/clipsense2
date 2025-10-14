import base64
import os
from typing import Dict, Any, Optional

try:
    from .config import Config
except ImportError:
    from config import Config

try:
    from openai import OpenAI
except Exception:
    OpenAI = None  # type: ignore


class OpenAIVisionClient:
    """Thin wrapper around OpenAI Vision to classify thumbnail images."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.enabled = Config.USE_OPENAI_VISION and (api_key or Config.OPENAI_API_KEY)
        self.api_key = api_key or Config.OPENAI_API_KEY
        self.model = model or Config.OPENAI_VISION_MODEL
        self._client = None
        if self.enabled and OpenAI is not None:
            try:
                self._client = OpenAI(api_key=self.api_key)
            except Exception as e:
                print(f"WARNING:openai_vision:Failed to initialize OpenAI client: {e}")
                self.enabled = False
        elif self.enabled and OpenAI is None:
            print("WARNING:openai_vision:openai package not available; disabling vision.")
            self.enabled = False

    def analyze_thumbnail(self, image_path: str) -> Dict[str, Any]:
        """
        Send a single thumbnail to OpenAI Vision and return structured hints.
        Returns empty dict if disabled or any error occurs.
        """
        if not self.enabled or not self._client:
            return {}

        if not os.path.exists(image_path):
            return {}

        try:
            with open(image_path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode("utf-8")

            prompt = (
                "You are classifying a single wedding video frame. "
                "Return a compact JSON with keys: scene (one of ceremony, reception, party, preparation, intimate_moments, scenic_moments), "
                "subjects (array of strings like bride, groom, guests, rings, bouquet, cake, dance, toast), "
                "actions (array), emotion (one of romantic, joyful, intimate, celebratory, neutral), and confidence (0-1). "
                "Keep it concise, valid JSON only."
            )

            resp = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{b64}",
                                },
                            },
                        ],
                    }
                ],
                temperature=0.2,
                max_tokens=300,
            )

            text = resp.choices[0].message.content if resp and resp.choices else "{}"
            # Best-effort parse (strip code fences if present)
            import re, json
            cleaned = text.strip()
            if cleaned.startswith("```"):
                cleaned = re.sub(r"^```[a-zA-Z]*\n", "", cleaned)
                if cleaned.endswith("```"):
                    cleaned = cleaned[:-3]
            cleaned = cleaned.strip()
            try:
                data = json.loads(cleaned)
                if isinstance(data, dict):
                    return data
            except Exception:
                pass
            return {"raw": text}
        except Exception as e:
            print(f"WARNING:openai_vision:Vision analysis failed: {e}")
            return {}

    def generate_clip_description(self, image_path: str) -> str:
        """
        Generate a 1-2 sentence descriptive analysis of a wedding video clip based on the first frame.
        Returns a human-readable description of what's happening in the clip.
        """
        if not self.enabled or not self._client:
            return "AI analysis not available"

        if not os.path.exists(image_path):
            return "Image not found"

        try:
            with open(image_path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode("utf-8")

            prompt = (
                "You are analyzing a wedding video frame to create a simple, clear description. "
                "Write 1-2 sentences that describe what's happening in this moment of the wedding. "
                "Be direct and factual - describe the people, actions, and setting without flowery language. "
                "Examples: 'The groom and groomsmen are getting ready in the dressing room, adjusting ties and cufflinks.' "
                "or 'The bride and groom are cutting the wedding cake while guests watch and take photos.' "
                "or 'Guests are dancing on the dance floor during the reception.' "
                "Keep it simple and straightforward."
            )

            resp = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{b64}",
                                },
                            },
                        ],
                    }
                ],
                temperature=0.3,
                max_tokens=150,
            )

            description = resp.choices[0].message.content if resp and resp.choices else "Unable to analyze this clip"
            return description.strip()
        except Exception as e:
            print(f"WARNING:openai_vision:Description generation failed: {e}")
            return "AI analysis unavailable"


