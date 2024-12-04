from uuid import uuid4
from cobwebai.repositories.project_repository import ProjectRepository
from cobwebai.repositories.user_repository import UsersRepository
from cobwebai.models import Project, User
from datetime import datetime

def test_create_project(db_session):
    user_repo = UsersRepository(db_session)
    repo = ProjectRepository(db_session)

    # Создаём пользователя для связи с проектом
    user = {"username": "UniqueUser", "password": "securepassword123"}
    created_user = user_repo.create_user(user)

    # Данные проекта
    project_data = {"name": "Test Project", "user_id": created_user.user_id}
    created_project = repo.create_project(project_data)

    # Проверяем, что проект создан
    assert created_project is not None
    assert created_project.name == project_data["name"]
    assert created_project.user_id == created_user.user_id

def test_get_all_projects(db_session):
    user_repo = UsersRepository(db_session)
    repo = ProjectRepository(db_session)

    # Создаём пользователя для связи с проектом
    user = {"username": "UniqueUser", "password": "securepassword123"}
    created_user = user_repo.create_user(user)
    project_1_data = {"name": "Test Project 1", "user_id": created_user.user_id}
    created_project_1 = repo.create_project(project_1_data)
    project_2_data = {"name": "Test Project 2", "user_id": created_user.user_id}
    created_project_2 = repo.create_project(project_2_data)

    projects = repo.get_all_projects()
    assert len(projects) == 2
    assert created_project_1 in projects
    assert created_project_2 in projects

def test_get_projects_by_user(db_session):
    user_repo = UsersRepository(db_session)
    repo = ProjectRepository(db_session)

    # Создаём пользователей для связи с проектом
    user_1 = {"username": "User_1", "password": "securepassword123"}
    created_user_1 = user_repo.create_user(user_1)
    user_2 = {"username": "User_2", "password": "securepassword123"}
    created_user_2 = user_repo.create_user(user_2)
    project_1_data = {"name": "Test Project 1", "user_id": created_user_1.user_id}
    created_project_1 = repo.create_project(project_1_data)
    project_2_data = {"name": "Test Project 2", "user_id": created_user_1.user_id}
    created_project_2 = repo.create_project(project_2_data)
    project_3_data = {"name": "Test Project 3", "user_id": created_user_2.user_id}
    created_project_3 = repo.create_project(project_3_data)
    

    projects_1 = repo.get_projects_by_user(created_user_1.user_id)
    projects_2 = repo.get_projects_by_user(created_user_2.user_id)
    assert len(projects_1) == 2
    assert len(projects_2) == 1
    assert created_project_1 in projects_1
    assert created_project_2 in projects_1
    assert created_project_3 in projects_2

def test_get_project_by_id(db_session):
    user_repo = UsersRepository(db_session)
    repo = ProjectRepository(db_session)

    # Создаём пользователя для связи с проектом
    user = {"username": "UniqueUser", "password": "securepassword123"}
    created_user = user_repo.create_user(user)
    project_1_data = {"name": "Test Project 1", "user_id": created_user.user_id}
    created_project_1 = repo.create_project(project_1_data)
    project_2_data = {"name": "Test Project 2", "user_id": created_user.user_id}
    created_project_2 = repo.create_project(project_2_data)
    non_existent_id = uuid4()

    project_1 = repo.get_project_by_id(created_project_1.project_id)
    project_2 = repo.get_project_by_id(created_project_2.project_id)
    non_existent_project = repo.get_project_by_id(non_existent_id)
    assert non_existent_project is None
    assert created_project_1 is project_1
    assert created_project_2 is project_2

def test_update_project(db_session):
    user_repo = UsersRepository(db_session)
    repo = ProjectRepository(db_session)

    # Создаём пользователя для связи с проектом
    user = {"username": "UniqueUser", "password": "securepassword123"}
    created_user = user_repo.create_user(user)
    project_1_data = {"name": "Test Project 1", "user_id": created_user.user_id}
    created_project_1 = repo.create_project(project_1_data)
    non_existent_id = uuid4()
    

    project_1 = repo.get_project_by_id(created_project_1.project_id)
    last_data = {"project_id": project_1.project_id, "created_at": project_1.created_at, "updated_at": project_1.updated_at}
    project_2 = repo.update_project(project_1.project_id, updated_at=datetime(2024, 12, 3))
    non_existent_project = repo.get_project_by_id(non_existent_id)
    assert non_existent_project is None
    assert last_data["project_id"] == project_2.project_id
    assert last_data["created_at"] == project_2.created_at
    assert last_data["updated_at"] != project_2.updated_at

def test_delete_project(db_session):
    user_repo = UsersRepository(db_session)
    repo = ProjectRepository(db_session)

    # Создаём пользователя для связи с проектом
    user = {"username": "UniqueUser", "password": "securepassword123"}
    created_user = user_repo.create_user(user)
    project_1_data = {"name": "Test Project 1", "user_id": created_user.user_id}
    created_project_1 = repo.create_project(project_1_data)

    # Удаляем проект
    result = repo.delete_project(created_project_1.project_id)
    assert result is True

    # Проверяем, что проект удалён
    deleted_project = repo.get_project_by_id(created_project_1.project_id)
    assert deleted_project is None