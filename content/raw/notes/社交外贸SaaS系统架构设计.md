# 外贸社媒运营 SaaS 系统架构设计

> 目标用户：中国外贸 B2B/B2C 从业者、外贸团队、出海品牌
> 核心定位：一站式海外社媒运营平台，解决跨语言、跨时区、多平台管理的核心痛点

---

## 一、外贸从业者核心痛点分析

| 痛点 | 具体表现 | 解决方案 |
|------|----------|----------|
| **多平台割裂** | Facebook/LinkedIn/Instagram/TikTok/YouTube/X/Pinterest 各自登录管理 | 统一聚合面板，OAuth一次绑定所有平台 |
| **语言障碍** | 英文内容创作困难，中式英语影响品牌形象 | AI 多语言内容生成 + 本地化润色 |
| **时区错位** | 国内白天是欧美深夜，无法实时互动 | 定时发布 + 智能推荐最佳发帖时段 |
| **获客难** | 社媒流量无法转化为询盘/B2B线索 | 社媒→独立站→询盘追踪，LinkedIn精准触达采购决策人 |
| **内容产出低效** | 缺乏产品素材，不会做视频 | AI 图文转视频，产品图自动适配各平台尺寸 |
| **效果难衡量** | 不知道哪条内容有效，ROI 不清晰 | 跨平台统一分析面板 + 询盘归因 |
| **成本敏感** | Buffer/Sprout Social/Hootsuite 等 $100-300/月太贵 | 开源核心 + 按需付费，支持自部署 |
| **合规风险** | 内容不当导致账号被封 | AI 合规检查 + 审核流程 |

---

## 二、总体架构

