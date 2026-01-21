#!/usr/bin/env python3
"""
Process markdown documentation files:
1. Extract Mermaid diagrams
2. Convert to SVG using mermaid-cli
3. Replace Mermaid code blocks with SVG images
4. Use content hash for SVG filenames
"""

import os
import re
import hashlib
import subprocess
import json
from pathlib import Path

SOURCE_DIR = Path("../../docs/apiserver")
CONTENT_DIR = Path("content")
STATIC_DIR = Path("static/diagrams")
MERMAID_TEMP = Path("temp_mermaid")

def setup_directories():
    """Create necessary directories"""
    CONTENT_DIR.mkdir(parents=True, exist_ok=True)
    STATIC_DIR.mkdir(parents=True, exist_ok=True)
    MERMAID_TEMP.mkdir(parents=True, exist_ok=True)

def hash_content(content):
    """Generate hash from content"""
    return hashlib.md5(content.encode('utf-8')).hexdigest()[:16]

def extract_mermaid_blocks(content):
    """Extract all Mermaid code blocks from markdown"""
    pattern = r'```mermaid\n(.*?)\n```'
    matches = re.finditer(pattern, content, re.DOTALL)
    return [(m.group(0), m.group(1)) for m in matches]

def convert_mermaid_to_svg(mermaid_code, output_path):
    """Convert Mermaid code to SVG using mmdc (mermaid-cli)"""
    # Create temporary input file
    temp_input = MERMAID_TEMP / "temp.mmd"
    
    temp_input.write_text(mermaid_code)
    
    try:
        # Try using mmdc if available
        result = subprocess.run(
            ['mmdc', '-i', str(temp_input), '-o', str(output_path), '-b', 'transparent'],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0 and output_path.exists() and output_path.stat().st_size > 1000:
            return True
        else:
            print(f"    Warning: mmdc conversion failed with return code {result.returncode}")
            if result.stderr:
                print(f"    Error: {result.stderr}")
    except FileNotFoundError:
        print(f"    Error: mmdc (mermaid-cli) not found. Install with: npm install -g @mermaid-js/mermaid-cli")
        pass
    except subprocess.TimeoutExpired:
        print(f"    Error: mmdc conversion timed out")
        pass
    
    # Fallback: Create a placeholder SVG with the mermaid code
    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600">
  <rect width="800" height="600" fill="#f9f9f9" stroke="#ddd" stroke-width="2"/>
  <text x="400" y="280" text-anchor="middle" font-family="monospace" font-size="14" fill="#666">
    Mermaid Diagram
  </text>
  <text x="400" y="310" text-anchor="middle" font-family="monospace" font-size="12" fill="#999">
    (Diagram conversion failed)
  </text>
  <foreignObject x="50" y="330" width="700" height="250">
    <div xmlns="http://www.w3.org/1999/xhtml" style="font-family: monospace; font-size: 10px; overflow: auto; white-space: pre;">
{mermaid_code[:500]}...
    </div>
  </foreignObject>
</svg>'''
    output_path.write_text(svg_content)
    return False

def process_markdown_file(source_file, output_file):
    """Process a single markdown file"""
    print(f"Processing {source_file.name}...")
    
    content = source_file.read_text()
    mermaid_blocks = extract_mermaid_blocks(content)
    
    if not mermaid_blocks:
        # No Mermaid blocks, just copy the file
        output_file.write_text(content)
        return 0
    
    # Process each Mermaid block
    diagram_count = 0
    for full_block, mermaid_code in mermaid_blocks:
        # Generate hash-based filename
        content_hash = hash_content(mermaid_code)
        svg_filename = f"diagram_{content_hash}.svg"
        svg_path = STATIC_DIR / svg_filename
        
        # Convert to SVG if not already exists
        if not svg_path.exists():
            if convert_mermaid_to_svg(mermaid_code, svg_path):
                print(f"  Created {svg_filename}")
                diagram_count += 1
        
        # Replace Mermaid block with SVG image
        svg_tag = f'<img src="/diagrams/{svg_filename}" alt="Diagram" class="mermaid-diagram" />'
        content = content.replace(full_block, svg_tag, 1)
    
    # Write processed content
    output_file.write_text(content)
    return diagram_count

def create_front_matter(title, weight, is_overview=False):
    """Create Hugo front matter"""
    # Overview should be at the top with negative weight
    if is_overview:
        weight = -1
        title = "Overview"
    return f'''---
title: "{title}"
weight: {weight}
---

'''

def get_title_from_content(content):
    """Extract title from markdown content"""
    match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if match:
        title = match.group(1)
        # Remove "pkg/xxx - " prefix for cleaner navigation
        title = re.sub(r'^pkg/[^-]+ - ', '', title)
        return title
    return "Untitled"

def main():
    """Main processing function"""
    print("Setting up directories...")
    setup_directories()
    
    print("\nProcessing markdown files...")
    total_diagrams = 0
    
    # Get all markdown files
    md_files = sorted(SOURCE_DIR.glob("*.md"))
    
    for idx, source_file in enumerate(md_files):
        # Skip SUMMARY.md
        if source_file.name == "SUMMARY.md":
            continue
        
        # Determine output filename
        if source_file.name == "README.md":
            output_file = CONTENT_DIR / "_index.md"
        else:
            # Remove number prefix for cleaner URLs
            name = source_file.stem
            if name[0].isdigit() and name[1].isdigit() and name[2] == '-':
                name = name[3:]
            output_file = CONTENT_DIR / f"{name}.md"
        
        # Read content to get title
        content = source_file.read_text()
        title = get_title_from_content(content)
        
        # Check if this is the overview file
        is_overview = source_file.name == "00-overview.md"
        
        # Add front matter
        front_matter = create_front_matter(title, idx, is_overview)
        
        # Process file
        diagram_count = process_markdown_file(source_file, output_file)
        
        # Add front matter to beginning
        processed_content = output_file.read_text()
        output_file.write_text(front_matter + processed_content)
        
        total_diagrams += diagram_count
        print(f"  ✓ {source_file.name} -> {output_file.name} ({diagram_count} diagrams)")
    
    print(f"\n✓ Processed {len(md_files)-1} files with {total_diagrams} diagrams")
    print(f"✓ Content directory: {CONTENT_DIR.absolute()}")
    print(f"✓ Diagrams directory: {STATIC_DIR.absolute()}")
    
    # Cleanup
    if MERMAID_TEMP.exists():
        for f in MERMAID_TEMP.glob("*"):
            f.unlink()
        MERMAID_TEMP.rmdir()

if __name__ == "__main__":
    main()
