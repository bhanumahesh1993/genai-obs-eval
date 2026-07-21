"""A simulated user that plays a persona so we can run whole
conversations without a human in the loop.

The stub below is scripted so the harness runs with no API key. In a
real suite you would replace `respond` with an LLM call whose system
prompt is the persona and goal, and whose reply is the user's next
message. Keep the interface identical and the harness never changes.
"""
from dataclasses import dataclass


@dataclass
class SimulatedUser:
    goal: str          # what this user is trying to achieve
    order_id: str      # the order they will name if asked
    persona: str = "polite, a little impatient"

    def opening(self) -> str:
        return f"Hi, I would like a refund for order {self.order_id}."

    def respond(self, agent_message: str) -> str:
        # A real user-simulator LLM would read agent_message and the
        # persona, then decide the next turn. The stub cooperates:
        text = agent_message.lower()
        if "order id" in text or "which order" in text:
            return f"It is {self.order_id}."
        if "anything else" in text:
            return "No, that is all. Thanks."
        return "Okay, thank you."