```
┌─────────────────────────────────────────────────────────────────────┐
│                       客户端层 (Client Layer)                         │
│  ┌──────────┐  ┌──────────┐  ┌───────────┐  ┌──────────────────┐   │
│  │ Web App  │  │ Mobile   │  │ WeChat    │  │ API Client       │   │
│  │ (React/  │  │ (React   │  │ Mini-     │  │ (REST + MCP)     │   │
│  │  Next.js)│  │  Native) │  │ Program   │  │  for n8n/Make    │   │
│  └──────────┘  └──────────┘  └───────────┘  └──────────────────┘   │
└──────────────────────────┬──────────────────────────────────────────┘
                           │ HTTPS / WSS
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       API 网关层 (Gateway Layer)                      │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────────────────┐  │
│  │ API Gateway │  │ Auth Gateway │  │ Rate Limiter / WAF         │  │
│  │ (Kong/Nginx)│  │ (JWT + OAuth)│  │ (per-key, per-tenant限流)   │  │
│  └─────────────┘  └──────────────┘  └────────────────────────────┘  │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     微服务层 (Microservices)                         │
│                                                                     │
│  ┌─────────┐ ┌───────────┐ ┌──────────┐ ┌──────────┐ ┌─────────┐  │
│  │用户与租户│ │内容管理服务│ │发布调度  │ │社媒收件箱│ │ 数据分析 │  │
│  │ 服务     │ │(Composer +│ │ 引擎     │ │(Social   │ │ 服务     │  │
│  │         │ │ Templates)│ │(Scheduler)│ │ Inbox)   │ │(Analytics│  │
│  └─────────┘ └───────────┘ └──────────┘ └──────────┘ └─────────┘  │
│  ┌─────────┐ ┌───────────┐ ┌──────────┐ ┌──────────┐ ┌─────────┐  │
│  │AI 内容  │ │ 媒体资产  │ │ 线索管理  │ │ 审批工作流│ │ 通知    │  │
│  │生成服务 │ │ 库服务    │ │(CRM整合) │ │ 服务     │ │ 服务     │  │
│  └─────────┘ └───────────┘ └──────────┘ └──────────┘ └─────────┘  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       集成层 (Integration Layer)                     │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │             社媒 API 适配器 (Provider Adapters)                 │   │
│  │  Facebook │ Instagram │ LinkedIn │ TikTok │ YouTube │ X/Twitter│  │
│  │  Pinterest │ Threads │ Bluesky │ Google Business │ Mastodon  │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌──────────────────────┐  ┌────────────────────────────────────┐   │
│  │  CRM 集成 (Salesforce │  │ 电商平台集成                        │   │
│  │  / HubSpot / 纷享销客)│  │ (Shopify / 阿里国际站 / Made-in-    │   │
│  └──────────────────────┘  │  China.com)                         │   │
│                            └────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     基础设施层 (Infrastructure)                       │
│                                                                     │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐ ┌───────────┐  │
│  │PostgreSQL│ │  Redis   │ │ 对象存储  │ │ 消息队列│ │ Temporal  │  │
│  │ (主库)    │ │ (缓存/   │ │ (S3兼容)  │ │ (Kafka/│ │ (工作流    │  │
│  │          │ │  Session)│ │          │ │  RMQ)  │ │  引擎)    │  │
│  └──────────┘ └──────────┘ └──────────┘ └────────┘ └───────────┘  │
│                                                                     │
│  ┌──────────┐ ┌──────────┐ ┌───────────────────────────────────┐   │
│  │  Elastic  │ │  Docker  │ │  部署环境                          │   │
│  │  Search   │ │  & K8s   │ │  阿里云 / 腾讯云 / AWS / 自部署    │   │
│  └──────────┘ └──────────┘ └───────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 三、技术选型

### 3.1 方案一：Postiz 技术栈路线（推荐，灵活性高）

| 层 | 技术选型 | 理由 |
|---|---------|------|
| 前端 | **Next.js 14+ (React) + Tailwind CSS + shadcn/ui** | SSR 利于 SEO，RSC 性能好，社区庞大 |
| 后端 | **NestJS (Node.js/TypeScript)** | 模块化架构，与前端同语言，生态丰富 |
| 数据库 | **PostgreSQL + Prisma ORM** | 类型安全，迁移方便，PostGIS 支持地理查询 |
| 缓存 | **Redis** | Session 存储、队列、缓存 |
| 工作流 | **Temporal** | 社媒发布需要可靠重试、定时、补偿事务 |
| 消息队列 | **RabbitMQ / Kafka** | 异步处理通知、数据回传 |
| 搜索引擎 | **Elasticsearch** | 社交收件箱搜索、媒体库 AI 搜索 |
| 对象存储 | **MinIO / 阿里云OSS / AWS S3** | 媒体文件存储 |
| 容器化 | **Docker + Docker Compose / Kubernetes** | 标准化部署 |
| AI 服务 | **OpenAI API / 通义千问 / Claude API** | 内容生成、翻译、分析 |

### 3.2 方案二：BrightBean 技术栈路线（适合快速 MVP）

| 层 | 技术选型 |
|---|---------|
| 后端 | **Python Django 5.x + DRF** |
| 前端 | **Django Templates + HTMX + Alpine.js + Tailwind CSS** |
| 数据库 | **PostgreSQL** |
| 工作流 | **Celery + Redis** |
| 部署 | **Docker + Caddy** |

> **建议 MVP 阶段先用 BrightBean 的 Django 路线，快速搭建核心功能；中期平滑迁移到 Postiz 的微服务架构以支撑多租户和高并发。**

---

## 四、核心模块详细设计

### 4.1 多租户与团队管理

```
Organization (组织)
  ├── Workspace (工作空间，多个)
  │   ├── Member (成员) — RBAC 角色：Owner / Admin / Editor / Viewer / Client
  │   ├── SocialAccount (社媒账号)
  │   ├── Post (内容)
  │   ├── Media (媒体)
  │   └── Settings (配置)
  └── Billing (计费)
