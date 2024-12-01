from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from cobwebai.models import File

class FileRepository:
    def __init__(self, db_session: Session):
        self.db = db_session

    def create_file(self, file_data: dict) -> File:
        new_file = File(**file_data)
        self.db.add(new_file)
        self.db.commit()
        self.db.refresh(new_file)
        return new_file

    def get_file_by_id(self, file_id: UUID) -> Optional[File]:
        return self.db.query(File).filter_by(file_id=file_id).first()

    def get_files_by_project(self, project_id: UUID) -> List[File]:
        return self.db.query(File).filter_by(project_id=project_id).all()

    def get_all_files(self) -> List[File]:
        return self.db.query(File).all()

    def delete_file(self, file_id: UUID) -> bool:
        file = self.get_file_by_id(file_id)
        if not file:
            return False
        self.db.delete(file)
        self.db.commit()
        return True
