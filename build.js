const fs = require('fs');
const path = require('path');

const docsDir = path.join(__dirname, 'docs');
const files = fs.readdirSync(docsDir).filter(f => f.endsWith('.md'));

const htmlTemplate = (title, body) => `<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${title} - 泰小虎文档中心</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
            background: #f5f5fa;
            color: #333;
            line-height: 1.8;
        }
        .topbar {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 16px 24px;
            position: sticky;
            top: 0;
            z-index: 100;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .topbar-inner {
            max-width: 960px;
            margin: 0 auto;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        .topbar a {
            color: #fff;
            text-decoration: none;
            font-size: 0.95em;
            opacity: 0.9;
            transition: opacity 0.2s;
        }
        .topbar a:hover { opacity: 1; }
        .topbar .home { font-weight: 600; font-size: 1.05em; }
        .content {
            max-width: 960px;
            margin: 30px auto;
            padding: 0 24px 60px;
            background: #fff;
            border-radius: 12px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.06);
            padding: 40px 48px;
        }
        h1 { font-size: 1.8em; color: #1a1a2e; margin: 32px 0 16px; padding-bottom: 8px; border-bottom: 2px solid #667eea; }
        h1:first-child { margin-top: 0; }
        h2 { font-size: 1.4em; color: #2d2d5e; margin: 28px 0 12px; padding-left: 12px; border-left: 4px solid #667eea; }
        h3 { font-size: 1.15em; color: #3d3d6e; margin: 20px 0 8px; }
        h4 { font-size: 1.05em; color: #4d4d7e; margin: 16px 0 6px; }
        p { margin: 10px 0; }
        ul, ol { margin: 8px 0 8px 24px; }
        li { margin: 4px 0; }
        table { width: 100%; border-collapse: collapse; margin: 16px 0; font-size: 0.92em; }
        th, td { border: 1px solid #e0e0e8; padding: 10px 14px; text-align: left; }
        th { background: #f0f0f8; font-weight: 600; color: #2d2d5e; }
        tr:nth-child(even) { background: #fafafe; }
        code { background: #f0f0f5; padding: 2px 6px; border-radius: 4px; font-size: 0.9em; color: #c7254e; }
        pre { background: #1e1e2e; color: #cdd6f4; padding: 20px; border-radius: 8px; overflow-x: auto; margin: 16px 0; font-size: 0.88em; line-height: 1.6; }
        pre code { background: none; color: inherit; padding: 0; }
        pre.ascii-art { background: #f8f8ff; color: #2d2d5e; border: 1px solid #e0e0e8; font-family: "Consolas", "Monaco", "Courier New", monospace; }
        blockquote { border-left: 4px solid #667eea; background: #f8f8ff; padding: 12px 20px; margin: 12px 0; color: #555; }
        strong { color: #1a1a2e; }
        hr { border: none; border-top: 1px solid #e0e0e8; margin: 24px 0; }
        a { color: #667eea; text-decoration: none; }
        a:hover { text-decoration: underline; }
        @media (max-width: 768px) {
            .content { padding: 20px; margin: 12px; }
            h1 { font-size: 1.4em; }
            h2 { font-size: 1.2em; }
            table { font-size: 0.82em; }
            th, td { padding: 6px 8px; }
        }
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
        ${body}
    </div>
</body>
</html>`;

// Check if content contains ASCII art box drawing characters
function containsAsciiArt(text) {
    const boxChars = /[┌┐└┘├┤┬┴┼─│┏┓┗┛┣┫┳┻╋━┃]/;
    return boxChars.test(text);
}

