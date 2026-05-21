from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import pytest
import json

from app.models.sales import ProductConfig, HoneySale
from app.models.honey_batch import HoneyBatch

class MockFunction:
    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments

class MockToolCall:
    def __init__(self, id, name, arguments):
        self.id = id
        self.function = MockFunction(name, arguments)

class MockMessage:
    def __init__(self, content, tool_calls=None):
        self.content = content
        self.tool_calls = tool_calls
        self.role = "assistant"
    
    def model_dump(self):
        return {
            "role": self.role,
            "content": self.content,
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                } for tc in self.tool_calls
            ] if self.tool_calls else None
        }

class MockChoice:
    def __init__(self, message, finish_reason):
        self.message = message
        self.finish_reason = finish_reason

class MockResponse:
    def __init__(self, choices):
        self.choices = choices


@pytest.mark.asyncio
async def test_ai_log_honey_sale_tool(client: TestClient, db: Session):
    # 1. Register and login to get authorization headers and current_user
    reg_response = client.post("/api/auth/register", json={
        "username": "aitester",
        "email": "aitester@example.com",
        "password": "strongpassword123",
        "first_name": "AI",
        "last_name": "Tester"
    })
    assert reg_response.status_code == 201
    
    login_response = client.post("/api/auth/login", data={
        "username": "aitester",
        "password": "strongpassword123"
    })
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create an Apiary
    apiary_resp = client.post("/api/apiaries", json={
        "name": "AI Apiary",
        "address": "AI Road 1"
    }, headers=headers)
    assert apiary_resp.status_code == 201
    apiary_id = apiary_resp.json()["id"]

    # Create a batch
    batch_resp = client.post(f"/api/honey-batches?apiary_id={apiary_id}", json={
        "batch_number": "L-02",
        "honey_type": "Rapshonig",
        "harvest_date": "2026-05-20",
        "quantity_kg": 50.0,
        "best_before_date": "2028-05-20",
        "is_exact_date": False
    }, headers=headers)
    assert batch_resp.status_code == 201

    # First mock response will call the tool log_honey_sale
    tool_call = MockToolCall(
        id="call_1",
        name="log_honey_sale",
        arguments='{"product_name": "Rapshonig", "quantity": 3, "total_price": 18, "sales_channel": "verkaufsstand", "batch_number": "L-02"}'
    )
    first_choice = MockChoice(
        message=MockMessage(content=None, tool_calls=[tool_call]),
        finish_reason="tool_calls"
    )
    
    # Second mock response returns the final user message
    second_choice = MockChoice(
        message=MockMessage(content="Ich habe den Verkauf von 3 Gläsern Rapshonig für 18€ am Verkaufsstand verbucht und mit Charge L-02 verknüpft."),
        finish_reason="stop"
    )
    
    responses = [MockResponse([first_choice]), MockResponse([second_choice])]
    
    with patch("litellm.acompletion", new_callable=AsyncMock) as mock_acompletion:
        mock_acompletion.side_effect = responses
        
        chat_resp = client.post(
            f"/api/ai/chat?apiary_id={apiary_id}",
            json={"query": "Notiere einen Verkauf: 3 Gläser Rapshonig für insgesamt 18 Euro am Verkaufsstand. Charge L-02."},
            headers=headers
        )
        assert chat_resp.status_code == 200
        data = chat_resp.json()
        assert "verbucht" in data["response"]

        # Check DB that the sale was actually logged
        sales = db.query(HoneySale).all()
        assert len(sales) == 1
        sale = sales[0]
        assert sale.quantity == 3
        assert sale.total_price == 18
        assert sale.sales_channel == "verkaufsstand"
        assert sale.batch is not None
        assert sale.batch.batch_number == "L-02"
        assert sale.product.name == "Rapshonig"
        assert sale.product.tax_rate == 7.0
