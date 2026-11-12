"""Google Cloud seat - the hosting plan for the service, PLAN ONLY.

ConnectionX's backend plan runs on Google Cloud: the service API on
Cloud Run, subscriber records modelled in Firestore, files in Cloud
Storage, and events on Pub/Sub. This module is the plan, not a
deployment: there are 0 live connections, no project is touched, and
deploying live is HOLD gate ``live_cloud_sync``. Any real deployment
needs Darion's own GCP project, sign-in, and billing - his steps.
"""
from __future__ import annotations

SERVICES = [
    {"service": "Cloud Run", "job": "host the ConnectionXService API", "scaling": "0 to 10 instances (modelled)"},
    {"service": "Firestore", "job": "subscriber records (modelled, synthetic only)", "scaling": "serverless"},
    {"service": "Cloud Storage", "job": "ledger exports, reports, backups", "scaling": "standard bucket (planned)"},
    {"service": "Pub/Sub", "job": "call / text / data events", "scaling": "serverless"},
    {"service": "Cloud Logging", "job": "service logs and council traces", "scaling": "serverless"},
]


def deployment_plan() -> dict:
    return {
        "platform": "Google Cloud",
        "services": SERVICES,
        "steps": [
            "owner creates or picks a GCP project (owner step)",
            "enable Cloud Run, Firestore, Cloud Storage, Pub/Sub APIs",
            "build the container from this repo's Dockerfile",
            "deploy to Cloud Run with synthetic data only",
            "point the app at the Cloud Run URL",
            "keep billing alerts on (owner account, owner control)",
        ],
        "deployed": False,
        "live_connections": 0,
        "gate": "live_cloud_sync = HOLD until the owner deploys it himself",
    }


def cloud_status() -> dict:
    return {"platform": "Google Cloud", "planned_services": len(SERVICES),
            "deployed": False, "live_connections": 0,
            "plan": deployment_plan()}
