import datetime
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from .validation import (
    BaseValidationModel, 
    TaskValidationMixin, 
    ThreadValidationMixin,
    UUIDValidationMixin
)


class ListThreadTask(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str
    task_text: str
    created_at: Optional[datetime.datetime]


class RetrieveThread(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    status: str
    created_at: Optional[datetime.datetime]
    thread_tasks: List[ListThreadTask]


class ListThread(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    status: str
    created_at: Optional[datetime.datetime]


class CreateThread(BaseValidationModel, TaskValidationMixin):
    task: str = Field(..., min_length=3, max_length=5000)
    background_mode: Optional[bool] = False
    extended_thinking_mode: Optional[bool] = False


class UpdateThread(BaseValidationModel, ThreadValidationMixin):
    title: str = Field(..., min_length=1, max_length=200)


class ListThreadMessage(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    thread_task: Optional[ListThreadTask]
    thread_chat_type: str
    thread_chat_from: str
    text: Optional[str]
    chain_of_thought: Optional[str]
    created_at: Optional[datetime.datetime]


class SendMessageObj(BaseValidationModel, TaskValidationMixin):
    text: str = Field(..., min_length=3, max_length=5000)
    background_mode: Optional[bool] = False
    extended_thinking_mode: Optional[bool] = False
