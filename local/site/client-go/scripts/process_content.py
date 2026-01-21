#!/usr/bin/env python3
"""
Process markdown files for Hugo site:
1. Copy markdown files to content directory
2. Add front matter for Hugo
3. Keep Mermaid diagrams as code blocks (will be rendered by mermaid.js in browser)
"""

import os
import sys
from pathlib import Path
import re

def add_front_matter(content, title, weight=0):
    """Add Hugo front matter to markdown content."""
    front_matter = f"""---
title: "{title}"
weight: {weight}
---

"""
    return front_matter + content

def process_markdown_file(input_file, output_file, weight=0):
    """Process a markdown file for Hugo."""
    print(f"Processing: {input_file.name}")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract title from first # heading or use filename
    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if title_match:
        title = title_match.group(1)
    else:
        title = input_file.stem.replace('-', ' ').title()
    
    # Add front matter
    processed_content = add_front_matter(content, title, weight)
    
    # Write processed content
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(processed_content)
    
    print(f"  Created: {output_file.name}")

def main():
    # Paths
    script_dir = Path(__file__).parent
    docs_dir = script_dir.parent.parent / 'docs' / 'client-go'
    content_dir = script_dir / 'content'
    
    # Create content directory
    content_dir.mkdir(exist_ok=True)
    
    # File mapping with weights for ordering
    file_mapping = {
        'README.md': ('_index.md', 1),
        '00-overview.md': ('00-overview.md', 2),
        '01-core-packages.md': ('01-core-packages.md', 3),
        '02-configuration.md': ('02-configuration.md', 4),
        '03-controller-infrastructure.md': ('03-controller-infrastructure.md', 5),
        '04-advanced-features.md': ('04-advanced-features.md', 6),
        '05-utilities.md': ('05-utilities.md', 7),
        '06-examples.md': ('06-examples.md', 8),
        'INDEX.md': ('index-page.md', 9),
    }
    
    print(f"Processing markdown files from {docs_dir}\n")
    
    for source_name, (target_name, weight) in file_mapping.items():
        source_file = docs_dir / source_name
        target_file = content_dir / target_name
        
        if not source_file.exists():
            print(f"Warning: {source_name} not found, skipping")
            continue
        
        try:
            process_markdown_file(source_file, target_file, weight)
        except Exception as e:
            print(f"Error processing {source_name}: {e}")
            continue
    
    print("\nProcessing complete!")
    print(f"Content files created in: {content_dir}")
    return 0

if __name__ == '__main__':
    sys.exit(main())