// Simple markdown to HTML converter
function mdToHtml(md) {
    let html = md;
    
    // Process code blocks first, but handle ASCII art separately
    const codeBlocks = [];
    const asciiArtBlocks = [];
    
    html = html.replace(/```[\s\S]*?```/g, match => {
        // Check if this is ASCII art (contains box drawing characters)
        if (containsAsciiArt(match)) {
            asciiArtBlocks.push(match);
            return `%%ASCIIART_${asciiArtBlocks.length - 1}%%`;
        } else {
            codeBlocks.push(match);
            return `%%CODEBLOCK_${codeBlocks.length - 1}%%`;
        }
    });
    
    const inlineCodes = [];
    html = html.replace(/`[^`]+`/g, match => {
        inlineCodes.push(match);
        return `%%INLINECODE_${inlineCodes.length - 1}%%`;
    });

    // Headers
    html = html.replace(/^######\s+(.+)$/gm, '<h6>$1</h6>');
    html = html.replace(/^#####\s+(.+)$/gm, '<h5>$1</h5>');
    html = html.replace(/^####\s+(.+)$/gm, '<h4>$1</h4>');
    html = html.replace(/^###\s+(.+)$/gm, '<h3>$1</h3>');
    html = html.replace(/^##\s+(.+)$/gm, '<h2>$1</h2>');
    html = html.replace(/^#\s+(.+)$/gm, '<h1>$1</h1>');

    // Bold and italic
    html = html.replace(/\*\*\*(.+?)\*\*\*/g, '<strong><em>$1</em></strong>');
    html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/\*(.+?)\*/g, '<em>$1</em>');

    // Horizontal rule
    html = html.replace(/^---+$/gm, '<hr>');

    // Blockquote
    html = html.replace(/^>\s+(.+)$/gm, '<blockquote>$1</blockquote>');

    // Unordered list
    html = html.replace(/^[\-\*]\s+(.+)$/gm, '<li>$1</li>');
    html = html.replace(/((?:<li>.*<\/li>\n?)+)/g, '<ul>$1</ul>');

    // Ordered list
    html = html.replace(/^\d+\.\s+(.+)$/gm, '<li>$1</li>');

    // Tables
    html = html.replace(/^(\|.+\|)\n(\|[\s\-:|]+\|)\n((?:\|.+\|\n?)*)/gm, (match, header, sep, body) => {
        const headers = header.split('|').filter(c => c.trim()).map(c => `<th>${c.trim()}</th>`).join('');
        const rows = body.trim().split('\n').map(row => {
            const cells = row.split('|').filter(c => c.trim()).map(c => `<td>${c.trim()}</td>`).join('');
            return `<tr>${cells}</tr>`;
        }).join('\n');
        return `<table><thead><tr>${headers}</tr></thead><tbody>${rows}</tbody></table>`;
    });

    // Paragraphs
    html = html.replace(/^(?!<[hultob]|%%)(.+)$/gm, '<p>$1</p>');
    // Remove empty paragraphs
    html = html.replace(/<p>\s*<\/p>/g, '');

    // Restore ASCII art blocks with special styling
    asciiArtBlocks.forEach((block, i) => {
        const code = block.replace(/```\w*\n?/, '').replace(/```$/, '');
        // Preserve whitespace and line breaks for ASCII art
        const formattedCode = code.replace(/</g, '&lt;').replace(/>/g, '&gt;');
        html = html.replace(`%%ASCIIART_${i}%%`, `<pre class="ascii-art"><code>${formattedCode}</code></pre>`);
    });

    // Restore code blocks
    codeBlocks.forEach((block, i) => {
        const code = block.replace(/```\w*\n?/, '').replace(/```$/, '');
        html = html.replace(`%%CODEBLOCK_${i}%%`, `<pre><code>${code.replace(/</g, '&lt;').replace(/>/g, '&gt;')}</code></pre>`);
    });
    
    // Restore inline codes
    inlineCodes.forEach((code, i) => {
        const inner = code.replace(/`/g, '');
        html = html.replace(`%%INLINECODE_${i}%%`, `<code>${inner}</code>`);
    });

    return html;
}

files.forEach(file => {
    const md = fs.readFileSync(path.join(docsDir, file), 'utf-8');
    const title = file.replace('.md', '');
    const body = mdToHtml(md);
    const html = htmlTemplate(title, body);
    const outName = file.replace('.md', '.html');
    fs.writeFileSync(path.join(docsDir, outName), html, 'utf-8');
    console.log(`✅ ${file} -> ${outName}`);
});

console.log('\n🎉 All done!');
