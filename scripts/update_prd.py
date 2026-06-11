#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PRD文档修改脚本
"""

import re
import sys

def fix_tables(content):
    """修复表格样式"""
    # 查找所有表格块并修复
    lines = content.split('\n')
    result = []
    in_table = False
    table_lines = []
    
    for line in lines:
        # 检测表格开始（包含 --- 或 === 的分隔线）
        if re.match(r'^[\s]*[-=]{3,}', line) and not in_table:
            in_table = True
            table_lines = [line]
        elif in_table:
            table_lines.append(line)
            # 检测表格结束（空行或新标题）
            if line.strip() == '' or line.startswith('#'):
                in_table = False
                # 处理表格
                fixed_table = process_table(table_lines[:-1] if line.startswith('#') else table_lines)
                result.extend(fixed_table)
                if line.startswith('#'):
                    result.append(line)
            elif len(table_lines) > 20:  # 防止无限累积
                in_table = False
                result.extend(table_lines)
        else:
            result.append(line)
    
    if in_table and table_lines:
        result.extend(process_table(table_lines))
    
    return '\n'.join(result)

def process_table(lines):
    """处理单个表格，确保格式正确"""
    # 简化为Markdown标准表格格式
    result = []
    header_found = False
    
    for line in lines:
        stripped = line.strip()
        # 跳过分隔线中的空内容
        if re.match(r'^[\s]*[-=]{3,}[\s]*$', stripped):
            if not header_found:
                result.append('| ' + ' | '.join(['---'] * 10) + ' |')  # 默认分隔线
                header_found = True
            continue
        
        # 处理内容行
        if stripped and not stripped.startswith('---') and not stripped.startswith('==='):
            # 将空格分隔转换为 | 分隔
            if '|' not in stripped:
                parts = re.split(r'\s{2,}', stripped)  # 两个以上空格分隔
                if len(parts) >= 2:
                    line = '| ' + ' | '.join(parts) + ' |'
            result.append(line)
            if not header_found and len(result) == 1:
                # 添加分隔线
                cols = line.count('|') - 1
                result.append('| ' + ' | '.join(['---'] * cols) + ' |')
                header_found = True
    
    return result

def add_prompt_button(content):
    """在Prompt工程设计部分添加跳转按钮"""
    prompt_section = "## 六、Prompt工程设计"
    if prompt_section in content:
        button_html = '''

<div style="margin: 16px 0; padding: 16px; background: #e8f4fd; border-radius: 8px; border-left: 4px solid #1890ff;">
  <strong>📄 Prompt完整文档</strong><br>
  详细的Prompt设计、版本管理、Coze集成指南请查看：
  <a href="https://ddyuan-spec.github.io/taixiaohu/docs/%E6%B3%B0%E5%B0%8F%E8%99%8E_Prompt%E5%AE%8C%E6%95%B4%E6%96%87%E6%A1%A3_V1.html" target="_blank" style="display: inline-block; margin-top: 8px; padding: 8px 16px; background: #1890ff; color: white; text-decoration: none; border-radius: 4px;">打开 Prompt 文档 →</a>
</div>

'''
        # 在六、Prompt工程设计标题后添加按钮
        content = content.replace(prompt_section, prompt_section + button_html)
    return content

def add_eval_button(content):
    """在评测体系部分添加跳转按钮"""
    eval_section = "## 八、评测体系"
    if eval_section in content:
        button_html = '''

<div style="margin: 16px 0; padding: 16px; background: #e6f4ea; border-radius: 8px; border-left: 4px solid #52c41a;">
  <strong>🧪 评测集完整文档</strong><br>
  详细的评测用例、评分标准、测试方法请查看：
  <a href="https://ddyuan-spec.github.io/taixiaohu/docs/%E6%B3%B0%E5%B0%8F%E8%99%8E_%E8%AF%84%E6%B5%8B%E9%9B%86_V1.html" target="_blank" style="display: inline-block; margin-top: 8px; padding: 8px 16px; background: #52c41a; color: white; text-decoration: none; border-radius: 4px;">打开 评测集 文档 →</a>
</div>

'''
        content = content.replace(eval_section, eval_section + button_html)
    return content

def add_prototype_links(content):
    """添加原型链接，删除冗余内容"""
    # 在相关章节添加原型链接
    prototype_section = """## 原型演示

<div style="margin: 16px 0; padding: 20px; background: #fff7e6; border-radius: 8px; border-left: 4px solid #fa8c16;">
  <strong>🎮 可交互原型</strong><br>
  
  <div style="margin-top: 12px;">
    <a href="https://ddyuan-spec.github.io/taixiaohu/prototype.html" target="_blank" style="display: inline-block; margin-right: 12px; padding: 10px 20px; background: #FF6B35; color: white; text-decoration: none; border-radius: 6px;">📱 移动APP交互原型 →</a>
    <a href="https://ddyuan-spec.github.io/taixiaohu/backend-prototype.html" target="_blank" style="display: inline-block; padding: 10px 20px; background: #1A365D; color: white; text-decoration: none; border-radius: 6px;">⚙️ 管理后台交互原型 →</a>
  </div>
