// frontend/src/lib/api.ts

// 从配置文件中导入后端接口地址
import { API_ROUTES } from "@/config/api";

// 这个函数用来检查后端是否在线
export async function checkBackendHealth() {
  // 请求 FastAPI 的 /api/health 接口
  const response = await fetch(API_ROUTES.health);

  // 如果 HTTP 状态码不是 2xx，就抛出错误
  if (!response.ok) {
    throw new Error("后端健康检查失败");
  }

  // 把后端返回的 JSON 转成 JS 对象
  return response.json();
}

// 这个函数用来请求后端的假登录检查
export async function checkAuth() {
  const response = await fetch(API_ROUTES.authCheck);

  if (!response.ok) {
    throw new Error("认证检查失败");
  }

  return response.json();
}

export async function streamChatMessage(
  message: string,
  onChunk: (chunk: string) => void,
) {
  // 发送 POST 请求给 FastAPI
  const response = await fetch(API_ROUTES.chatStream, {
    method: "POST",

    // 告诉后端：我发送的是 JSON
    headers: {
      "Content-Type": "application/json",
    },

    // 把 JS 对象转成 JSON 字符串
    // 后端的 ChatMessage 会接收这里的 message
    body: JSON.stringify({
      message,
    }),
  });

  // 如果后端返回错误，就抛出异常
  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(errorText || "聊天接口请求失败");
  }

  // response.body 是浏览器提供的流式响应体
  // 如果没有 body，说明当前环境不支持流式读取
  if (!response.body) {
    throw new Error("当前浏览器不支持流式响应");
  }

  // 创建 reader，用来一段一段读取后端返回的数据
  const reader = response.body.getReader();

  // TextDecoder 用来把二进制数据转成字符串
  const decoder = new TextDecoder("utf-8");

  // 不断读取流
  while (true) {
    // reader.read() 每次读取一小块数据
    const { done, value } = await reader.read();

    // done 为 true，说明后端流式输出结束
    if (done) {
      break;
    }

    // value 是 Uint8Array，需要解码成字符串
    const chunk = decoder.decode(value, {
      stream: true,
    });

    // 把这一小段文本交给页面使用
    onChunk(chunk);
  }
}
