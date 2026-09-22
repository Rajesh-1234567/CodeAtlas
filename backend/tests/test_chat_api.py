from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_chat_endpoint_returns_answer(monkeypatch):
    def mock_chat(repository_id, request):
        return {
            "answer": "Payment processing is handled by the payment service.",
            "sources": [
                {
                    "file": "payment/service.py",
                    "start_line": 20,
                    "end_line": 48,
                    "symbol": "process_payment",
                }
            ],
        }

    monkeypatch.setattr(
        "app.main.chat_service.chat",
        mock_chat,
    )

    response = client.post(
        "/repositories/repo-123/chat",
        json={
            "question": "How does payment processing work?"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["answer"] == (
        "Payment processing is handled by the payment service."
    )

    assert len(data["sources"]) == 1
    assert data["sources"][0]["file"] == "payment/service.py"
    assert data["sources"][0]["start_line"] == 20
    assert data["sources"][0]["end_line"] == 48
    assert data["sources"][0]["symbol"] == "process_payment"


def test_chat_endpoint_returns_404_for_missing_repository(
    monkeypatch,
):
    from app.services.repository_service import (
        RepositoryNotFoundError,
    )

    def mock_chat(repository_id, request):
        raise RepositoryNotFoundError(
            "Repository not found."
        )

    monkeypatch.setattr(
        "app.main.chat_service.chat",
        mock_chat,
    )

    response = client.post(
        "/repositories/missing-repo/chat",
        json={
            "question": "How does authentication work?"
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == (
        "Repository not found."
    )


def test_chat_endpoint_rejects_empty_question():
    response = client.post(
        "/repositories/repo-123/chat",
        json={
            "question": ""
        },
    )

    assert response.status_code == 422


def test_chat_endpoint_rejects_missing_question():
    response = client.post(
        "/repositories/repo-123/chat",
        json={}
    )

    assert response.status_code == 422