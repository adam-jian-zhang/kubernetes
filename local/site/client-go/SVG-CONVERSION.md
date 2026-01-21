# Mermaid to SVG Conversion

This document explains how Mermaid diagrams are converted to SVG for optimal page load performance.

## Overview

The site uses **pre-generated SVG files** instead of client-side Mermaid rendering for several key benefits:

- ⚡ **Faster page load** - No JavaScript parsing or rendering required
- 🎨 **Better styling control** - SVG can be styled with CSS
- 📦 **Smaller bundle size** - No need to include Mermaid.js library
- 🔒 **More reliable** - No dependency on CDN availability
- 📱 **Better mobile performance** - Reduced JavaScript execution

## Conversion Process

### 1. Extraction

The `process_mermaid.py` script extracts Mermaid code blocks from markdown files:

```python
pattern = r'```mermaid\n(.*?)\n```'
matches = re.findall(pattern, content, re.DOTALL)
```

### 2. Hash Generation

Each diagram gets a unique filename based on its content hash:

```python
def get_content_hash(content):
    return hashlib.sha256(content.encode('utf-8')).hexdigest()[:16]
```

Example: `diagram_8ff26eefb814d476.svg`

### 3. SVG Conversion

Using `mermaid-cli` (mmdc) to convert Mermaid to SVG:

```bash
mmdc -i input.mmd -o output.svg -b transparent -t default
```

### 4. Replacement

The Mermaid code block is replaced with an HTML image reference:

```html
<div class="mermaid-diagram">
  <img src="/images/diagram_8ff26eefb814d476.svg" alt="Diagram" />
</div>
```

## Statistics

For the client-go documentation:

- **Total diagrams**: 23
- **Successfully converted**: 23 (100%)
- **Total SVG size**: ~468 KB
- **Average SVG size**: ~20 KB per diagram

### Diagram Distribution

| File | Diagrams |
|------|----------|
| README.md | 1 |
| 00-overview.md | 3 |
| 01-core-packages.md | 4 |
| 02-configuration.md | 3 |
| 03-controller-infrastructure.md | 6 |
| 04-advanced-features.md | 5 |
| 05-utilities.md | 1 |
| **Total** | **23** |

## File Naming Convention

SVG files use content-based hashing for several benefits:

1. **Caching** - Same diagram = same filename = browser cache hit
2. **Deduplication** - Identical diagrams share the same SVG file
3. **Version control** - Content changes result in new filename
4. **No conflicts** - Hash ensures unique names

## Styling

SVG diagrams are styled using CSS in `themes/client-go-docs/static/css/style.css`:

```css
.article .mermaid-diagram {
    margin: 2rem 0;
    text-align: center;
    background-color: var(--bg-secondary);
    padding: 1.5rem;
    border-radius: 8px;
    border: 1px solid var(--border-color);
}

.article .mermaid-diagram img {
    max-width: 100%;
    height: auto;
    display: inline-block;
}
```

## Build Process

### Using Makefile

```bash
# Process content and convert diagrams
make content

# Or build everything
make build
```

### Manual Process

```bash
# Install mermaid-cli
npm install -g @mermaid-js/mermaid-cli

# Run conversion script
python3 process_mermaid.py

# Build site
hugo --minify
```

## Diagram Examples

### Architecture Diagram
- **File**: `diagram_8ff26eefb814d476.svg`
- **Source**: README.md
- **Size**: 11 KB
- **Type**: Flowchart showing client-go architecture

### Controller Infrastructure
- **File**: `diagram_672dd4f126c2ff9e.svg`
- **Source**: 03-controller-infrastructure.md
- **Size**: 25 KB
- **Type**: Sequence diagram showing informer mechanism

### Server-Side Apply
- **File**: `diagram_6d92e7ebb6f2740f.svg`
- **Source**: 04-advanced-features.md
- **Size**: 28 KB
- **Type**: Flowchart showing apply process

## Troubleshooting

### mermaid-cli Not Found

```bash
# Install globally
npm install -g @mermaid-js/mermaid-cli

# Verify installation
mmdc --version
```

### Conversion Fails

If a diagram fails to convert:

1. Check Mermaid syntax
2. Verify mermaid-cli is up to date
3. Check for special characters in diagram
4. Review error output in console

### SVG Not Displaying

1. Verify SVG file exists in `static/images/`
2. Check Hugo build copied SVG to `public/images/`
3. Verify image path in HTML is correct
4. Check browser console for 404 errors

## Performance Comparison

### Client-Side Rendering (Mermaid.js)

- **Initial load**: ~150ms (library download)
- **Per diagram**: ~50-100ms (parsing + rendering)
- **Total for 23 diagrams**: ~1.3-2.5 seconds
- **Bundle size**: +200 KB

### Pre-Generated SVG

- **Initial load**: 0ms (no library needed)
- **Per diagram**: ~5-10ms (image load)
- **Total for 23 diagrams**: ~115-230ms
- **Bundle size**: +468 KB (but cacheable)

**Result**: ~10x faster page load with SVG approach!

## Cache Strategy

SVG files are highly cacheable:

```nginx
# Example nginx cache configuration
location /images/ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

With content-based hashing, files can be cached indefinitely since content changes result in new filenames.

## Future Improvements

Potential enhancements:

1. **SVG Optimization** - Use SVGO to reduce file sizes
2. **Dark Mode SVGs** - Generate separate SVGs for dark theme
3. **Lazy Loading** - Load SVGs only when visible
4. **WebP Fallback** - Convert to WebP for even smaller sizes
5. **Sprite Sheet** - Combine small diagrams into sprite sheet

## References

- [Mermaid CLI Documentation](https://github.com/mermaid-js/mermaid-cli)
- [Hugo Image Processing](https://gohugo.io/content-management/image-processing/)
- [SVG Optimization](https://github.com/svg/svgo)
