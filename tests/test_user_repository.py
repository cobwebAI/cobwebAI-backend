import pytest
from sqlalchemy.exc import IntegrityError
from cobwebai.repositories.user_repository import UsersRepository
from cobwebai.models import User

def test_get_user_by_id(db_session):
    repo = UsersRepository(db_session)

    # Создаём пользователя
    user_data = {"username": "TestUser", "password": "securepassword123"}
    created_user = repo.create_user(user_data)

    # Проверяем получение пользователя по ID
    fetched_user = repo.get_user_by_id(created_user.user_id)
    assert fetched_user is not None
    assert fetched_user.user_id == created_user.user_id
    assert fetched_user.username == created_user.username

def test_get_all_users(db_session):
    repo = UsersRepository(db_session)

    # Создаём несколько пользователей
    user1 = repo.create_user({"username": "User1", "password": "pass1"})
    user2 = repo.create_user({"username": "User2", "password": "pass2"})

    # Проверяем получение всех пользователей
    users = repo.get_all_users()
    assert len(users) == 2
    assert user1 in users
    assert user2 in users

def test_get_user_by_username(db_session):
    repo = UsersRepository(db_session)

    # Создаём пользователя
    user_data = {"username": "TestUser", "password": "securepassword123"}
    created_user = repo.create_user(user_data)

    # Проверяем получение пользователя по username
    fetched_user = repo.get_user_by_username(user_data["username"])
    assert fetched_user is not None
    assert fetched_user.username == created_user.username
    assert fetched_user.password == created_user.password

def test_create_user(db_session):
    repo = UsersRepository(db_session)

    # Создаём пользователя
    user_data = {"username": "UniqueUser", "password": "securepassword123"}
    created_user = repo.create_user(user_data)

    # Проверяем, что пользователь был создан
    assert created_user is not None
    assert created_user.username == "UniqueUser"
    assert created_user.password == "securepassword123"

def test_delete_user(db_session):
    repo = UsersRepository(db_session)

    # Создаём пользователя
    user_data = {"username": "TestUser", "password": "securepassword123"}
    created_user = repo.create_user(user_data)

    # Удаляем пользователя
    repo.delete_user(created_user.user_id)

    # Проверяем, что пользователь был удалён
    deleted_user = repo.get_user_by_id(created_user.user_id)
    assert deleted_user is None

def test_unique_username_constraint(db_session):
    repo = UsersRepository(db_session)

    # Создаём пользователя
    user_data = {"username": "DuplicateUser", "password": "password1"}
    dup_user_data = {"username": "DuplicateUser", "password": "password2"}
    repo.create_user(user_data)

    # Пытаемся создать пользователя с таким же username
    with pytest.raises(IntegrityError):
        repo.create_user(dup_user_data)
