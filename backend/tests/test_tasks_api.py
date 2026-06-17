from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import date, timedelta
from app.models.task import Task

def test_tasks_crud_and_recurrence(client: TestClient, db: Session):
    # 1. Register and login
    reg_response = client.post("/api/auth/register", json={
        "username": "tasktester",
        "email": "tasktester@example.com",
        "password": "strongpassword123",
        "first_name": "Task",
        "last_name": "Tester"
    })
    assert reg_response.status_code == 201
    
    login_response = client.post("/api/auth/login", data={
        "username": "tasktester",
        "password": "strongpassword123"
    })
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Create apiary
    apiary_resp = client.post("/api/apiaries", json={
        "name": "Task Apiary",
        "address": "Hive Road 10"
    }, headers=headers)
    assert apiary_resp.status_code == 201
    apiary_id = apiary_resp.json()["id"]
    
    # 3. Create a task without recurrence
    today_str = date.today().isoformat()
    task_resp = client.post(f"/api/tasks?apiary_id={apiary_id}", json={
        "title": "Clean Hives",
        "description": "Perform spring cleaning",
        "due_date": today_str,
        "priority": "HIGH",
        "is_recurring": False
    }, headers=headers)
    assert task_resp.status_code == 201
    task_data = task_resp.json()
    assert task_data["title"] == "Clean Hives"
    assert task_data["description"] == "Perform spring cleaning"
    assert task_data["due_date"] == today_str
    assert task_data["priority"] == "HIGH"
    assert task_data["is_completed"] is False
    assert task_data["is_recurring"] is False
    task_id = task_data["id"]
    
    # 4. List tasks (should have 1 task)
    list_resp = client.get(f"/api/tasks?apiary_id={apiary_id}", headers=headers)
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1
    
    # 5. Complete task
    complete_resp = client.post(f"/api/tasks/{task_id}/complete", headers=headers)
    assert complete_resp.status_code == 200
    assert complete_resp.json()["is_completed"] is True
    assert complete_resp.json()["completed_at"] is not None
    
    # List pending tasks (should have 0)
    list_pending_resp = client.get(f"/api/tasks?apiary_id={apiary_id}&is_completed=false", headers=headers)
    assert len(list_pending_resp.json()) == 0
    
    # 6. Create a recurring task (Weekly)
    rec_task_resp = client.post(f"/api/tasks?apiary_id={apiary_id}", json={
        "title": "Water feeder",
        "due_date": today_str,
        "priority": "MEDIUM",
        "is_recurring": True,
        "recurrence_interval": "WEEKLY"
    }, headers=headers)
    assert rec_task_resp.status_code == 201
    rec_task_id = rec_task_resp.json()["id"]
    
    # Complete the recurring task
    rec_complete_resp = client.post(f"/api/tasks/{rec_task_id}/complete", headers=headers)
    assert rec_complete_resp.status_code == 200
    
    # It should have automatically spawned a new task for next week
    list_all_resp = client.get(f"/api/tasks?apiary_id={apiary_id}", headers=headers)
    all_tasks = list_all_resp.json()
    assert len(all_tasks) == 3  # Clean Hives (completed), Water feeder (completed), Water feeder (pending next week)
    
    pending_task = next(t for t in all_tasks if not t["is_completed"])
    assert pending_task["title"] == "Water feeder"
    
    expected_next_due = (date.today() + timedelta(weeks=1)).isoformat()
    assert pending_task["due_date"] == expected_next_due
    assert pending_task["is_recurring"] is True
    assert pending_task["recurrence_interval"] == "WEEKLY"
    
    # 7. Delete task
    delete_resp = client.delete(f"/api/tasks/{rec_task_id}", headers=headers)
    assert delete_resp.status_code == 204
    
    # Check that deleted task is gone
    final_list_resp = client.get(f"/api/tasks?apiary_id={apiary_id}", headers=headers)
    assert len(final_list_resp.json()) == 2


