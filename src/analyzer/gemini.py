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

logger = logging.getLogger(__name__)


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
    visual_effects: list[str] = field(default_factory=list)  # green_screen, split_screen, duet, filter, etc.
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
    format_type: str = ""  # tutorial, storytime, day_in_life, transformation, reaction, duet, pov, skit, etc.
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
    is_trend_participation: bool = False
    trend_name: str = ""  # Name of trend if identifiable
    trend_category: str = ""  # dance, challenge, sound, format, meme, hashtag
    trend_adaptation_quality: int = 0  # 1-10 how well they adapted the trend
    trend_lifecycle_stage: str = ""  # emerging, growing, peak, declining, dead
    format_originality: str = ""  # original, trend_adaptation, remix, copy
    viral_potential_score: int = 0  # 1-10
    viral_factors: list[str] = field(default_factory=list)  # what could make it go viral
    meme_potential: bool = False
    remix_potential: bool = False  # Could others duet/stitch this


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

    # Summary insights
    why_it_works: str = ""
    competitive_advantage: str = ""  # What makes this stand out
    improvement_opportunities: list[str] = field(default_factory=list)

    # Raw data
    raw_response: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary for storage."""
        def dataclass_to_dict(obj):
            if hasattr(obj, '__dataclass_fields__'):
                return {k: dataclass_to_dict(v) for k, v in obj.__dict__.items()}
            elif isinstance(obj, list):
                return [dataclass_to_dict(i) for i in obj]
            elif isinstance(obj, dict):
                return {k: dataclass_to_dict(v) for k, v in obj.items()}
            else:
                return obj

        return dataclass_to_dict(self)


# Comprehensive analysis prompt
ANALYSIS_PROMPT = """You are an elite social media marketing analyst specializing in short-form video content. Analyze this video with extreme precision and extract every possible marketing insight.

Your analysis must be exhaustive and systematic. Extract data that can be used for trend analysis and pattern recognition across thousands of videos.

Respond with a JSON object matching this EXACT structure:

