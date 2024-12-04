from uuid import uuid4
from cobwebai.repositories.file_repository import FileRepository
from cobwebai.repositories.user_repository import UsersRepository
from cobwebai.repositories.project_repository import ProjectRepository
from cobwebai.models import File

def test_create_file(db_session):
    user_repo = UsersRepository(db_session)
    project_repo = ProjectRepository(db_session)
    repo = FileRepository(db_session)

    # Создаём пользователя для связи с проектом
    user = {"username": "UniqueUser", "password": "securepassword123"}
    created_user = user_repo.create_user(user)

    # Данные проекта
    project_data = {"name": "Test Project", "user_id": created_user.user_id}
    created_project = project_repo.create_project(project_data)

    file_data = {
        "name": "Test File",
        "content": "This is test content",
        "project_id": created_project.project_id,
    }
    created_file = repo.create_file(file_data)

    assert created_file.name == file_data["name"]
    assert created_file.content == file_data["content"]
    assert created_file.project_id == file_data["project_id"]
    assert created_file.file_id is not None
    assert created_file.created_at is not None

def test_get_file_by_id(db_session):
    user_repo = UsersRepository(db_session)
    project_repo = ProjectRepository(db_session)
    repo = FileRepository(db_session)

    # Создаём пользователя для связи с проектом
    user = {"username": "UniqueUser", "password": "securepassword123"}
    created_user = user_repo.create_user(user)

    # Данные проекта
    project_data = {"name": "Test Project", "user_id": created_user.user_id}
    created_project = project_repo.create_project(project_data)

    file_data = {
        "name": "Test File",
        "content": "This is test content",
        "project_id": created_project.project_id,
    }
    created_file = repo.create_file(file_data)

    # Проверяем, что файл можно найти по ID
    found_file = repo.get_file_by_id(created_file.file_id)
    assert found_file is not None
    assert found_file.file_id == created_file.file_id

    # Проверяем, что несуществующий ID возвращает None
    non_existent_file = repo.get_file_by_id(uuid4())
    assert non_existent_file is None

def test_get_files_by_project(db_session):
    user_repo = UsersRepository(db_session)
    project_repo = ProjectRepository(db_session)
    repo = FileRepository(db_session)

    # Создаём пользователя для связи с проектом
    user = {"username": "UniqueUser", "password": "securepassword123"}
    created_user = user_repo.create_user(user)

    # Данные проекта
    project_1_data = {"name": "Test Project 1", "user_id": created_user.user_id}
    created_project_1 = project_repo.create_project(project_1_data)

    project_2_data = {"name": "Test Project 2", "user_id": created_user.user_id}
    created_project_2 = project_repo.create_project(project_2_data)

    file_1_data = {"name": "File 1", "content": "Content 1", "project_id": created_project_1.project_id}
    file_2_data = {"name": "File 2", "content": "Content 2", "project_id": created_project_1.project_id}
    file_3_data = {"name": "File 3", "content": "Content 3", "project_id": created_project_2.project_id}  # Другая связь

    repo.create_file(file_1_data)
    repo.create_file(file_2_data)
    repo.create_file(file_3_data)

    project_files = repo.get_files_by_project(created_project_1.project_id)
    assert len(project_files) == 2
    assert all(file.project_id == created_project_1.project_id for file in project_files)

def test_get_all_files(db_session):
    user_repo = UsersRepository(db_session)
    project_repo = ProjectRepository(db_session)
    repo = FileRepository(db_session)

    # Создаём пользователя для связи с проектом
    user = {"username": "UniqueUser", "password": "securepassword123"}
    created_user = user_repo.create_user(user)

    # Данные проекта
    project_1_data = {"name": "Test Project 1", "user_id": created_user.user_id}
    created_project_1 = project_repo.create_project(project_1_data)

    project_2_data = {"name": "Test Project 2", "user_id": created_user.user_id}
    created_project_2 = project_repo.create_project(project_2_data)

    file_1_data = {"name": "File 1", "content": "Content 1", "project_id": created_project_1.project_id}
    file_2_data = {"name": "File 2", "content": "Content 2", "project_id": created_project_2.project_id}

    repo.create_file(file_1_data)
    repo.create_file(file_2_data)

    all_files = repo.get_all_files()
    assert len(all_files) == 2
    assert set(file.name for file in all_files) == {"File 1", "File 2"}

def test_delete_file(db_session):
    user_repo = UsersRepository(db_session)
    project_repo = ProjectRepository(db_session)
    repo = FileRepository(db_session)

    # Создаём пользователя для связи с проектом
    user = {"username": "UniqueUser", "password": "securepassword123"}
    created_user = user_repo.create_user(user)

    # Данные проекта
    project_data = {"name": "Test Project", "user_id": created_user.user_id}
    created_project = project_repo.create_project(project_data)

    file_data = {"name": "Test File", "content": "This is test content", "project_id": created_project.project_id}
    created_file = repo.create_file(file_data)

    # Удаляем файл
    assert repo.delete_file(created_file.file_id) is True

    # Проверяем, что файл больше не существует
    assert repo.get_file_by_id(created_file.file_id) is None

    # Попытка удалить несуществующий файл
    assert repo.delete_file(uuid4()) is False
