"""
Video analyzer using Google Gemini 2.0.

Comprehensive marketing intelligence extraction for trend analysis.
"""

import asyncio
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Any
import logging
import json

from google import genai
from google.genai import types

from config.settings import settings
from src.utils import safe_int, safe_float, dataclass_to_dict

logger = logging.getLogger(__name__)

# Load prompts from external files at module initialization
_PROMPTS_DIR = Path(__file__).parent.parent.parent / "config" / "prompts"
ANALYSIS_PROMPT = (_PROMPTS_DIR / "analysis.txt").read_text(encoding="utf-8")
EDUCATIONAL_ANALYSIS_PROMPT = (_PROMPTS_DIR / "educational.txt").read_text(encoding="utf-8")
COMBINED_ANALYSIS_PROMPT = (_PROMPTS_DIR / "combined.txt").read_text(encoding="utf-8")


@dataclass
class HookAnalysis:
    """Detailed hook/attention-grab analysis."""
    hook_type: str = ""  # question, statement, shock, visual, sound, text, action
    hook_text: str = ""  # Exact text if text-based hook
    hook_technique: str = ""  # open_loop, curiosity_gap, pattern_interrupt, controversy, transformation, etc.
    hook_timing_seconds: float = 0.0  # When the hook hits (0 = immediate)
    hook_strength: int = 0  # 1-10 score
    attention_retention_method: str = ""  # How they keep attention after hook


@dataclass
class AudioAnalysis:
    """Comprehensive audio/sound analysis."""
    sound_name: str = ""  # Identified song/sound name
    sound_artist: str = ""  # Artist if identifiable
    sound_category: str = ""  # trending_audio, original_audio, voiceover, dialogue, asmr, ambient
    is_trending_sound: bool = False
    sound_mood: str = ""  # energetic, chill, dramatic, comedic, emotional, etc.
    sound_tempo: str = ""  # fast, medium, slow
    voice_present: bool = False
    voice_type: str = ""  # creator_voice, ai_voice, other_person, multiple
    voice_tone: str = ""  # conversational, authoritative, excited, sarcastic, etc.
    speech_pace: str = ""  # fast, medium, slow
    sound_effects: list[str] = field(default_factory=list)  # whoosh, ding, bass_drop, etc.
    audio_editing: list[str] = field(default_factory=list)  # speed_change, reverb, echo, cuts


@dataclass
class VisualAnalysis:
    """Comprehensive visual analysis."""
    visual_style: str = ""  # aesthetic, raw, polished, cinematic, casual, etc.
    color_palette: list[str] = field(default_factory=list)  # dominant colors
    lighting_type: str = ""  # natural, studio, neon, moody, bright, etc.
    camera_type: str = ""  # selfie, pov, tripod, handheld, drone
    camera_movement: list[str] = field(default_factory=list)  # pan, zoom, static, tracking
    transition_types: list[str] = field(default_factory=list)  # cut, swipe, zoom, morph, etc.
    text_overlays: list[dict] = field(default_factory=list)  # [{text, style, position, timing}]
    visual_effects: list[str] = field(default_factory=list)  # green_screen, split_screen, duet, stitch, collab, filter, picture_in_picture, etc.
    editing_pace: str = ""  # fast_cuts, medium, slow, single_shot
    estimated_cuts_count: int = 0
    face_visibility: str = ""  # full_face, partial, no_face, multiple_people
    setting_type: str = ""  # home, business, outdoor, studio, car, etc.
    setting_details: str = ""  # specific location context
    thumbnail_elements: list[str] = field(default_factory=list)  # what makes first frame compelling
    b_roll_used: bool = False
    props_products: list[str] = field(default_factory=list)  # notable items shown


@dataclass
class ContentStructure:
    """Content format and structure analysis."""
    format_type: str = ""  # tutorial, storytime, day_in_life, transformation, reaction, duet, pov, skit, explainer, demo, walkthrough, commentary, vlog, shorts, etc.
    narrative_structure: str = ""  # linear, before_after, problem_solution, list, reveal, etc.
    pacing: str = ""  # fast, medium, slow, varied
    estimated_duration_seconds: int = 0
    scene_count: int = 0
    has_intro: bool = False
    has_outro: bool = False
    loop_friendly: bool = False  # Does it loop seamlessly
    cliffhanger_used: bool = False
    series_potential: bool = False  # Could this be a series