```

- 参考 BrightBean 的无限组织/工作空间/成员设计
- 每租户独立数据池（Row-Level Security 或 Schema-per-Tenant）
- **外贸场景特色：Client Portal** — 客户无需注册即可通过魔法链接预览/审批内容

### 4.2 社媒账号集成（Provider Layer）

参考 BrightBean 的 Provider 架构 + Postiz 的多平台支持：

```
providers/
├── base.py              # BaseProvider 抽象类
├── facebook.py          # Meta Graph API
├── instagram.py
├── instagram_direct.py  # Instagram Login (Business/Creator)
├── linkedin_personal.py # LinkedIn OIDC
├── linkedin_company.py  # LinkedIn Community Management API
├── tiktok.py            # TikTok Content Posting API
├── youtube.py           # YouTube Data API v3
├── pinterest.py         # Pinterest API
├── threads.py           # Threads API
├── bluesky.py           # Bluesky AT Protocol
├── x.py                 # X/Twitter API v2
├── google_business.py   # Google Business Profile API
└── mastodon.py          # Mastodon OAuth
```

**核心原则**：直接对接各平台官方 API，不经过第三方聚合层，数据完全自主掌控。

**外贸特化策略**：
- LinkedIn 是企业级 B2B 获客核心渠道，优先优化 LinkedIn 公司页和个人号双通道
- TikTok/YouTube 用于产品视频展示，支持中英双语字幕
- Pinterest 用于产品图册（家居/服装/礼品行业）

### 4.3 AI 内容生成引擎

这是外贸场景最核心的差异化模块：

```
┌─────────────────────────────────────────────────────────────┐
│                   AI Content Engine                          │
│                                                             │
│  ┌────────────┐  ┌──────────────┐  ┌────────────────────┐  │
│  │ 多语言翻译  │  │ 产品描述→社媒 │  │ 图片/视频生成      │  │
│  │ 中→英/西/  │  │ 帖文自动生成   │  │ 产品图→各平台尺寸  │  │
│  │ 法/阿/葡   │  │ (AIDA/SONPL) │  │ AI 文生视频       │  │
│  └────────────┘  └──────────────┘  └────────────────────┘  │
│                                                             │
│  ┌────────────┐  ┌──────────────┐  ┌────────────────────┐  │
│  │ 帖文优化    │  │ 最佳发布时间  │  │ 合规检查            │  │
│  │ 中式英文→   │  │ 基于目标市场  │  │ 各平台规则检查      │  │
│  │ 本地化表达  │  │ 算法推荐     │  │ + 敏感词过滤        │  │
│  └────────────┘  └──────────────┘  └────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 4.4 内容发布调度引擎

参考 BrightBean 的 `process_tasks` worker 和 Temporal 工作流引擎：

```
Schedule Post Request
       │
       ▼
┌──────────────────┐
│ Validation &     │
│ Rate Limit Check │──────── 检查各平台配额
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ 暂存为 Draft     │──→ 如需审批，进入 Approval Workflow
└────────┬─────────┘
         │
         ▼
┌──────────────────┐     ┌─────────────────────┐
│ Temporal Workflow│────→│ Publish Activity    │
│ (可靠重试)        │     │   ├─ Facebook API   │
│                  │     │   ├─ LinkedIn API   │
│                  │     │   └─ ...            │
│                  │     └─────────┬───────────┘
│                  │               │ 失败
│                  │     ┌─────────▼───────────┐
│                  │     │ Retry with Backoff  │
│                  │     │ (指数退避, 最多3次)   │
│                  │     └─────────────────────┘
└──────────────────┘
         │
         ▼
┌──────────────────┐
│ 写入 Publish Log │──→ 90天发布审计日志
└──────────────────┘
```

**外贸场景特化**：支持"多平台一次发布"（LinkedIn + Facebook + X 同时推送同一条产品动态，各平台内容自动适配）

### 4.5 统一社媒收件箱 (Social Inbox)

参考 BrightBean 的 Social Inbox + sentiment analysis：

- 跨平台聚合评论、私信、@提及
- 外贸场景：**自动识别询盘意向** — AI 分类"询价/样品/合作/投诉"
- 支持团队分配 + 回复模板
- Webhook 即时推送（钉钉/企微通知，不错过海外客户）

### 4.6 数据分析与归因

```
┌─────────────────────────────────────────────┐
│            Analytics Engine                   │
│                                              │
│  各平台原生 API → 统一数据模型 → KPI 面板     │
│                                              │
│  ┌────────────────────────────────────────┐  │
│  │  核心指标                               │  │
│  │  ├─ 曝光 (Impressions)                  │  │
│  │  ├─ 互动 (Engagement Rate)              │  │
│  │  ├─ 点击 (Clicks)                       │  │
│  │  ├─ 粉丝增长 (Follower Growth)          │  │
│  │  └─ 询盘线索 (Lead Attribution)         │◄── 外贸核心KPI
│  └────────────────────────────────────────┘  │
│                                              │
│  对比功能：本周 vs 上周 vs 去年同期            │
│  最佳帖文分析：什么类型的帖文互动最高            │
└─────────────────────────────────────────────┘
```

**询盘归因**（外贸独有）：
- 每条社媒帖文挂载 UTM 参数 + 短链接
- 追踪：帖文曝光 → 独立站访问 → 询盘表单提交 → 成交
- 完整 LTV 归因链路