def test_tasks_outlook_recurrence(client: TestClient, db: Session):
    # 1. Register and login
    reg_response = client.post("/api/auth/register", json={
        "username": "recurrence_tester",
        "email": "rectest@example.com",
        "password": "strongpassword123",
        "first_name": "Rec",
        "last_name": "Tester"
    })
    assert reg_response.status_code == 201
    
    login_response = client.post("/api/auth/login", data={
        "username": "recurrence_tester",
        "password": "strongpassword123"
    })
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Create apiary
    apiary_resp = client.post("/api/apiaries", json={
        "name": "Recur Test Apiary",
        "address": "Recur Lane 1"
    }, headers=headers)
    assert apiary_resp.status_code == 201
    apiary_id = apiary_resp.json()["id"]
    
    # 3. Create a task with WEEKLY recurrence, every 2 weeks, on Mondays (0) and Wednesdays (2)
    # Let's anchor the due date to a specific known date to make assertions deterministic
    # Let's choose 2026-06-15 which is a Monday.
    due_date_str = "2026-06-15"
    end_date_str = "2026-06-30"  # Recurrence end limit
    
    task_resp = client.post(f"/api/tasks?apiary_id={apiary_id}", json={
        "title": "Recurring Clean",
        "due_date": due_date_str,
        "priority": "LOW",
        "is_recurring": True,
        "is_all_day": False,
        "due_time": "10:30",
        "recurrence_interval_type": "WEEKLY",
        "recurrence_interval_value": 2,
        "recurrence_weekdays": "0,2",
        "recurrence_end_date": end_date_str
    }, headers=headers)
    assert task_resp.status_code == 201
    task_data = task_resp.json()
    assert task_data["is_all_day"] is False
    assert task_data["due_time"] == "10:30"
    assert task_data["recurrence_interval_type"] == "WEEKLY"
    assert task_data["recurrence_interval_value"] == 2
    assert task_data["recurrence_weekdays"] == "0,2"
    assert task_data["recurrence_end_date"] == end_date_str
    task_id = task_data["id"]
    
    # 4. Complete this task (it is set to 2026-06-15, which is a Monday)
    # The next weekday in "0,2" (Mon, Wed) is Wednesday (2), which is 2026-06-17.
    complete_resp = client.post(f"/api/tasks/{task_id}/complete", headers=headers)
    assert complete_resp.status_code == 200
    
    # Verify a new task was spawned for Wednesday 2026-06-17
    list_resp = client.get(f"/api/tasks?apiary_id={apiary_id}&is_completed=false", headers=headers)
    assert list_resp.status_code == 200
    pending_tasks = list_resp.json()
    assert len(pending_tasks) == 1
    next_task = pending_tasks[0]
    assert next_task["due_date"] == "2026-06-17"
    assert next_task["due_time"] == "10:30"
    assert next_task["is_all_day"] is False
    next_task_id = next_task["id"]
    
    # 5. Complete this task (2026-06-17, which is a Wednesday)
    # Since there are no more active weekdays this week (Wed is the last one, Mon was already passed),
    # it must skip to the next week interval (value = 2 weeks).
    # Next occurrence starts in 2 weeks on Monday: (2026-06-15 + 2 weeks) = 2026-06-29.
    complete2_resp = client.post(f"/api/tasks/{next_task_id}/complete", headers=headers)
    assert complete2_resp.status_code == 200
    
    # Verify the new task is spawned for 2026-06-29
    list_resp2 = client.get(f"/api/tasks?apiary_id={apiary_id}&is_completed=false", headers=headers)
    pending_tasks2 = list_resp2.json()
    assert len(pending_tasks2) == 1
    next_task2 = pending_tasks2[0]
    assert next_task2["due_date"] == "2026-06-29"
    next_task2_id = next_task2["id"]
    
    # 6. Complete this task (2026-06-29, Monday)
    # Next weekday in "0,2" is Wed, 2026-07-01. But the recurrence_end_date is 2026-06-30.
    # Therefore, NO new task should be spawned because 2026-07-01 > 2026-06-30.
    complete3_resp = client.post(f"/api/tasks/{next_task2_id}/complete", headers=headers)
    assert complete3_resp.status_code == 200
    
    # Verify no pending tasks are left
    list_resp3 = client.get(f"/api/tasks?apiary_id={apiary_id}&is_completed=false", headers=headers)
    assert len(list_resp3.json()) == 0

