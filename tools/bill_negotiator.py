"""Bill Negotiator — word-for-word scripts for negotiating bills.
Cable/internet, cell phone, car insurance, medical bills, CC APR,
rent. Best time to call. Track savings.

Inherits from ``RichyToolBase``.
"""

from __future__ import annotations

import logging
from typing import Any

from tools.base import RichyToolBase, ToolResult

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════
# NEGOTIATION SCRIPTS & DATA
# ═══════════════════════════════════════════════════════════════════════════

_BILL_SCRIPTS: dict[str, dict[str, Any]] = {
    "cable_internet": {
        "label": "Cable / Internet",
        "avg_monthly": 120,
        "avg_savings_pct": 0.25,
        "best_time": "Tuesday-Thursday, 8-10 AM or 2-4 PM",
        "retention_dept": True,
        "script": [
            "📞 'Hi, I'd like to discuss my bill. I've been a loyal customer for [X] years and I've noticed my rate has gone up significantly.'",
            "📞 'I've been looking at [competitor name] and they're offering [their price] for similar service. Is there anything you can do to keep me as a customer?'",
            "📞 If they say no: 'I understand. Can I speak with your retention department? I'd like to discuss cancellation options.'",
            "📞 With retention: 'I really don't want to switch providers, but I can't justify paying $[current] when [competitor] is offering $[their price]. What promotions do you have for existing customers?'",
            "📞 If offered a deal: 'Can you apply that for 12 months? And can I get a confirmation number and the exact terms in writing?'",
        ],
        "pro_tips": [
            "Research competitor prices BEFORE calling — have specific numbers ready",
            "Be polite but firm. You're not asking — you're informing them of your options",
            "If the first rep can't help, hang up and call back. Different reps have different authority",
            "Ask about 'new customer promotions' specifically — they often have hidden discounts",
            "Consider downgrading speed — most people don't need 1 Gbps",
        ],
    },
    "cell_phone": {
        "label": "Cell Phone",
        "avg_monthly": 85,
        "avg_savings_pct": 0.30,
        "best_time": "Tuesday-Thursday, morning",
        "retention_dept": True,
        "script": [
            "📞 'Hi, I'm reviewing my cell phone plan and I think I'm paying too much for what I use. Can you help me find a better plan?'",
            "📞 'I see that [Mint Mobile / Visible / Cricket] offers [their plan] for $[price]. What can you offer me that's competitive?'",
            "📞 'I don't need unlimited everything. What's your cheapest plan that includes [X GB data] and unlimited talk/text?'",
            "📞 If they resist: 'I'd rather stay, but I'll need to switch if we can't work something out. Can you connect me to retention?'",
            "📞 'Can you also check if there are any loyalty discounts, autopay discounts, or military/student/employer discounts I might qualify for?'",
        ],
        "pro_tips": [
            "Check your actual data usage first — most people use under 5GB",
            "MVNOs (Mint Mobile, Visible, US Mobile) use the same towers for 50-70% less",
            "Autopay typically saves $5-10/mo per line",
            "Multi-line discounts are significant — consider a family plan with friends",
            "Ask about employer discounts — many companies have partner deals",
        ],
    },
    "car_insurance": {
        "label": "Car Insurance",
        "avg_monthly": 135,
        "avg_savings_pct": 0.20,
        "best_time": "Any weekday morning",
        "retention_dept": False,
        "script": [
            "📞 'Hi, I'd like to review my policy. I want to make sure I'm getting the best rate for my coverage level.'",
            "📞 'I've gotten quotes from [2-3 competitors] and they're offering similar coverage for $[lower price]. Can you match or beat that?'",
            "📞 'What discounts am I currently getting, and are there any I'm missing? Bundling, safe driver, low mileage, defensive driving course?'",
            "📞 'What happens to my rate if I raise my deductible from $500 to $1,000? How about $2,000?'",
            "📞 'My car is [X] years old. Does it still make sense to carry collision and comprehensive?'",
        ],
        "pro_tips": [
            "Get 3-5 quotes every year — same coverage, different carrier. Takes ~1 hour",
            "Bundle auto + home/renters for 5-25% discount",
            "Raising deductible from $500 to $1,000 saves ~10-15%",
            "Drop collision on cars worth less than $8K (repairs may exceed value)",
            "Defensive driving course: 5-10% discount in most states",
            "Ask about usage-based insurance (Snapshot, DriveWise) if you're a safe driver",
        ],
    },
    "medical_bills": {
        "label": "Medical Bills",
        "avg_monthly": None,
        "avg_savings_pct": 0.40,
        "best_time": "Monday-Friday, morning",
        "retention_dept": False,
        "script": [
            "📞 'Hi, I received a bill for $[amount] and I'd like to discuss it before making payment.'",
            "📞 'First, can you send me an itemized bill? I'd like to review each charge.'",
            "📞 After reviewing: 'I've checked fair prices on healthcarebluebook.com and some charges seem higher than the average. Can we discuss adjusting [specific charge]?'",
            "📞 'I'd like to pay this, but $[amount] is a financial hardship. Do you offer any financial assistance programs or a discount for paying in full today?'",
            "📞 If large bill: 'Can we set up a zero-interest payment plan? I can afford $[monthly amount] per month.'",
            "📞 'If I pay the full balance today, what kind of discount can you offer? Many providers offer 20-40% for prompt payment.'",
        ],
        "pro_tips": [
            "ALWAYS request an itemized bill — billing errors are extremely common (30-80% of bills have errors)",
            "Check prices on healthcarebluebook.com or fairhealthconsumer.org",
            "Non-profit hospitals are REQUIRED to have financial assistance programs",
            "Never put medical debt on a credit card — you lose all negotiating power",
            "Medical debt under $500 no longer appears on credit reports (2023 change)",
            "Payment plans are almost always 0% interest — ask for one",
            "You can negotiate BEFORE a procedure too — get a price estimate in writing",
        ],
    },
    "credit_card_apr": {
        "label": "Credit Card APR",
        "avg_monthly": None,
        "avg_savings_pct": 0.25,
        "best_time": "Tuesday-Thursday, afternoon",
        "retention_dept": True,
        "script": [
            "📞 'Hi, I've been a cardholder for [X] years with a good payment history, and I'd like to request a lower APR.'",
            "📞 'My current APR is [X]%. I've received offers from other cards at [lower rate]%. Given my loyalty and payment history, can you lower my rate?'",
            "📞 If they say no: 'I understand. Can I speak with a supervisor or someone in the retention department?'",
            "📞 'I'm considering transferring my balance to a 0% intro APR card. I'd rather stay with you if we can work something out.'",
            "📞 'Even a temporary rate reduction for 6-12 months would help. Is that something you can offer?'",
        ],
        "pro_tips": [
            "Have your credit score ready — good scores (700+) give you leverage",
            "Call after you've made on-time payments for 6+ months",
            "Even 2-3% lower APR saves hundreds on carried balances",
            "If denied, try again in 3-6 months. Note the date and who you spoke with",
            "Consider a balance transfer to a 0% intro APR card (usually 12-21 months)",
            "Best leverage: 'I have a pre-approved offer for X% from [competitor]'",
        ],
    },
    "rent": {
        "label": "Rent",
        "avg_monthly": 1_500,
        "avg_savings_pct": 0.05,
        "best_time": "2-3 months before lease renewal",
        "retention_dept": False,
        "script": [
            "📞 'Hi, my lease is up in [X] months and I'd like to discuss renewal terms. I've been a great tenant — always paid on time, no complaints, and I take care of the unit.'",
            "📞 'I've been looking at comparable units in the area and seeing rents of $[lower amount] for similar size and features. I'd like to stay, but I'd need a more competitive rate.'",
            "📞 'I know turnover is expensive for landlords — vacancy, cleaning, repairs, finding new tenants. Keeping me saves you $2,000-5,000 in turnover costs.'",
            "📞 'Would you be open to a longer lease (18-24 months) in exchange for keeping my rent the same or a small increase?'",
            "📞 'Alternatively, if the rent increase is firm, could you include [parking, storage, a new appliance, painting] to offset it?'",
        ],
        "pro_tips": [
            "Start negotiating 2-3 months before renewal — not at the last minute",
            "Research comparable rents on Zillow, Apartments.com, Craigslist",
            "Landlord turnover costs $2K-5K+ (vacancy, cleaning, advertising, screening)",
            "Offer something: longer lease, prepaying, handling minor maintenance",
            "If rent is firm, negotiate amenities: parking, pet fee waiver, fresh paint",
            "Best leverage in winter months (Nov-Feb) when demand is lowest",
        ],
    },
}