</div>

"""
    
    # 在业务流程图后添加原型链接
    if "## 三、业务流程图" in content:
        content = content.replace("## 三、业务流程图", prototype_section + "## 三、业务流程图")
    
    return content

def remove_appendix(content):
    """删除附录"""
    # 找到附录开始的位置
    appendix_pattern = r'# 附录.*$'
    content = re.sub(appendix_pattern, '', content, flags=re.DOTALL)
    return content.strip()

def add_flowchart_link(content):
    """添加流程图链接"""
    # 替换"（流程图待后续补充）"
    flowchart_placeholder = "（流程图待后续补充）"
    flowchart_link = """（<a href="https://ddyuan-spec.github.io/taixiaohu/docs/业务流程图.html" target="_blank">点击查看完整流程图 →</a>）"""
    content = content.replace(flowchart_placeholder, flowchart_link)
    return content

def remove_redundant_prompt_content(content):
    """删除Prompt章节中的冗余内容，只保留跳转按钮"""
    # 找到六、Prompt工程设计章节
    pattern = r'(## 六、Prompt工程设计.*?)## 七、'
    match = re.search(pattern, content, re.DOTALL)
    if match:
        section = match.group(1)
        # 保留标题和按钮，删除其他内容
        new_section = """## 六、Prompt工程设计

<div style="margin: 16px 0; padding: 16px; background: #e8f4fd; border-radius: 8px; border-left: 4px solid #1890ff;">
  <strong>📄 Prompt完整文档</strong><br>
  Prompt架构设计、System Prompt、意图选择规范、各场景Prompt详情、Coze集成指南等完整内容请查看：
  <a href="https://ddyuan-spec.github.io/taixiaohu/docs/%E6%B3%B0%E5%B0%8F%E8%99%8E_Prompt%E5%AE%8C%E6%95%B4%E6%96%87%E6%A1%A3_V1.html" target="_blank" style="display: inline-block; margin-top: 8px; padding: 8px 16px; background: #1890ff; color: white; text-decoration: none; border-radius: 4px;">打开 Prompt 文档 →</a>
</div>

"""
        content = content.replace(section, new_section)
    return content

def remove_redundant_eval_content(content):
    """删除评测章节中的冗余内容，只保留跳转按钮"""
    # 找到八、评测体系章节
    pattern = r'(## 八、评测体系.*?)## 九、'
    match = re.search(pattern, content, re.DOTALL)
    if match:
        section = match.group(1)
        # 保留标题和按钮，删除其他内容
        new_section = """## 八、评测体系

<div style="margin: 16px 0; padding: 16px; background: #e6f4ea; border-radius: 8px; border-left: 4px solid #52c41a;">
  <strong>🧪 评测集完整文档</strong><br>
  评测用例（50+条）、五维度评分标准、测试方法、通过标准等完整内容请查看：
  <a href="https://ddyuan-spec.github.io/taixiaohu/docs/%E6%B3%B0%E5%B0%8F%E8%99%8E_%E8%AF%84%E6%B5%8B%E9%9B%86_V1.html" target="_blank" style="display: inline-block; margin-top: 8px; padding: 8px 16px; background: #52c41a; color: white; text-decoration: none; border-radius: 4px;">打开 评测集 文档 →</a>
</div>

"""
        content = content.replace(section, new_section)
    return content

def update_data_flywheel(content):
    """更新数据飞轮与迭代机制章节"""
    old_section = """## 十二、数据飞轮与迭代机制

效果提升 ← 模型/Prompt优化 ← 问题归因分析

• 每周汇总线上Bad Case，归类失败原因

• 每月评估是否需要Prompt调优或模型升级

• 每季度评审数据飞轮运转效率"""
    
    new_section = """## 十二、数据飞轮与迭代机制

### 12.1 迭代闭环流程

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  收集反馈   │ → │  问题归因   │ → │  优化实施   │ → │  效果验证   │
│  (Bad Case) │    │  (分类分析) │    │  (Prompt/   │    │  (A/B测试)  │
│             │    │             │    │  知识库)    │    │             │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
       ↑                                                        │
       └────────────────────────────────────────────────────────┘
                        (数据回流)
