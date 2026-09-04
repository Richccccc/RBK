/**
 * blog-api Worker
 * - api.rbk.beauty  : 反代 Vercel 后端（原逻辑不变）
 * - img.rbk.beauty  : 反代 GitHub raw 图床，走 Cloudflare CDN 长缓存
 *
 * 面板环境变量：BACKEND_ORIGIN = https://rbk-three.vercel.app
 * 图片仓库路径常量在下方 IMAGE_REPO / IMAGE_BRANCH，换仓库时改这里。
 */
const IMAGE_REPO = "Richccccc/RBK-Images";
const IMAGE_BRANCH = "main";

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const origin = request.headers.get("Origin") || "";
    const cors = {
      "Access-Control-Allow-Origin": origin || "*",
      "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type,Authorization",
    };
    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: cors });
    }

    // ---- 图片域名：img.rbk.beauty/images/xxx.jpg -> GitHub raw ----
    if (url.hostname === "img.rbk.beauty") {
      const cache = caches.default;
      let hit = await cache.match(request);
      if (hit) return hit;

      const target =
        "https://raw.githubusercontent.com/" +
        IMAGE_REPO +
        "/" +
        IMAGE_BRANCH +
        url.pathname;
      const upstream = await fetch(target);
      if (!upstream.ok) {
        return new Response("Image not found", {
          status: 404,
          headers: { ...cors, "Content-Type": "text/plain; charset=utf-8" },
        });
      }
      const headers = new Headers(upstream.headers);
      headers.set("Cache-Control", "public, max-age=31536000, immutable");
      headers.set("Access-Control-Allow-Origin", "*");
      const resp = new Response(upstream.body, {
        status: upstream.status,
        headers,
      });
      await cache.put(request, resp.clone());
      return resp;
    }

    // ---- API 域名：原样反代后端 ----
    return fetch(env.BACKEND_ORIGIN + url.pathname + url.search, request);
  },
};
