"""
Hashtag generator using Google Gemini.

Converts niche descriptions into relevant, searchable hashtags.
"""

import asyncio
import logging
from dataclasses import dataclass
from typing import Optional

from google import genai
from google.genai import types

from config.settings import settings

logger = logging.getLogger(__name__)


HASHTAG_PROMPT = """You are a social media marketing expert specializing in TikTok and Instagram content discovery.

Given a niche description, generate a list of relevant hashtags that creators in this space actively use.

Niche: {niche_description}
Platform: {platform}

Requirements:
1. Generate exactly {count} hashtags
2. Mix popular (high-volume) hashtags with niche (targeted) ones
3. Include variations: singular/plural, abbreviations, related terms
4. Focus on hashtags that have VIDEO content, not just photos
5. Avoid overly generic hashtags like #fyp, #viral, #trending, #foryou
6. Include industry-specific jargon and slang
7. Consider what creators in this niche would actually tag their content with

Return ONLY the hashtags, one per line, WITHOUT the # symbol.
No explanations, no numbering, just the hashtag text.

Example output for "cocktail bartending":
bartender
mixology
cocktails
barlife
craftcocktails
bartenderlife
homebar
drinkstagram
cocktailsofinstagram
bartending"""


@dataclass
class HashtagGenerationResult:
    """Result of hashtag generation."""
    success: bool
    hashtags: list[str]
    niche_description: str
    platform: str
    error: Optional[str] = None


class HashtagGenerator:
    """Generate relevant hashtags from niche descriptions using Gemini."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.gemini_api_key
        self.model = model or "gemini-2.0-flash-lite"  # Use lite model for fast text generation

        if not self.api_key:
            raise ValueError(
                "Gemini API key required. Set GEMINI_API_KEY in .env"
            )

        self.client = genai.Client(api_key=self.api_key)
        logger.info(f"HashtagGenerator initialized with model: {self.model}")

    async def generate_hashtags(
        self,
        niche_description: str,
        platform: str = "tiktok",
        count: int = 10,
    ) -> HashtagGenerationResult:
        """
        Generate hashtags from a niche description.

        Args:
            niche_description: Description of the content niche (e.g., "cocktail bartending content")
            platform: Target platform (tiktok or instagram)
            count: Number of hashtags to generate

        Returns:
            HashtagGenerationResult with list of hashtags
        """
        try:
            logger.info(f"Generating {count} hashtags for: {niche_description}")

            prompt = HASHTAG_PROMPT.format(
                niche_description=niche_description,
                platform=platform,
                count=count,
            )

            loop = asyncio.get_event_loop()

            def do_generation():
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=[
                        types.Content(
                            role="user",
                            parts=[types.Part.from_text(text=prompt)],
                        )
                    ],
                    config=types.GenerateContentConfig(
                        temperature=0.7,  # Some creativity but not too random
                        max_output_tokens=500,
                    ),
                )
                return response.text

            response_text = await loop.run_in_executor(None, do_generation)

            # Parse response - one hashtag per line
            hashtags = self._parse_hashtags(response_text, count)

            logger.info(f"Generated {len(hashtags)} hashtags: {hashtags[:5]}...")

            return HashtagGenerationResult(
                success=True,
                hashtags=hashtags,
                niche_description=niche_description,
                platform=platform,
            )

        except Exception as e:
            logger.error(f"Hashtag generation failed: {e}")
            return HashtagGenerationResult(
                success=False,
                hashtags=[],
                niche_description=niche_description,
                platform=platform,
                error=str(e),
            )

    def _parse_hashtags(self, response_text: str, expected_count: int) -> list[str]:
        """Parse and clean hashtags from Gemini response."""
        lines = response_text.strip().split('\n')
        hashtags = []

        for line in lines:
            # Clean up the line
            tag = line.strip().lower()

            # Remove # if present
            if tag.startswith('#'):
                tag = tag[1:]

            # Remove numbering like "1." or "1)"
            if tag and tag[0].isdigit():
                parts = tag.split('.', 1)
                if len(parts) > 1:
                    tag = parts[1].strip()
                else:
                    parts = tag.split(')', 1)
                    if len(parts) > 1:
                        tag = parts[1].strip()

            # Skip empty, too short, or generic tags
            if not tag or len(tag) < 2:
                continue
            if tag in {'fyp', 'viral', 'trending', 'foryou', 'foryoupage'}:
                continue

            # Remove any remaining special characters except underscores
            tag = ''.join(c for c in tag if c.isalnum() or c == '_')

            if tag and tag not in hashtags:
                hashtags.append(tag)

        # Return up to expected count
        return hashtags[:expected_count]


# Module-level singleton
_generator: Optional[HashtagGenerator] = None


def get_hashtag_generator() -> HashtagGenerator:
    """Get or create the hashtag generator singleton."""
    global _generator
    if _generator is None:
        _generator = HashtagGenerator()
    return _generator
