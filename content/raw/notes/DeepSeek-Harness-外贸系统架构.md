# DeepSeek Harness 外贸系统 — AI 即操作系统

> 用户在 DeepSeek Harness 对话框里说一句话，AI 自动操控所有系统

---

## 架构总览

```
┌──────────────────────────────────────────────────────────────┐
│                DeepSeek Harness (:3081)                       │
│                「外贸 AI 统一入口」                              │
│                                                              │
│  用户：「帮我查一下 ABC Trading 的背景，发个产品目录给他」         │
│                                                              │
│  AI 理解意图 → 选择工具 → 执行 → 返回结果                      │
└────────────────────┬─────────────────────────────────────────┘
                     │ Function Calling (tool calls)
                     ▼
┌──────────────────────────────────────────────────────────────┐
│           dsh-trade-tools (自建插件)                           │
│           注册为 DeepSeek Harness 的工具集                      │
│                                                              │
│  工具 1: wordpress_publish    → 发布/更新独立站内容              │
│  工具 2: wordpress_products   → 查询/管理产品目录               │
│  工具 3: social_schedule      → 排期社媒帖文                    │
│  工具 4: social_analytics     → 查询社媒数据                    │
│  工具 5: whatsapp_send        → 发送 WhatsApp 消息              │
│  工具 6: whatsapp_history     → 查询聊天记录                    │
│  工具 7: crm_contacts         → 管理客户信息                    │
│  工具 8: crm_inquiries        → 管理询盘                       │
│  工具 9: due_diligence        → 客户背调                       │
│  工具 10: seo_audit           → SEO 审计                       │
│  工具 11: product_sync        → Obsidian→独立站同步             │
│  工具 12: email_send          → 发送开发信                      │
└────────────────────┬─────────────────────────────────────────┘
                     │ HTTP 调用
                     ▼
┌──────────────────────────────────────────────────────────────┐
│              后端服务层 (Docker 容器)                            │
│                                                              │
│  WordPress :8080     产品目录 + 独立站                          │
│  Postiz    :4007     社媒排期发布                               │
│  CRM       :3000     客户数据管理                               │
│  WhatsApp  (API)     客户沟通                                  │
│  Obsidian  (本地)    知识库                                    │
└──────────────────────────────────────────────────────────────┘
```

---

## 实现方式：两种路径对比

### 路径 A：DeepSeek Harness 原生插件（推荐）

在 `deepseek-harness-repo/packages/` 下创建 `trade/` 插件组，每个工具是一个 Cordis 插件。

**优点**：
- 与 DeepSeek Harness 深度集成
- 工具注册后自动出现在 AI 的工具列表里
- 可以利用 Code Mode、权限系统、审批流程
- 用户体验最无缝

**缺点**：
- 需要理解 Cordis 插件系统
- 代码在 deepseek-harness-repo 内，跟随版本更新

### 路径 B：独立 API 中间件 + 一个桥接插件

建一个独立的 Node.js 服务 `dsh-trade-api`，DeepSeek Harness 只需一个 `http_request` 工具调用它。

**优点**：
- 独立部署，不侵入 DeepSeek Harness 源码
- 开发调试更简单
- 可以独立升级

**缺点**：
- 多一层网络调用
- AI 需要理解何时调用哪个端点

---

## 推荐：路径 A — 原生插件方式

### 插件目录结构

```
deepseek-harness-repo/packages/trade/
├── tool-wordpress/          # WordPress 工具
│   ├── src/
│   │   ├── index.ts         # 插件入口
│   │   ├── publish.ts       # 发布内容
│   │   ├── products.ts      # 产品管理
│   │   └── types.ts         # 类型定义
│   ├── package.json
│   └── tsconfig.json
│
├── tool-social/             # 社媒工具
│   ├── src/
│   │   ├── index.ts
│   │   ├── schedule.ts      # 排期发布
│   │   └── analytics.ts     # 数据分析
│   └── package.json
│
├── tool-whatsapp/           # WhatsApp 工具
│   ├── src/
│   │   ├── index.ts
│   │   ├── send.ts          # 发送消息
│   │   └── history.ts       # 聊天记录
│   └── package.json
│
├── tool-crm/                # CRM 工具
│   ├── src/
│   │   ├── index.ts
│   │   ├── contacts.ts      # 联系人管理
│   │   └── inquiries.ts     # 询盘管理
│   └── package.json
│
├── tool-research/           # 背调工具
│   ├── src/
│   │   ├── index.ts
│   │   └── due-diligence.ts # 客户背调
│   └── package.json
│
└── tool-seo/                # SEO 工具
    ├── src/
    │   ├── index.ts
    │   └── audit.ts         # SEO 审计
    └── package.json
```

### 单个工具的代码示例

