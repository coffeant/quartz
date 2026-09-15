"""
import_skills.py — 将 marketingskills 仓库的 50 个技能导入 Wiki
"""
import re
from pathlib import Path

REPO = Path("D:/go-to-marketing/raw/_marketingskills/skills")
WIKI_DIR = Path("D:/go-to-marketing/wiki/skills")
WIKI_DIR.mkdir(exist_ok=True)

def extract_frontmatter(content: str):
    """提取 YAML front matter"""
    m = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if not m:
        return {}, content
    fm = {}
    for line in m.group(1).split('\n'):
        if ':' in line:
            k, v = line.split(':', 1)
            fm[k.strip()] = v.strip().strip('"').strip("'")
    return fm, content[m.end():]

def clean_content(text: str, max_lines: 200):
    """截取核心内容，去掉过长的引用和代码块"""
    lines = text.split('\n')
    return '\n'.join(lines[:max_lines])

def skill_to_wiki(skill_dir: Path) -> dict:
    """将单个技能转为 Wiki 页面内容"""
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return None
    
    content = skill_md.read_text(encoding='utf-8')
    fm, body = extract_frontmatter(content)
    
    name = fm.get('name', skill_dir.name)
    desc = fm.get('description', '')
    
    # 提取引用目录中的文件列表
    refs_dir = skill_dir / "references"
    refs = []
    if refs_dir.exists():
        refs = [f.name for f in refs_dir.glob("*.md")]
    
    return {
        'name': name,
        'description': desc,
        'body': body,
        'refs': refs,
        'source': f"raw/_marketingskills/skills/{skill_dir.name}/SKILL.md"
    }

def main():
    skills = []
    for d in sorted(REPO.iterdir()):
        if d.is_dir() and (d / "SKILL.md").exists():
            info = skill_to_wiki(d)
            if info:
                skills.append(info)
    
    # 为每个技能生成 Wiki 页面
    for s in skills:
        # 截取 description 的前200字作为摘要
        short_desc = s['description'][:200].rsplit(' ', 1)[0] + '...' if len(s['description']) > 200 else s['description']
        
        # 构建引用列表
        refs_section = ""
        if s['refs']:
            refs_section = "\n## 参考文件\n" + "\n".join(f"- `{r}`" for r in s['refs'])
        
        wiki_content = f"""---
type: concept
tags: [gtm, marketing-skill, {s['name']}]
created: 2026-09-14
updated: 2026-09-14
status: stable
source_repo: coreyhaines31/marketingskills
---

# {s['name']}

## 定义

{short_desc}

## 触发场景

<!-- 从 description 中提取的触发关键词 -->

## 核心内容

{s['body']}
{refs_section}

## 关联

- [[B2B-SaaS-GTM]]
- [[Marketing-Skills-Index]]

## 来源

- [{s['source']}](../../{s['source']})
"""
        out_path = WIKI_DIR / f"{s['name']}.md"
        out_path.write_text(wiki_content, encoding='utf-8')
    
    # 生成索引页
    index_lines = []
    for s in skills:
        index_lines.append(f"| [[{s['name']}]] | {s['description'][:80]}... | stable |")
    
    index_content = f"""---
type: topic
tags: [gtm, marketing-skills]
created: 2026-09-14
updated: 2026-09-14
status: stable
---

# Marketing Skills Index

> 来源: [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills)
> 共 {len(skills)} 个营销技能

## 技能列表

| 技能 | 简介 | 状态 |
|------|------|------|
{chr(10).join(index_lines)}

## 使用方式

每个技能页面包含：
- **定义**：该技能解决什么问题
- **触发场景**：什么情况下使用
- **核心内容**：完整的技能指令和方法论
- **参考文件**：原始仓库中的参考材料

## 分类

### 获取 (Acquisition)
- [[ads]] - 付费广告投放
- [[cold-email]] - 冷邮件开发
- [[seo-audit]] - SEO 审计
- [[ai-seo]] - AI 搜索优化
- [[programmatic-seo]] - 程序化 SEO
- [[content-strategy]] - 内容策略
- [[social]] - 社交媒体运营
- [[public-relations]] - 公关
- [[influencer-marketing]] - 网红营销
- [[directory-submissions]] - 目录提交

### 转化 (Activation & Conversion)
- [[copywriting]] - 营销文案
- [[copy-editing]] - 文案编辑
- [[cro]] - 转化率优化
- [[popups]] - 弹窗优化
- [[signup]] - 注册优化
- [[onboarding]] - 新用户引导
- [[paywalls]] - 付费墙设计
- [[pricing]] - 定价策略

### 留存 (Retention)
- [[emails]] - 邮件自动化
- [[sms]] - 短信营销
- [[churn-prevention]] - 流失预防

### 增长 (Revenue & Referral)
- [[referrals]] - 推荐计划
- [[launch]] - 产品发布
- [[offers]] - Offer 设计
- [[free-tools]] - 免费工具获客

### 研究与分析
- [[customer-research]] - 客户研究
- [[competitor-profiling]] - 竞品分析
- [[competitors]] - 竞品对比页
- [[analytics]] - 数据分析
- [[attribution]] - 归因分析
- [[ab-testing]] - A/B 测试

### 战略与规划
- [[marketing-plan]] - 营销计划
- [[marketing-ideas]] - 营销创意
- [[marketing-loops]] - 营销自动化
- [[marketing-council]] - 营销顾问团
- [[marketing-psychology]] - 营销心理学
- [[product-marketing]] - 产品营销
- [[positioning]] → [[Positioning]]

### 销售与营收
- [[sales-enablement]] - 销售赋能
- [[revops]] - 营收运营
- [[prospecting]] - 客户开发

### 其他
- [[aso]] - 应用商店优化
- [[ad-creative]] - 广告素材
- [[image]] - 图片生成
- [[video]] - 视频制作
- [[schema]] - 结构化数据
- [[site-architecture]] - 网站架构
- [[events]] - 活动营销
- [[community-marketing]] - 社区营销
- [[co-marketing]] - 联合营销
- [[lead-magnets]] - 引流磁铁
- [[free-tools]] - 免费工具
"""
    (WIKI_DIR / "Marketing-Skills-Index.md").write_text(index_content, encoding='utf-8')
    
    print(f"✓ 导入 {len(skills)} 个技能到 wiki/skills/")
    print(f"✓ 索引页: wiki/skills/Marketing-Skills-Index.md")

if __name__ == "__main__":
    import sys, io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    main()
