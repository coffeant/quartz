# 竞品监测 → AI 再造 → Idea Kanban — 完整工作流

> 基于 BrightBean Studio 现有代码（Idea + IdeaGroup + Kanban board）
> 目标：在 Create 页面加一个"竞品监测"Tab，选爆款 → AI 变成自己的 → 落入 Unassigned → 反复润色 → 发布

---

## 一、现有代码中已有的部分

### 1.1 Idea 看板（可直接复用）

| 现有组件 | 位置 | 状态 |
|---------|------|------|
| `Idea` 模型 | `apps/composer/models.py:115` | ✅ 有 `title`, `description`, `tags`, `media_asset`, `group`, `post` |
| `IdeaGroup`（看板列） | `apps/composer/models.py:90` | ✅ 默认列：Unassigned → To Do → In Progress → Done |
| Kanban 渲染 | `templates/composer/create_landing.html` | ✅ 完整 UI，拖拽支持 |
| Idea CRUD | `apps/composer/views.py:1848` | ✅ `idea_create`, `idea_edit`, 移动、删除 |
| Idea → Post 转化 | `apps/composer/views.py` 中 `convert_to_post` | ✅ 已有 |
| 媒体附件 | `IdeaMedia` 模型 | ✅ |

### 1.2 需要新增的部分

| 组件 | 说明 |
|------|------|
| **竞品账号管理** | 用户添加竞品社媒账号 URL（LinkedIn/Facebook/TikTok） |
| **内容采集** | 定时拉取竞品的最新帖文+视频 |
| **竞品内容 Feed** | 在 Create 页面新增 "Competitor" Tab，展示采集到的内容 |
| **AI 内容再造** | 选一篇竞品爆文 → AI 分析结构 → 结合自己产品生成新 Idea |
| **Idea 润色** | 在 Idea 编辑器中加入 AI 辅助按钮："更专业"/"加参数"/"改语气" |

---

## 二、完整用户流程

```
                      ┌───────────────────────┐
                      │  Create 页面            │
                      │                        │
                      │  Tab: Ideas(看板)       │
                      │  Tab: Competitor(新增)  │  ← 用户点这里
                      └──────────┬────────────┘
                                 │
                                 ▼
               ┌───────────────────────────────────┐
               │  Competitor Feed                   │
               │                                    │
               │  竞品A - LinkedIn - 2小时前          │
               │  ┌─────────────────────────────┐   │
               │  │ "Our new CNC machine..."    │   │
               │  │ [图片] [💡 Use this]        │   │  ← 用户点击
               │  └─────────────────────────────┘   │
               │                                    │
               │  竞品B - TikTok - 5小时前           │
               │  ┌─────────────────────────────┐   │
               │  │ [视频] [💡 Use this]         │   │
               │  └─────────────────────────────┘   │
               │                                    │
               │  竞品A - Facebook - 昨天            │
               │  ┌─────────────────────────────┐   │
               │  │ "How to choose..."          │   │
               │  │ [图片] [💡 Use this]        │   │
               │  └─────────────────────────────┘   │
               └───────────────────────────────────┘
                                 │ 用户点击 "💡 Use this"
                                 ▼
               ┌───────────────────────────────────┐
               │  AI 再造弹窗                       │
               │                                    │
               │  原文: "Our new CNC machine..."     │
               │  ─────────────────────────────     │
               │  我的产品: 激光切割机 XYZ-2000      │  ← 用户输入或选择
               │  目标平台: LinkedIn                 │
               │  语气:    [专业] [案例] [技术]      │
               │                                    │
               │  [✨ 生成我的版本]                  │
               │                                    │
               │  结果预览:                          │
               │  "Introducing XYZ-2000..."         │  ← AI 生成
               │  [不满意] [这个好 ✓]                │
               └───────────────────────────────────┘
                                 │ 用户点击 "这个好"
                                 ▼
               ┌───────────────────────────────────┐
               │  Idea 自动创建 → 落入 Unassigned    │
               │                                    │
               │  Idea(title="激光切割机新品发布")    │
               │  description="Introducing XYZ-..."  │
               │  status=UNASSIGNED                  │
               │  group=Unassigned 列                │
               │  tags=["竞品A-灵感"]                │
               │  media=原帖封面图(作为参考)          │
               └───────────────────────────────────┘
                                 │
                                 ▼
               ┌───────────────────────────────────┐
               │  用户在看板中拖到 "In Progress"     │
               │  点击编辑 → 看到 AI 润色按钮:       │
               │                                    │
               │  [✨ 更专业] [✨ 加技术参数]         │
               │  [✨ 缩短] [✨ 加CTA]               │
               │  [✨ 翻译英文] [✨ 翻译西班牙语]     │
               │                                    │
               │  每次点击 → AI 重新生成 description  │
               │  用户可以反复润色                    │
               └───────────────────────────────────┘
                                 │
                                 ▼
               ┌───────────────────────────────────┐
               │  满意后 → "Convert to Post"        │
               │                                    │
               │  进入已有流程:                      │
               │  Composer → 完善 caption/media     │
               │  → 选择平台 → 排期 → 审批 → 发布    │
               └───────────────────────────────────┘
```

---

## 三、竞品账号管理

需要新增的数据模型：

