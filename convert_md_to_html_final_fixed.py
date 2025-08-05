#!/usr/bin/env python3
import os
import re
import glob
from pathlib import Path
import sys

def process_markdown_content(content):
    """Process markdown content and convert to HTML with kids book styling"""
    
    # Convert headers first
    content = re.sub(r'^# (.+)$', r'<h1 class="chapter-title">\1</h1>', content, flags=re.MULTILINE)
    
    # Convert horizontal rules
    content = re.sub(r'^\*\*\*$', r'<hr style="border: none; height: 2px; background: linear-gradient(90deg, var(--primary-color), var(--secondary-color)); margin: 2rem 0; border-radius: 1px;">', content, flags=re.MULTILINE)
    
    # Convert paragraphs (split by double newlines)
    paragraphs = content.split('\n\n')
    processed_paragraphs = []
    
    for para in paragraphs:
        para = para.strip()
        if not para or para.startswith('<h1') or para.startswith('<hr'):
            processed_paragraphs.append(para)
            continue
            
        # Process in specific order to avoid conflicts
        
        # 1. Handle image references first (before any other processing)
        if '![' in para and '](' in para:
            para = re.sub(r'!\[([^\]]+)\]\(([^)]+)\)', 
                         r'<div class="image-container"><img src="../../../\2" alt="\1" /><div class="image-caption">\1</div></div>', para)
            processed_paragraphs.append(para)
            continue
        
        # 2. Handle magic words (Hebrew words in italics)
        para = re.sub(r'\*([^*]+)\*', r'<span class="magic-word">\1</span>', para)
        
        # 3. Handle character names
        para = re.sub(r'\b(Noa|Ima|Abba|Dad)\b', r'<span class="character-name">\1</span>', para)
        
        # 4. Handle magical effects
        para = re.sub(r'(A tiny shimmer|The ice cream wiggled|The pretzel crumbs|A flock of pigeons)', 
                     r'<div class="magical-effect">\1</div>', para)
        
        # 5. Handle dialogue (text in quotes) - only if not already in HTML tags
        if '"' in para and not para.startswith('<'):
            # Use a more careful approach to avoid conflicts
            # First, temporarily replace existing HTML tags
            para = para.replace('<span class="', '___SPAN_START___')
            para = para.replace('</span>', '___SPAN_END___')
            para = para.replace('<div class="', '___DIV_START___')
            para = para.replace('</div>', '___DIV_END___')
            
            # Now process dialogue
            para = re.sub(r'"([^"]+)"', r'<span class="dialogue">"\1"</span>', para)
            
            # Restore the temporary replacements
            para = para.replace('___SPAN_START___', '<span class="')
            para = para.replace('___SPAN_END___', '</span>')
            para = para.replace('___DIV_START___', '<div class="')
            para = para.replace('___DIV_END___', '</div>')
        
        # Wrap in paragraph tags if not already wrapped and not empty
        if para and not para.startswith('<') and not para.startswith('<div'):
            para = f'<p>{para}</p>'
            
        processed_paragraphs.append(para)
    
    return '\n\n'.join(processed_paragraphs)

def create_html_page(chapter_num, title, content, total_chapters):
    """Create HTML page with kids book design"""
    
    prev_chapter = chapter_num - 1 if chapter_num > 1 else None
    next_chapter = chapter_num + 1 if chapter_num < total_chapters else None
    
    navigation_html = f'''
    <div class="navigation">
        <button class="nav-button" onclick="window.location.href='chapter_{prev_chapter}.html'" {"disabled" if prev_chapter is None else ""}>
            ← Previous Chapter
        </button>
        <button class="nav-button" onclick="window.location.href='chapter_{next_chapter}.html'" {"disabled" if next_chapter is None else ""}>
            Next Chapter →
        </button>
    </div>
    ''' if prev_chapter or next_chapter else ''
    
    html_template = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Berlin Magic Book</title>
    <link rel="stylesheet" href="../style.css">
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 class="book-title">Berlin Magic Book</h1>
            <div class="chapter-number">Chapter {chapter_num}</div>
        </div>
        
        <div class="content">
            {content}
        </div>
        
        {navigation_html}
    </div>
</body>
</html>'''
    
    return html_template

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Convert Markdown to HTML for kids book.')
    parser.add_argument('--input_dir', type=str, required=True, help='Input directory with markdown files')
    parser.add_argument('--output_dir', type=str, required=True, help='Output directory for HTML files')
    args = parser.parse_args()

    md_files = glob.glob(os.path.join(args.input_dir, 'chapter_*.md'))
    md_files.sort()  # Ensure they're in order
    
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Converting {len(md_files)} chapters...")
    
    for i, md_file in enumerate(md_files, 1):
        print(f"Processing {md_file}...")
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
        title = title_match.group(1) if title_match else f"Chapter {i}"
        processed_content = process_markdown_content(content)
        html_content = create_html_page(i, title, processed_content, len(md_files))
        output_file = output_dir / f'chapter_{i}.html'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"Created {output_file}")
    print(f"\nConversion complete! {len(md_files)} HTML files created in {output_dir}")
    print("CSS file: book/book_text/html/style.css")

if __name__ == "__main__":
    main() 