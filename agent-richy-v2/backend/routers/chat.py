"""Chat router — /api/chat + /api/chat/stream (SSE)."""

import json
import logging
from typing import Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from agents import get_agent, route_to_agent
from core.intent_detection import build_enriched_context, detect_intent
from core.response_cache import set_session_cache
from core.skill_prompts import build_skill_context
from services.response_formatter import format_response
from models.structured_response import StructuredResponse
from models.chat import ChatRequest

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/chat", tags=["chat"])

# In-memory chat history per session (replace with DB later)
_chat_histories: dict[str, list[dict]] = {}
_profiles: dict[str, dict] = {}


def _get_profile(session_id: str) -> dict:
    """Get or create a default profile dict for the session."""
    if session_id not in _profiles:
        _profiles[session_id] = {
            "name": "Friend",
            "age": None,
            "user_type": "adult",
            "monthly_income": 0,
            "monthly_expenses": 0,
            "savings_balance": 0,
            "emergency_fund": 0,
            "debts": {},
            "debt_interest_rates": {},
            "credit_score": None,
            "goals": [],
            "risk_tolerance": "medium",
        }
    return _profiles[session_id]


def _get_history(session_id: str) -> list[dict]:
    if session_id not in _chat_histories:
        _chat_histories[session_id] = []
    return _chat_histories[session_id]


@router.post("", response_model=StructuredResponse)
async def chat(request: ChatRequest):
    """Main chat endpoint — synchronous full response."""
    session_id = request.session_id or "default"
    message = request.message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    # Build enriched context (intent, calculators, RAG)
    context = build_enriched_context(message, session_id=session_id)

    # If we got a cached response, return it
    if context.get("cached_response"):
        return format_response(
            raw_text=context["cached_response"],
            agent=request.agent or "coach_richy",
            intent=context["intent"].get("intent"),
        )

    # Route to appropriate agent
    agent_key = request.agent or context.get("suggested_agent", "coach_richy")
    suggested_agent = route_to_agent(message, agent_key)
    agent = get_agent(agent_key)

    # Get profile and history
    profile_dict = _get_profile(session_id)
    history = _get_history(session_id)

    # Build the user message with enrichment
    enriched_message = message
    if context.get("enriched_prompt"):
        enriched_message = f"{message}\n\n{context['enriched_prompt']}"

    # ── Skill prompt injection ───────────────────────────────────────
    skill_context = build_skill_context(request.skill, request.optimizer_expenses)
    if skill_context:
        logger.info(f"[skill-detection] Injecting '{request.skill}' prompt for session {session_id}")

    # Create a simple profile object the agents can use
    from models.profile import FinancialProfile
    profile = FinancialProfile(**{
        k: v for k, v in profile_dict.items()
        if k in FinancialProfile.model_fields
    })

    # Call the agent
    try:
        result = agent.send_message(
            user_input=enriched_message,
            chat_history=history,
            profile=profile,
            financial_plan={},
            client=_get_llm_client(),
            provider=_get_provider(),
            extra_system_prompt=skill_context or None,
        )

        # Handle streaming response from OpenAI
        if hasattr(result, '__iter__') and not isinstance(result, str):
            full_text = ""
            for chunk in result:
                if hasattr(chunk, 'choices') and chunk.choices:
                    delta = chunk.choices[0].delta
                    if delta and delta.content:
                        full_text += delta.content
            raw_text = full_text
        else:
            raw_text = result

    except Exception as e:
        logger.error(f"Agent error: {e}")
        raw_text = agent._offline_response(message, profile)

    # Extract financial data from response
    extracted = agent.extract_financial_data(raw_text)
    if extracted:
        for key, value in extracted.items():
            if key in profile_dict and value is not None:
                profile_dict[key] = value

    # Update chat history
    history.append({"role": "user", "content": message})
    history.append({"role": "assistant", "content": raw_text})

    # Cache the response
    set_session_cache(session_id, message, raw_text)

    # Format structured response
    intent = context.get("intent", {})
    return format_response(
        raw_text=raw_text,
        agent=agent_key,
        intent=intent.get("intent"),
        calculator_name=intent.get("calculator"),
        calculator_result=context.get("calculator_result"),
        suggested_agent=suggested_agent if suggested_agent != agent_key else None,
    )


