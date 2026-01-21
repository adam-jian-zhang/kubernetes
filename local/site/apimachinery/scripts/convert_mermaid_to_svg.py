#!/usr/bin/env python3

import os
import re
import hashlib
import subprocess
import tempfile
from pathlib import Path

# Directories
SCRIPT_DIR = Path(__file__).parent
SITE_DIR = SCRIPT_DIR.parent
CONTENT_DIR = SITE_DIR / "content"
STATIC_DIR = SITE_DIR / "static" / "diagrams"
DOCS_SOURCE = SITE_DIR.parent.parent / "docs" / "apimachinery"

def hash_content(content):
    """Generate MD5 hash of content"""
    return hashlib.md5(content.encode()).hexdigest()[:8]

def convert_mermaid_to_svg(mermaid_code, output_path):
    """Convert mermaid code to SVG using mmdc CLI"""
    # Create temporary mermaid file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.mmd', delete=False) as f:
        f.write(mermaid_code)
        temp_mmd = f.name
    
    try:
        # Run mmdc to convert to SVG
        result = subprocess.run(
            ['mmdc', '-i', temp_mmd, '-o', str(output_path), 
             '--theme', 'default', '--backgroundColor', 'transparent'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            print(f"  ⚠️  mmdc error: {result.stderr}")
            return False
        
        return True
    except subprocess.TimeoutExpired:
        print(f"  ⚠️  mmdc timeout")
        return False
    except FileNotFoundError:
        print(f"  ⚠️  mmdc not found. Install with: npm install -g @mermaid-js/mermaid-cli")
        return False
    finally:
        # Clean up temp file
        try:
            os.unlink(temp_mmd)
        except:
            pass

def process_markdown_file(input_path, output_path, diagrams_dir):
    """Process a markdown file, extracting and converting mermaid diagrams"""
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract mermaid diagrams
    pattern = r'```mermaid\n(.*?)```'
    diagram_count = 0
    
    def replace_mermaid(match):
        nonlocal diagram_count
        mermaid_code = match.group(1)
        hash_id = hash_content(mermaid_code)
        svg_filename = f'diagram-{hash_id}.svg'
        svg_path = diagrams_dir / svg_filename
        mmd_path = diagrams_dir / f'diagram-{hash_id}.mmd'
        
        # Save mermaid source
        mmd_path.write_text(mermaid_code, encoding='utf-8')
        
        # Convert to SVG
        if convert_mermaid_to_svg(mermaid_code, svg_path):
            diagram_count += 1
            print(f"    ✓ Converted diagram {hash_id}")
        else:
            print(f"    ✗ Failed to convert diagram {hash_id}")
        
        # Return image reference
        return f'![Diagram](/diagrams/{svg_filename})'
    
    # Replace all mermaid blocks
    content = re.sub(pattern, replace_mermaid, content, flags=re.DOTALL)
    
    # Fix internal markdown links: convert .md to / for Hugo
    # Match: [text](filename.md) -> [text](filename/)
    # Only fix internal links (not external URLs)
    content = re.sub(r'\]\((\d+-[a-z-]+)\.md\)', r'](\1/)', content)
    content = re.sub(r'\]\((README)\.md\)', r'](/)', content)
    
    # Remove the first H1 heading since Hugo template will add the title
    # Match: # Title at the start of content (after any whitespace)
    content = re.sub(r'^\s*#\s+[^\n]+\n', '', content, count=1)
    
    # Add front matter
    filename = input_path.name
    if filename == 'README.md':
        title = 'k8s.io/apimachinery Documentation'
        weight = 0
    else:
        # Extract title from filename
        title = filename.replace('.md', '').replace('-', ' ')
        title = re.sub(r'^\d+\s*', '', title)  # Remove leading numbers
        title = ' '.join(word.capitalize() for word in title.split())
        
        # Extract weight from filename
        weight_match = re.match(r'^(\d+)', filename)
        weight = int(weight_match.group(1)) if weight_match else 99
    
    front_matter = f'''---
title: "{title}"
weight: {weight}
---

'''
    
    content = front_matter + content
    
    # Write output
    output_filename = '_index.md' if filename == 'README.md' else filename
    output_file = output_path / output_filename
    output_file.write_text(content, encoding='utf-8')
    
    return diagram_count

def main():
    # Use the global directory constants
    # Create directories
    CONTENT_DIR.mkdir(parents=True, exist_ok=True)
    STATIC_DIR.mkdir(parents=True, exist_ok=True)
    
    print("=== Converting Mermaid Diagrams to SVG ===\n")
    
    # Process all markdown files
    total_files = 0
    total_diagrams = 0
    
    for md_file in sorted(DOCS_SOURCE.glob('*.md')):
        print(f"Processing: {md_file.name}")
        diagram_count = process_markdown_file(md_file, CONTENT_DIR, STATIC_DIR)
        total_files += 1
        total_diagrams += diagram_count
    
    print(f'\n=== Summary ===')
    print(f'Files processed: {total_files}')
    print(f'Diagrams converted: {total_diagrams}')
    print(f'Content written to: {CONTENT_DIR}')
    print(f'Diagrams written to: {STATIC_DIR}')
    print(f'\n✓ Fixed: Removed duplicate H1 titles')

if __name__ == '__main__':
    main()
