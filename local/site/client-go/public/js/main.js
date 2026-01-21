// ===== Theme Toggle =====
const themeToggle = document.getElementById('theme-toggle');
const html = document.documentElement;
const themeIcon = themeToggle.querySelector('i');

// Load saved theme or default to light
const savedTheme = localStorage.getItem('theme') || 'light';
html.setAttribute('data-theme', savedTheme);
updateThemeIcon(savedTheme);

themeToggle.addEventListener('click', () => {
    const currentTheme = html.getAttribute('data-theme');
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    
    html.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateThemeIcon(newTheme);
});

function updateThemeIcon(theme) {
    if (theme === 'dark') {
        themeIcon.classList.remove('fa-moon');
        themeIcon.classList.add('fa-sun');
        themeToggle.title = 'Switch to light mode';
    } else {
        themeIcon.classList.remove('fa-sun');
        themeIcon.classList.add('fa-moon');
        themeToggle.title = 'Switch to dark mode';
    }
}

// ===== Menu Toggle (Mobile & Collapse) =====
const menuToggle = document.getElementById('menu-toggle');
const sidebar = document.getElementById('sidebar');
const menuIcon = menuToggle.querySelector('i');

// Load saved sidebar state
const savedSidebarState = localStorage.getItem('sidebarCollapsed');
if (savedSidebarState === 'true') {
    sidebar.classList.add('collapsed');
    updateMenuIcon(true);
}

menuToggle.addEventListener('click', () => {
    if (window.innerWidth <= 768) {
        // Mobile: toggle sidebar visibility
        sidebar.classList.toggle('mobile-open');
    } else {
        // Desktop: toggle sidebar collapse
        const isCollapsed = sidebar.classList.toggle('collapsed');
        localStorage.setItem('sidebarCollapsed', isCollapsed);
        updateMenuIcon(isCollapsed);
    }
});

function updateMenuIcon(isCollapsed) {
    if (isCollapsed) {
        menuIcon.classList.remove('fa-bars');
        menuIcon.classList.add('fa-angles-right');
        menuToggle.title = 'Expand menu';
    } else {
        menuIcon.classList.remove('fa-angles-right');
        menuIcon.classList.add('fa-bars');
        menuToggle.title = 'Collapse menu';
    }
}

// Close mobile menu when clicking outside
document.addEventListener('click', (e) => {
    if (window.innerWidth <= 768) {
        if (!sidebar.contains(e.target) && !menuToggle.contains(e.target)) {
            sidebar.classList.remove('mobile-open');
        }
    }
});

// ===== Resizable Sidebar =====
const resizeHandle = document.getElementById('resize-handle');
let isResizing = false;
let startX = 0;
let startWidth = 0;

resizeHandle.addEventListener('mousedown', (e) => {
    if (sidebar.classList.contains('collapsed')) return;
    
    isResizing = true;
    startX = e.clientX;
    startWidth = sidebar.offsetWidth;
    resizeHandle.classList.add('resizing');
    document.body.style.cursor = 'col-resize';
    document.body.style.userSelect = 'none';
    
    e.preventDefault();
});

document.addEventListener('mousemove', (e) => {
    if (!isResizing) return;
    
    const diff = e.clientX - startX;
    const newWidth = startWidth + diff;
    
    // Constrain width between min and max
    const minWidth = parseInt(getComputedStyle(sidebar).minWidth);
    const maxWidth = parseInt(getComputedStyle(sidebar).maxWidth);
    
    if (newWidth >= minWidth && newWidth <= maxWidth) {
        sidebar.style.width = newWidth + 'px';
        localStorage.setItem('sidebarWidth', newWidth);
    }
});

document.addEventListener('mouseup', () => {
    if (isResizing) {
        isResizing = false;
        resizeHandle.classList.remove('resizing');
        document.body.style.cursor = '';
        document.body.style.userSelect = '';
    }
});

// Load saved sidebar width
const savedWidth = localStorage.getItem('sidebarWidth');
if (savedWidth && !sidebar.classList.contains('collapsed')) {
    sidebar.style.width = savedWidth + 'px';
}

