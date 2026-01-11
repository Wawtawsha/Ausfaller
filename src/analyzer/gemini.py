"""
Video analyzer using Google Gemini 2.0.

Analyzes video content including visual elements, audio, and text.
"""

import asyncio
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
import logging
import json

from google import genai
from google.genai import types

from config.settings import settings

logger = logging.getLogger(__name__)


@dataclass
class VideoAnalysis:
    """Analysis result for a video."""
    success: bool
    video_path: Optional[str] = None
    error: Optional[str] = None

    # Content analysis
    description: str = ""
    visual_elements: list[str] = field(default_factory=list)
    text_overlays: list[str] = field(default_factory=list)
    audio_description: str = ""
    music_or_sound: Optional[str] = None

    # Marketing analysis
    tone: str = ""  # funny, educational, emotional, etc.
    hook: str = ""  # What grabs attention in first 3 seconds
    call_to_action: Optional[str] = None
    target_audience: str = ""
    content_category: str = ""  # food, nightlife, tutorial, etc.

    # Recommendations
    why_it_works: str = ""
    replicability_score: int = 0  # 1-10
    replication_tips: list[str] = field(default_factory=list)

    # Raw response for debugging
    raw_response: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "video_path": self.video_path,
            "error": self.error,
            "description": self.description,
            "visual_elements": self.visual_elements,
            "text_overlays": self.text_overlays,
            "audio_description": self.audio_description,
            "music_or_sound": self.music_or_sound,
            "tone": self.tone,
            "hook": self.hook,
            "call_to_action": self.call_to_action,
            "target_audience": self.target_audience,
            "content_category": self.content_category,
            "why_it_works": self.why_it_works,
            "replicability_score": self.replicability_score,
            "replication_tips": self.replication_tips,
        }


# Analysis prompt template
ANALYSIS_PROMPT = """Analyze this short-form video for social media marketing insights.

Provide your analysis as a JSON object with the following structure:
{
    "description": "Brief description of what happens in the video",
    "visual_elements": ["list", "of", "notable", "visual", "elements"],
    "text_overlays": ["any", "text", "shown", "on", "screen"],
    "audio_description": "Description of audio/speech content",
    "music_or_sound": "Name of song/sound if identifiable, or description",
    "tone": "The overall tone (funny, educational, emotional, inspiring, edgy, etc.)",
    "hook": "What grabs attention in the first 3 seconds",
    "call_to_action": "Any call to action present, or null",
    "target_audience": "Who this content appeals to",
    "content_category": "Category (food, nightlife, tutorial, lifestyle, etc.)",
    "why_it_works": "Brief explanation of why this video is engaging",
    "replicability_score": 7,
    "replication_tips": ["tip1", "tip2", "tip3"]
}

Focus on actionable insights for someone wanting to create similar content for restaurant/bar/nightlife promotion.

Respond ONLY with the JSON object, no other text."""


