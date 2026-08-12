#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成睡眠任务闭环一期原型平铺图集 index.html（GitHub Pages 可浏览 + 可复制 URL）"""
import os, urllib.parse

ROOT = os.path.dirname(os.path.abspath(__file__))
CANVAS = os.path.join(ROOT, "画布")

PAGES_BASE = "https://ddyuan-spec.github.io/taixiaohu/睡眠任务闭环一期/画布/"

# 逻辑分组顺序（按用户线下的产品流程）
GROUPS = [
    ("首页", [
        "首页-无任务.png",
        "首页-有任务.png",
        "首页-有任务 —已完成.png",
        "首页-健康日报生成弹窗.png",
    ]),
    ("睡眠", [
        "睡眠—无任务.png",
        "睡眠 —有任务.png",
        "睡眠 —有任务 已完成.png",
    ]),
    ("健康打卡", [
        "健康打卡—无任务.png",
        "健康打卡—有任务.png",
        "健康打卡—领取任务.png",
        "健康打卡—添加自定义任务.png",
        "健康打卡—全部任务完成.png",
    ]),
    ("任务详情 / 通知 / 弹窗", [
        "任务详情页.png",
        "每日消息通知.png",
        "每日首次完成任务弹窗.png",
    ]),
]

def enc(name: str) -> str:
    return urllib.parse.quote(name)

cards = []
for gname, files in GROUPS:
    items = []
    for f in files:
        p = os.path.join(CANVAS, f)
        if not os.path.exists(p):
            print("WARN 缺失:", f)
            continue
        url = PAGES_BASE + enc(f)
        items.append(f"""      <figure class="card">
        <img loading="lazy" src="{url}" alt="{f}" onclick="window.open('{url}','_blank')">
        <figcaption>
          <span class="name" title="{f}">{f}</span>
          <button class="copy" data-url="{url}" onclick="copyUrl(this)">复制链接</button>
        </figcaption>
      </figure>""")
    cards.append(f"""    <section class="group">
      <h2>{gname}</h2>
      <div class="grid">
{chr(10).join(items)}
      </div>
    </section>""")

html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>泰小虎 · 睡眠任务闭环一期 · 原型平铺图集</title>
<style>
  * {{ box-sizing: border-box; }}
  body {{ font-family: -apple-system, "PingFang SC", "Microsoft YaHei", sans-serif;
         margin: 0; background: #f6f7f9; color: #1f2329; }}
  header {{ padding: 28px 32px 12px; }}
  header h1 {{ margin: 0 0 6px; font-size: 22px; }}
  header p {{ margin: 0; color: #646a73; font-size: 13px; }}
  main {{ padding: 12px 32px 48px; }}
  .group {{ margin-top: 28px; }}
  .group h2 {{ font-size: 16px; border-left: 4px solid #3370ff; padding-left: 10px; margin: 0 0 14px; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 16px; }}
  .card {{ margin: 0; background: #fff; border: 1px solid #e5e6eb; border-radius: 10px; overflow: hidden;
          box-shadow: 0 1px 3px rgba(0,0,0,.04); }}
  .card img {{ width: 100%; display: block; cursor: zoom-in; background: #fafbfc; }}
  .card figcaption {{ display: flex; align-items: center; justify-content: space-between; gap: 8px;
                     padding: 8px 10px; border-top: 1px solid #f0f1f3; }}
  .name {{ font-size: 12px; color: #41464c; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
  .copy {{ flex: 0 0 auto; border: 1px solid #d0d3d9; background: #fff; color: #3370ff;
          border-radius: 6px; padding: 4px 10px; font-size: 12px; cursor: pointer; }}
  .copy:hover {{ background: #f0f5ff; }}
  .copy.done {{ color: #2ea121; border-color: #b7eb8f; }}
</style>
</head>
<body>
<header>
  <h1>泰小虎 · 睡眠任务闭环一期 · 原型平铺图集</h1>
  <p>线下制作的 C 端平铺原型（共 {sum(len(f) for _,f in GROUPS)} 张）· 来源压缩包「泰小虎睡眠任务闭环一期 (1).zip」· 归档于 GitHub Pages，供后续撰写 PRD 引用</p>
</header>
<main>
{chr(10).join(cards)}
</main>
<script>
  function copyUrl(btn) {{
    const u = btn.getAttribute('data-url');
    navigator.clipboard.writeText(u).then(() => {{
      btn.textContent = '已复制'; btn.classList.add('done');
      setTimeout(() => {{ btn.textContent = '复制链接'; btn.classList.remove('done'); }}, 1500);
    }});
  }}
</script>
</body>
</html>
"""

out = os.path.join(ROOT, "index.html")
with open(out, "w", encoding="utf-8") as f:
    f.write(html)
print("生成:", out, len(html), "bytes")
