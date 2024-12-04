from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from cobwebai.models import Project

class ProjectRepository:
    def __init__(self, db_session: Session):
        self.db = db_session

    def create_project(self, project_data: dict) -> Project:
        new_project = Project(**project_data)
        self.db.add(new_project)
        self.db.commit()
        self.db.refresh(new_project)
        return new_project

    def get_project_by_id(self, project_id: UUID) -> Optional[Project]:
        return self.db.query(Project).filter_by(project_id=project_id).first()

    def get_all_projects(self) -> List[Project]:
        return self.db.query(Project).all()

    def get_projects_by_user(self, user_id: UUID) -> List[Project]:
        return self.db.query(Project).filter_by(user_id=user_id).all()

    def update_project(self, project_id: UUID, **kwargs) -> Optional[Project]:
        project = self.get_project_by_id(project_id)
        if not project:
            return None
        for key, value in kwargs.items():
            setattr(project, key, value)
        self.db.commit()
        self.db.refresh(project)
        return project

    def delete_project(self, project_id: UUID) -> bool:
        project = self.get_project_by_id(project_id)
        if not project:
            return False
        self.db.delete(project)
        self.db.commit()
        return True

