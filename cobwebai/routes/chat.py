import uuid
import asyncio
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from cobwebai.repository.chats import ChatsRepository
from cobwebai.repository.files import FilesRepository
from cobwebai.repository.notes import NotesRepository
from cobwebai.utils.auth import current_active_user
from cobwebai.models import User, Chat, Message
from cobwebai.models.message import MessageRole
from cobwebai.tasks.utils import llmtools
from cobwebai_lib.chat import ChatAttachment, Message as LibMessage, ChatRole
from cobwebai.schemas.chats import (
    SendMessageRequest,
    ChatFull,
    AttachmentType,
    ChatMessage,
    SendMessageResponse,
)


router = APIRouter(prefix="/api/v1/chat", tags=["chat"])


@router.get("/{chat_id}", response_model=ChatFull)
async def get_chat(
    chat_id: uuid.UUID,
    user: User = Depends(current_active_user),
    repository: ChatsRepository = Depends(),
):
    chat = await repository.get_chat(user.id, chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return ChatFull.model_validate(chat, from_attributes=True)


@router.post("/{chat_id}/message", response_model=SendMessageResponse)
async def send_message(
    chat_id: uuid.UUID | Literal["new"],
    request: SendMessageRequest,
    user: User = Depends(current_active_user),
    chats_repository: ChatsRepository = Depends(),
    files_repository: FilesRepository = Depends(),
    notes_repository: NotesRepository = Depends(),
) -> SendMessageResponse:
    attached_file_ids = []
    attached_note_ids = []

    for attachment in request.attachments:
        if attachment.type == AttachmentType.FILE:
            attached_file_ids.append(attachment.id)
        elif attachment.type == AttachmentType.NOTE:
            attached_note_ids.append(attachment.id)

    attached_files = await files_repository.get_files_by_ids(user.id, attached_file_ids)
    attached_notes = await notes_repository.get_notes_by_ids(user.id, attached_note_ids)

    if len(attached_files) != len(attached_file_ids):
        raise HTTPException(status_code=400, detail="Some files not found")

    if len(attached_notes) != len(attached_note_ids):
        raise HTTPException(status_code=400, detail="Some notes not found")

    attached_files_c = list(
        map(lambda n: ChatAttachment(n.file_id, n.content), attached_files)
    )
    attached_notes_c = list(
        map(lambda n: ChatAttachment(n.note_id, n.content), attached_notes)
    )

    history_converted = []

    if chat_id != "new":
        if chat := await chats_repository.get_chat(user.id, chat_id):
            for msg in chat.messages:
                history_converted.append(
                    LibMessage(
                        role=(
                            ChatRole.BOT
                            if msg.role == MessageRole.ASSISTANT
                            else ChatRole.USER
                        ),
                        raw_text=msg.content,
                        attachment=msg.attachments,
                    )
                )

    user_msg, bot_msg = await llmtools.chat_with_rag(
        user_id=user.id,
        project_id=request.project_id,
        user_prompt=request.content,
        attachments=attached_notes_c,
        rag_attachments=attached_files_c,
        history=history_converted,
    )

    user_message = Message(
        role=MessageRole.USER,
        content=user_msg.raw_text,
        attachments=user_msg.attachment,
    )

    if chat_id == "new":
        # TODO: chat_name = await generate_chat_name(message.content)
        chat_name = request.content[:10] + ("..." if len(request.content) > 10 else "")

        chat = Chat(
            project_id=request.project_id,
            name=chat_name,
            messages=[user_message],
        )

        chat = await chats_repository.create_chat(user.id, chat)
    else:
        user_message.chat_id = chat_id
        await chats_repository.add_message(user.id, user_message)
        chat = await chats_repository.get_chat(user.id, chat_id)

    answer_message = Message(
        chat_id=chat.chat_id,
        role=MessageRole.ASSISTANT,
        content=bot_msg.raw_text,
    )

    await chats_repository.add_message(user.id, answer_message)
    await chats_repository.commit()
    return SendMessageResponse(
        chat_id=chat.chat_id,
        chat_name=chat.name,
        assistant_answer=ChatMessage.model_validate(
            answer_message, from_attributes=True
        ),
    )


@router.post("/{chat_id}/regenerate", response_model=ChatMessage)
async def regenerate_message(
    chat_id: uuid.UUID,
    user: User = Depends(current_active_user),
    chats_repository: ChatsRepository = Depends(),
) -> ChatMessage:
    last_message = await chats_repository.get_last_message(user.id, chat_id)
    if not last_message:
        raise HTTPException(status_code=404, detail="Last message not found")

    if last_message.role != MessageRole.USER:
        raise HTTPException(
            status_code=400, detail="Cannot regenerate assistant message"
        )

    await asyncio.sleep(1)

    answer_message = Message(
        chat_id=chat_id,
        role=MessageRole.ASSISTANT,
        content=f"Echo: {last_message.content}",
    )

    await chats_repository.add_message(user.id, answer_message)
    await chats_repository.commit()
    return ChatMessage.model_validate(answer_message, from_attributes=True)