```

### 12.2 后台功能支撑

**数据飞轮工作台**（管理后台功能）：
- Bad Case归因分析：支持按Prompt问题/知识库缺失/模型限制/意图识别错误分类标记
- 优化任务管理：待优化 → 优化中 → 已验证 → 已上线的全流程跟踪
- A/B测试管理：Prompt版本对比、流量分配、显著性分析
- 知识库优化建议：自动识别高频未命中问题，推荐新增/更新文档

### 12.3 迭代节奏

| 周期 | 动作 | 负责人 |
|------|------|--------|
| 每周 | 汇总线上Bad Case，归类失败原因 | 运营团队 |
| 每月 | 评估Prompt调优需求，实施优化 | 产品+技术 |
| 每季度 | 评审数据飞轮运转效率，调整策略 | 项目组 |

**相关文档：** [管理后台原型 - 数据飞轮模块](https://ddyuan-spec.github.io/taixiaohu/backend-prototype.html)"""
    
    content = content.replace(old_section, new_section)
    return content

def main():
    # 读取PRD文件
    input_file = r"C:\Users\13364\AppData\Roaming\TRAE SOLO CN\ModularData\ai-agent\work-mode-projects\6a13aa213e650191190c1c56\taixiaohu_PRD_V1.3.md"
    output_file = r"c:\Users\13364\.trae-cn\work\6a13aa213e650191190c1c59\taixiaohu-site\docs\taixiaohu_PRD_V1.3.html"
    
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 应用所有修改
    print("1. 修复表格样式...")
    content = fix_tables(content)
    
    print("2. 添加流程图链接...")
    content = add_flowchart_link(content)
    
    print("3. 添加Prompt跳转按钮，删除冗余内容...")
    content = remove_redundant_prompt_content(content)
    
    print("4. 添加评测集跳转按钮，删除冗余内容...")
    content = remove_redundant_eval_content(content)
    
    print("5. 添加原型链接...")
    content = add_prototype_links(content)
    
    print("6. 更新数据飞轮章节...")
    content = update_data_flywheel(content)
    
    print("7. 删除附录...")
    content = remove_appendix(content)
    
    # 转换为HTML
    html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>泰小虎PRD V1.3 - 产品需求文档</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
            background: #f5f5fa;
            color: #333;
            line-height: 1.8;
        }}
        .topbar {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 16px 24px;
            position: sticky;
            top: 0;
            z-index: 100;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .topbar-inner {{
            max-width: 960px;
            margin: 0 auto;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}
        .topbar a {{
            color: #fff;
            text-decoration: none;
            font-size: 0.95em;
            opacity: 0.9;
            transition: opacity 0.2s;
        }}
        .topbar a:hover {{ opacity: 1; }}
        .topbar .home {{ font-weight: 600; font-size: 1.05em; }}
        .content {{
            max-width: 960px;
            margin: 30px auto;
            padding: 40px 48px;
            background: #fff;
            border-radius: 12px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.06);
        }}
        h1 {{ font-size: 1.8em; color: #1a1a2e; margin: 32px 0 16px; padding-bottom: 8px; border-bottom: 2px solid #667eea; }}
        h1:first-child {{ margin-top: 0; }}
        h2 {{ font-size: 1.4em; color: #2d2d5e; margin: 28px 0 12px; padding-left: 12px; border-left: 4px solid #667eea; }}
        h3 {{ font-size: 1.15em; color: #3d3d6e; margin: 20px 0 8px; }}
        h4 {{ font-size: 1.05em; color: #4d4d7e; margin: 16px 0 6px; }}
        p {{ margin: 10px 0; }}
        ul, ol {{ margin: 8px 0 8px 24px; }}
        li {{ margin: 4px 0; }}
        table {{ width: 100%; border-collapse: collapse; margin: 16px 0; font-size: 0.92em; }}
        th, td {{ border: 1px solid #e0e0e8; padding: 10px 14px; text-align: left; }}
        th {{ background: #f0f0f8; font-weight: 600; color: #2d2d5e; }}
        tr:nth-child(even) {{ background: #fafafe; }}
        code {{ background: #f0f0f5; padding: 2px 6px; border-radius: 4px; font-size: 0.9em; color: #c7254e; }}
        pre {{ background: #1e1e2e; color: #cdd6f4; padding: 20px; border-radius: 8px; overflow-x: auto; margin: 16px 0; font-size: 0.88em; line-height: 1.6; }}
        pre code {{ background: none; color: inherit; padding: 0; }}
        blockquote {{ border-left: 4px solid #667eea; background: #f8f8ff; padding: 12px 20px; margin: 12px 0; color: #555; }}
        strong {{ color: #1a1a2e; }}
        hr {{ border: none; border-top: 1px solid #e0e0e8; margin: 24px 0; }}
        a {{ color: #667eea; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        .mermaid {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 16px 0; text-align: center; }}
        @media (max-width: 768px) {{
            .content {{ padding: 20px; margin: 12px; }}
            h1 {{ font-size: 1.4em; }}
            h2 {{ font-size: 1.2em; }}
            table {{ font-size: 0.82em; }}
            th, td {{ padding: 6px 8px; }}
        }}
    </style>
</head>
<body>
    <div class="topbar">
        <div class="topbar-inner">
            <a href="../index.html" class="home">🐯 泰小虎 文档中心</a>
            <a href="../index.html">← 返回目录</a>
        </div>
    </div>
    <div class="content">
{content}
    </div>
    <script>
        mermaid.initialize({{ startOnLoad: true }});
    </script>
</body>
</html>"""
    
    # 保存文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\n✅ PRD已更新并保存到: {output_file}")

if __name__ == '__main__':
    main()
