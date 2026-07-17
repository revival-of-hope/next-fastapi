from app.utils.config import settings
from app.utils.chat import stream_response, create_stream, create_client


class DeepSeekClient:
    DEFAULT_MODEL = "deepseek-v4-pro"

    DEFAULT_SYSTEM_PROMPT = """
    以后的回答都要称呼我为李华,优先输出"你好,李华!"
    """


class Clients:
    def __init__(self):
        self.deepseek: DeepSeekClient = DeepSeekClient()


clients = Clients()


def stream_agent(
    user_message: str,
    system_prompt: str,
    model: str,
) -> Generator[str, None, None]:

    # 创建流式请求。
    stream = clients.deepseek.chat.completions.create(
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
    for chunk in stream:
        # 某些 chunk 可能没有 choices
        if not chunk.choices:
            continue

        # delta 表示“这一次新增的内容”。
        delta = chunk.choices[0].delta

        # delta.content 可能是 None。
        # 只有真的有文本内容时，才 yield 给外部。
        if delta.content:
            yield delta.content