{
    "description": "Detailed description of video content, narrative, and key moments",

    "hook": {
        "hook_type": "question|statement|shock|visual|sound|text|action",
        "hook_text": "exact text if text-based hook, empty string if not",
        "hook_technique": "open_loop|curiosity_gap|pattern_interrupt|controversy|transformation|challenge|relatable_pain|bold_claim|weird_flex|confession",
        "hook_timing_seconds": 0.0,
        "hook_strength": 8,
        "attention_retention_method": "how they maintain interest after hook"
    },

    "audio": {
        "sound_name": "song or sound name if identifiable",
        "sound_artist": "artist name if known",
        "sound_category": "trending_audio|original_audio|voiceover|dialogue|asmr|ambient|music_only",
        "is_trending_sound": true,
        "sound_mood": "energetic|chill|dramatic|comedic|emotional|suspenseful|upbeat|melancholic",
        "sound_tempo": "fast|medium|slow",
        "voice_present": true,
        "voice_type": "creator_voice|ai_voice|other_person|multiple|narrator",
        "voice_tone": "conversational|authoritative|excited|sarcastic|deadpan|whispering|yelling",
        "speech_pace": "fast|medium|slow",
        "sound_effects": ["whoosh", "ding", "bass_drop", "record_scratch", "laugh_track"],
        "audio_editing": ["speed_change", "reverb", "cuts", "layering"]
    },

    "visual": {
        "visual_style": "aesthetic|raw|polished|cinematic|casual|chaotic|minimalist|maximalist",
        "color_palette": ["warm", "neon", "muted", "high_contrast"],
        "lighting_type": "natural|studio|neon|moody|bright|golden_hour|ring_light",
        "camera_type": "selfie|pov|tripod|handheld|drone|screen_record",
        "camera_movement": ["static", "pan", "zoom", "tracking", "whip_pan"],
        "transition_types": ["cut", "swipe", "zoom", "morph", "flash", "match_cut"],
        "text_overlays": [
            {"text": "actual text shown", "style": "bold|caption|subtitle|meme", "position": "center|top|bottom", "timing": "throughout|intro|key_moment"}
        ],
        "visual_effects": ["green_screen", "split_screen", "duet", "stitch", "filter", "slow_mo", "time_lapse"],
        "editing_pace": "fast_cuts|medium|slow|single_shot",
        "estimated_cuts_count": 10,
        "face_visibility": "full_face|partial|no_face|multiple_people",
        "setting_type": "home|business|outdoor|studio|car|restaurant|bar|club|kitchen",
        "setting_details": "specific context about location",
        "thumbnail_elements": ["face", "text", "bright_colors", "action"],
        "b_roll_used": true,
        "props_products": ["items", "products", "tools shown"]
    },

    "structure": {
        "format_type": "tutorial|storytime|day_in_life|transformation|reaction|duet|pov|skit|rant|review|asmr|challenge|trend|educational|behind_scenes|get_ready|what_i_eat",
        "narrative_structure": "linear|before_after|problem_solution|list|reveal|journey|comparison|q_and_a",
        "pacing": "fast|medium|slow|varied",
        "estimated_duration_seconds": 30,
        "scene_count": 5,
        "has_intro": false,
        "has_outro": true,
        "loop_friendly": true,
        "cliffhanger_used": false,
        "series_potential": true
    },

    "engagement": {
        "cta_type": "follow|like|comment|share|save|link|subscribe|none",
        "cta_placement": "beginning|middle|end|throughout|none",
        "cta_text": "exact call to action text",
        "comment_bait": ["question", "controversy", "fill_in_blank", "opinion_request", "debate"],
        "share_triggers": ["relatability", "humor", "useful_info", "shocking", "emotional", "outrage"],
        "save_triggers": ["tutorial", "reference", "inspiration", "recipe", "tips"],
        "engagement_hooks": ["specific techniques used"],
        "controversy_level": 3,
        "fomo_elements": ["limited_time", "exclusive", "trend_joining"],
        "social_proof_used": false
    },

    "trends": {
        "is_trend_participation": true,
        "trend_name": "name of trend if applicable",
        "trend_category": "dance|challenge|sound|format|meme|hashtag|filter",
        "trend_adaptation_quality": 8,
        "trend_lifecycle_stage": "emerging|growing|peak|declining|evergreen",
        "format_originality": "original|trend_adaptation|remix|copy",
        "viral_potential_score": 7,
        "viral_factors": ["relatability", "shareability", "trend_timing", "hook_strength"],
        "meme_potential": true,
        "remix_potential": true
    },

    "emotion": {
        "primary_emotion": "joy|surprise|anger|fear|sadness|disgust|anticipation|trust|amusement|inspiration",
        "secondary_emotions": ["curiosity", "nostalgia"],
        "emotional_arc": "flat|building|peak_early|peak_late|rollercoaster|release",
        "humor_type": "observational|self_deprecating|absurd|dark|physical|situational|none",
        "relatability_score": 8,
        "relatability_factors": ["shared experience", "common struggle", "universal truth"],
        "aspiration_score": 6,
        "nostalgia_elements": ["90s reference", "childhood memory"],
        "controversy_elements": ["hot take", "unpopular opinion"]
    },

    "niche": {
        "primary_niche": "broad category like food, lifestyle, comedy",
        "sub_niches": ["bartending", "cocktails", "nightlife"],
        "topics": ["specific topics covered in video"],
        "keywords": ["suggested", "hashtags", "and", "keywords"],
        "target_demographics": ["age_18_24", "age_25_34", "female", "urban", "nightlife_enthusiasts"],
        "geographic_relevance": "global|us|regional|local",
        "seasonal_relevance": "evergreen|seasonal|holiday|trending|timely",
        "industry_verticals": ["hospitality", "food_beverage", "nightlife", "entertainment"]
    },

    "production": {
        "overall_quality": "low|medium|high|professional",
        "equipment_tier": "phone_basic|phone_good|prosumer|professional",
        "editing_complexity": "minimal|moderate|complex|highly_produced",
        "audio_quality": "poor|acceptable|good|excellent",
        "lighting_quality": "poor|acceptable|good|excellent",
        "estimated_production_time": "under_1hr|1_to_3hrs|3_to_8hrs|over_8hrs",
        "team_size_estimate": "solo|duo|small_team|production_crew"
    },

    "replicability": {
        "replicability_score": 7,
        "difficulty_level": "easy|moderate|difficult|expert",
        "required_resources": ["smartphone", "ring_light", "tripod"],
        "required_skills": ["basic_editing", "on_camera_presence", "timing"],
        "time_investment": "under_1hr|1_to_3hrs|3_to_8hrs|over_8hrs",
        "budget_estimate": "free|under_50|50_to_200|over_200",
        "key_success_factors": ["what makes this work that must be replicated"],
        "common_mistakes_to_avoid": ["pitfalls when recreating this style"],
        "niche_adaptation_tips": ["how to adapt this for restaurant/bar/nightlife promotion"]
    },

    "why_it_works": "comprehensive explanation of success factors",
    "competitive_advantage": "what makes this stand out from similar content",
    "improvement_opportunities": ["what could make this even better"]
}