@dataclass
class EngagementMechanics:
    """Engagement triggers and tactics."""
    cta_type: str = ""  # follow, like, comment, share, save, link, none
    cta_placement: str = ""  # beginning, middle, end, throughout, none
    cta_text: str = ""  # Exact CTA if present
    comment_bait: list[str] = field(default_factory=list)  # techniques used (question, controversy, fill_blank, etc.)
    share_triggers: list[str] = field(default_factory=list)  # relatability, humor, useful_info, shocking, etc.
    save_triggers: list[str] = field(default_factory=list)  # tutorial, reference, inspiration, etc.
    engagement_hooks: list[str] = field(default_factory=list)  # specific techniques
    controversy_level: int = 0  # 0-10
    fomo_elements: list[str] = field(default_factory=list)
    social_proof_used: bool = False


@dataclass
class TrendSignals:
    """Trend identification and signals."""
    source_platform: str = ""  # tiktok, youtube_shorts, youtube
    is_trend_participation: bool = False
    trend_name: str = ""  # Name of trend if identifiable
    trend_category: str = ""  # dance, challenge, sound, format, meme, hashtag, tutorial_style
    trend_adaptation_quality: int = 0  # 1-10 how well they adapted the trend
    trend_lifecycle_stage: str = ""  # emerging, growing, peak, declining, dead
    format_originality: str = ""  # original, trend_adaptation, remix, copy
    viral_potential_score: int = 0  # 1-10
    viral_factors: list[str] = field(default_factory=list)  # what could make it go viral
    meme_potential: bool = False
    remix_potential: bool = False  # Could others duet/stitch/react to this


@dataclass
class EmotionalAnalysis:
    """Emotional content analysis."""
    primary_emotion: str = ""  # joy, surprise, anger, fear, sadness, disgust, anticipation, trust
    secondary_emotions: list[str] = field(default_factory=list)
    emotional_arc: str = ""  # flat, building, peak_early, rollercoaster, etc.
    humor_type: str = ""  # observational, self_deprecating, absurd, dark, physical, none
    relatability_score: int = 0  # 1-10
    relatability_factors: list[str] = field(default_factory=list)
    aspiration_score: int = 0  # 1-10 (does it make you want something)
    nostalgia_elements: list[str] = field(default_factory=list)
    controversy_elements: list[str] = field(default_factory=list)


@dataclass
class NicheAnalysis:
    """Topic and niche classification."""
    primary_niche: str = ""  # broad category
    sub_niches: list[str] = field(default_factory=list)  # specific subcategories
    topics: list[str] = field(default_factory=list)  # specific topics covered
    keywords: list[str] = field(default_factory=list)  # suggested hashtags/keywords
    target_demographics: list[str] = field(default_factory=list)  # age, gender, interests
    geographic_relevance: str = ""  # global, us, regional, local
    seasonal_relevance: str = ""  # evergreen, seasonal, timely, trending
    industry_verticals: list[str] = field(default_factory=list)  # hospitality, food, nightlife, etc.


@dataclass
class ProductionAnalysis:
    """Production quality assessment."""
    overall_quality: str = ""  # low, medium, high, professional
    equipment_tier: str = ""  # phone_basic, phone_good, prosumer, professional
    editing_complexity: str = ""  # minimal, moderate, complex, highly_produced
    audio_quality: str = ""  # poor, acceptable, good, excellent
    lighting_quality: str = ""  # poor, acceptable, good, excellent
    estimated_production_time: str = ""  # minutes, hours, days
    team_size_estimate: str = ""  # solo, small_team, production_crew


@dataclass
class ReplicabilityAnalysis:
    """How to replicate this content."""
    replicability_score: int = 0  # 1-10
    difficulty_level: str = ""  # easy, moderate, difficult, expert
    required_resources: list[str] = field(default_factory=list)  # camera, lighting, location, props, etc.
    required_skills: list[str] = field(default_factory=list)  # editing, acting, speaking, etc.
    time_investment: str = ""  # <1hr, 1-3hrs, 3-8hrs, 8+hrs
    budget_estimate: str = ""  # free, low, medium, high
    key_success_factors: list[str] = field(default_factory=list)
    common_mistakes_to_avoid: list[str] = field(default_factory=list)
    niche_adaptation_tips: list[str] = field(default_factory=list)  # how to adapt for hospitality/nightlife


