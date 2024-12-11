import base64

from tests.conftest import test_session
from user.service.authentication import encode_access_token
from user.models import User




def test_health_check(client, test_session):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"ping": "pong"}


def test_user_sign_up(client, test_session):
    # given:

    # when
    response = client.post(
        "/users",
        json={"username": "test_user", "password": "pw"},
    )
    # then:
    assert response.status_code == 201
    assert response.json()["id"]
    assert response.json()["username"] == "test_user"
    assert response.json()["password"]

    assert test_session.query(User).filter_by(username="test_user").first()

def test_user_login(client, test_session):
    # given
    new_user = User.create(username="test_user", password="pw")
    test_session.add(new_user)
    test_session.commit()

    # when
    encoded_bytes = base64.b64encode(b"test_user:pw")

    response = client.post(
        "/users/login",
        headers={"Authorization": "Basic " + encoded_bytes.decode("utf-8")},
    )
    # then
    assert response.status_code == 200
    assert response.json()["access_token"]

def test_get_me(client, test_session):
    # given
    new_user = User.create(username="test_user", password="pw")
    test_session.add(new_user)
    test_session.commit()

    access_token = encode_access_token(user_id=new_user.id)
    # when
    response = client.get(
        "/users/me",
        headers={"Authorization": "bearer " + access_token},
    )
    # then
    assert response.status_code == 200
    assert response.json()["id"] == new_user.id
    assert response.json()["username"] == new_user.username
    assert response.json()["password"] == new_user.password

def test_update_me(client, test_session):
    # given
    new_user = User.create(username="test_user", password="pw")
    test_session.add(new_user)
    test_session.commit()

    old_password = new_user.password

    access_token = encode_access_token(user_id=new_user.id)
    # when
    response = client.patch(
        "/users/me",
        json={"new_password": "new_password"},
        headers={"Authorization": "bearer " + access_token},
    )
    # then
    assert response.status_code == 200
    assert response.json()["id"] == new_user.id
    assert response.json()["username"] == new_user.username
    assert response.json()["password"] != old_password

def test_delete_me(client, test_session):
    # given
    new_user = User.create(username="test_user", password="pw")
    test_session.add(new_user)
    test_session.commit()
    access_token = encode_access_token(user_id=new_user.id)
    # when
    response = client.delete(
        "/users/me",
        headers={"Authorization": "bearer " + access_token},
    )
    # then
    assert response.status_code == 204