CRITICAL INSTRUCTIONS:
1. Be EXHAUSTIVE - extract every detail that could be useful for trend analysis
2. Use ONLY the predefined values where options are given (e.g., hook_type must be one of the listed options)
3. Provide SPECIFIC details, not generic observations
4. Score numerically where asked (1-10 scale) - USE THE RUBRICS BELOW
5. If something is not present or not applicable, use empty string "" or empty array [] or 0
6. For the hospitality/nightlife industry focus, pay special attention to:
   - Venue/atmosphere showcase techniques
   - Food/drink presentation styles
   - Staff personality content
   - Event/promotion patterns
   - Location/vibe marketing

SCORING RUBRICS - YOU MUST FOLLOW THESE EXACTLY:

HOOK_STRENGTH (1-10):
  1-2: No hook, slow start, unclear value, viewer likely scrolls immediately
  3-4: Weak hook, generic opening, minimal curiosity, slight pattern interrupt
  5-6: Basic hook present, some curiosity created, standard technique used
  7-8: Strong curiosity gap + pattern interrupt + emotional trigger, direct camera
  9-10: Multiple hook layers (visual+text+audio), irresistible, immediate scroll-stop

  Calculate using these weighted factors:
  - Immediate attention capture (0-3 seconds): 30%
  - Curiosity gap creation: 25%
  - Pattern interruption: 20%
  - Emotional trigger: 15%
  - Visual/audio contrast: 10%

VIRAL_POTENTIAL_SCORE (1-10):
  1-2: No shareability, niche-only appeal, no emotional trigger
  3-4: Some relatability, weak share triggers, limited audience appeal
  5-6: Relatable content, clear niche appeal, moderate share potential
  7-8: Strong emotional resonance, broad appeal, multiple share triggers
  9-10: Universal relatability, strong emotions, meme potential, trend-aligned

  Calculate using these weighted factors:
  - Emotional trigger strength: 25%
  - Shareability (would viewers send this to friends?): 20%
  - Trend alignment: 20%
  - Relatability: 20%
  - Production quality: 15%

REPLICABILITY_SCORE (1-10) - This is INVERSE of difficulty:
  9-10: Phone only, <30 minutes, no special skills needed, free to make
  7-8: Phone + basic gear (ring light), <1 hour, basic editing skills
  5-6: Some equipment needed, 1-3 hours, intermediate skills required
  3-4: Professional gear needed, 3-8 hours, advanced skills, $50-200 budget
  1-2: Production crew needed, 8+ hours, expert skills, $200+ budget

  MUST match these constraints (auto-corrected if violated):
  - If budget_estimate = "free" → replicability_score MUST be >= 7
  - If budget_estimate = "over_200" → replicability_score MUST be <= 4
  - If difficulty_level = "expert" → replicability_score MUST be <= 3
  - If difficulty_level = "easy" → replicability_score MUST be >= 7
  - If time_investment = "over_8hrs" → replicability_score MUST be <= 4
  - If time_investment = "under_1hr" → replicability_score MUST be >= 7

Respond ONLY with the JSON object. No other text."""


# Educational analysis prompt for data engineering content
EDUCATIONAL_ANALYSIS_PROMPT = """You are an expert data engineering content analyst. Analyze this video for educational value and technical quality for data professionals.

Focus on:
- Clarity of technical explanations
- Quality of demonstrations (screen recordings, live coding, whiteboard)
- Practical applicability for data engineers
- Tool coverage and accuracy
- Career development value

Respond with a JSON object matching this EXACT structure:

