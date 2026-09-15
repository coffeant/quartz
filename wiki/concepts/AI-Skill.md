---
type: concept
tags: [AI, Skill, 外贸, Agent]
created: 2026-09-14
status: stable
---

# AI Skill

## 定义
Skill 是把重复做的事固化成的能力模块，相当于给 AI 装上的"技能包"。一个 Skill 通常包含：提示词模板、工作流定义、工具调用规则。

## 关键要点

### Skill 的价值
- **省 token**：预定义的工作流比每次从零描述节省大量 token
- **标准化**：确保每次执行结果一致
- **可迁移**：换 Agent 时，Skill 可以带走

### 使用策略
1. **先用别人的**：互联网上已经有大量现成 Skill
2. **找星标高的**：GitHub 上星标多的 Skill 经过更多验证
3. **注意开源协议**：商用需要注意许可证
4. **再收敛成自己的**：跑通后，根据自己的需求定制

### Skill vs 知识库
| 维度 | Skill | 知识库 |
|------|-------|--------|
| 内容 | 怎么做事 | 公司信息 |
| 变化 | 相对稳定 | 持续更新 |
| 用途 | 执行任务 | 提供信息 |

### 常见 Skill 类型
- **Prospecting**：客户挖掘
- **Cold Email**：开发信撰写
- **Content Creation**：内容生产
- **Data Analysis**：数据分析

## 关联
- [[AI知识库]] — Skill + 知识库 = AI 的核心资产
- [[Agent-选型]] — 选 Agent 后装 Skill
- [[Source-AI落地实战系列]] — 第 3 篇详细讲解

## 来源
- raw/clips/③｜给 AI 装技能别自己造，外面早就有人做好了.md

## 待确认
- Skill 的最佳实践格式？
- 如何评估一个 Skill 的质量？