@router.post("/stream")
async def chat_stream(request: ChatRequest):
    """SSE streaming chat endpoint."""
    session_id = request.session_id or "default"
    message = request.message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    context = build_enriched_context(message, session_id=session_id)

    if context.get("cached_response"):
        async def cached_gen():
            resp = format_response(
                raw_text=context["cached_response"],
                agent=request.agent or "coach_richy",
                intent=context["intent"].get("intent"),
            )
            yield f"data: {json.dumps(resp.model_dump())}\n\n"
            yield "data: [DONE]\n\n"
        return StreamingResponse(cached_gen(), media_type="text/event-stream")

    agent_key = request.agent or context.get("suggested_agent", "coach_richy")
    agent = get_agent(agent_key)
    profile_dict = _get_profile(session_id)
    history = _get_history(session_id)

    enriched_message = message
    if context.get("enriched_prompt"):
        enriched_message = f"{message}\n\n{context['enriched_prompt']}"

    # ── Skill prompt injection ───────────────────────────────────────
    skill_context = build_skill_context(request.skill, request.optimizer_expenses)
    if skill_context:
        logger.info(f"[skill-detection] Injecting '{request.skill}' prompt for stream session {session_id}")

    from models.profile import FinancialProfile
    profile = FinancialProfile(**{
        k: v for k, v in profile_dict.items()
        if k in FinancialProfile.model_fields
    })

    async def generate():
        try:
            result = agent.send_message(
                user_input=enriched_message,
                chat_history=history,
                profile=profile,
                financial_plan={},
                client=_get_llm_client(),
                provider=_get_provider(),
                extra_system_prompt=skill_context or None,
            )

            full_text = ""
            if hasattr(result, '__iter__') and not isinstance(result, str):
                for chunk in result:
                    if hasattr(chunk, 'choices') and chunk.choices:
                        delta = chunk.choices[0].delta
                        if delta and delta.content:
                            text = delta.content
                            full_text += text
                            yield f"data: {json.dumps({'type': 'token', 'content': text})}\n\n"
            else:
                full_text = result
                # Simulate streaming for offline responses
                words = full_text.split()
                for i in range(0, len(words), 3):
                    chunk_text = " ".join(words[i:i+3]) + " "
                    yield f"data: {json.dumps({'type': 'token', 'content': chunk_text})}\n\n"

            # Send final structured response
            intent = context.get("intent", {})
            structured = format_response(
                raw_text=full_text,
                agent=agent_key,
                intent=intent.get("intent"),
                calculator_name=intent.get("calculator"),
                calculator_result=context.get("calculator_result"),
                suggested_agent=route_to_agent(message, agent_key),
            )

            yield f"data: {json.dumps({'type': 'complete', 'response': structured.model_dump()})}\n\n"

            # Update history
            history.append({"role": "user", "content": message})
            history.append({"role": "assistant", "content": full_text})
            set_session_cache(session_id, message, full_text)

        except Exception as e:
            logger.error(f"Streaming error: {e}")
            offline = agent._offline_response(message, profile)
            yield f"data: {json.dumps({'type': 'token', 'content': offline})}\n\n"
            structured = format_response(raw_text=offline, agent=agent_key)
            yield f"data: {json.dumps({'type': 'complete', 'response': structured.model_dump()})}\n\n"

        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


# ── LLM client helpers ───────────────────────────────────────────────────

_llm_client = None
_llm_provider = "openai"


def _get_llm_client():
    global _llm_client, _llm_provider
    if _llm_client is not None:
        return _llm_client

    from core.config import OPENAI_API_KEY, GOOGLE_API_KEY

    if OPENAI_API_KEY:
        try:
            from openai import OpenAI
            _llm_client = OpenAI(api_key=OPENAI_API_KEY)
            _llm_provider = "openai"
            return _llm_client
        except ImportError:
            pass

    if GOOGLE_API_KEY:
        try:
            import google.generativeai as genai
            genai.configure(api_key=GOOGLE_API_KEY)
            _llm_client = genai
            _llm_provider = "gemini"
            return _llm_client
        except ImportError:
            pass

    return None


def _get_provider() -> str:
    return _llm_provider