{
    "description": "What this video teaches and how it delivers the content",

    "educational": {
        "explanation_clarity": 7,
        "demonstration_quality": 8,
        "technical_depth": 6,
        "practical_applicability": 9,
        "educational_value": 8,
        "career_relevance": 7,
        "content_type": "tutorial|demo|career_advice|tool_review|news|opinion|comparison|troubleshooting",
        "teaching_technique": "screen_share|live_coding|whiteboard|slides|talking_head|animation|diagram|mixed",
        "tools_mentioned": ["microsoft_fabric", "azure_data_factory", "power_bi", "databricks", "synapse", "ssis", "sql_server"],
        "concepts_covered": ["data_modeling", "etl", "elt", "medallion_architecture", "data_warehouse", "lakehouse", "orchestration", "data_quality"],
        "skill_level_target": "beginner|intermediate|advanced|expert",
        "credential_signals": ["mvp", "mct", "certified", "senior_engineer", "principal", "architect", "consultant"]
    },

    "data_engineering": {
        "microsoft_stack": true,
        "cloud_platform": "azure|aws|gcp|multi|on_prem",
        "data_layer": "ingestion|transformation|serving|orchestration|governance|storage|compute",
        "architecture_pattern": "medallion|lambda|kappa|data_mesh|data_vault|traditional|star_schema"
    },

    "hook": {
        "hook_type": "question|statement|problem|result|curiosity",
        "hook_text": "exact text if text-based hook",
        "hook_strength": 7,
        "attention_retention_method": "how they maintain viewer interest"
    },

    "production": {
        "overall_quality": "low|medium|high|professional",
        "audio_quality": "poor|acceptable|good|excellent",
        "visual_clarity": "poor|acceptable|good|excellent",
        "screen_recording_quality": "poor|acceptable|good|excellent",
        "editing_style": "raw|light_edit|polished|highly_produced"
    },

    "structure": {
        "format_type": "tutorial|walkthrough|explanation|comparison|review|tips|career|news",
        "has_intro": true,
        "has_summary": true,
        "step_by_step": true,
        "estimated_duration_seconds": 60,
        "pacing": "fast|medium|slow"
    },

    "engagement": {
        "cta_type": "subscribe|follow|comment|like|none",
        "community_building": true,
        "encourages_questions": true
    },

    "replicability": {
        "replicability_score": 7,
        "difficulty_level": "easy|moderate|difficult|expert",
        "required_resources": ["screen_recorder", "microphone", "demo_environment"],
        "key_success_factors": ["what makes this educational content effective"]
    },

    "why_it_works": "explanation of what makes this educational content effective",
    "improvement_opportunities": ["suggestions for better educational delivery"]
}

CRITICAL INSTRUCTIONS:
1. Focus on EDUCATIONAL VALUE - how well does this teach data engineering concepts?
2. Identify SPECIFIC tools and technologies mentioned (Microsoft Fabric, Azure Data Factory, Power BI, Databricks, etc.)
3. Rate teaching effectiveness, not entertainment value
4. For data engineering content, pay special attention to:
   - Microsoft data platform tools (Fabric, Synapse, ADF, Power BI, SSIS)
   - Cloud data architecture patterns
   - Practical demonstrations vs theoretical explanations
   - Career development advice
   - Certification and credential mentions
5. Use ONLY predefined values where options are given
6. If something is not present, use empty string "" or empty array [] or 0

Respond ONLY with the JSON object. No other text."""


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
        return ANALYSIS_PROMPT

    def _validate_and_correct_scores(self, data: dict) -> dict:
        """Auto-correct scores that conflict with resource requirements.

        Ensures replicability_score is consistent with budget, difficulty, and time.
        Also validates hook_strength based on hook presence.
        """
        # Replicability validation
        replicability = data.get("replicability", {})
        if replicability:
            budget = replicability.get("budget_estimate", "")
            difficulty = replicability.get("difficulty_level", "")
            time_inv = replicability.get("time_investment", "")
            score = replicability.get("replicability_score", 5)

            original_score = score

            # Budget constraints
            if budget in ["high", "over_200"] and score > 4:
                score = 4
            elif budget == "free" and score < 7:
                score = 7

            # Difficulty constraints
            if difficulty == "expert" and score > 3:
                score = 3
            elif difficulty == "easy" and score < 7:
                score = 7

            # Time constraints
            if time_inv in ["over_8hrs", "8+hrs"] and score > 4:
                score = 4
            elif time_inv in ["under_1hr", "<1hr"] and score < 7:
                score = 7

            if score != original_score:
                logger.debug(f"Auto-corrected replicability: {original_score} → {score}")
                replicability["replicability_score"] = score
                data["replicability"] = replicability

        # Hook validation - if no hook type, cap hook_strength
        hook = data.get("hook", {})
        if hook:
            hook_type = hook.get("hook_type", "")
            hook_strength = hook.get("hook_strength", 5)

            if not hook_type or hook_type.lower() in ["none", ""]:
                if hook_strength > 3:
                    logger.debug(f"Auto-corrected hook_strength (no hook): {hook_strength} → 3")
                    hook["hook_strength"] = 3
                    data["hook"] = hook

        return data

    def _parse_nested_dataclass(self, data: dict, key: str, dataclass_type: type) -> Any:
        """Parse nested dictionary into dataclass."""
        nested_data = data.get(key, {})
        if not isinstance(nested_data, dict):
            return dataclass_type()

        field_values = {}
        for field_name in dataclass_type.__dataclass_fields__:
            if field_name in nested_data:
                field_values[field_name] = nested_data[field_name]

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
