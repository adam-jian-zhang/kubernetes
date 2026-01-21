#!/usr/bin/env python3
"""
Process Mermaid diagrams in markdown files:
1. Extract Mermaid code blocks
2. Generate hash-based filenames
3. Convert to SVG using mermaid-cli
4. Replace Mermaid blocks with SVG image references
"""

import os
import re
import hashlib
import subprocess
import sys
import tempfile
from pathlib import Path

def get_content_hash(content):
    """Generate SHA256 hash of content for filename."""
    return hashlib.sha256(content.encode('utf-8')).hexdigest()[:16]

def extract_mermaid_blocks(content):
    """Extract all Mermaid code blocks from markdown content."""
    pattern = r'```mermaid\n(.*?)\n```'
    matches = re.findall(pattern, content, re.DOTALL)
    return matches

def convert_mermaid_to_svg(mermaid_code, output_path):
    """Convert Mermaid code to SVG using mermaid-cli (mmdc)."""
    # Create temporary mermaid file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.mmd', delete=False) as temp_file:
        temp_mmd = temp_file.name
        temp_file.write(mermaid_code)
    
    try:
        # Convert using mmdc (mermaid-cli)
        # Use --puppeteerConfigFile to avoid permission issues
        result = subprocess.run(
            [
                'mmdc',
                '-i', temp_mmd,
                '-o', str(output_path),
                '-b', 'transparent',
                '-t', 'default'
            ],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            print(f"Warning: Failed to convert diagram: {result.stderr}")
            return False
            
        return True
        
    except FileNotFoundError:
        print("Error: mermaid-cli (mmdc) not found.")
        print("Install with: npm install -g @mermaid-js/mermaid-cli")
        return False
    except subprocess.TimeoutExpired:
        print(f"Error: Timeout converting diagram")
        return False
    except Exception as e:
        print(f"Error converting diagram: {e}")
        return False
    finally:
        # Clean up temp file
        try:
            os.unlink(temp_mmd)
        except:
            pass

def fix_markdown_links(content):
    """Fix markdown links to work with Hugo's URL structure."""
    # Replace .md links with Hugo-friendly links
    # Example: [text](file.md) -> [text](file/)
    # Example: [text](file.md#anchor) -> [text](file/#anchor)
    content = re.sub(r'\]\(([^)]+)\.md(#[^)]+)?\)', r'](\1/\2)', content)
    return content

def process_markdown_file(input_file, output_file, images_dir):
    """Process a markdown file to convert Mermaid diagrams to SVG."""
    print(f"Processing: {input_file.name}")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix markdown links for Hugo
    content = fix_markdown_links(content)
    
    # Extract Mermaid blocks
    mermaid_blocks = extract_mermaid_blocks(content)
    
    if not mermaid_blocks:
        # No Mermaid blocks, just copy the file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  No Mermaid diagrams found")
        return
    
    print(f"  Found {len(mermaid_blocks)} Mermaid diagram(s)")
    
    # Process each Mermaid block
    converted = 0
    for i, mermaid_code in enumerate(mermaid_blocks):
        # Generate hash-based filename
        content_hash = get_content_hash(mermaid_code)
        svg_filename = f"diagram_{content_hash}.svg"
        svg_path = images_dir / svg_filename
        
        # Convert to SVG if not already exists
        if not svg_path.exists():
            print(f"  Converting diagram {i+1}/{len(mermaid_blocks)}...")
            if convert_mermaid_to_svg(mermaid_code, svg_path):
                print(f"    Created: {svg_filename}")
                converted += 1
            else:
                print(f"    Failed to create SVG, keeping Mermaid code")
                continue
        else:
            print(f"  Using cached: {svg_filename}")
            converted += 1
        
        # Replace Mermaid block with SVG image reference
        mermaid_block = f"```mermaid\n{mermaid_code}\n```"
        svg_reference = f'<div class="mermaid-diagram"><img src="/images/{svg_filename}" alt="Diagram" /></div>'
        content = content.replace(mermaid_block, svg_reference, 1)
    
    # Write processed content
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"  Converted {converted}/{len(mermaid_blocks)} diagrams")
    print(f"  Saved: {output_file.name}")

def main():
    # Paths
    script_dir = Path(__file__).parent
    docs_dir = script_dir.parent.parent / 'docs' / 'client-go'
    content_dir = script_dir / 'content'
    images_dir = script_dir / 'static' / 'images'
    
    # Create directories
    content_dir.mkdir(exist_ok=True)
    images_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if mmdc is available
    try:
        result = subprocess.run(['mmdc', '--version'], capture_output=True, check=True)
        print(f"Using mermaid-cli: {result.stdout.decode().strip()}\n")
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("Error: mermaid-cli (mmdc) not found or not working.")
        print("Install with: npm install -g @mermaid-js/mermaid-cli")
        return 1
    
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
    
    total_diagrams = 0
    total_converted = 0
    
    for source_name, (target_name, weight) in file_mapping.items():
        source_file = docs_dir / source_name
        target_file = content_dir / target_name
        
        if not source_file.exists():
            print(f"Warning: {source_name} not found, skipping")
            continue
        
        # Read source file
        with open(source_file, 'r', encoding='utf-8') as f:
            source_content = f.read()
        
        # Extract title
        title_match = re.search(r'^#\s+(.+)$', source_content, re.MULTILINE)
        title = title_match.group(1) if title_match else source_name.replace('-', ' ').title()
        
        # Add front matter
        front_matter = f"""---
title: "{title}"
weight: {weight}
---

"""
        
        # Process mermaid diagrams
        mermaid_blocks = extract_mermaid_blocks(source_content)
        if mermaid_blocks:
            total_diagrams += len(mermaid_blocks)
            
        try:
            # Process file
            temp_file = content_dir / f"temp_{target_name}"
            process_markdown_file(source_file, temp_file, images_dir)
            
            # Read processed content and add front matter
            with open(temp_file, 'r', encoding='utf-8') as f:
                processed_content = f.read()
            
            with open(target_file, 'w', encoding='utf-8') as f:
                f.write(front_matter + processed_content)
            
            # Remove temp file
            temp_file.unlink()
            
            # Count converted diagrams
            svg_refs = len(re.findall(r'<div class="mermaid-diagram">', processed_content))
            total_converted += svg_refs
            
        except Exception as e:
            print(f"Error processing {source_name}: {e}")
            continue
        
        print()
    
    print(f"Processing complete!")
    print(f"Total diagrams: {total_diagrams}")
    print(f"Converted to SVG: {total_converted}")
    print(f"Content files created in: {content_dir}")
    print(f"SVG files created in: {images_dir}")
    return 0

if __name__ == '__main__':
    sys.exit(main())
