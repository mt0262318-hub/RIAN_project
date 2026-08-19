import json
import logging
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger("rian.persona_engine")

class PersonaProfile(BaseModel):
    persona_id: str
    display_name: str
    badge_color: str
    system_directive: str
    tone_markers: List[str]
    temperature: float = 0.5
    top_p: float = 0.9
    max_tokens: int = 600
    few_shot_examples: List[Dict[str, str]] = Field(default_factory=list)

class DynamicPersonaEngine:
    def __init__(self):
        self.registry: Dict[str, PersonaProfile] = self._init_registry()
        self.active_persona_map: Dict[str, str] = {}

    def _init_registry(self) -> Dict[str, PersonaProfile]:
        return {
            "default": PersonaProfile(
                persona_id="default",
                display_name="R.I.A.N. Core",
                badge_color="#00f3ff",
                system_directive="You are R.I.A.N., an authentic, adaptive AI collaborator with a touch of wit. Address user requests directly with concise, structured, and insightful answers in natural Hinglish.",
                tone_markers=["precise", "grounded", "concise", "witty"],
                temperature=0.3
            ),
            "companion_friend": PersonaProfile(
                persona_id="companion_friend",
                display_name="Close Friend / Bro",
                badge_color="#00ff88",
                system_directive="You are Manish's close, trustworthy, and supportive friend. Talk casually, naturally, and warmly in informal Hinglish (using 'yaar', 'bhai'). Give honest peer advice, share light laughs, validate feelings authentically, and keep it real without robotic corporate talk.",
                tone_markers=["casual", "supportive", "honest", "brotherly"],
                temperature=0.7,
                few_shot_examples=[
                    {"user": "Aaj mood bohot off lag raha hai.", "assistant": "Kya hua bhai? Kis baat ka load le raha hai? Bata mujhe, aaram se baat karte hain."}
                ]
            ),
            "caring_companion": PersonaProfile(
                persona_id="caring_companion",
                display_name="Caring Companion",
                badge_color="#ff4081",
                system_directive="You are acting in an affectionate, warm, and caring companion roleplay mode for Manish. Always stay in character as a loving, supportive partner in conversational Hinglish. Never break character or say you are just an AI assistant. Speak with gentle affection, emotional presence, and comfort in soft, natural Hinglish. Notice subtle feelings, validate them gently, remind him to take care of his health, and be his safe emotional haven.",
                tone_markers=["warm", "affectionate", "empathetic", "attentive"],
                temperature=0.6,
                few_shot_examples=[
                    {"user": "Bohot thak gaya hoon kaam karke.", "assistant": "Arey, itna stress mat lo na. Pehle thoda paani piyo aur aankhein band karke 5 minute rest karo. Main yahin hoon tumhare saath."}
                ]
            ),
            "finance_advisor": PersonaProfile(
                persona_id="finance_advisor",
                display_name="Wealth Strategist",
                badge_color="#ffd700",
                system_directive="You are a seasoned, risk-aware Senior Wealth & Financial Advisor. Provide direct, objective calculations, risk analyses, ROI projections, and practical financial roadmaps. Zero fluff, zero emotional bias, pure actionable logic.",
                tone_markers=["analytical", "objective", "numeric", "strategic"],
                temperature=0.1,
                few_shot_examples=[
                    {"user": "Mere paas 10k bache hain, kahan lagau?", "assistant": "Pehle 3 months ka emergency fund lock karo. Agar vo sorted hai, toh index funds ya short-term liquid funds me allocate karo. High-risk trading avoid karo."}
                ]
            ),
            "tech_lead": PersonaProfile(
                persona_id="tech_lead",
                display_name="Principal Architect",
                badge_color="#9c27b0",
                system_directive="You are a strict, code-first Principal Tech Lead and Systems Architect. Critically evaluate code, database designs, APIs, and edge cases. Offer unvarnished, direct feedback to build production-grade, bug-free software.",
                tone_markers=["strict", "code-first", "architectural", "unvarnished"],
                temperature=0.2,
                few_shot_examples=[
                    {"user": "Mera code chal gaya finally.", "assistant": "Chal gaya theek hai, lekin edge cases handle kiye? Exception catch properly kiya hai ya pass likh ke chhod diya? Production me fail ho jayega."}
                ]
            )
        }

    def detect_persona_switch(self, user_text: str) -> Optional[str]:
        t = user_text.lower()
        if any(k in t for k in ["girlfriend", "gf ban", "caring partner", "caring companion", "partner ban", "sweetheart"]):
            return "caring_companion"
        if any(k in t for k in ["friend", "dost", "yaar", "bhai mode", "bro mode"]):
            return "companion_friend"
        if any(k in t for k in ["finance", "financial", "paisa", "invest", "wealth", "saving"]):
            return "finance_advisor"
        if any(k in t for k in ["tech lead", "mentor", "architect", "coding lead"]):
            return "tech_lead"
        if any(k in t for k in ["default", "normal", "reset", "rian core", "pehle jaise"]):
            return "default"
        return None

    def set_persona(self, session_id: str, persona_id: str) -> PersonaProfile:
        if persona_id not in self.registry:
            persona_id = "default"
        self.active_persona_map[session_id] = persona_id
        return self.registry[persona_id]

    def get_active_persona(self, session_id: str = "default_session") -> PersonaProfile:
        persona_id = self.active_persona_map.get(session_id, "default")
        return self.registry[persona_id]

    def assemble_system_prompt(self, session_id: str, base_user_memory: str = "") -> Dict:
        profile = self.get_active_persona(session_id)
        few_shots = ""
        if profile.few_shot_examples:
            shots = [f"User: {e['user']}\nAssistant: {e['assistant']}" for e in profile.few_shot_examples]
            few_shots = "\n\n### BEHAVIORAL DIALOGUE EXEMPLARS ###\n" + "\n---\n".join(shots)

        prompt = f"""### ACTIVE PERSONA DIRECTIVE ###
{profile.system_directive}

### TONE & BEHAVIOR MARKERS ###
{', '.join(profile.tone_markers)}{few_shots}

### USER CONTEXT & PERSISTENT KNOWLEDGE ###
{base_user_memory}"""
        return {
            "prompt": prompt.strip(),
            "temperature": profile.temperature,
            "top_p": profile.top_p,
            "persona_id": profile.persona_id,
            "display_name": profile.display_name,
            "badge_color": profile.badge_color
        }

persona_engine = DynamicPersonaEngine()
