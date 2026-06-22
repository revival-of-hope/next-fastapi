// frontend/src/app/page.tsx

"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

export default function HomePage() {
  const router = useRouter();

  // checking 表示正在检查用户是否刚刚通过验证
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    // 读取 auth 页面设置的临时验证标记
    const authPassed = sessionStorage.getItem("authPassed");

    // 如果没有这个标记，说明用户不是从 /auth 验证成功回来的
    // 所以必须先跳转到 /auth
    if (authPassed !== "true") {
      router.replace("/auth");
      return;
    }

    // 如果有这个标记，说明用户刚刚在 /auth 页面验证成功
    // 这一次允许他进入根路由
    setChecking(false);

    // 删除临时标记
    // 这样用户下一次重新访问 / 时，还是会被要求再次验证
    //
    // 用 setTimeout 是为了避免开发环境 React Strict Mode
    // 导致 useEffect 执行两次时出现立刻跳回 /auth 的问题。
    setTimeout(() => {
      sessionStorage.removeItem("authPassed");
    }, 500);
  }, [router]);

  if (checking) {
    return (
      <main className="flex min-h-screen items-center justify-center">
        <p>正在检查验证状态...</p>
      </main>
    );
  }

  return (
    <main className="mx-auto flex min-h-screen max-w-3xl flex-col justify-center gap-6 p-8">
      <h1 className="text-4xl font-bold">首页</h1>

      <p className="text-muted-foreground">
        你已经通过验证，现在可以访问根路由。
      </p>
    </main>
  );
}
