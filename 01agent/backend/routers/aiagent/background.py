from fastapi import APIRouter, Depends, status
from sqlmodel import Session, select, and_
from db.database import get_session
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
import json
from utils import ai_prompts
from utils.procedures import CustomError, extract_json
from dependencies.auth_dependencies import get_current_user_dependency
from db.models import (
    User,
    Thread,
    ThreadStatus,
    ThreadTask,
    ThreadTaskStatus,
    ThreadMessage,
    ThreadChatType,
    ThreadChatFromChoices,
    ThreadTaskMemoryEntry,
)
from schemas.aiagent import BackgroundNextStepRequest
from utils.agentic_tools import run_tool_server_side
from utils import llm_provider
from utils.router_helpers import prepare_screenshot_for_llm, get_action_history, get_memory_items


router = APIRouter(
    prefix='/aiagent/background',
    tags=['aiagent', 'background'],
    dependencies=[Depends(get_current_user_dependency)]
)


@router.post('/{tid}/next_step')
async def next_step(tid: str, next_step_req: BackgroundNextStepRequest, db: Session = Depends(get_session),
              user: User = Depends(get_current_user_dependency)):
    instance = db.exec(select(Thread).where(and_(
        Thread.id == tid,
        Thread.user_id == user.id,
        Thread.status == ThreadStatus.WORKING
    ))).first()

    if not instance:
        raise CustomError(status.HTTP_404_NOT_FOUND, 'Thread not found')

    task = db.exec(select(ThreadTask).where(and_(
        ThreadTask.thread_id == tid,
        ThreadTask.status == ThreadTaskStatus.WORKING,
    ))).first()

    if not task:
        raise CustomError(status.HTTP_404_NOT_FOUND, 'Thread has no running task')

    if task.extended_thinking_mode is True:
        llm = llm_provider.get_llm(agent='computer_use', temperature=1.0, thinking_enabled=True)
    else:
        llm = llm_provider.get_llm(agent='computer_use', temperature=0.0)

    previous_tasks = db.exec(select(ThreadTask).where(and_(
        ThreadTask.thread.has(Thread.user_id == user.id),
        ThreadTask.thread.has(Thread.status != ThreadStatus.DELETED),
    )).order_by(ThreadTask.created_at.desc()).limit(10)).all()
    previous_tasks_arr = []
    for previous_task in previous_tasks:
        previous_tasks_arr.append({
            'task': previous_task.task_text,
            'status': previous_task.status,
        })

    screenshot_user_message_block, screenshot_s3_path = prepare_screenshot_for_llm(next_step_req.screenshot_b64)
    
    action_history = get_action_history(db, task.id, ThreadChatType.BACKGROUND_MODE_BROWSER)
    
    memory_items_arr = get_memory_items(db, task, user.id)

    computer_use_user_message = [
        {
            'type': 'text',
            'text': f'Current Task: {task.task_text}'
        },
        {
            'type': 'text',
            'text': f'Current URL: {next_step_req.current_url}'
        },
        {
            'type': 'text',
            'text': f'Current Open Tabs: {json.dumps(next_step_req.current_open_tabs)}'
        }
    ]

    if len(memory_items_arr) > 0:
        computer_use_user_message.append({
            'type': 'text',
            'text': f'Stored Memory Items: \n {json.dumps(memory_items_arr)}'
        })
    if len(action_history) > 0:
        computer_use_user_message.append({
            'type': 'text',
            'text': f'Previous Actions (Limited to 5, newest first): \n {json.dumps(action_history)}'
        })
    if len(previous_tasks_arr) > 0:
        computer_use_user_message.append({
            'type': 'text',
            'text': f'Previous Tasks: \n {json.dumps(previous_tasks_arr)}'
        })
    
    computer_use_text_prompt = computer_use_user_message.copy()
    
    if screenshot_user_message_block:
        computer_use_user_message.append(screenshot_user_message_block)

    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content=ai_prompts.BG_MODE_BROWSER_AGENT_PROMPT),
        HumanMessage(content=computer_use_user_message),
    ])

    chain = prompt | llm
    response = await chain.ainvoke({})

    print('Token Usage: ', response.usage_metadata)

    response_data = None
    if task.extended_thinking_mode is True:
        for response_item in response.content:
            if response_item.get('type') == 'reasoning_content':
                thinking_message = ThreadMessage(
                    thread_id=instance.id,
                    thread_task_id=task.id,
                    thread_chat_type=ThreadChatType.THINKING,
                    thread_chat_from=ThreadChatFromChoices.FROM_AI,
                    chain_of_thought=response_item.get('reasoning_content', {}).get('text'),
                )
                db.add(thinking_message)
                db.commit()
                db.refresh(thinking_message)
            elif response_item.get('type') == 'text':
                response_data = extract_json(response_item.get('text'))
    else:
        response_data = extract_json(response.content)

    ai_message = ThreadMessage(
        thread_id=instance.id,
        thread_task_id=task.id,
        thread_chat_type=ThreadChatType.BACKGROUND_MODE_BROWSER,
        thread_chat_from=ThreadChatFromChoices.FROM_AI,
        screenshot=screenshot_s3_path,
        prompt=json.dumps(computer_use_text_prompt),
        text=json.dumps(response_data),
    )
    db.add(ai_message)
    db.commit()
    db.refresh(ai_message)

    if response_data.get('current_state', {}).get('save_to_memory', False):
        memory_text = response_data['current_state'].get('memory')
        if memory_text:
            memory_entry = ThreadTaskMemoryEntry(
                thread_task_id=task.id,
                text=memory_text,
            )
            db.add(memory_entry)
            db.commit()
            db.refresh(memory_entry)

    # Iterate over all actions
    actions_arr = response_data.get('actions', [])
    for act in actions_arr:
        action_type = act.get('action')

        if action_type == 'task_completed' and len(actions_arr) == 1:
            task.status = ThreadTaskStatus.COMPLETED
            db.add(task)
            db.commit()
            db.refresh(task)

            instance.status = ThreadStatus.STANDBY
            db.add(instance)
            db.commit()
            db.refresh(instance)

            

        elif action_type == 'task_failed':
            task.status = ThreadTaskStatus.FAILED
            db.add(task)
            db.commit()
            db.refresh(task)

            instance.status = ThreadStatus.STANDBY
            db.add(instance)
            db.commit()
            db.refresh(instance)

            

        elif action_type == 'tool_use':
            tool = act['params'].get('tool')
            args = act['params'].get('args', {})

            if tool == 'save_to_memory':
                memory_entry = ThreadTaskMemoryEntry(
                    thread_task_id=task.id,
                    text=args.get('text', ''),
                )
                db.add(memory_entry)
                db.commit()
                db.refresh(memory_entry)

            elif tool in ['read_pdf', 'fetch_url', 'summarize_youtube_video']:
                tool_output_text = run_tool_server_side(tool, args)
                memory_entry = ThreadTaskMemoryEntry(
                    thread_task_id=task.id,
                    text=tool_output_text,
                )
                db.add(memory_entry)
                db.commit()
                db.refresh(memory_entry)

    return response_data