@dataclass
class EducationalAnalysis:
    """Educational content quality metrics for B2B/technical content."""
    explanation_clarity: int = 0  # 1-10: How clearly concepts are explained
    demonstration_quality: int = 0  # 1-10: Quality of visual demos/walkthroughs
    technical_depth: int = 0  # 1-10: Level of technical detail
    practical_applicability: int = 0  # 1-10: Can viewers apply this immediately?
    educational_value: int = 0  # 1-10: Overall learning value
    career_relevance: int = 0  # 1-10: Career development value

    content_type: str = ""  # tutorial, demo, career_advice, tool_review, news, opinion, comparison
    teaching_technique: str = ""  # screen_share, live_coding, whiteboard, slides, talking_head, animation
    tools_mentioned: list[str] = field(default_factory=list)  # fabric, adf, power_bi, databricks, etc.
    concepts_covered: list[str] = field(default_factory=list)  # etl, data_modeling, medallion, orchestration
    skill_level_target: str = ""  # beginner, intermediate, advanced, expert
    credential_signals: list[str] = field(default_factory=list)  # mvp, mct, certified, senior_engineer


@dataclass
class DataEngineeringContext:
    """Data engineering specific context."""
    microsoft_stack: bool = False  # Uses Microsoft tools (Fabric, ADF, Power BI)
    cloud_platform: str = ""  # azure, aws, gcp, multi, on_prem
    data_layer: str = ""  # ingestion, transformation, serving, orchestration, governance
    architecture_pattern: str = ""  # medallion, lambda, kappa, data_mesh, traditional


@dataclass
class TechnicalSpecs:
    """Observable technical video specifications."""
    video_resolution: str = ""  # 480p|720p|1080p|4k
    aspect_ratio: str = ""  # 9:16|16:9|1:1|4:5|other
    has_captions: bool = False
    caption_style: str = ""  # burned_in|auto_generated|none
    audio_language: str = ""  # english|spanish|other|multilingual|none


@dataclass
class BrandSafety:
    """Brand safety and content classification."""
    brand_safety_score: int = 0  # 1-10: advertiser-friendly rating
    content_rating: str = ""  # all_ages|teen|mature|adult
    sponsorship_fit: list[str] = field(default_factory=list)  # brand categories that fit
    copyright_risk: str = ""  # low|medium|high


