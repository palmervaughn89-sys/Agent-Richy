"""Base agent class for all AI financial coaches."""

import json
import re
import logging
from abc import ABC, abstractmethod
from typing import Optional

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Abstract base class for all Agent Richy financial coaches.

    Each agent has a distinct personality, expertise area, and system prompt.
    All agents share common response formatting and error handling.
    """

    def __init__(self, name: str, icon: str, specialty: str):
        """Initialize agent with identity.

        Args:
            name: Display name for the agent.
            icon: Emoji icon for the agent.
            specialty: Short description of expertise area.
        """
        self.name = name
        self.icon = icon
        self.specialty = specialty

    @abstractmethod
    def get_system_prompt(self, user_profile: dict, financial_plan: dict) -> str:
        """Build the system prompt for this agent.

        Args:
            user_profile: Dict of known user financial data.
            financial_plan: Current financial plan data.

        Returns:
            Complete system prompt string.
        """
        pass

    def _build_known_data(self, profile) -> str:
        """Build a summary of known user data for the system prompt.

        Args:
            profile: UserProfile object.

        Returns:
            Formatted string of known data.
        """
        known = []
        if profile.name:
            known.append(f"Name: {profile.name}")
        if profile.age:
            known.append(f"Age: {profile.age}")
        if profile.monthly_income:
            known.append(f"Monthly income: ${profile.monthly_income:,.0f}")
        if profile.monthly_expenses:
            known.append(f"Monthly expenses: ${profile.monthly_expenses:,.0f}")
        if profile.savings_balance:
            known.append(f"Savings: ${profile.savings_balance:,.0f}")
        if profile.emergency_fund:
            known.append(f"Emergency fund: ${profile.emergency_fund:,.0f}")
        if profile.debts:
            for name, bal in profile.debts.items():
                rate = profile.debt_interest_rates.get(name, 0)
                known.append(f"Debt - {name}: ${bal:,.0f} @ {rate * 100:.1f}%")
        if profile.credit_score:
            known.append(f"Credit score: {profile.credit_score}")
        if profile.goals:
            known.append(f"Goals: {', '.join(profile.goals)}")
        if profile.risk_tolerance and profile.risk_tolerance != "medium":
            known.append(f"Risk tolerance: {profile.risk_tolerance}")
        return "; ".join(known) if known else "Nothing yet — need to ask questions"

    def _format_base_rules(self) -> str:
        """Return the standard response rules appended to every agent prompt."""
        return """
RESPONSE RULES:
- Keep responses under 350 words
- Use markdown formatting: **bold** for key numbers, bullet points for lists, ### for headers
- Show specific calculations when relevant (e.g., "$500/mo at 7% for 25 years = $405,537")
- End every response with a clear **Next Step** or action item
- Always ask at least one clarifying question if you don't have enough info
- Never give vague platitudes — be specific and actionable
- Include a disclaimer when giving investment or tax advice: "*I'm an AI coach, not a licensed financial advisor. Consult a professional for personalized advice.*"
- After gathering key financial data, include a JSON block at the END of your response
  wrapped in ```json ... ``` with any data you've learned. Use this format:
  {"monthly_income": 5000, "monthly_expenses": 3500, "savings": 2000,
    "emergency_fund": 500, "credit_score": 680,
    "debts": {"credit_card": {"balance": 5000, "rate": 0.22, "min_payment": 150}},
    "goals": ["emergency fund", "pay off credit card"],
    "budget": {"needs": 2500, "wants": 600, "savings": 400},
    "recommendations": ["Build $1000 emergency fund first", "Attack credit card with avalanche method"],
    "risk_level": "moderate"}
  Only include fields you actually learned. Don't guess.