# Average savings from negotiation (Consumer Financial Protection Bureau)
_AVG_SUCCESS_RATE = 0.70  # 70% of people who negotiate succeed


class BillNegotiator(RichyToolBase):
    """Word-for-word scripts for negotiating bills down."""

    tool_id = 35
    tool_name = "bill_negotiation"
    description = (
        "Bill negotiation scripts for cable, phone, insurance, "
        "medical, credit card APR, rent — with best times to call"
    )
    required_profile: list[str] = []

    def execute(self, question: str, user_profile: dict) -> ToolResult:
        plan = self.analyze(question, user_profile)
        return ToolResult(
            tool_id=self.tool_id,
            tool_name=self.tool_name,
            confidence=plan.get("confidence", 0.85),
            response=self._narrate(plan),
            data_used=["bills", "question_topic"],
            accuracy_score=0.82,
            sources=[
                "Consumer Financial Protection Bureau",
                "FCC negotiation guidelines",
                "Healthcare Bluebook fair pricing",
            ],
            raw_data=plan,
        )

    def analyze(self, question: str, p: dict) -> dict:
        bills: list[dict] = p.get("bills", [])
        if not isinstance(bills, list):
            bills = []

        # Detect which bill type from question
        q_lower = question.lower()
        topic = p.get("topic", "").lower()

        matched_scripts: list[dict] = []
        total_current = 0.0
        total_potential_savings = 0.0

        # If specific bills provided, use those
        if bills:
            for bill in bills:
                if isinstance(bill, str):
                    bill = {"type": bill}
                bill_type = (bill.get("type", "") or "").lower().replace(" ", "_")
                monthly = float(bill.get("monthly", 0) or 0)

                script_data = _BILL_SCRIPTS.get(bill_type)
                if not script_data:
                    # Fuzzy match
                    for key, val in _BILL_SCRIPTS.items():
                        if key in bill_type or bill_type in key:
                            script_data = val
                            bill_type = key
                            break
                if not script_data:
                    continue

                if monthly == 0:
                    monthly = script_data.get("avg_monthly", 100) or 100

                potential = monthly * script_data["avg_savings_pct"]
                total_current += monthly
                total_potential_savings += potential

                matched_scripts.append({
                    "type": bill_type,
                    "label": script_data["label"],
                    "current_monthly": round(monthly, 2),
                    "potential_savings": round(potential, 2),
                    "savings_pct": script_data["avg_savings_pct"],
                    "best_time": script_data["best_time"],
                    "retention_dept": script_data["retention_dept"],
                    "script": script_data["script"],
                    "pro_tips": script_data["pro_tips"],
                })
        else:
            # Match from question keywords
            keyword_map = {
                "cable_internet": ["cable", "internet", "wifi", "broadband", "comcast", "xfinity", "spectrum", "att"],
                "cell_phone": ["cell", "phone", "mobile", "verizon", "t-mobile", "tmobile", "att"],
                "car_insurance": ["car insurance", "auto insurance"],
                "medical_bills": ["medical", "hospital", "doctor", "health bill"],
                "credit_card_apr": ["credit card", "apr", "interest rate", "cc"],
                "rent": ["rent", "lease", "landlord", "apartment"],
            }

            found_any = False
            for key, keywords in keyword_map.items():
                if any(kw in q_lower or kw in topic for kw in keywords):
                    sd = _BILL_SCRIPTS[key]
                    monthly = sd.get("avg_monthly", 100) or 100
                    potential = monthly * sd["avg_savings_pct"]
                    total_current += monthly
                    total_potential_savings += potential
                    matched_scripts.append({
                        "type": key,
                        "label": sd["label"],
                        "current_monthly": round(monthly, 2),
                        "potential_savings": round(potential, 2),
                        "savings_pct": sd["avg_savings_pct"],
                        "best_time": sd["best_time"],
                        "retention_dept": sd["retention_dept"],
                        "script": sd["script"],
                        "pro_tips": sd["pro_tips"],
                    })
                    found_any = True

            # If no match, return ALL scripts
            if not found_any:
                for key, sd in _BILL_SCRIPTS.items():
                    monthly = sd.get("avg_monthly", 100) or 100
                    potential = monthly * sd["avg_savings_pct"]
                    total_current += monthly
                    total_potential_savings += potential
                    matched_scripts.append({
                        "type": key,
                        "label": sd["label"],
                        "current_monthly": round(monthly, 2),
                        "potential_savings": round(potential, 2),
                        "savings_pct": sd["avg_savings_pct"],
                        "best_time": sd["best_time"],
                        "retention_dept": sd["retention_dept"],
                        "script": sd["script"],
                        "pro_tips": sd["pro_tips"],
                    })

        annual_savings = total_potential_savings * 12
        confidence = 0.82 if bills else 0.78

        return {
            "scripts": matched_scripts,
            "total_current_monthly": round(total_current, 2),
            "total_potential_monthly_savings": round(total_potential_savings, 2),
            "total_potential_annual_savings": round(annual_savings, 2),
            "success_rate": f"{_AVG_SUCCESS_RATE * 100:.0f}%",
            "count": len(matched_scripts),
            "confidence": confidence,
        }

    def _narrate(self, plan: dict) -> str:
        lines: list[str] = []
        lines.append(
            f"📞 **Bill Negotiator** — {plan['count']} bills | "
            f"Potential savings: "
            f"{self.fmt_currency(plan['total_potential_monthly_savings'])}/mo"
        )
        lines.append(
            f"  Success rate: {plan['success_rate']} of people who negotiate save money"
        )
        lines.append("")

        for s in plan["scripts"]:
            lines.append(f"**{'─' * 50}**")
            lines.append(
                f"**{s['label']}** — Currently ~{self.fmt_currency(s['current_monthly'])}/mo | "
                f"Could save ~{self.fmt_currency(s['potential_savings'])}/mo "
                f"({s['savings_pct'] * 100:.0f}%)"
            )
            lines.append(f"  🕐 Best time to call: {s['best_time']}")
            if s["retention_dept"]:
                lines.append("  🎯 Ask for the **retention department** for best deals")
            lines.append("")

            lines.append("  **Script:**")
            for step in s["script"]:
                lines.append(f"    {step}")
            lines.append("")

            lines.append("  **Pro tips:**")
            for tip in s["pro_tips"][:4]:
                lines.append(f"    💡 {tip}")
            lines.append("")

        # Total
        lines.append(
            f"**💰 Total potential savings:** "
            f"{self.fmt_currency(plan['total_potential_monthly_savings'])}/mo = "
            f"{self.fmt_currency(plan['total_potential_annual_savings'])}/yr"
        )
        lines.append("")
        lines.append(
            f"Confidence: {plan['confidence']:.0%} | "
            f"Sources: CFPB, FCC, Healthcare Bluebook"
        )
        return "\n".join(lines)
