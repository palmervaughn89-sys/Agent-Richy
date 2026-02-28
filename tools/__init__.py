"""Richy financial tools package.

Provides the base tool class, individual tool implementations,
and the ToolRouter for question → tool routing.
"""

from tools.base import RichyToolBase
from tools.router import ToolRouter
from tools.smart_grocery import SmartGrocery
from tools.debt_destroyer import DebtDestroyer
from tools.savings_sage import SavingsSage
from tools.invest_intel import InvestIntel
from tools.tax_estimator import TaxEstimator
from tools.mortgage_calc import MortgageCalc
from tools.retirement_planner import RetirementPlanner
from tools.kid_coach import KidCoach
from tools.insurance_guide import InsuranceGuide
from tools.net_worth import NetWorthTracker
from tools.emergency_fund import EmergencyFund
from tools.subscription_tracker import SubscriptionTracker
from tools.bill_negotiator import BillNegotiator
from tools.side_hustle import SideHustle
from tools.inflation_impact import InflationImpact
from tools.goal_planner import GoalPlanner
from tools.portfolio_builder import PortfolioBuilder
from tools.economic_calendar import EconomicCalendar

__all__ = [
    "RichyToolBase",
    "ToolRouter",
    "SmartGrocery",
    "DebtDestroyer",
    "SavingsSage",
    "InvestIntel",
    "TaxEstimator",
    "MortgageCalc",
    "RetirementPlanner",
    "KidCoach",
    "InsuranceGuide",
    "NetWorthTracker",
    "EmergencyFund",
    "SubscriptionTracker",
    "BillNegotiator",
    "SideHustle",
    "InflationImpact",
    "GoalPlanner",
    "PortfolioBuilder",
    "EconomicCalendar",
]