- If the user shares financial data, ALWAYS include the JSON extraction block
"""

    def send_message(self, user_input: str, chat_history: list,
                     profile, financial_plan: dict,
                     client=None, provider: str = "openai",
                     extra_system_prompt: Optional[str] = None) -> str:
        """Send a message to the LLM and get a response.

        Args:
            user_input: The user's message.
            chat_history: List of previous messages.
            profile: UserProfile object.
            financial_plan: Current financial plan dict.
            client: LLM client instance (OpenAI or Gemini).
            provider: 'openai' or 'gemini'.
            extra_system_prompt: Additional system prompt text (e.g. from skill detection).

        Returns:
            The assistant's response string, or a streaming response.
        """
        if not client:
            return self._offline_response(user_input, profile)

        try:
            system_prompt = self.get_system_prompt(
                user_profile=self._profile_to_dict(profile),
                financial_plan=financial_plan,
            )

            # Append skill-specific prompt if detected
            if extra_system_prompt:
                system_prompt = f"{system_prompt}\n\n{extra_system_prompt}"

            if provider == "gemini":
                return self._send_gemini(client, system_prompt, user_input,
                                         chat_history, profile)

            # OpenAI path (default)
            messages = [{"role": "system", "content": system_prompt}]
            for msg in chat_history[-20:]:
                messages.append({"role": msg["role"], "content": msg["content"]})
            messages.append({"role": "user", "content": user_input})

            response = client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                temperature=0.7,
                max_tokens=1000,
                stream=True,
            )
            return response  # Return the stream for the caller to handle

        except Exception as e:
            logger.error(f"LLM call failed for {self.name}: {e}")
            return self._offline_response(user_input, profile)

    def _send_gemini(self, genai_module, system_prompt: str, user_input: str,
                     chat_history: list, profile, stream: bool = False):
        """Send message via Google Gemini.

        Args:
            genai_module: The google.generativeai module.
            system_prompt: System prompt text.
            user_input: User message.
            chat_history: Chat history.
            profile: User profile.
            stream: If True, return a streaming response iterator.

        Returns:
            Response text string, or streaming iterator if stream=True.
        """
        try:
            model = genai_module.GenerativeModel(
                "gemini-1.5-flash",
                system_instruction=system_prompt,
            )
            # Build conversation history
            history_parts = []
            for msg in chat_history[-20:]:
                role = "user" if msg["role"] == "user" else "model"
                history_parts.append({"role": role, "parts": [msg["content"]]})

            chat = model.start_chat(history=history_parts)
            response = chat.send_message(user_input, stream=stream)
            if stream:
                return response  # caller iterates chunks
            return response.text
        except Exception as e:
            logger.error(f"Gemini call failed for {self.name}: {e}")
            return self._offline_response(user_input, profile)

    def _offline_response(self, user_input: str, profile) -> str:
        """Generate a helpful offline response. Override in subclasses for specialization."""
        return (
            f"I'd love to help with that! 💡\n\n"
            f"To give you the best {self.specialty.lower()} advice, tell me about:\n"
            f"- Your **income** (monthly take-home)\n"
            f"- Your **biggest expenses**\n"
            f"- Any **debts** you're dealing with\n"
            f"- Your **financial goals**\n\n"
            f"Set up an `OPENAI_API_KEY` for full AI-powered {self.name} conversations. 🔑"
        )

    def _profile_to_dict(self, profile) -> dict:
        """Convert UserProfile to a dict summary for the system prompt."""
        return {
            "name": profile.name,
            "age": profile.age,
            "user_type": profile.user_type,
            "monthly_income": profile.monthly_income,
            "monthly_expenses": profile.monthly_expenses,
            "savings_balance": profile.savings_balance,
            "emergency_fund": profile.emergency_fund,
            "debts": profile.debts,
            "debt_interest_rates": profile.debt_interest_rates,
            "credit_score": profile.credit_score,
            "goals": profile.goals,
            "risk_tolerance": profile.risk_tolerance,
        }

    @staticmethod
    def extract_financial_data(response: str) -> Optional[dict]:
        """Extract JSON financial data from an agent response.

        Args:
            response: The full assistant response text.

        Returns:
            Dict of financial data or None.
        """
        pattern = r"```json\s*(\{.*?\})\s*```"
        match = re.search(pattern, response, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                logger.warning("Failed to parse JSON from response")
        return None

    @staticmethod
    def strip_json_block(response: str) -> str:
        """Remove JSON extraction blocks from display text.

        Args:
            response: The full assistant response text.

        Returns:
            Cleaned response without JSON blocks.
        """
        return re.sub(r"\s*```json\s*\{.*?\}\s*```\s*", "", response, flags=re.DOTALL).strip()

    @staticmethod
    def detect_topic(message: str) -> str:
        """Detect the financial topic of a user message for agent routing.

        Args:
            message: User's message text.

        Returns:
            Topic key string.
        """
        msg = message.lower()
        if any(w in msg for w in ["budget", "spend", "expense", "50/30/20", "spending"]):
            return "budget"
        if any(w in msg for w in ["invest", "stock", "portfolio", "401k", "roth", "etf", "index"]):
            return "invest"
        if any(w in msg for w in ["debt", "owe", "credit card", "loan", "student loan", "payoff"]):
            return "debt"
        if any(w in msg for w in ["save", "emergency", "fund", "savings", "goal"]):
            return "savings"
        if any(w in msg for w in ["kid", "child", "teen", "allowance", "young", "teach"]):
            return "kids"
        return "general"

    @staticmethod
    def suggest_agent(topic: str) -> str:
        """Suggest the best agent for a given topic.

        Args:
            topic: Topic key from detect_topic.

        Returns:
            Agent key string.
        """
        mapping = {
            "budget": "budget_bot",
            "invest": "invest_intel",
            "debt": "debt_destroyer",
            "savings": "savings_sage",
            "kids": "kid_coach",
            "general": "coach_richy",
        }
        return mapping.get(topic, "coach_richy")
