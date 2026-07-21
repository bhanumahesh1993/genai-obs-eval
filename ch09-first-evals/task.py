"""The task under evaluation: a tiny support assistant.

The eval harness only cares that the task maps a question string
to an answer string. Swap this stub for a real model call and the
rest of the harness is unchanged.
"""
import os


def answer(question: str) -> str:
    """Return an answer to a support question."""
    # A real implementation would call an LLM here, for example:
    #   from openai import OpenAI          # use any capable model
    #   client = OpenAI()
    #   resp = client.chat.completions.create(
    #       model="gpt-5.2",               # use any capable model
    #       messages=[{"role": "user", "content": question}],
    #   )
    #   return resp.choices[0].message.content
    canned = {
        "How long do I have to return an item?":
            "You have 30 days from delivery to return an item.",
        "Do refunds cost anything?":
            "Refunds are completely free of charge.",
        "This is the third time I have contacted you!":
            "I am sorry for the trouble. Let me fix this now.",
    }
    return canned.get(question, "I am not sure, let me check.")
