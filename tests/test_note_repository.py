from uuid import uuid4
from cobwebai.repositories.note_repository import NoteRepository
from cobwebai.repositories.user_repository import UsersRepository
from cobwebai.repositories.project_repository import ProjectRepository
import time

def test_create_note(db_session):
    user_repo = UsersRepository(db_session)
    project_repo = ProjectRepository(db_session)
    repo = NoteRepository(db_session)

    # Создаём пользователя для связи с проектом
    user = {"username": "UniqueUser", "password": "securepassword123"}
    created_user = user_repo.create_user(user)

    # Данные проекта
    project_data = {"name": "Test Project", "user_id": created_user.user_id}
    created_project = project_repo.create_project(project_data)

    note_data = {
        "name": "Test Note",
        "content": "This is a test note",
        "project_id": created_project.project_id,
    }
    created_note = repo.create_note(note_data)

    assert created_note.name == note_data["name"]
    assert created_note.content == note_data["content"]
    assert created_note.project_id == note_data["project_id"]
    assert created_note.note_id is not None
    assert created_note.created_at is not None

def test_get_note_by_id(db_session):
    user_repo = UsersRepository(db_session)
    project_repo = ProjectRepository(db_session)
    repo = NoteRepository(db_session)

    # Создаём пользователя для связи с проектом
    user = {"username": "UniqueUser", "password": "securepassword123"}
    created_user = user_repo.create_user(user)

    # Данные проекта
    project_data = {"name": "Test Project", "user_id": created_user.user_id}
    created_project = project_repo.create_project(project_data)

    note_data = {
        "name": "Test Note",
        "content": "This is a test note",
        "project_id": created_project.project_id,
    }
    created_note = repo.create_note(note_data)

    # Проверяем, что заметку можно найти по ID
    found_note = repo.get_note_by_id(created_note.note_id)
    assert found_note is not None
    assert found_note.note_id == created_note.note_id

    # Проверяем, что несуществующий ID возвращает None
    non_existent_note = repo.get_note_by_id(uuid4())
    assert non_existent_note is None

def test_get_notes_by_project(db_session):
    user_repo = UsersRepository(db_session)
    project_repo = ProjectRepository(db_session)
    repo = NoteRepository(db_session)

    # Создаём пользователя для связи с проектом
    user = {"username": "UniqueUser", "password": "securepassword123"}
    created_user = user_repo.create_user(user)

    # Данные проектов
    project_1_data = {"name": "Test Project 1", "user_id": created_user.user_id}
    created_project_1 = project_repo.create_project(project_1_data)

    project_2_data = {"name": "Test Project 2", "user_id": created_user.user_id}
    created_project_2 = project_repo.create_project(project_2_data)

    note_1_data = {"name": "Note 1", "content": "Content 1", "project_id": created_project_1.project_id}
    note_2_data = {"name": "Note 2", "content": "Content 2", "project_id": created_project_1.project_id}
    note_3_data = {"name": "Note 3", "content": "Content 3", "project_id": created_project_2.project_id}  # Другая связь

    repo.create_note(note_1_data)
    repo.create_note(note_2_data)
    repo.create_note(note_3_data)

    project_notes = repo.get_notes_by_project(created_project_1.project_id)
    assert len(project_notes) == 2
    assert all(note.project_id == created_project_1.project_id for note in project_notes)

def test_update_note(db_session):
    user_repo = UsersRepository(db_session)
    project_repo = ProjectRepository(db_session)
    repo = NoteRepository(db_session)

    # Создаём пользователя и проект
    user = {"username": "UniqueUser", "password": "securepassword123"}
    created_user = user_repo.create_user(user)
    project_data = {"name": "Test Project", "user_id": created_user.user_id}
    created_project = project_repo.create_project(project_data)

    # Создаём заметку
    note_data = {"name": "Original Name", "content": "Original Content", "project_id": created_project.project_id}
    created_note = repo.create_note(note_data)

    # Обновляем заметку
    updated_note = repo.update_note(created_note.note_id, name="Updated Name", content="Updated Content")

    assert updated_note is not None
    assert updated_note.name == "Updated Name"
    assert updated_note.content == "Updated Content"
    assert updated_note.updated_at > created_note.created_at

def test_delete_note(db_session):
    user_repo = UsersRepository(db_session)
    project_repo = ProjectRepository(db_session)
    repo = NoteRepository(db_session)

    # Создаём пользователя для связи с проектом
    user = {"username": "UniqueUser", "password": "securepassword123"}
    created_user = user_repo.create_user(user)

    # Данные проекта
    project_data = {"name": "Test Project", "user_id": created_user.user_id}
    created_project = project_repo.create_project(project_data)

    note_data = {"name": "Test Note", "content": "This is test content", "project_id": created_project.project_id}
    created_note = repo.create_note(note_data)

    # Удаляем заметку
    assert repo.delete_note(created_note.note_id) is True

    # Проверяем, что заметка больше не существует
    assert repo.get_note_by_id(created_note.note_id) is None

    # Попытка удалить несуществующую заметку
    assert repo.delete_note(uuid4()) is False