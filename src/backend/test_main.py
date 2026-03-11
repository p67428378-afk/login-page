from fastapi.testclient import TestClient
from .main import app

client = TestClient(app)

def test_logout_functionality():
    # Simulate a login to get a session token
    login_response = client.post(
        "/api/login",
        data={"username": "testuser", "password": "testpassword"}
    )
    assert login_response.status_code == 200
    session_token = login_response.cookies.get("session_token")
    assert session_token is not None

    # Simulate logout with the session token
    logout_response = client.get(
        "/api/logout",
        cookies={"session_token": session_token}
    )
    assert logout_response.status_code == 200
    assert logout_response.json() == {"message": "Logged out successfully"}

    # Verify that the session token cookie is deleted
    assert "session_token" not in logout_response.cookies

    # Try to access a protected endpoint after logout
    protected_response = client.get(
        "/api/user",
        cookies={"session_token": session_token}
    )
    assert protected_response.status_code == 401
    assert protected_response.json() == {"detail": "Invalid session token"}
