"use client";

import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";

import { streamChatMessage } from "@/lib/api";

export default function ChatPage() {
  // 保存用户输入的问题
  const [message, setMessage] = useState("");

  // 保存模型返回的答案
  const [answer, setAnswer] = useState("");

  // 保存加载状态
  const [loading, setLoading] = useState(false);

  // 保存错误信息
  const [error, setError] = useState("");

  // 表单提交时执行这个函数
  async function handleSubmit(event: any) {
    // 阻止浏览器默认刷新页面
    event.preventDefault();

    // 去掉前后空格后，如果没有内容，就不发送请求
    if (!message.trim()) {
      return;
    }

    // 每次提问前，先清空旧答案和旧错误
    setAnswer("");
    setError("");

    // 进入加载状态
    setLoading(true);

    try {
      // 调用封装好的流式请求函数
      await streamChatMessage(message, (chunk) => {
        // 每收到一小段内容，就追加到 answer 后面
        setAnswer((prev) => prev + chunk);
      });
    } catch (err) {
      // 如果请求失败，就把错误显示到页面上
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("发生未知错误");
      }
    } finally {
      // 无论成功还是失败，最后都退出加载状态
      setLoading(false);
    }
  }

  return (
    <main className="mx-auto flex min-h-screen max-w-3xl flex-col gap-6 p-8">
      <section className="space-y-2">
        <h1 className="text-3xl font-bold">AI Chat</h1>
        <p className="text-muted-foreground">
          这个页面会调用 FastAPI 的 /api/chat/stream 接口。
        </p>
      </section>

      <form onSubmit={handleSubmit} className="space-y-4">
        <Textarea
          value={message}
          onChange={(event) => setMessage(event.target.value)}
          placeholder="请输入你想问 AI 的问题"
          className="min-h-32"
        />

        <Button type="submit" disabled={loading}>
          {loading ? "生成中..." : "发送"}
        </Button>
      </form>

      {error && (
        <div className="rounded-lg border border-red-300 p-4 text-red-600">
          {error}
        </div>
      )}

      <section className="rounded-lg border p-4">
        <h2 className="mb-2 font-semibold">模型回答</h2>

        {answer ? (
          <pre className="whitespace-pre-wrap text-sm leading-7">{answer}</pre>
        ) : (
          <p className="text-sm text-muted-foreground">还没有回答。</p>
        )}
      </section>
    </main>
  );
}