### 4.7 线索管理（外贸 CRM 整合）

```
Social Post → Click → Landing Page → Inquiry Form
                                         │
                                         ▼
┌─────────────────────────────────────────────┐
│                Lead Service                   │
│                                              │
│  ├─ 自动抓取社媒询盘评论/私信                 │
│  ├─ LinkedIn Sales Navigator 集成             │
│  ├─ 线索评分 (意向度 + 公司规模 + 地区)        │
│  ├─ 自动分配至对应业务员                       │
│  └─ 与 阿里国际站 / 纷享销客 / HubSpot 同步    │
└─────────────────────────────────────────────┘
```

---

## 五、数据模型核心设计

### 5.1 多租户模型

```prisma
model Organization {
  id          String   @id @default(cuid())
  name        String
  slug        String   @unique
  avatar      String?
  plan        PlanType @default(FREE)
  createdAt   DateTime @default(now())
  deletedAt   DateTime?
  workspaces  Workspace[]
  members     Member[]
  apiKeys     ApiKey[]
}

model Workspace {
  id          String   @id @default(cuid())
  name        String
  organization Organization @relation(fields: [organizationId], references: [id])
  organizationId String
  branding    Json?      // 白标：logo、主色调
  timezone    String     @default("Asia/Shanghai")
  defaultHashtags String[]
  posts       Post[]
  socialAccounts SocialAccount[]
  media       Media[]
  members     Member[]
}
```

### 5.2 发布模型

```prisma
model Post {
  id              String   @id @default(cuid())
  workspaceId     String
  title           String?
  content         Json     // 各平台内容 [{platform: "linkedin", text: "..."}, ...]
  media           Media[]
  status          PostStatus @default(DRAFT)
  // DRAFT → PENDING_APPROVAL → SCHEDULED → PUBLISHING → PUBLISHED / FAILED
  scheduledAt     DateTime?
  publishedAt     DateTime?
  createdAt       DateTime @default(now())
  createdBy       String   // 用户 ID

  platforms       PostPlatform[] // 目标发布平台
  publishLogs     PublishLog[]
  analytics       PostAnalytics[]
  approvals       Approval[]
}

model PostPlatform {
  id          String   @id @default(cuid())
  postId      String
  accountId   String   // 关联 SocialAccount
  platform    Platform
  status      PublishStatus @default(PENDING)
  platformPostId String?  // 发布后在平台的Post ID
  errorMessage String?
  publishedAt DateTime?
}
```

---

## 六、安全性设计

| 安全领域 | 方案 | 参考 |
|---------|------|------|
| 凭据存储 | AES-256 加密后存入数据库，密钥环境变量注入 | BrightBean 的 `encrypted_fields` |
| OAuth Token | 使用 Refresh Token 自动续期，减少用户手动重连 | Postiz OAuth 模式 |
| API 认证 | JWT + API Key (Bearer Token) 双体系 | BrightBean API Key 设计 |
| 权限控制 | RBAC (Organization → Workspace → Member)，每个端点鉴权 | BrightBean members middleware |
| 数据隔离 | Row-Level Security 或 Schema-per-Tenant | |
| 审计日志 | 所有发布操作记录 90 天可追溯 | BrightBean Publish Log |
| 2FA | TOTP 双因素认证 | BrightBean 路线图 |
| 社媒合规 | 不代理、不聚合、不爬取，只用官方 OAuth | Postiz Compliance 声明 |

---

## 七、部署架构

### 7.1 自部署方案（面向技术型用户）

```
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  Caddy/Nginx  │  │  PostgreSQL  │  │   Redis       │
│  (反向代理+   │  │  (主从复制)    │  │  (主从/集群)   │
│  自动HTTPS)   │  └──────────────┘  └──────────────┘
└──────┬───────┘
       │
┌──────▼────────────────────────────────────────┐
│             Docker Compose / K8s               │
│                                                │
│  ┌──────────┐ ┌──────────┐ ┌────────────────┐ │
│  │ Web App  │ │ API App  │ │  Background     │ │
│  │ (Next.js)│ │ (NestJS) │ │  Worker         │ │
│  └──────────┘ └──────────┘ │  (Temporal)     │ │
│                            └────────────────┘ │
│  ┌──────────┐ ┌──────────┐ ┌────────────────┐ │
│  │ MinIO    │ │ Elastic- │ │  Temporal       │ │
│  │ (对象存储) │ │  search  │ │  Server          │ │
│  └──────────┘ └──────────┘ └────────────────┘ │
└────────────────────────────────────────────────┘
```

