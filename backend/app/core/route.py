from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.core.client import stream_agent

app = FastAPI()


origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatMessage(BaseModel):
    message: str


@app.get("/api/health")
async def homepage() -> dict:
    return {"message": "Hello,World!"}


@app.get("/api/auth")
async def check() -> dict:
    return {
        "message": "我懒得写验证了,你直接进来吧",
        "ok": True,
    }


@app.post("/api/chat", response_class=StreamingResponse)
async def chat(request: ChatMessage):
    # return stream_agent(request.message)

    return StreamingResponse(
        stream_agent(request.message),
        headers={
            "Cache-Control": "no-cache",
        },
    )
