// frontend/src/config/api.ts

// 这里保存后端 FastAPI 的地址
// 开发环境下，FastAPI 通常运行在 http://127.0.0.1:8000
//
// process.env.NEXT_PUBLIC_API_BASE_URL 会读取 .env.local 里的配置
// 如果没配置，就默认使用 http://127.0.0.1:8000
//
// 注意：Next.js 中如果要在浏览器端读取环境变量，变量名必须以 NEXT_PUBLIC_ 开头。
// 这是 Next.js 官方约定。不要把 API Key 这种秘密放到 NEXT_PUBLIC_ 里。
export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

// 把所有后端接口统一放在这里
// 以后后端路由改了，只需要改这个文件
export const API_ROUTES = {
  health: `${API_BASE_URL}/api/health`,
  authCheck: `${API_BASE_URL}/api/auth`,
  chatStream: `${API_BASE_URL}/api/chat`,
};
