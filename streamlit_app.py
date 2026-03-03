"""Internal operator console for Partner OS v2."""

from __future__ import annotations

import json
from typing import Any

import requests
import streamlit as st


st.set_page_config(page_title="Partner OS v2 Console", layout="wide")


if "api_base" not in st.session_state:
    st.session_state["api_base"] = "http://127.0.0.1:8000"
if "token" not in st.session_state:
    st.session_state["token"] = ""
if "username" not in st.session_state:
    st.session_state["username"] = "admin"
if "password" not in st.session_state:
    st.session_state["password"] = "admin123"


def api_request(method: str, path: str, *, payload: dict[str, Any] | None = None) -> tuple[int, Any]:
    url = f"{st.session_state['api_base'].rstrip('/')}{path}"
    headers = {}
    if st.session_state.get("token"):
        headers["Authorization"] = f"Bearer {st.session_state['token']}"

    try:
        response = requests.request(method=method, url=url, headers=headers, json=payload, timeout=20)
    except requests.RequestException as exc:
        return 0, {"error": str(exc)}

    try:
        body = response.json()
    except ValueError:
        body = {"raw": response.text}

    return response.status_code, body


st.title("Partner OS v2 Operator Console")

with st.sidebar:
    st.subheader("Connection")
    st.text_input("API Base URL", key="api_base")
    st.text_input("Username", key="username")
    st.text_input("Password", type="password", key="password")

    if st.button("Login"):
        status, body = api_request(
            "POST",
            "/api/v1/auth/login",
            payload={"username": st.session_state["username"], "password": st.session_state["password"]},
        )
        if status == 200:
            st.session_state["token"] = body["access_token"]
            st.success("Authenticated")
        else:
            st.error(f"Login failed: {status} {body}")

    st.caption("Token set" if st.session_state.get("token") else "No token")


tab_health, tab_leads, tab_ai, tab_timeline = st.tabs(["Health", "Leads", "AI", "Timeline"])

with tab_health:
    if st.button("Refresh Health"):
        status, body = api_request("GET", "/api/v1/health")
        st.write(f"Status: {status}")
        st.json(body)

with tab_leads:
    st.subheader("Create Lead")
    with st.form("lead_create_form"):
        source = st.text_input("Source", value="referral")
        name = st.text_input("Name", value="")
        email = st.text_input("Email", value="")
        submitted = st.form_submit_button("Create Lead")
        if submitted:
            status, body = api_request(
                "POST",
                "/api/v1/leads",
                payload={"source": source, "name": name, "email": email or None},
            )
            st.write(f"Status: {status}")
            st.json(body)

    st.subheader("Transition Lead")
    with st.form("lead_transition_form"):
        lead_id = st.text_input("Lead ID")
        to_state = st.text_input("To State", value="attempted_contact")
        recommendation_id = st.text_input("Recommendation ID")
        reason = st.text_input("Reason", value="AI recommendation accepted")
        do_transition = st.form_submit_button("Transition")
        if do_transition:
            payload = {
                "to_state": to_state,
                "recommendation_id": recommendation_id or None,
                "reason": reason,
            }
            status, body = api_request("POST", f"/api/v1/leads/{lead_id}/transitions", payload=payload)
            st.write(f"Status: {status}")
            st.json(body)

with tab_ai:
    st.subheader("Create AI Session")
    with st.form("ai_session_form"):
        entity_type = st.selectbox("Entity Type", ["lead", "analysis", "deal", "case"])
        entity_id = st.text_input("Entity ID")
        context_payload_raw = st.text_area("Context JSON", value='{"intent": "review"}')
        create_session = st.form_submit_button("Create Session")
        if create_session:
            try:
                context_payload = json.loads(context_payload_raw or "{}")
            except json.JSONDecodeError as exc:
                st.error(f"Invalid JSON: {exc}")
            else:
                status, body = api_request(
                    "POST",
                    "/api/v1/ai/sessions",
                    payload={
                        "entity_type": entity_type,
                        "entity_id": entity_id,
                        "context_payload": context_payload,
                        "prompt_version": "v1",
                    },
                )
                st.write(f"Status: {status}")
                st.json(body)

    st.subheader("Generate Recommendation")
    with st.form("ai_reco_form"):
        session_id = st.text_input("Session ID")
        action = st.text_input("Action", value="lead_transition_attempted_contact")
        context_override_raw = st.text_area("Context Override JSON", value='{"note": "follow up now"}')
        generate = st.form_submit_button("Generate")
        if generate:
            try:
                context_override = json.loads(context_override_raw or "{}")
            except json.JSONDecodeError as exc:
                st.error(f"Invalid JSON: {exc}")
            else:
                status, body = api_request(
                    "POST",
                    "/api/v1/ai/recommendations",
                    payload={
                        "session_id": session_id,
                        "action": action,
                        "context_override": context_override,
                    },
                )
                st.write(f"Status: {status}")
                st.json(body)

    st.subheader("Approve Recommendation")
    with st.form("ai_approve_form"):
        recommendation_id = st.text_input("Recommendation ID")
        decision = st.selectbox("Decision", ["approved", "rejected"])
        reason = st.text_input("Reason", value="Manager review complete")
        approve = st.form_submit_button("Submit Decision")
        if approve:
            status, body = api_request(
                "POST",
                f"/api/v1/ai/recommendations/{recommendation_id}/approve",
                payload={"decision": decision, "reason": reason},
            )
            st.write(f"Status: {status}")
            st.json(body)

with tab_timeline:
    with st.form("timeline_form"):
        entity_type_filter = st.text_input("Entity Type (optional)")
        entity_id_filter = st.text_input("Entity ID (optional)")
        limit = st.number_input("Limit", min_value=1, max_value=500, value=100)
        fetch = st.form_submit_button("Fetch Timeline")
        if fetch:
            params = []
            if entity_type_filter:
                params.append(f"entity_type={entity_type_filter}")
            if entity_id_filter:
                params.append(f"entity_id={entity_id_filter}")
            params.append(f"limit={int(limit)}")
            query = "?" + "&".join(params)
            status, body = api_request("GET", f"/api/v1/timeline{query}")
            st.write(f"Status: {status}")
            st.json(body)
