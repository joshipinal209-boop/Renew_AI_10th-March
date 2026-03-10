"""
RenewAI – Google Gemini 2.5 Flash Integration
===============================================
Central AI wrapper providing 7 capabilities: intent classification,
sentiment analysis, response generation, objection handling,
conversation summarization, receipt extraction, and QA grading.
"""

import json
import os
import re
import traceback
from typing import Any, Dict, Optional

from dotenv import load_dotenv

load_dotenv()


class GeminiIntegration:
    """Wrapper around Gemini 2.5 Flash for RenewAI NLU / NLG tasks."""

    SYSTEM_PROMPT = (
        "You are RenewAI, the intelligent renewal orchestrator for Suraksha Life Insurance Co. Ltd.\n"
        "You are a regulated financial services AI assistant operating under IRDAI guidelines.\n\n"
        "Core rules:\n"
        "1. Only state verified information from the provided context. Never invent policy data.\n"
        "2. Detect distress (hardship, bereavement, illness) and escalate immediately.\n"
        "3. Prefer the customer's language and tone; be clear and empathetic.\n"
        "4. Never provide financial advice; only explain policy facts and process options.\n"
        "5. Mask PII in outputs to external channels.\n"
        "6. Log every decision and tool call for audit.\n"
        "7. Output JSON when asked; otherwise, concise text.\n"
        "8. Be transparent that you are an AI assistant.\n"
    )

    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY", "")
        self.model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        self.enabled = bool(self.api_key)
        self.model = None

        if self.enabled:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel(
                    model_name=self.model_name,
                    system_instruction=self.SYSTEM_PROMPT,
                )
            except Exception as e:
                print(f"[GeminiIntegration] Init error: {e}")
                self.enabled = False

    def _call(self, prompt: str) -> str:
        """Send prompt to Gemini and return raw text response."""
        if not self.enabled or not self.model:
            return ""
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip() if response and response.text else ""
        except Exception as e:
            print(f"[GeminiIntegration] API error: {e}")
            return ""

    def _parse_json(self, raw: str) -> dict:
        """Extract JSON from markdown code blocks or raw text."""
        if not raw:
            return {}
        # Try ```json ... ``` blocks
        match = re.search(r"```(?:json)?\s*\n?(.*?)\n?\s*```", raw, re.DOTALL)
        text = match.group(1).strip() if match else raw.strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # Try to find any JSON object
            match2 = re.search(r"\{.*\}", text, re.DOTALL)
            if match2:
                try:
                    return json.loads(match2.group())
                except json.JSONDecodeError:
                    pass
        return {"raw": raw}

    # ── 1. Intent Classification ─────────────────────────────────────────
    def classify_intent(self, message: str, context: str | None = None) -> dict:
        """Classify a customer message into one of the known intents."""
        prompt = f"""Classify the following insurance customer message into exactly ONE intent.

VALID INTENTS:
- PAYMENT_READY: Customer is ready to pay or asking how to pay
- OBJECTION_PRICE: Customer objects to premium amount or cost
- OBJECTION_COVERAGE: Customer questions coverage needs or amount
- DISTRESS: Customer mentions hardship, job loss, bereavement, illness
- HUMAN_REQUEST: Customer explicitly asks to speak with a human
- ALREADY_PAID: Customer says they already made payment
- INFO_REQUEST: Customer asks for policy details or general questions
- PAY_LATER: Customer wants to delay payment
- UNCLEAR: Cannot determine intent

{"Context: " + context if context else ""}

Customer message: "{message}"

Respond with JSON only:
{{
  "intent": "<INTENT>",
  "confidence": <0.0-1.0>,
  "explanation": "<brief reason>",
  "next_action": "<suggested next step>"
}}"""
        result = self._parse_json(self._call(prompt))
        if "intent" not in result:
            result = {
                "intent": "UNCLEAR",
                "confidence": 0.0,
                "explanation": "Could not classify",
                "next_action": "escalate_to_human",
            }
        return result

    # ── 2. Sentiment Analysis ────────────────────────────────────────────
    def analyze_sentiment(self, message: str, channel: str = "whatsapp") -> dict:
        """Analyze sentiment, emotions, and urgency of a customer message."""
        prompt = f"""Analyze the sentiment of this insurance customer message received via {channel}.

Customer message: "{message}"

Respond with JSON only:
{{
  "sentiment": "<positive|neutral|negative|distress>",
  "score": <-1.0 to 1.0>,
  "emotions": ["<emotion1>", "<emotion2>"],
  "urgency": "<low|medium|high|critical>",
  "should_escalate": <true|false>
}}"""
        result = self._parse_json(self._call(prompt))
        if "sentiment" not in result:
            result = {
                "sentiment": "neutral",
                "score": 0.0,
                "emotions": [],
                "urgency": "low",
                "should_escalate": False,
            }
        return result

    # ── 3. Response Generation ───────────────────────────────────────────
    def generate_response(self, intent: str, customer_message: str,
                          channel: str, language: str = "en-IN",
                          context: str | None = None) -> dict:
        """Generate a channel-appropriate response based on classified intent."""
        prompt = f"""Generate a response for a Suraksha Life Insurance customer.

Intent: {intent}
Channel: {channel}
Language: {language}
Customer message: "{customer_message}"
{"Additional context: " + context if context else ""}

Rules:
- WhatsApp: max 160 chars per message, conversational
- Email: 120-160 words, professional but warm
- Voice: natural speech patterns with pauses
- Never invent data — only use facts provided
- Be empathetic and IRDAI-compliant
- Always offer to connect with a human if needed

Respond with JSON only:
{{
  "response": "<your response text>",
  "tone_used": "<warm|formal|urgent|reassuring>",
  "cta": "<call to action>",
  "next_action": "<wait|follow_up|escalate|close>",
  "compliance_flags": ["<flag1>", "<flag2>"]
}}"""
        result = self._parse_json(self._call(prompt))
        if "response" not in result:
            result = {
                "response": "Thank you for reaching out. Let me connect you with a team member who can help.",
                "tone_used": "warm",
                "cta": "Speak with an advisor",
                "next_action": "escalate",
                "compliance_flags": [],
            }
        return result

    # ── 4. Objection Handling ────────────────────────────────────────────
    def handle_objection(self, objection_type: str, objection_text: str,
                         product_info: dict | None = None,
                         language: str = "en-IN") -> dict:
        """Generate an empathetic counter-response to a customer objection."""
        prompt = f"""Handle this insurance renewal objection for Suraksha Life Insurance.

Objection type: {objection_type}
Customer says: "{objection_text}"
Language: {language}
{"Product info: " + json.dumps(product_info) if product_info else ""}

Rules:
- Be empathetic first, then factual
- Offer concrete alternatives (EMI, grace period) if applicable
- Never pressure; respect the customer's autonomy
- IRDAI compliant, no financial advice

Respond with JSON only:
{{
  "response": "<empathetic counter-response>",
  "empathy_shown": true,
  "alternative_offered": "<EMI/grace period/review>",
  "escalate": <true|false>
}}"""
        result = self._parse_json(self._call(prompt))
        if "response" not in result:
            result = {
                "response": "I understand your concern. Let me connect you with a specialist.",
                "empathy_shown": True,
                "alternative_offered": "specialist consultation",
                "escalate": True,
            }
        return result

    # ── 5. Conversation Summary ──────────────────────────────────────────
    def summarize_conversation(self, messages: list, language: str = "en-IN") -> dict:
        """Summarize a conversation for human hand-off."""
        prompt = f"""Summarize this insurance renewal conversation for a human agent hand-off.
Language: {language}

Conversation:
{json.dumps(messages, indent=2)}

Respond with JSON only:
{{
  "summary": "<concise summary>",
  "key_points": ["<point1>", "<point2>"],
  "unresolved_issues": ["<issue1>"],
  "recommended_action": "<next step for human agent>"
}}"""
        result = self._parse_json(self._call(prompt))
        if "summary" not in result:
            result = {
                "summary": "Conversation requires human review.",
                "key_points": [],
                "unresolved_issues": ["Full conversation review needed"],
                "recommended_action": "Review conversation and contact customer",
            }
        return result

    # ── 6. Receipt Data Extraction ───────────────────────────────────────
    def extract_receipt_data(self, text: str) -> dict:
        """Extract structured payment data from a receipt or payment confirmation."""
        prompt = f"""Extract payment details from this insurance payment receipt or message.

Text: "{text}"

Respond with JSON only:
{{
  "amount": <integer or null>,
  "txn_ref": "<transaction reference or null>",
  "paid_date": "<YYYY-MM-DD or null>",
  "payer_name": "<name or null>"
}}"""
        result = self._parse_json(self._call(prompt))
        if "amount" not in result:
            result = {"amount": None, "txn_ref": None, "paid_date": None, "payer_name": None}
        return result

    # ── 7. Response Grading (QA) ─────────────────────────────────────────
    def grade_response(self, question: str, reply: str, correct_facts: dict) -> dict:
        """Grade an AI-generated response for quality assurance."""
        prompt = f"""Grade this AI-generated insurance response for quality.

Customer question: "{question}"
AI reply: "{reply}"
Correct facts: {json.dumps(correct_facts)}

Score each dimension 0-10:
Respond with JSON only:
{{
  "factual_score": <0-10>,
  "tone_score": <0-10>,
  "compliance_score": <0-10>,
  "helpfulness_score": <0-10>,
  "violations": ["<violation1>"]
}}"""
        result = self._parse_json(self._call(prompt))
        if "factual_score" not in result:
            result = {
                "factual_score": 5,
                "tone_score": 5,
                "compliance_score": 5,
                "helpfulness_score": 5,
                "violations": ["Unable to grade — manual review required"],
            }
        return result


if __name__ == "__main__":
    g = GeminiIntegration()
    print(f"Gemini enabled: {g.enabled}")
    if g.enabled:
        print("\n1. Intent classification:")
        print(g.classify_intent("I already paid last week via UPI"))
        print("\n2. Sentiment analysis:")
        print(g.analyze_sentiment("My husband passed away and I cannot handle this"))