```python
class CompetitorAccount(models.Model):
    """竞品社媒账号"""
    workspace = ForeignKey(Workspace)
    name = CharField(max_length=255)           # 竞品名称
    platform = CharField(choices=PLATFORMS)     # linkedin / facebook / tiktok
    profile_url = URLField()                   # 主页 URL
    external_id = CharField()                  # 平台上的 ID
    avatar_url = URLField(blank=True)          # 头像
    is_active = BooleanField(default=True)
    last_fetched_at = DateTimeField(null=True)
    created_at = DateTimeField(auto_now_add=True)

class CompetitorPost(models.Model):
    """采集到的竞品内容"""
    account = ForeignKey(CompetitorAccount, related_name="posts")
    platform_post_id = CharField(unique=True)   # 平台原始 post ID
    content = TextField()                      # 文案内容
    media_urls = JSONField(default=list)       # 图片/视频 URL 列表
    media_type = CharField()                   # image / video / carousel
    posted_at = DateTimeField()                # 发布时间
    likes_count = IntegerField(default=0)      # 互动数据
    comments_count = IntegerField(default=0)
    shares_count = IntegerField(default=0)
    view_count = IntegerField(null=True)       # 播放量（视频）
    fetched_at = DateTimeField(auto_now_add=True)
```

**采集方式**（不需要自己爬，降低法律风险）：

| 方式 | 说明 |
|------|------|
| **用户手动粘贴** | 用户浏览竞品社媒，觉得好的帖文直接粘贴链接 → 系统解析并保存 |
| **RSS/Webhook 订阅** | LinkedIn/Facebook 等部分平台支持内容通知 |
| **API 读取** | 通过各家 API 读取竞品公开内容（需竞品账号授权，较难） |
| **第三方工具导入** | 用户从 SocialDatabase 等工具导出竞品数据后导入 |

> 建议 MVP 先做**用户手动粘贴链接 → 自动解析**，后期再考虑自动采集。

**用户贴链接的流程**：
```
用户在竞品页面看到好帖文 → 复制链接
  → 粘贴到 BrightBean Competitor Tab 的输入框
  → 系统自动解析（Open Graph / oEmbed API）
  → 保存为 CompetitorPost
  → 展示在 Feed 列表
```

---

## 四、AI 再造引擎逻辑

### 4.1 从竞品内容 → 新 Idea 的转换

```
竞品原文:
"Our new CNC machining center delivers ±0.005mm precision. 
Perfect for aerospace and medical components. 
Visit our website for more details."

AI 分析并提取:
  结构: Hook(精度数据) → 应用领域 → CTA(官网)
  角度: 技术参数驱动
  语气: 专业自信

用户输入: 我的产品是 激光切割机 XYZ-2000，主要卖点是 速度快30%

AI 生成新的:
"XYZ-2000: 30% faster cutting speed without compromising precision.
Ideal for sheet metal fabrication and automotive parts.
Get a quote today → [link]"
```

### 4.2 Idea 编辑器内的 AI 润色按钮

在现有的 Idea 编辑弹窗中增加一组 AI 动作按钮：

```
┌─────────────────────────────────────────────┐
│  编辑 Idea                                    │
│                                              │
│  Title: 激光切割机新品发布                      │
│                                              │
│  Description:                                │
│  ┌─────────────────────────────────────────┐ │
│  │ Introducing XYZ-2000...                 │ │
│  │                                         │ │
│  └─────────────────────────────────────────┘ │
│                                              │
│  AI 润色:                                     │
│  [✨ 更专业] [✨ 加技术参数] [✨ 缩短到3句话]   │
│  [✨ 加 CTA]  [✨ 翻译英文] [✨ 更口语化]       │
│                                              │
│  [保存] [取消]                                 │
└─────────────────────────────────────────────┘
```

实现方式：点击任意润色按钮 → HTMX POST 到 AI 服务 → 携带当前 description + 润色指令 → AI 返回新的 description → 替换 textarea 内容（用户可继续手动修改）。

### 4.3 修改点清单

| 文件 | 修改内容 |
|------|---------|
| **新文件** `apps/competitor/models.py` | `CompetitorAccount` + `CompetitorPost` 模型 |
| **新文件** `apps/competitor/services.py` | 内容采集逻辑（URL 解析、oEmbed） |
| **新文件** `apps/competitor/views.py` | Feed 展示、采集、AI 再造 |
| **新文件** `apps/competitor/urls.py` | 路由 |
| `templates/composer/create_landing.html` | 增加 "Competitor" Tab，新增 Feed 面板 |
| `apps/composer/views.py` | `idea_create` 增加 AI 参数入口 |
| `apps/composer/templates/.../idea_modal.html` | 编辑弹窗中增加 AI 润色按钮行 |
| **新文件** `apps/ai_assistant/client.py` | AI API 客户端 |
| **新文件** `apps/ai_assistant/prompts.py` | Prompt 模板：再造 / 润色 / 翻译 |
| `apps/ai_assistant/views.py` | HTMX endpoint: `/ai/adapt-from-competitor/`, `/ai/refine-idea/`, `/ai/translate-idea/` |

---

## 五、这个方案 vs 已有方案对比

| 维度 | 现有 Intelligence | 这个方案 |
|------|------------------|---------|
| 输入 | 用户自己的 YouTube 视频 | **竞品社媒帖文** |
| 输出 | 评分/分析报告 | **新的 Idea（可直接发布的内容）** |
| 和 Idea 看板的关系 | 无关 | **直接创建 Idea → 落入 Unassigned** |
| 用户感知 | 独立分析工具 | **从灵感采集到内容发布的闭环** |
| 核心价值 | 知道自己的内容好不好 | **知道竞品在做什么 → AI 变成自己的** |

## 六、一句话总结

> **这不是一个 "AI 写文章" 的功能，而是一条流水线：**  
> **刷竞品 → 选爆款 → AI 再造 → Idea 看板 → 反复润色 → Convert to Post → 发布**  
>  
> 所有已有的基础设施（Idea 模型、Kanban UI、Composer、Publisher）都**不需要改动**，  
> 只需要在 **上游接一个 "竞品采集 → AI 再造" 的入口**，  
> 在 **下游 Idea 编辑器里加一组 "AI 润色" 按钮**。