### 7.2 SaaS 云部署方案（面向平台运营方）

| 服务 | 阿里云 | 腾讯云 | AWS |
|------|--------|--------|-----|
| 计算 | ACK / ECS | TKE / CVM | ECS / EKS |
| 数据库 | RDS PostgreSQL | TDSQL | RDS PostgreSQL |
| 缓存 | Redis | CRS | ElastiCache |
| 存储 | OSS | COS | S3 |
| CDN | CDN | CDN | CloudFront |
| AI | 通义千问 API | 混元大模型 | Bedrock |

---

## 八、外贸特色功能矩阵

| 功能 | 优先级 | 说明 |
|------|--------|------|
| **LinkedIn 深度集成** | P0 | B2B 外贸核心渠道，公司页 + 个人号双通，InMail 回复 |
| **AI 中→英/西/法/阿/葡 内容生成** | P0 | 产品描述自动转化为本地化社媒帖文 |
| **多平台一次发布** | P0 | 一条产品动态同步到 FB/LinkedIn/X/Pinterest |
| **询盘自动识别** | P0 | AI 识别评论/私信中的采购意向并自动分配 |
| **最佳发帖时间推荐** | P1 | 基于目标市场时区（美东/欧洲/中东） |
| **社媒→独立站归因** | P1 | UTM + 短链接追踪完整转化路径 |
| **产品图→视频自动生成** | P1 | 适合 TikTok/YouTube Shorts/Reels |
| **合规检查** | P1 | 各平台内容政策 + 目标市场敏感词过滤 |
| **客户门户 (Client Portal)** | P2 | 外贸代理给客户审批内容，无需客户注册 |
| **WhatsApp Business 集成** | P2 | 外贸沟通核心渠道，统一收件箱 |
| **阿里国际站数据对接** | P2 | 将国际站产品库同步至社媒内容库 |
| **团队协作与审批流** | P2 | 外贸团队：业务员→主管→客户 三级审批 |

---

## 九、商业化模型

| 层 | 免费版 | 专业版 ($29/月) | 企业版 ($99/月) |
|----|--------|----------------|----------------|
| 社媒账号数 | 3个 | 10个 | 无限 |
| 工作空间 | 1个 | 5个 | 无限 |
| AI 生成次数 | 50次/月 | 500次/月 | 无限 |
| 团队成员 | 2人 | 10人 | 无限 |
| 客户门户 | — | ✓ | ✓ |
| 高级分析 | — | ✓ | ✓ |
| API 访问 | — | 1000次/天 | 10000次/天 |
| 白标 | — | — | ✓ |
| 自部署 | ✓ | ✓ | ✓ |

---

## 十、路线图建议

```
Phase 1 (MVP - 2个月)
├── 多租户 + 团队管理
├── Facebook / LinkedIn / X 发布
├── 基础日历调度
├── 简单内容编辑器
└── AI 翻译 (中→英)

Phase 2 (核心 - 2个月)
├── Instagram / TikTok / YouTube / Pinterest
├── 多平台一次发布
├── AI 内容生成 (产品→帖文)
├── 统一社媒收件箱
├── 基础分析面板
└── 审批工作流

Phase 3 (增长 - 3个月)
├── 询盘自动识别 + 线索管理
├── CRM 集成
├── 视频自动生成
├── 最佳发布时间推荐
├── 客户门户
├── API + Webhook + MCP
└── WhatsApp Business

Phase 4 (生态 - 持续)
├── 阿里国际站集成
├── 归因分析
├── AI Agent 自动发帖
├── 移动端 App
├── 小程序
└── 社媒竞品监控
```

---

## 十一、核心参考来源总结

| 项目 | 可借鉴的核心价值 |
|------|----------------|
| **BrightBean Studio** | Provider 架构模式、多租户 RBAC 实现、HTMX 轻量前端、加密凭据存储、审批工作流、Client Portal 设计 |
| **Postiz** | 微服务架构（Next.js+NestJS+Temporal）、AI 内容生成范式、API 优先设计、N8N/Make 集成、多平台适配器 |
| **SocialDatabase** | 跨平台统一面板、AI 内容创作、3B+ 受众画像、内容库 AI 搜索、Paid+Organic 统一管理 |
