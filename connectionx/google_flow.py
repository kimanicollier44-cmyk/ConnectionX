"""Google Flow seat - ALL 4 flows, PLAN ONLY.

FlowX, Workspace Studio, Flow Filmmaking, and the DataX google_flow
engine, routed for both brains (the Gemini Argon 4 Extended Thinking
decider and the Muse advisor). Nothing is rendered, sent, or
generated live: live video generation is HOLD gate
``live_video_generation``, and every plan carries rendered=False
and live_calls=0.
"""
from __future__ import annotations

FLOWX_SUBTASKS = [
    "ingest topic", "outline beats", "draft script", "split scenes",
    "write image prompts", "write motion prompts", "plan transitions",
    "plan captions", "plan voiceover", "assemble timeline",
    "export storyboard", "export shot list", "archive plan",
]

BRAINS = ["Gemini Argon 4 Extended Thinking", "Muse"]


def flowx(topic: str) -> dict:
    return {"flow": "FlowX", "topic": topic, "brains": BRAINS,
            "subtasks": FLOWX_SUBTASKS, "subtask_count": len(FLOWX_SUBTASKS),
            "queue_wait": 0, "rendered": False, "live_calls": 0}


def workspace_studio(topic: str) -> dict:
    return {"flow": "Workspace Studio", "topic": topic, "brains": BRAINS,
            "starters": ["gmail email_trigger", "google_forms form_trigger",
                         "webhook webhook_listener"],
            "steps": ["send_chat_message", "card_layout"],
            "plan": [f"Doc outline for '{topic}'", "Slide beats (5)",
                     "Speaker notes draft", "Share list: owner only"],
            "sent_anywhere": False, "rendered": False, "live_calls": 0}


def filmmaking(topic: str) -> dict:
    scenes = [
        {"track": "setup", "seconds": 6,
         "prompt": f"Title card: '{topic}' over a free phone ringing on Wi-Fi, dark navy neon"},
        {"track": "explain", "seconds": 20,
         "prompt": f"Narrated walkthrough of {topic}: plastic SIM becomes eSIM, SMS becomes RCS, step by step"},
        {"track": "diagram", "seconds": 14,
         "prompt": f"Animated diagram for {topic}: a call hops phone to Wi-Fi to tower to internet"},
        {"track": "recap", "seconds": 8,
         "prompt": "Recap card: talk $0, text $0, bill $0, then the ConnectionX title"},
    ]
    return {"flow": "Flow Filmmaking", "topic": topic, "brains": BRAINS,
            "tracks": ["setup", "explain", "diagram", "recap"],
            "scenes": scenes,
            "total_seconds": sum(s["seconds"] for s in scenes),
            "rendered": False, "live_calls": 0,
            "render": "HOLD - plan only; rendering needs Darion's own Google Flow access"}


def datax_flow(topic: str) -> dict:
    return {"flow": "DataX google_flow", "engine_id": "google_flow",
            "topic": topic, "brains": BRAINS,
            "plan": ["route topic to FlowX", "attach filmmaking storyboard",
                     "log plan in registry"],
            "rendered": False, "live_calls": 0}


def merged_plan(topic: str = "ConnectionX: a free phone service, everything upgraded") -> dict:
    flows = [flowx(topic), workspace_studio(topic), filmmaking(topic),
             datax_flow(topic)]
    return {"topic": topic, "flows": flows,
            "flow_names": [f["flow"] for f in flows],
            "all_flows_used": len(flows) == 4,
            "total_live_calls": sum(f["live_calls"] for f in flows),
            "anything_rendered": any(f["rendered"] for f in flows)}


def carbon_flow_plan(topic: str) -> dict:
    """The plan as routed for the Argon 4 decider."""
    plan = merged_plan(topic)
    plan["brain"] = "Gemini Argon 4 Extended Thinking"
    return plan


def muse_flow_plan(topic: str) -> dict:
    """The plan as routed for the Muse advisor."""
    plan = merged_plan(topic)
    plan["brain"] = "Muse"
    return plan
