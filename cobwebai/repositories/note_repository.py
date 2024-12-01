from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from cobwebai.models import Note
from datetime import datetime, timezone

class NoteRepository:
    def __init__(self, db_session: Session):
        self.db = db_session

    def create_note(self, note_data: dict) -> Note:
        """
        Создает новую заметку в базе данных.
        """
        new_note = Note(**note_data)
        self.db.add(new_note)
        self.db.commit()
        self.db.refresh(new_note)
        return new_note

    def get_note_by_id(self, note_id: UUID) -> Optional[Note]:
        """
        Возвращает заметку по её уникальному идентификатору.
        """
        return self.db.query(Note).filter_by(note_id=note_id).first()

    def get_notes_by_project(self, project_id: UUID) -> List[Note]:
        """
        Возвращает список заметок, связанных с конкретным проектом.
        """
        return self.db.query(Note).filter_by(project_id=project_id).all()

    def get_all_notes(self) -> List[Note]:
        """
        Возвращает список всех заметок в базе данных.
        """
        return self.db.query(Note).all()

    def update_note(self, note_id: UUID, **kwargs) -> Optional[Note]:
        """
        Обновляет данные заметки.
        """
        note = self.get_note_by_id(note_id)
        if not note:
            return None
        for key, value in kwargs.items():
            setattr(note, key, value)
        note.updated_at = datetime.now(tz=timezone.utc)
        self.db.commit()
        self.db.refresh(note)
        return note

    def delete_note(self, note_id: UUID) -> bool:
        """
        Удаляет заметку по её идентификатору.
        """
        note = self.get_note_by_id(note_id)
        if not note:
            return False
        self.db.delete(note)
        self.db.commit()
        return True