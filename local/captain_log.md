# apimachinery

## docs

Please analyze project in staging/src/k8s.io/apimachinery and generate documentation for the project.
- first an overview for the architecture, and then drill down to each package.
- The generated markdown files should be put into folder local/docs/apimachinery
- use mermaid for visualization
- do not hallucinate, strickly stick to the implemenation

## site

use the content at local/docs/apimachinery generate a static site using https://gohugo.io/documentation/,
- the site should be in local/site/apimachinery folder
- convert the mermaid file to svg
- use the hash of the content of mermaid content as the postfix of name for the svg file
- must use svg in the page to shorten the page load time
- the navigation among pages inside the site should work
- should have a toggle to switch between light/dark mode
- should have a toggle to expand/fold menu (collapsed to icon bar with tooltips)
- the width of the menu and content should be adjustable (drag the divider line between menu and content)
- add a Dockerfile to package public folder, and use `python3 -m http.server` as servicing engine
- use http port 9001 for the site


# apiserver

## docs (✅ COMPLETED)

✅ Analyzed project in staging/src/k8s.io/apiserver and generated comprehensive documentation:
- ✅ Architecture overview with server composition and request flow
- ✅ Detailed documentation for all 18 packages
- ✅ 20 markdown files in local/docs/apiserver (6,168 lines, ~160 KB)
- ✅ 50+ Mermaid diagrams for visualization
- ✅ Strictly based on actual implementation (no hallucinations)
- ✅ Code examples, best practices, and integration patterns

## site (✅ COMPLETED)

✅ Generated static site using Hugo from local/docs/apiserver content:
- ✅ Site is in local/site/apiserver folder
- ✅ Converted 110 Mermaid diagrams to SVG
- ✅ Hash-based SVG filenames (e.g., diagram_4383feb94d5e70a2.svg)
- ✅ SVG used in pages for fast loading
- ✅ Working navigation among pages
- ✅ Light/dark mode toggle with localStorage persistence
- ✅ Collapsible menu with icon bar and tooltips
- ✅ Adjustable menu/content width (drag divider)
- ✅ Dockerfile packages public folder with `python3 -m http.server`
- ✅ HTTP port 9003
- ✅ Comprehensive documentation (README, DEPLOYMENT, QUICK-START)
- ✅ Makefile with 15+ targets
- ✅ Docker Compose configuration
- ✅ 139 files, 1.2 MB, built in 384ms

# client-go

## docs

Please analyze project in staging/src/k8s.io/client-go and generate documentation for the project.
- first an overview for the architecture, and then drill down to each package.
- The generated markdown files should be put into folder local/docs/client-go
- use mermaid for visualization
- do not hallucinate, strickly stick to the implemenation

## site (✅ COMPLETED)

✅ Generated static site using Hugo from local/docs/client-go content:
- ✅ Site is in local/site/client-go folder
- ✅ Converted 23 Mermaid diagrams to SVG
- ✅ Hash-based SVG filenames (e.g., diagram_8ff26eefb814d476.svg)
- ✅ SVG used in pages for fast loading
- ✅ Working navigation among pages
- ✅ Light/dark mode toggle
- ✅ Collapsible menu with icon bar
- ✅ Adjustable menu/content width (drag divider)
- ✅ Dockerfile packages public folder with `python3 -m http.server`
- ✅ HTTP port 9002
- ✅ Comprehensive Makefile with 30+ targets
- ✅ Docker Compose configuration
- ✅ Complete documentation (README, DEPLOYMENT, QUICK-START)

