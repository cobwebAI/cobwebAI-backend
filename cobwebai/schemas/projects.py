from uuid import UUID
from pydantic import BaseModel, Field
from typing import Literal
from datetime import datetime

from .files import FileShort
from .tests import TestShort
from .notes import NoteShort
from .chats import ChatShort


class ProjectShort(BaseModel):
    id: UUID = Field(validation_alias="project_id")
    name: str


class GetProjectsResponse(BaseModel):
    projects: list[ProjectShort]


class CreateProjectRequest(BaseModel):
    name: str


class GetProjectResponse(BaseModel):
    id: UUID = Field(validation_alias="project_id")
    name: str

    files: list[FileShort]
    tests: list[TestShort]
    notes: list[NoteShort]
    chats: list[ChatShort]


class UpdateProjectRequest(BaseModel):
    name: str
