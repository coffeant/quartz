# 🧠 Go-to-Market 知识库

基于 Karpathy LLM Wiki 理论搭建的自生长个人知识库。

## 架构

```
Raw   → 原始资料（文章、对话、灵感、研究）
Wiki  → AI 整理的知识节点（概念、实体、主题、来源）
Schema → 归档规则（如何处理冲突、更新、引用）
```

## 工作流

1. **Raw 输入**：剪藏文章、粘贴对话、记录灵感
2. **Schema 驱动**：Agent 按规则识别概念 → 创建/补充 Wiki 页面
3. **持续演化**：每个输入都留下结构化结果，知识库持续生长

## 目录结构

```
├── raw/              # 原始资料层
│   ├── articles/     # 剪藏/收藏的文章
│   ├── chats/        # AI 对话记录
│   ├── notes/        # 随手记的灵感
│   ├── clips/        # 浏览器剪藏
│   └── research/     # 市场研究、竞品分析
├── wiki/             # 知识沉淀层
│   ├── concepts/     # 核心概念定义
│   ├── entities/     # 具体实体（公司、人物、产品）
│   ├── topics/       # 主题页面（聚合多概念）
│   ├── sources/      # 来源摘要
│   └── frameworks/   # 方法论框架
├── schema/           # 规则层
│   ├── AGENTS.md     # Agent 指令（核心）
│   ├── _index.md     # 知识库索引
│   └── changelog.md  # 变更记录
└── templates/        # 模板
```

## 快速开始

1. 在 `raw/` 下放入一篇文章
2. Agent 识别 → 在 `wiki/` 创建对应页面
3. 页面之间自动建立双链关联
4. 查询时 Agent 优先检索 Wiki 层