@dataclass
class VideoAnalysis:
    """Complete marketing intelligence for a video."""
    success: bool
    video_path: Optional[str] = None
    error: Optional[str] = None

    # Core description
    description: str = ""

    # Detailed analysis components
    hook: HookAnalysis = field(default_factory=HookAnalysis)
    audio: AudioAnalysis = field(default_factory=AudioAnalysis)
    visual: VisualAnalysis = field(default_factory=VisualAnalysis)
    structure: ContentStructure = field(default_factory=ContentStructure)
    engagement: EngagementMechanics = field(default_factory=EngagementMechanics)
    trends: TrendSignals = field(default_factory=TrendSignals)
    emotion: EmotionalAnalysis = field(default_factory=EmotionalAnalysis)
    niche: NicheAnalysis = field(default_factory=NicheAnalysis)
    production: ProductionAnalysis = field(default_factory=ProductionAnalysis)
    replicability: ReplicabilityAnalysis = field(default_factory=ReplicabilityAnalysis)

    # Educational/B2B analysis (for data_engineering niche mode)
    educational: EducationalAnalysis = field(default_factory=EducationalAnalysis)
    data_engineering: DataEngineeringContext = field(default_factory=DataEngineeringContext)

    # Technical specifications and brand safety
    technical: TechnicalSpecs = field(default_factory=TechnicalSpecs)
    brand_safety: BrandSafety = field(default_factory=BrandSafety)

    # Summary insights
    why_it_works: str = ""
    competitive_advantage: str = ""  # What makes this stand out
    improvement_opportunities: list[str] = field(default_factory=list)

    # Raw data
    raw_response: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary for storage."""
        return dataclass_to_dict(self)


class GeminiAnalyzer:
    """Analyze videos using Gemini for comprehensive marketing intelligence."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        niche_mode: Optional[str] = None
    ):
        self.api_key = api_key or settings.gemini_api_key
        self.model = model or settings.gemini_model
        self.niche_mode = niche_mode or settings.niche_mode

        if not self.api_key:
            raise ValueError(
                "Gemini API key required. Set GEMINI_API_KEY in .env"
            )

        self.client = genai.Client(api_key=self.api_key)
        logger.info(f"GeminiAnalyzer initialized with model: {self.model}, niche_mode: {self.niche_mode}")

    def _get_prompt(self) -> str:
        """Get the appropriate analysis prompt based on niche mode."""
        if self.niche_mode == "data_engineering":
            return EDUCATIONAL_ANALYSIS_PROMPT
        elif self.niche_mode == "both":
            return COMBINED_ANALYSIS_PROMPT
        return ANALYSIS_PROMPT

    def _validate_and_correct_scores(self, data: dict) -> dict:
        """Auto-correct scores that conflict with observable factors.

        Validates all three key scores against their supporting data:
        - hook_strength: validated against hook_type, technique, timing
        - viral_potential_score: validated against trends, engagement, relatability
        - replicability_score: validated against budget, difficulty, time
        """
        try:
            return self._do_validate_scores(data)
        except Exception as e:
            logger.warning(f"Score validation failed, using raw data: {e}")
            return data

    def _validate_hook_score(self, hook: dict) -> dict:
        """Validate and correct hook_strength based on observable factors.

        Rules:
        - No hook type: cap at 3
        - Strong techniques (open_loop, curiosity_gap, etc.): floor at 6
        - Late hooks (>3s): cap at 5
        - Text hook without text: cap at 4
        - Immediate hooks (<=1s) with technique: floor at 5
        """
        if not hook:
            return hook

        hook_type = hook.get("hook_type", "")
        hook_technique = hook.get("hook_technique", "")
        hook_timing = safe_float(hook.get("hook_timing_seconds", 0), 0.0)
        hook_text = hook.get("hook_text", "")
        score = safe_int(hook.get("hook_strength", 5), 5)
        original = score

        # No hook type = weak hook (cap at 3)
        if not hook_type or hook_type.lower() in ["none", ""]:
            score = min(score, 3)

        # Strong techniques deserve minimum scores (floor at 6)
        strong_techniques = ["open_loop", "curiosity_gap", "pattern_interrupt", "controversy"]
        if hook_technique.lower() in strong_techniques and score < 6:
            score = max(score, 6)

        # Late hooks are weaker - if hook hits after 3s, cap at 5
        if hook_timing > 3.0 and score > 5:
            score = min(score, 5)

        # Text hook without text is suspicious - cap at 4
        if hook_type.lower() == "text" and not hook_text and score > 4:
            score = min(score, 4)

        # Immediate hooks (0-1s) with good technique get floor of 5
        if hook_timing <= 1.0 and hook_technique and score < 5:
            score = max(score, 5)

        if score != original:
            logger.debug(f"Auto-corrected hook_strength: {original} -> {score}")
            hook["hook_strength"] = score

        return hook

    def _validate_viral_score(
        self,
        trends: dict,
        engagement: dict,
        emotion: dict,
    ) -> dict:
        """Validate and correct viral_potential_score based on observable factors.

        Rules:
        - Declining/dead trends: cap at 5
        - Peak/growing trends: floor at 5
        - Meme + remix potential: floor at 6
        - Direct copies: cap at 4
        - 4+ viral factors: floor at 5
        - 3+ share triggers: floor at 5
        - Viral shouldn't exceed relatability by more than 3
        """
        if not trends:
            return trends

        viral_score = safe_int(trends.get("viral_potential_score", 5), 5)
        original = viral_score

        lifecycle = trends.get("trend_lifecycle_stage", "").lower()
        meme_potential = trends.get("meme_potential", False)
        remix_potential = trends.get("remix_potential", False)
        originality = trends.get("format_originality", "").lower()
        viral_factors = trends.get("viral_factors", [])

        # Dying trends cap viral potential at 5
        if lifecycle in ["declining", "dead"] and viral_score > 5:
            viral_score = min(viral_score, 5)

        # Peak trends get floor of 5
        if lifecycle in ["peak", "growing"] and viral_score < 5:
            viral_score = max(viral_score, 5)

        # Meme + remix potential = high viral floor (6)
        if meme_potential and remix_potential and viral_score < 6:
            viral_score = max(viral_score, 6)

        # Direct copies have limited viral potential (cap at 4)
        if originality == "copy" and viral_score > 4:
            viral_score = min(viral_score, 4)

        # Many viral factors = should have decent score (floor at 5)
        if len(viral_factors) >= 4 and viral_score < 5:
            viral_score = max(viral_score, 5)

        # Cross-check with engagement share triggers
        if engagement:
            share_triggers = engagement.get("share_triggers", [])
            if len(share_triggers) >= 3 and viral_score < 5:
                viral_score = max(viral_score, 5)

        # Cross-check with relatability - viral shouldn't exceed relatability by 4+
        if emotion:
            relatability = safe_int(emotion.get("relatability_score", 5), 5)
            if viral_score > relatability + 3:
                viral_score = min(viral_score, relatability + 3)

        if viral_score != original:
            logger.debug(f"Auto-corrected viral_potential: {original} -> {viral_score}")
            trends["viral_potential_score"] = viral_score

        return trends

    def _validate_replicability_score(self, replicability: dict) -> dict:
        """Validate and correct replicability_score based on observable factors.

        Rules:
        - High budget: cap at 4
        - Free budget: floor at 7
        - Low budget: floor at 6
        - Expert difficulty: cap at 3
        - Difficult: cap at 5
        - Easy: floor at 7
        - Moderate: cap at 7
        - 8+ hours: cap at 4
        - 3-8 hours: cap at 6
        - Under 1 hour: floor at 7
        """
        if not replicability:
            return replicability

        budget = str(replicability.get("budget_estimate", "")).lower()
        difficulty = str(replicability.get("difficulty_level", "")).lower()
        time_inv = str(replicability.get("time_investment", "")).lower()
        score = safe_int(replicability.get("replicability_score", 5), 5)
        original = score

        # Budget constraints
        if budget in ["high", "over_200", "over 200"] and score > 4:
            score = min(score, 4)
        elif budget == "free" and score < 7:
            score = max(score, 7)
        elif budget == "low" and score < 6:
            score = max(score, 6)

        # Difficulty constraints
        if difficulty == "expert" and score > 3:
            score = min(score, 3)
        elif difficulty == "difficult" and score > 5:
            score = min(score, 5)
        elif difficulty == "easy" and score < 7:
            score = max(score, 7)
        elif difficulty == "moderate" and score > 7:
            score = min(score, 7)

        # Time constraints
        if time_inv in ["over_8hrs", "8+hrs", ">8hrs"] and score > 4:
            score = min(score, 4)
        elif time_inv in ["3-8hrs", "3_8hrs"] and score > 6:
            score = min(score, 6)
        elif time_inv in ["under_1hr", "<1hr", "under 1hr"] and score < 7:
            score = max(score, 7)

        if score != original:
            logger.debug(f"Auto-corrected replicability: {original} -> {score}")
            replicability["replicability_score"] = score

        return replicability

    def _do_validate_scores(self, data: dict) -> dict:
        """Internal score validation logic.

        Validates all three key scores against their supporting data:
        - hook_strength: validated against hook_type, technique, timing
        - viral_potential_score: validated against trends, engagement, relatability
        - replicability_score: validated against budget, difficulty, time
        """
        hook = data.get("hook", {})
        if hook:
            data["hook"] = self._validate_hook_score(hook)

        trends = data.get("trends", {})
        if trends:
            engagement = data.get("engagement", {})
            emotion = data.get("emotion", {})
            data["trends"] = self._validate_viral_score(trends, engagement, emotion)

        replicability = data.get("replicability", {})
        if replicability:
            data["replicability"] = self._validate_replicability_score(replicability)

        return data

    def _parse_nested_dataclass(self, data: dict, key: str, dataclass_type: type) -> Any:
        """Parse nested dictionary into dataclass with type coercion."""
        nested_data = data.get(key, {})
        if not isinstance(nested_data, dict):
            return dataclass_type()

        field_values = {}
        for field_name, field_info in dataclass_type.__dataclass_fields__.items():
            if field_name in nested_data:
                value = nested_data[field_name]
                field_type = field_info.type

                # Coerce types for common mismatches
                if field_type == int or field_type == 'int':
                    value = safe_int(value, 0)
                elif field_type == float or field_type == 'float':
                    value = safe_float(value, 0.0)
                elif field_type == bool or field_type == 'bool':
                    if isinstance(value, str):
                        value = value.lower() in ('true', '1', 'yes')
                    else:
                        value = bool(value) if value is not None else False

                field_values[field_name] = value

        try:
            return dataclass_type(**field_values)
        except Exception as e:
            logger.warning(f"Failed to parse {key}: {e}")
            return dataclass_type()

    async def analyze_video(
        self,
        video_path: Path,
        custom_prompt: Optional[str] = None,
    ) -> VideoAnalysis:
        """
        Analyze a video file with comprehensive marketing intelligence extraction.

        Args:
            video_path: Path to video file
            custom_prompt: Optional custom prompt (uses default if not provided)

        Returns:
            VideoAnalysis with comprehensive marketing intelligence
        """
        if not video_path.exists():
            return VideoAnalysis(
                success=False,
                video_path=str(video_path),
                error=f"Video file not found: {video_path}",
            )

        file_size_mb = video_path.stat().st_size / 1024 / 1024
        if file_size_mb > 100:
            return VideoAnalysis(
                success=False,
                video_path=str(video_path),
                error=f"Video too large: {file_size_mb:.1f}MB (max 100MB)",
            )

        try:
            logger.info(f"Analyzing video: {video_path.name}")

            prompt = custom_prompt or self._get_prompt()

            loop = asyncio.get_event_loop()

            def do_analysis():
                video_file = self.client.files.upload(file=video_path)
                logger.info(f"Uploaded file: {video_file.name}, state: {video_file.state}")

                max_wait = 120
                wait_interval = 3
                waited = 0
                while video_file.state.name != "ACTIVE" and waited < max_wait:
                    logger.info(f"Waiting for file to process... ({waited}s)")
                    time.sleep(wait_interval)
                    waited += wait_interval
                    video_file = self.client.files.get(name=video_file.name)

                if video_file.state.name != "ACTIVE":
                    raise RuntimeError(f"File did not become ACTIVE after {max_wait}s. State: {video_file.state.name}")

                logger.info(f"File ready: {video_file.name}")

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

                try:
                    self.client.files.delete(name=video_file.name)
                except Exception:
                    pass

                return response.text

            response_text = await loop.run_in_executor(None, do_analysis)

            # Clean up JSON
            response_text = response_text.strip()
            if response_text.startswith("```"):
                lines = response_text.split("\n")
                response_text = "\n".join(lines[1:-1])

            try:
                data = json.loads(response_text)
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse JSON response: {e}")
                return VideoAnalysis(
                    success=True,
                    video_path=str(video_path),
                    description=response_text[:500],
                    raw_response=response_text,
                )

            # Validate and auto-correct scores
            data = self._validate_and_correct_scores(data)

            logger.info(f"Analysis complete: {video_path.name}")

            # Build comprehensive analysis
            return VideoAnalysis(
                success=True,
                video_path=str(video_path),
                description=data.get("description", ""),
                hook=self._parse_nested_dataclass(data, "hook", HookAnalysis),
                audio=self._parse_nested_dataclass(data, "audio", AudioAnalysis),
                visual=self._parse_nested_dataclass(data, "visual", VisualAnalysis),
                structure=self._parse_nested_dataclass(data, "structure", ContentStructure),
                engagement=self._parse_nested_dataclass(data, "engagement", EngagementMechanics),
                trends=self._parse_nested_dataclass(data, "trends", TrendSignals),
                emotion=self._parse_nested_dataclass(data, "emotion", EmotionalAnalysis),
                niche=self._parse_nested_dataclass(data, "niche", NicheAnalysis),
                production=self._parse_nested_dataclass(data, "production", ProductionAnalysis),
                replicability=self._parse_nested_dataclass(data, "replicability", ReplicabilityAnalysis),
                educational=self._parse_nested_dataclass(data, "educational", EducationalAnalysis),
                data_engineering=self._parse_nested_dataclass(data, "data_engineering", DataEngineeringContext),
                technical=self._parse_nested_dataclass(data, "technical", TechnicalSpecs),
                brand_safety=self._parse_nested_dataclass(data, "brand_safety", BrandSafety),
                why_it_works=data.get("why_it_works", ""),
                competitive_advantage=data.get("competitive_advantage", ""),
                improvement_opportunities=data.get("improvement_opportunities", []),
                raw_response=response_text,
            )

        except Exception as e:
            error_str = str(e)

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
        max_concurrent: int = 2,
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
                await asyncio.sleep(3)  # Rate limit buffer
                return result

        tasks = [analyze_with_semaphore(path) for path in video_paths]
        return await asyncio.gather(*tasks)