class GeminiAnalyzer:
    """Analyze videos using Gemini 2.0 Flash."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.gemini_api_key
        self.model = model or settings.gemini_model

        if not self.api_key:
            raise ValueError(
                "Gemini API key required. Set GEMINI_API_KEY in .env"
            )

        # Initialize the client
        self.client = genai.Client(api_key=self.api_key)
        logger.info(f"GeminiAnalyzer initialized with model: {self.model}")

    async def analyze_video(
        self,
        video_path: Path,
        custom_prompt: Optional[str] = None,
    ) -> VideoAnalysis:
        """
        Analyze a video file.

        Args:
            video_path: Path to video file
            custom_prompt: Optional custom prompt (uses default if not provided)

        Returns:
            VideoAnalysis with content and marketing insights
        """
        if not video_path.exists():
            return VideoAnalysis(
                success=False,
                video_path=str(video_path),
                error=f"Video file not found: {video_path}",
            )

        # Check file size (Gemini has limits)
        file_size_mb = video_path.stat().st_size / 1024 / 1024
        if file_size_mb > 100:
            return VideoAnalysis(
                success=False,
                video_path=str(video_path),
                error=f"Video too large: {file_size_mb:.1f}MB (max 100MB)",
            )

        try:
            logger.info(f"Analyzing video: {video_path.name}")

            prompt = custom_prompt or ANALYSIS_PROMPT

            # Upload and analyze video
            loop = asyncio.get_event_loop()

            def do_analysis():
                # Upload file
                video_file = self.client.files.upload(file=video_path)
                logger.info(f"Uploaded file: {video_file.name}, state: {video_file.state}")

                # Wait for file to become ACTIVE (processing can take a few seconds)
                max_wait = 60  # seconds
                wait_interval = 2
                waited = 0
                while video_file.state.name != "ACTIVE" and waited < max_wait:
                    logger.info(f"Waiting for file to process... ({waited}s)")
                    time.sleep(wait_interval)
                    waited += wait_interval
                    video_file = self.client.files.get(name=video_file.name)

                if video_file.state.name != "ACTIVE":
                    raise RuntimeError(f"File did not become ACTIVE after {max_wait}s. State: {video_file.state.name}")

                logger.info(f"File ready: {video_file.name}")

                # Generate content
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=[
                        types.Content(
                            role="user",
                            parts=[
                                types.Part.from_uri(
                                    file_uri=video_file.uri,
                                    mime_type=video_file.mime_type,
                                ),
                                types.Part.from_text(text=prompt),
                            ],
                        ),
                    ],
                )

                # Cleanup uploaded file
                try:
                    self.client.files.delete(name=video_file.name)
                except Exception:
                    pass

                return response.text

            response_text = await loop.run_in_executor(None, do_analysis)

            # Clean up JSON (remove markdown code blocks if present)
            response_text = response_text.strip()
            if response_text.startswith("```"):
                lines = response_text.split("\n")
                # Remove first and last lines (```json and ```)
                response_text = "\n".join(lines[1:-1])

            try:
                data = json.loads(response_text)
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse JSON response: {e}")
                return VideoAnalysis(
                    success=True,  # Analysis succeeded, just parsing failed
                    video_path=str(video_path),
                    description=response_text[:500],
                    raw_response=response_text,
                )

            logger.info(f"Analysis complete: {video_path.name}")

            return VideoAnalysis(
                success=True,
                video_path=str(video_path),
                description=data.get("description", ""),
                visual_elements=data.get("visual_elements", []),
                text_overlays=data.get("text_overlays", []),
                audio_description=data.get("audio_description", ""),
                music_or_sound=data.get("music_or_sound"),
                tone=data.get("tone", ""),
                hook=data.get("hook", ""),
                call_to_action=data.get("call_to_action"),
                target_audience=data.get("target_audience", ""),
                content_category=data.get("content_category", ""),
                why_it_works=data.get("why_it_works", ""),
                replicability_score=data.get("replicability_score", 0),
                replication_tips=data.get("replication_tips", []),
                raw_response=response_text,
            )

        except Exception as e:
            error_str = str(e)

            # Provide helpful guidance for quota errors
            if "RESOURCE_EXHAUSTED" in error_str or "429" in error_str:
                if "limit: 0" in error_str:
                    logger.error(
                        "Gemini API quota is 0. Your API key doesn't have billing enabled. "
                        "Go to https://console.cloud.google.com to enable billing, or "
                        "create a new API key at https://aistudio.google.com/apikey"
                    )
                else:
                    logger.error(f"Gemini rate limit hit. Try again in a few seconds.")
            else:
                logger.error(f"Gemini analysis failed: {e}")

            return VideoAnalysis(
                success=False,
                video_path=str(video_path),
                error=error_str,
            )

    async def analyze_batch(
        self,
        video_paths: list[Path],
        max_concurrent: int = 2,  # Gemini has rate limits
    ) -> list[VideoAnalysis]:
        """
        Analyze multiple videos.

        Args:
            video_paths: List of video file paths
            max_concurrent: Max concurrent analyses

        Returns:
            List of VideoAnalysis results
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def analyze_with_semaphore(path: Path) -> VideoAnalysis:
            async with semaphore:
                result = await self.analyze_video(path)
                # Add delay between analyses to avoid rate limits
                await asyncio.sleep(2)
                return result

        tasks = [analyze_with_semaphore(path) for path in video_paths]
        return await asyncio.gather(*tasks)