以 WordPress 产品查询工具为例：

```typescript
// packages/trade/tool-wordpress/src/products.ts

import type { Context } from '@deepseek-ai/cordis'
import { defineTool } from '@deepseek-ai/dsh-tools'

export const name = 'wordpress-products'
export const inject = ['tools']

const WP_URL = process.env.WORDPRESS_URL || 'http://localhost:8080'
const WP_USER = process.env.WORDPRESS_USER || 'admin'
const WP_APP_PASSWORD = process.env.WORDPRESS_APP_PASSWORD || ''

async function wpFetch(endpoint: string, options?: RequestInit) {
  const url = `${WP_URL}/wp-json/wp/v2${endpoint}`
  const auth = Buffer.from(`${WP_USER}:${WP_APP_PASSWORD}`).toString('base64')
  return fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Basic ${auth}`,
      ...options?.headers,
    },
  })
}

export function apply(ctx: Context) {
  // 工具 1：查询产品列表
  ctx.tools.register(defineTool({
    name: 'wp_get_products',
    description: '查询独立站产品目录，支持按分类、关键词筛选',
    parameters: {
      category: { type: 'string', description: '产品分类：screws/bolts/nuts/washers/anchors' },
      keyword: { type: 'string', description: '搜索关键词' },
      page: { type: 'number', description: '页码，默认1' },
      per_page: { type: 'number', description: '每页数量，默认10' },
    },
    output: {
      schema: {
        type: 'object',
        properties: {
          total: { type: 'number' },
          products: { type: 'array' },
        },
      },
      render: (_args, value) => [{
        type: 'text',
        text: `找到 ${value.total} 个产品：\n${
          value.products.map((p: any) =>
            `- ${p.title} (${p.sku}) - ${p.status}`
          ).join('\n')
        }`,
      }],
    },
    async execute(args, exec) {
      const params = new URLSearchParams()
      if (args.category) params.set('categories', args.category)
      if (args.keyword) params.set('search', args.keyword)
      params.set('page', String(args.page || 1))
      params.set('per_page', String(args.per_page || 10))

      const res = await wpFetch(`/posts?${params}`)
      const products = await res.json()
      const total = parseInt(res.headers.get('X-WP-Total') || '0')

      return { total, products }
    },
  }))

  // 工具 2：发布产品
  ctx.tools.register(defineTool({
    name: 'wp_publish_product',
    description: '发布新产品到独立站',
    parameters: {
      title: { type: 'string', required: true, description: '产品标题（英文）' },
      content: { type: 'string', required: true, description: '产品描述 HTML' },
      sku: { type: 'string', required: true, description: '产品SKU' },
      category: { type: 'string', description: '产品分类' },
      status: {
        type: 'string',
        enum: ['draft', 'publish'],
        description: '发布状态',
        default: 'draft',
      },
    },
    output: {
      schema: {
        type: 'object',
        properties: {
          id: { type: 'number' },
          url: { type: 'string' },
          status: { type: 'string' },
        },
      },
      render: (_args, value) => [{
        type: 'text',
        text: `产品已发布：${value.url} (状态: ${value.status})`,
      }],
    },
    async execute(args, exec) {
      const res = await wpFetch('/posts', {
        method: 'POST',
        body: JSON.stringify({
          title: args.title,
          content: args.content,
          status: args.status || 'draft',
          meta: { _sku: args.sku },
        }),
      })
      const post = await res.json()
      return {
        id: post.id,
        url: post.link,
        status: post.status,
      }
    },
  }))

  // 工具 3：更新产品
  ctx.tools.register(defineTool({
    name: 'wp_update_product',
    description: '更新已有产品的信息',
    parameters: {
      id: { type: 'number', required: true, description: '产品ID' },
      title: { type: 'string', description: '新标题' },
      content: { type: 'string', description: '新描述' },
      status: { type: 'string', enum: ['draft', 'publish'] },
    },
    output: {
      schema: { type: 'object', properties: { success: { type: 'boolean' } } },
      render: (_args, value) => [{
        type: 'text',
        text: value.success ? '产品更新成功' : '产品更新失败',
      }],
    },
    async execute(args, exec) {
      const body: any = {}
      if (args.title) body.title = args.title
      if (args.content) body.content = args.content
      if (args.status) body.status = args.status

      await wpFetch(`/posts/${args.id}`, {
        method: 'POST',
        body: JSON.stringify(body),
      })
      return { success: true }
    },
  }))
}
```

### 同理，其他工具的注册

```typescript
// WhatsApp 工具
export function apply(ctx: Context) {
  ctx.tools.register(defineTool({
    name: 'whatsapp_send',
    description: '通过 WhatsApp 发送消息给客户',
    parameters: {
      to: { type: 'string', required: true, description: '客户手机号（含国际区号）' },
      message: { type: 'string', required: true, description: '消息内容' },
      template: { type: 'string', description: '预设模板名（可选）' },
    },
    output: {
      schema: { type: 'object', properties: { success: { type: 'boolean' }, messageId: { type: 'string' } } },
      render: (_args, value) => [{
        type: 'text',
        text: value.success ? `消息已发送 (ID: ${value.messageId})` : '发送失败',
      }],
    },
    async execute(args, exec) {
      const res = await fetch('http://localhost:3090/whatsapp/send', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ to: args.to, message: args.message }),
      })
      return res.json()
    },
  }))
}

