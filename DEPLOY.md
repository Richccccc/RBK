# 个人博客部署手册

前后端分离 + 全免费部署，**全部境外、无需 ICP 备案**，免费档即可稳定支撑 10 人访问。

## 架构与选型

| 部分 | 技术栈 | 部署平台 | 说明 |
|------|--------|----------|------|
| 前端 | Vue 3 + Naive UI + TipTap | Cloudflare Pages | 免费静态托管，全球 CDN |
| 后端 | FastAPI + SQLAlchemy | Render | 免费 Web 服务（15 分钟休眠，靠保活防睡） |
| 数据库 | MySQL 兼容 | TiDB Cloud Serverless | 免费、自动扩容、自动备份 |
| 保活 | — | GitHub Actions | 每 10 分钟 ping 一次后端 |

> 三个平台都在境外，**不需要备案**。国内访问延迟偏高但可用，介意可给前端套 Cloudflare 加速（已经就是 Cloudflare 了）。

---

## 一、准备

需要注册 4 个账号（都用邮箱即可，免费）：

1. [GitHub](https://github.com)
2. [Cloudflare](https://cloudflare.com)
3. [Render](https://render.com)
4. [TiDB Cloud](https://tidbcloud.com)

本地需安装 **Git**：[下载地址](https://git-scm.com/)（安装后命令行里 `git --version` 能出结果即可）。

---

## 二、把项目推送到 GitHub

```bash
cd g:\RichPro
git init
git add .
git commit -m "init: personal blog"
git branch -M main
git remote add origin https://github.com/<你的用户名>/<仓库名>.git
git push -u origin main
```

> `.env`、`node_modules`、`dist` 已加入 `.gitignore`，不会被提交，放心。

---

## 三、创建 TiDB 数据库

1. 登录 TiDB Cloud → Create Cluster → 选 **Serverless**（免费档）。
2. 创建后，在集群里用 SQL 建库：

   ```sql
   CREATE DATABASE blog CHARACTER SET utf8mb4;
   ```

3. 记录连接信息（Host、端口 4000、用户名、密码），拼成连接串（先记下，后面填到 Render）：

   ```
   mysql+pymysql://<USER>:<PASSWORD>@<HOST>:4000/blog?charset=utf8mb4
   ```

   例如：`mysql+pymysql://3xxxxx.root:abc123@gateway01.ap-southeast-1.prod.aws.tidbcloud.com:4000/blog?charset=utf8mb4`

---

## 四、部署后端到 Render

### 方式 A：Blueprint（推荐，仓库里已带 render.yaml）

1. Render 控制台 → **New +** → **Blueprint** → 连接 GitHub 仓库。
2. Render 读取根目录 `render.yaml`，自动创建服务 `myblog-api`（Root Directory 已设为 `backend`）。
3. 在服务里填写 **Environment Variables**：

   | 变量 | 值 | 说明 |
   |------|-----|------|
   | `DATABASE_URL` | 上面的 TiDB 连接串 | 必填 |
   | `JWT_SECRET` | 一串随机字符（如 `x8Kq2...`） | 必填，随便打 |
   | `DB_SSL` | `true` | TiDB 强制 TLS（已按不校验证书的方式连接） |
   | `TOKEN_EXPIRE_MINUTES` | `10080` | 可选，默认 7 天 |

### 方式 B：手动创建

1. **New +** → **Web Service** → 连接仓库。
2. 配置：
   - **Root Directory**：`backend`
   - **Build Command**：`pip install -r requirements.txt`
   - **Start Command**：`uvicorn app.main:app --host 0.0.0.0 --port $PORT`
3. 环境变量同方式 A。

### 验证

部署完成后得到一个地址，例如 `https://myblog-api.onrender.com`，记下它。

浏览器打开 `https://myblog-api.onrender.com/api/health`，返回：

```json
{"status":"ok"}
```

即后端成功（首次启动会自动建表 + 写入默认管理员 `admin`）。

---

## 五、部署前端到 Cloudflare Pages

1. Cloudflare 控制台 → **Workers & Pages** → **Create** → **Pages** → **Connect to Git** → 选 GitHub 仓库。
2. 构建配置：

   | 配置项 | 值 |
   |--------|-----|
   | Framework preset | Vue (Vite) |
   | Build command | `npm run build` |
   | Build output directory | `dist` |
   | Root directory | `frontend` |

   > 「Root directory」如果仓库就是本项目根目录，务必填 `frontend`（因为前端在子目录）。

3. 添加环境变量（构建期）：

   | 变量 | 值 |
   |------|-----|
   | `VITE_API_BASE` | `https://myblog-api.onrender.com/api` |

4. 点 **Save and Deploy**。

> `frontend/public/_redirects` 已配好 SPA 路由回退，直接刷新、直达 `/post/1` 都不会 404。

部署完成后得到前端地址，例如 `https://blog.pages.dev`，这就是你的博客入口。

---

## 六、保活（防止后端休眠）

Render 免费服务 **15 分钟无访问会休眠**，下次访问要冷启动约 30~50 秒。用固定频率访问让它保持唤醒：

### 方案 A：GitHub Actions（仓库里已带）

1. 进入 GitHub 仓库 → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**：
   - 名称：`BACKEND_URL`
   - 值：`https://myblog-api.onrender.com`
2. 仓库里的 `.github/workflows/keepalive.yml` 已配好每 10 分钟访问一次 `/api/health`。

### 方案 B：UptimeRobot（更稳定，推荐）

1. 注册 [UptimeRobot](https://uptimerobot.com)（免费）。
2. 新建 Monitor → HTTP(s) → 填 `https://myblog-api.onrender.com/api/health`，监控间隔选 **5 分钟**。

> 两个方案二选一即可；UptimeRobot 更准时，GitHub Actions 免费够用。

---

## 七、首次使用

1. 打开前端地址 → 自动跳转登录页。
2. 默认管理员：`admin` / `admin123456`。
3. 登录后在左上角菜单里「新建博客」，或「导入 Word」把 `.docx` 一键转成图文博客。

> 这是个人博客，只设了这一个账号。想换账号可在登录页用「注册」再建一个，或之后再加「修改密码」功能。

---

## 八、常见问题

**Q：第一次打开很慢（几十秒）？**
Render 冷启动，正常。保活生效后基本不再触发。

**Q：连不上 TiDB（数据库报错）？**
确认 `DB_SSL=true`。或改用更安全的证书方式：在 TiDB Cloud 下载 CA 证书，把 `DB_SSL_CA` 设为证书路径、`DB_SSL` 留空。

**Q：免费会不会崩 / 够不够用？**
个人博客 + 10 人并发完全够。TiDB 免费档按量自动扩容；Cloudflare Pages 免费无限静态流量；瓶颈只在 Render 免费单实例（CPU 有限），够用。

**Q：国内访问慢？**
境外部署延迟偏高属正常；前端在 Cloudflare（有中国节点加速）会好一些。要更快或高可用就得付费或迁国内（国内需备案）。

**Q：图片存哪？怕丢吗？**
图片以 base64 内联存进 TiDB（MySQL），不依赖服务器本地磁盘，**Render 重启/休眠不会丢图**。想省空间后续可切到 Cloudflare R2 对象存储。

---

## 附：改代码后如何更新线上

每次 `git push` 到 `main` 分支后：

- **前端**：Cloudflare Pages 自动重新构建部署。
- **后端**：若用 Blueprint/关联代码，Render 自动重新构建；否则在 Render 手动 **Manual Deploy**。