// ===== Smooth Scrolling for Anchor Links =====
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        const href = this.getAttribute('href');
        if (href === '#') return;
        
        e.preventDefault();
        const target = document.querySelector(href);
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// ===== Copy Code Blocks =====
document.querySelectorAll('pre code').forEach((block) => {
    const pre = block.parentElement;
    const button = document.createElement('button');
    button.className = 'copy-button';
    button.innerHTML = '<i class="fas fa-copy"></i>';
    button.title = 'Copy code';
    
    button.addEventListener('click', async () => {
        try {
            await navigator.clipboard.writeText(block.textContent);
            button.innerHTML = '<i class="fas fa-check"></i>';
            button.style.color = '#28a745';
            setTimeout(() => {
                button.innerHTML = '<i class="fas fa-copy"></i>';
                button.style.color = '';
            }, 2000);
        } catch (err) {
            console.error('Failed to copy:', err);
        }
    });
    
    pre.style.position = 'relative';
    pre.appendChild(button);
});

// Add copy button styles dynamically
const style = document.createElement('style');
style.textContent = `
    .copy-button {
        position: absolute;
        top: 8px;
        right: 8px;
        background: var(--bg-tertiary);
        border: 1px solid var(--border-color);
        border-radius: 4px;
        padding: 6px 10px;
        cursor: pointer;
        opacity: 0;
        transition: opacity 0.2s, background-color 0.2s;
        font-size: 14px;
        color: var(--text-secondary);
    }
    
    pre:hover .copy-button {
        opacity: 1;
    }
    
    .copy-button:hover {
        background: var(--bg-secondary);
    }
`;
document.head.appendChild(style);

// ===== Table of Contents (if exists) =====
const article = document.querySelector('.article');
if (article) {
    const headings = article.querySelectorAll('h2, h3');
    if (headings.length > 3) {
        const toc = document.createElement('div');
        toc.className = 'table-of-contents';
        toc.innerHTML = '<h3>Table of Contents</h3><ul></ul>';
        
        const tocList = toc.querySelector('ul');
        headings.forEach((heading, index) => {
            const id = heading.id || `heading-${index}`;
            heading.id = id;
            
            const li = document.createElement('li');
            li.className = heading.tagName.toLowerCase();
            li.innerHTML = `<a href="#${id}">${heading.textContent}</a>`;
            tocList.appendChild(li);
        });
        
        // Insert TOC after first paragraph or at the beginning
        const firstP = article.querySelector('p');
        if (firstP) {
            firstP.after(toc);
        } else {
            article.insertBefore(toc, article.firstChild);
        }
    }
}

// Add TOC styles
const tocStyle = document.createElement('style');
tocStyle.textContent = `
    .table-of-contents {
        background: var(--bg-secondary);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        padding: 1.5rem;
        margin: 2rem 0;
    }
    
    .table-of-contents h3 {
        margin-top: 0;
        margin-bottom: 1rem;
        font-size: 1.25rem;
    }
    
    .table-of-contents ul {
        list-style: none;
        margin: 0;
        padding: 0;
    }
    
    .table-of-contents li {
        margin: 0.5rem 0;
    }
    
    .table-of-contents li.h3 {
        margin-left: 1.5rem;
        font-size: 0.95em;
    }
    
    .table-of-contents a {
        color: var(--text-link);
        text-decoration: none;
        border-bottom: none;
    }
    
    .table-of-contents a:hover {
        color: var(--text-link-hover);
    }
`;
document.head.appendChild(tocStyle);

// ===== Responsive Handling =====
function handleResize() {
    if (window.innerWidth > 768) {
        sidebar.classList.remove('mobile-open');
        updateMenuIcon(sidebar.classList.contains('collapsed'));
    } else {
        menuIcon.classList.remove('fa-angles-right');
        menuIcon.classList.add('fa-bars');
        menuToggle.title = 'Toggle menu';
    }
}

window.addEventListener('resize', handleResize);
handleResize();

// ===== Initialize =====
console.log('client-go documentation site loaded');