// CRM 工具
export function apply(ctx: Context) {
  ctx.tools.register(defineTool({
    name: 'crm_search_contacts',
    description: '搜索CRM中的客户联系人',
    parameters: {
      query: { type: 'string', required: true, description: '搜索关键词（公司名/人名/邮箱）' },
      status: { type: 'string', enum: ['lead', 'prospect', 'customer', 'inactive'] },
    },
    output: {
      schema: { type: 'object', properties: { contacts: { type: 'array' }, total: { type: 'number' } } },
      render: (_args, value) => [{
        type: 'text',
        text: `找到 ${value.total} 个联系人：\n${
          value.contacts.map((c: any) =>
            `- ${c.name} (${c.company}) - ${c.status} - ${c.email}`
          ).join('\n')
        }`,
      }],
    },
    async execute(args, exec) {
      const res = await fetch('http://localhost:3001/api/contacts/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: args.query, status: args.status }),
      })
      return res.json()
    },
  }))
}

// 客户背调工具
export function apply(ctx: Context) {
  ctx.tools.register(defineTool({
    name: 'due_diligence',
    description: '对客户进行背景调查，包括公司信息、信用评估、制裁检查',
    parameters: {
      company_name: { type: 'string', required: true, description: '公司名称' },
      country: { type: 'string', description: '所在国家' },
      website: { type: 'string', description: '公司网站（可选）' },
    },
    output: {
      schema: {
        type: 'object',
        properties: {
          company_info: { type: 'object' },
          risk_level: { type: 'string' },
          credit_score: { type: 'number' },
          recommendation: { type: 'string' },
        },
      },
      render: (_args, value) => [{
        type: 'text',
        text: `背调报告：${value.company_info?.name || 'N/A'}
风险等级：${value.risk_level}
信用评分：${value.credit_score}/100
建议：${value.recommendation}`,
      }],
    },
    async execute(args, exec) {
      // 调用本地背调 API（自建或第三方）
      const res = await fetch('http://localhost:3090/research/company', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          company: args.company_name,
          country: args.country,
          website: args.website,
        }),
      })
      return res.json()
    },
  }))
}
```

---

## 配置：cordis.yml

在 DeepSeek Harness 的配置文件中加载外贸工具：

```yaml
# cordis.yml
plugins:
  # 原有基础插件
  - name: dsh-base
    bundle: true

  # 加载外贸工具包
  - name: dsh-trade-tools
    bundle: true
    config:
      wordpress:
        url: 'http://localhost:8080'
        user: 'admin'
        app_password: 'xxxx xxxx xxxx xxxx'
      whatsapp:
        api_url: 'http://localhost:3090'
        api_key: 'your-whatsapp-api-key'
      crm:
        url: 'http://localhost:3001'
        api_key: 'your-crm-api-key'
      postiz:
        url: 'http://localhost:4007'
        api_key: 'your-postiz-api-key'
```

---

## 用户交互示例

### 场景 1：发布新产品

```
用户：帮我把 M10x30 六角螺栓 8.8 级镀锌 发布到独立站

AI 思考：
  1. 从 Obsidian 知识库读取产品 Markdown
  2. 调用 wp_publish_product 发布到 WordPress
  3. 返回发布结果

AI：产品已发布到独立站：
- 标题：M10x30 Hex Bolt Grade 8.8 Hot Dip Galvanized
- 链接：https://yoursite.com/products/m10x30-hex-bolt
- 状态：草稿（需要你确认后上线）

需要我把它发布上线吗？或者先发到 Facebook 做推广？
```

### 场景 2：客户背调

```
用户：查一下 ABC Trading LLC (UAE) 的背景

AI 思考：
  1. 调用 due_diligence 工具
  2. 从 web search 获取公司信息
  3. 检查制裁名单
  4. 生成背调报告

AI：背调报告 — ABC Trading LLC

📋 基本信息
- 国家：UAE, Dubai
- 行业：Hardware & Building Materials
- 规模：50-200 人
- 成立：2015 年

✅ 风险评估
- 制裁检查：通过（OFAC/EU/UN）
- 信用评分：72/100
- 风险等级：🟢 LOW

