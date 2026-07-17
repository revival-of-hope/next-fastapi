import uvicorn
from fastapi import FastAPI
from app.core.main import api_router
from starlette.middleware.cors import CORSMiddleware

app = FastAPI(
    title="demo",
    openapi_url="/api/openapi.json",
)

app.include_router(api_router, prefix="/api")
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


def main():
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        workers=1,
    )


if __name__ == "__main__":
    main()
