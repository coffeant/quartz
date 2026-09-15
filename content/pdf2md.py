"""
pdf2md.py — MinerU 下载的 Markdown 自动整理入知识库
用法:
  1. 在 https://mineru.net/OpenSourceTools/Extractor 上传 PDF 并下载 .md
  2. 把下载的 .md 文件放到 D:\go-to-marketing\raw\_mineru_outbox\
  3. 运行: python pdf2md.py
"""
import sys, io, shutil
from pathlib import Path
from datetime import date

# 路径配置
VAULT = Path("D:/go-to-marketing")
OUTBOX = VAULT / "raw/_mineru_outbox"
ARTICLES = VAULT / "raw/articles"

def main():
    OUTBOX.mkdir(parents=True, exist_ok=True)
    ARTICLES.mkdir(parents=True, exist_ok=True)
    
    # 扫描 outbox 中的所有 .md 文件
    files = list(OUTBOX.glob("*.md")) + list(OUTBOX.glob("*.markdown"))
    
    if not files:
        print(f"📁 没有找到 Markdown 文件")
        print(f"请把 MinerU 下载的 .md 文件放到: {OUTBOX}")
        return
    
    print(f"找到 {len(files)} 个文件，整理中...\n")
    
    for f in files:
        # 读取原始内容
        content = f.read_text(encoding="utf-8")
        
        # 提取标题
        title = f.stem.replace("_", " ").replace("-", " ")
        for line in content.split("\n"):
            clean = line.strip().lstrip("#").strip()
            if clean and len(clean) > 2:
                title = clean
                break
        
        # 构建带 front matter 的最终文件
        front = f"""---
type: article
source_pdf: {f.name}
tool: MinerU
tags: []
ingested: {date.today()}
---

# {title}

"""
        out_path = ARTICLES / f.name
        out_path.write_text(front + content, encoding="utf-8")
        
        # 从 outbox 删除已处理的文件
        f.unlink()
        
        print(f"  ✓ {f.name} → raw/articles/{f.name}")
    
    print(f"\n完成！{len(files)} 个文件已整理到 raw/articles/")

if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    main()
