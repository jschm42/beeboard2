"""Tests for the Bee-Agent job CRUD and proposal acceptance."""
import pytest
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


def _register_and_login(client: TestClient, username: str) -> tuple[str, str]:
    """Helper: register a user, login, return (token, apiary_id)."""
    client.post("/api/auth/register", json={
        "username": username,
        "email": f"{username}@example.com",
        "password": "strongpassword123",
        "first_name": "Bee",
        "last_name": "Agent",
    })
    resp = client.post("/api/auth/login", data={
        "username": username, "password": "strongpassword123"
    })
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    apiary_resp = client.post("/api/apiaries", json={"name": f"{username} Apiary"}, headers=headers)
    apiary_id = apiary_resp.json()["id"]
    return token, apiary_id


def test_bee_agent_job_crud(client: TestClient, db: Session):
    token, apiary_id = _register_and_login(client, "beejobuser")
    headers = {"Authorization": f"Bearer {token}"}

    # Create job
    create_resp = client.post(
        f"/api/bee-agent/jobs?apiary_id={apiary_id}",
        json={
            "name": "Varroa-Überwachung",
            "custom_prompt": "Strenge Varroa-Kontrolle bitte.",
            "scope": "IMKEREI",
            "include_weather_data": False,
            "include_locations": True,
            "include_hives": True,
            "include_journal_entries": True,
            "max_journal_entries": 10,
            "cron_expression": "0 8 * * *",
            "is_active": True,
            "execution_mode": "SUGGESTION",
        },
        headers=headers,
    )
    assert create_resp.status_code == 201
    job = create_resp.json()
    assert job["name"] == "Varroa-Überwachung"
    assert job["scope"] == "IMKEREI"
    assert job["include_locations"] is True
    assert job["include_hives"] is True
    assert job["execution_mode"] == "SUGGESTION"
    assert job["is_active"] is True
    job_id = job["id"]

    # List jobs
    list_resp = client.get(f"/api/bee-agent/jobs?apiary_id={apiary_id}", headers=headers)
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1

    # Update job
    update_resp = client.put(
        f"/api/bee-agent/jobs/{job_id}",
        json={"name": "Varroa-Überwachung (aktualisiert)", "is_active": False},
        headers=headers,
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["name"] == "Varroa-Überwachung (aktualisiert)"
    assert update_resp.json()["is_active"] is False

    # Delete job
    del_resp = client.delete(f"/api/bee-agent/jobs/{job_id}", headers=headers)
    assert del_resp.status_code == 204

    # Confirm deletion
    list_after = client.get(f"/api/bee-agent/jobs?apiary_id={apiary_id}", headers=headers)
    assert len(list_after.json()) == 0


def test_bee_agent_proposal_accept(client: TestClient, db: Session):
    """Accepting a proposal must create a task and mark the proposal as accepted."""
    token, apiary_id = _register_and_login(client, "beeproposaluser")
    headers = {"Authorization": f"Bearer {token}"}

    # Create job
    job_resp = client.post(
        f"/api/bee-agent/jobs?apiary_id={apiary_id}",
        json={
            "name": "Test Job",
            "scope": "IMKEREI",
            "cron_expression": "0 8 * * *",
            "execution_mode": "SUGGESTION",
        },
        headers=headers,
    )
    assert job_resp.status_code == 201
    job_id = job_resp.json()["id"]

    # Insert a proposal directly via DB (simulates what the cron job would do)
    from app.models.bee_agent import BeeAgentProposal
    proposal = BeeAgentProposal(
        job_id=job_id,
        apiary_id=apiary_id,
        title="Varroa behandeln",
        description="Hohe Milbenzahl festgestellt.",
        priority="HIGH",
    )
    db.add(proposal)
    db.commit()
    db.refresh(proposal)
    proposal_id = proposal.id

    # List proposals
    list_resp = client.get(
        f"/api/bee-agent/proposals?apiary_id={apiary_id}", headers=headers
    )
    assert list_resp.status_code == 200
    proposals = list_resp.json()
    assert len(proposals) == 1
    assert proposals[0]["is_accepted"] is False

    # Accept proposal → creates a task
    accept_resp = client.post(
        f"/api/bee-agent/proposals/{proposal_id}/accept", headers=headers
    )
    assert accept_resp.status_code == 200
    data = accept_resp.json()
    assert data["status"] == "success"
    task_id = data["task_id"]

    # Verify task was created
    task_resp = client.get(f"/api/tasks?apiary_id={apiary_id}", headers=headers)
    assert task_resp.status_code == 200
    tasks = task_resp.json()
    assert any(t["id"] == task_id for t in tasks)
    created_task = next(t for t in tasks if t["id"] == task_id)
    assert created_task["title"] == "Varroa behandeln"
    assert created_task["priority"] == "HIGH"

    # Proposal is now marked accepted
    list_after = client.get(
        f"/api/bee-agent/proposals?apiary_id={apiary_id}", headers=headers
    )
    assert list_after.json()[0]["is_accepted"] is True

    # Accepting again must fail
    second_accept = client.post(
        f"/api/bee-agent/proposals/{proposal_id}/accept", headers=headers
    )
    assert second_accept.status_code == 400


def test_bee_agent_invalid_scope(client: TestClient, db: Session):
    """Creating a job with an invalid scope must return 400."""
    token, apiary_id = _register_and_login(client, "beeinvalidscope")
    headers = {"Authorization": f"Bearer {token}"}

    # Scope validation should raise bad request
    resp = client.post(
        f"/api/bee-agent/jobs?apiary_id={apiary_id}",
        json={
            "name": "Bad Job",
            "scope": "INVALID_SCOPE",
            "cron_expression": "0 8 * * *",
        },
        headers=headers,
    )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_bee_agent_prompt_builder(db: Session):
    """BeeAgentPromptBuilder should produce a non-empty system prompt."""
    from app.models.bee_agent import BeeAgentJob
    from app.services.bee_agent_prompt_builder import BeeAgentPromptBuilder

    # Create a minimal job object (not persisted to DB; we just test prompt building)
    job = BeeAgentJob(
        name="Test",
        apiary_id="fake-apiary-id",
        scope="IMKEREI",
        include_weather_data=False,
        include_journal_entries=False,
        execution_mode="SUGGESTION",
        cron_expression="0 8 * * *",
    )

    builder = BeeAgentPromptBuilder(job, db)
    prompt = await builder.build_system_prompt()
    assert "proposals" in prompt
    assert "JSON" in prompt


@pytest.mark.asyncio
async def test_bee_agent_prompt_builder_with_custom_prompt(db: Session):
    """Custom prompt suffix must be present in the assembled system prompt."""
    from app.models.bee_agent import BeeAgentJob
    from app.services.bee_agent_prompt_builder import BeeAgentPromptBuilder

    job = BeeAgentJob(
        name="Custom Prompt Job",
        apiary_id="fake-apiary-id",
        scope="IMKEREI",
        include_weather_data=False,
        include_journal_entries=False,
        execution_mode="SUGGESTION",
        cron_expression="0 8 * * *",
        custom_prompt="Achte besonders auf Varroa.",
    )

    builder = BeeAgentPromptBuilder(job, db)
    prompt = await builder.build_system_prompt()
    assert "Achte besonders auf Varroa." in prompt


@pytest.mark.asyncio
async def test_bee_agent_prompt_builder_with_weather(db: Session):
    """If include_weather_data is True, weather data context must be appended."""
    from app.models.bee_agent import BeeAgentJob
    from app.models.location import Location
    from app.services.bee_agent_prompt_builder import BeeAgentPromptBuilder

    # Setup location with coordinates
    loc = Location(
        name="Test Stand",
        address="Test Address",
        apiary_id="fake-apiary-id",
        latitude=48.208,
        longitude=16.373,
    )
    db.add(loc)

    db.commit()
    db.refresh(loc)

    job = BeeAgentJob(
        name="Weather Job",
        apiary_id="fake-apiary-id",
        scope="IMKEREI",
        include_weather_data=True,
        include_journal_entries=False,
        execution_mode="SUGGESTION",
        cron_expression="0 8 * * *",
    )

    mock_weather = {
        "temp": 18.5,
        "humidity": 65,
        "wind_speed": 3.2,
        "weather": [{"description": "leicht bewölkt"}]
    }

    with patch("app.services.weather.fetch_current_weather", new_callable=AsyncMock, return_value=mock_weather):
        builder = BeeAgentPromptBuilder(job, db)
        prompt = await builder.build_system_prompt()
        assert "Test Stand" in prompt
        assert "18.5" in prompt
        assert "leicht bewölkt" in prompt

    # Cleanup
    db.delete(loc)
    db.commit()




