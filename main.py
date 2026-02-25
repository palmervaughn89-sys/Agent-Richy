#!/usr/bin/env python3
"""Agent Richy — Interactive Financial Coaching for Everyone.

Entry point: routes users to the Youth or Adult module based on age.
"""

import sys
from agent_richy.profiles import UserProfile
from agent_richy.utils.helpers import (
    print_header,
    print_divider,
    wrap_text,
    prompt,
    parse_number,
    get_openai_client,
)

BANNER = r"""
 █████╗  ██████╗ ███████╗███╗   ██╗████████╗    ██████╗ ██╗ ██████╗██╗  ██╗██╗   ██╗
██╔══██╗██╔════╝ ██╔════╝████╗  ██║╚══██╔══╝    ██╔══██╗██║██╔════╝██║  ██║╚██╗ ██╔╝
███████║██║  ███╗█████╗  ██╔██╗ ██║   ██║       ██████╔╝██║██║     ███████║ ╚████╔╝
██╔══██║██║   ██║██╔══╝  ██║╚██╗██║   ██║       ██╔══██╗██║██║     ██╔══██║  ╚██╔╝
██║  ██║╚██████╔╝███████╗██║ ╚████║   ██║       ██║  ██║██║╚██████╗██║  ██║   ██║
╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝   ╚═╝       ╚═╝  ╚═╝╚═╝ ╚═════╝╚═╝  ╚═╝   ╚═╝
"""


def main() -> None:
    print(BANNER)
    print_header("Welcome to Agent Richy — Your Personal Financial Coach 💰")
    print(wrap_text(
        "I'm here to help EVERYONE level up financially — whether you're "
        "a kid learning about money, a teenager starting to earn, or an "
        "adult trying to break the paycheck-to-paycheck cycle.\n\n"
        "Let's start by getting to know you!"
    ))

    # --- Name ---
    name = prompt("What's your name?:")
    if not name:
        name = "Friend"

    # --- Age ---
    age = None
    while age is None:
        age_raw = parse_number(prompt("How old are you?:"))
        if age_raw and 5 <= age_raw <= 120:
            age = int(age_raw)
        else:
            print("Please enter a valid age (5–120).")

    # --- Create profile ---
    profile = UserProfile(name=name, age=age)

    # --- Optional LLM client ---
    llm_client = get_openai_client()
    if llm_client:
        print("\n🤖 AI assistant connected — I'll give personalized advice!")
    else:
        print("\n📚 Running in offline mode — you'll still get great guidance!")

    # --- Route to module ---
    if age < 18:
        print_divider()
        print(f"\n🎉 Hey {name}!  You're getting a head start on money skills — that's awesome!")
        print(wrap_text("Let me take you to the youth financial lab.\n"))
        from agent_richy.modules.youth import YouthModule
        module = YouthModule(profile, llm_client)
        module.run()
    else:
        print_divider()
        print(f"\n💪 {name}, let's take control of your financial future!")
        print(wrap_text("Heading to the adult financial planning suite.\n"))
        from agent_richy.modules.adult import AdultModule
        module = AdultModule(profile, llm_client)
        module.run()

    print_divider()
    print(wrap_text(
        "\nThanks for using Agent Richy!  Remember: small consistent actions "
        "beat big occasional efforts every single time.  You've got this! 🚀\n"
    ))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSee you next time!  Keep building that wealth! 💰")
        sys.exit(0)
