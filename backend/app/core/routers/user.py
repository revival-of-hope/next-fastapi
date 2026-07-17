from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.utils.deps import SessionDep
from app.core.client import stream_agent

router = APIRouter(prefix="/user", tags=["user"])


@router.post("/{user_id}/chat")
async def chat(
    user_message: str,
    user_id: int,
    session: SessionDep,
) -> StreamingResponse:
    # return stream_agent(request.message)

    return StreamingResponse(
        stream_agent(user_id, user_message, session),
        headers={
            "Cache-Control": "no-cache",
        },
    )
