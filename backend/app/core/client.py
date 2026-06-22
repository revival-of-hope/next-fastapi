from app.utils.config import settings
from openai import OpenAI  # type: ignore[import]
from typing import Generator

client = OpenAI(
    api_key=settings.DEEPSEEK_API_KEY,
    base_url=settings.DEEPSEEK_URL,
)

DEFAULT_MODEL = "deepseek-v4-pro"

DEFAULT_SYSTEM_PROMPT = """
以后的回答都要称呼我为李华,优先输出"你好,李华!"
"""


def stream_agent(
    user_message: str,
    system_prompt: str = DEFAULT_SYSTEM_PROMPT,
    model: str = DEFAULT_MODEL,
) -> Generator[str, None, None]:
    """
    流式调用。

    适合场景：
    - 前端像 ChatGPT 一样，一个字一个字显示；
    - FastAPI StreamingResponse；
    - SSE 流式接口。

    这个函数不会一次性 return 完整内容，
    而是不断 yield 模型新生成的小片段。
    """

    # 创建流式请求。
    stream = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_message,
            },
        ],
        # stream=True 是流式输出的关键。
        stream=True,
        reasoning_effort="high",
    )

    # stream 是一个可迭代对象。
    # 模型每生成一点内容，就会返回一个 chunk。
    for chunk in stream:
        # 某些 chunk 可能没有 choices，保险起见先判断。
        if not chunk.choices:
            continue

        # delta 表示“这一次新增的内容”。
        delta = chunk.choices[0].delta

        # delta.content 可能是 None。
        # 只有真的有文本内容时，才 yield 给外部。
        if delta.content:
            yield delta.content