👤 决策人
- 采购经理：Ahmed Al-Rashid
- LinkedIn：linkedin.com/in/ahmed-rashid

💡 建议
- 推荐跟进，客户资质良好
- 建议提供 CE/PVOC 认证产品
- 首单建议 LC 结算

需要我把这个客户添加到 CRM 并安排跟进吗？
```

### 场景 3：社媒发帖

```
用户：给 Facebook 发一条关于不锈钢螺丝的产品帖

AI 思考：
  1. 从 Obsidian 读取不锈钢螺丝产品信息
  2. AI 生成英文帖文（含 CTA）
  3. 调用 social_schedule 排期发布

AI：已为你准备了 3 条帖文，选择哪条？

1️⃣ 技术科普型
"Did you know? Stainless steel screws (304/316) can withstand
salt spray corrosion for 1000+ hours. Perfect for coastal
construction projects. 🏗️
#Fasteners #StainlessSteel #Construction"

2️⃣ 客户案例型
"Another successful shipment of 304 stainless steel screws
to Dubai! 5 tons, ready for your next project.
📩 DM us for pricing"
#Fasteners #Dubai #Export"

3️⃣ 促销型
"🔥 Stainless Steel Screws - Factory Direct Price!
✅ 304/316 grade
✅ CE Certified
✅ MOQ: 1 ton
📩 Get your free quote today!"
#StainlessSteel #Hardware"

选择一条，或者告诉我修改方向？
```

### 场景 4：WhatsApp 跟进

```
用户：给上周询价的 ABC Trading 发个 WhatsApp，问他们对报价的看法

AI 思考：
  1. 从 CRM 查找 ABC Trading 的联系方式
  2. 从 CRM 查找最近的报价记录
  3. 生成跟进消息
  4. 调用 whatsapp_send 发送

AI：已找到 ABC Trading 的 WhatsApp：+971-50-XXXX-XXX

已发送以下消息：

"Dear Ahmed,

Hope this message finds you well.

We sent you the quotation for M10x30 Hex Bolts (Grade 8.8)
last Tuesday. Just wanted to follow up — do you have any
questions or need any modifications?

We can also offer:
• Free samples for quality testing
• Flexible payment terms for first orders

Looking forward to your feedback.

Best regards"

消息已发送，我会在对方回复后通知你。
```

---

## 自建 API 中间件（处理插件无法直接调用的服务）

有些服务（如 WhatsApp API、背调查询）需要一个薄 API 层：

```
dsh-trade-api/
├── src/
│   ├── index.ts              # Express/Fastify 入口
│   ├── routes/
│   │   ├── whatsapp.ts       # WhatsApp Business API 代理
│   │   ├── research.ts       # 背调查询（Web Search + AI）
│   │   └── product-sync.ts   # Obsidian → WordPress 同步
│   └── services/
│       ├── whatsapp-client.ts
│       ├── research-agent.ts
│       └── obsidian-reader.ts
├── package.json
└── docker-compose.yml        # 与 DeepSeek Harness 一起部署
```

这个中间件只做**协议转换**，不带业务逻辑。DeepSeek Harness 的 AI 做所有决策。

---

## 端口总览

| 服务 | 端口 | 说明 |
|------|------|------|
| DeepSeek Harness | 3081 | AI 统一入口（用户界面） |
| dsh-trade-api | 3090 | 中间件（WhatsApp/背调等） |
| WordPress | 8080 | 独立站 |
| Postiz | 4007 | 社媒排期 |
| CRM App | 3000 | CRM 前端 |
| CRM API | 3001 | CRM 后端 |
| Obsidian | — | 本地编辑器 |

---

## 用户使用流程

```
1. 启动所有 Docker 容器
2. 打开浏览器 → http://localhost:3081
3. 在 DeepSeek Harness 对话框里输入自然语言指令
4. AI 自动选择工具、执行操作、返回结果
5. 用户确认或修改
```

---

## 商业化包装

对外销售时：

1. **一键安装包**：Docker Compose 一键启动所有服务
2. **预配置模板**：针对不同行业（紧固件/建材/机械）预置产品模板
3. **SaaS 版**：云端部署，用户只需打开浏览器
4. **自部署版**：客户自己的服务器运行，数据完全自主
5. **培训服务**：教客户如何用自然语言操控系统

定价：
- 基础版：¥1999/月（独立站 + 社媒 + 基础 CRM）
- 专业版：¥4999/月（+ WhatsApp + 背调 + AI 内容生成）
- 企业版：¥9999/月（+ 多租户 + API + 白标）
- 自部署版：¥49999/一次性

---

*创建时间：2026-09-01*
*核心理念：AI 即操作系统，自然语言即操控界面*
