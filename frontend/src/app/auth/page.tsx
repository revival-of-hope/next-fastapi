"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

import { Button } from "@/components/ui/button";
import { checkAuth } from "@/lib/api";

export default function AuthPage() {
  // 用来跳转页面
  const router = useRouter();

  // 保存后端返回的信息
  const [message, setMessage] = useState("请点击按钮检查登录状态");

  async function handleCheckAuth() {
    // 点击按钮后，进入加载状态

    try {
      // 请求 FastAPI 的 /api/auth/check
      const data = await checkAuth();

      if (data.ok) {
        sessionStorage.setItem("authPassed", "true");

        // 显示后端返回的信息
        setMessage(data.message ?? "验证成功，正在跳转到首页...");

        // 验证成功后跳回根路由
        setTimeout(() => {
          router.replace("/");
        }, 1000);
      } else {
        // 如果后端返回 ok: false，就停留在 auth 页面
        setMessage("验证失败，请稍后再试");
      }
    } catch (error) {
      // 如果后端没有启动、接口写错、跨域失败，都会进入这里
      setMessage("请求认证接口失败");
    }
  }

  return (
    <main className="mx-auto flex min-h-screen max-w-2xl flex-col items-center justify-center gap-6 p-8">
      <h1 className="text-3xl font-bold">Auth Page</h1>

      <p className="rounded-lg border p-4">{message}</p>

      <Button onClick={handleCheckAuth}>{"检查登录状态"}</Button>
    </main>
  );
}
