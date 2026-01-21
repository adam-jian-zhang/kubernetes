// Sidebar Resize Functionality
(function() {
    const SIDEBAR_WIDTH_KEY = 'apiserver-sidebar-width';
    const MIN_WIDTH = 200;
    const MAX_WIDTH = 600;
    
    const sidebar = document.getElementById('sidebar');
    const resizeHandle = document.getElementById('resize-handle');
    const root = document.documentElement;
    
    let isResizing = false;
    let startX = 0;
    let startWidth = 0;
    
    // Load saved width
    function loadSidebarWidth() {
        const savedWidth = localStorage.getItem(SIDEBAR_WIDTH_KEY);
        if (savedWidth && !sidebar.classList.contains('collapsed')) {
            setSidebarWidth(parseInt(savedWidth));
        }
    }
    
    // Set sidebar width
    function setSidebarWidth(width) {
        // Clamp width between min and max
        width = Math.max(MIN_WIDTH, Math.min(MAX_WIDTH, width));
        root.style.setProperty('--sidebar-width', `${width}px`);
        localStorage.setItem(SIDEBAR_WIDTH_KEY, width);
    }
    
    // Start resizing
    function startResize(e) {
        if (sidebar.classList.contains('collapsed')) {
            return;
        }
        
        isResizing = true;
        startX = e.clientX;
        startWidth = sidebar.offsetWidth;
        
        resizeHandle.classList.add('resizing');
        document.body.style.cursor = 'col-resize';
        document.body.style.userSelect = 'none';
        
        // Prevent text selection during resize
        e.preventDefault();
    }
    
    // Perform resize
    function resize(e) {
        if (!isResizing) return;
        
        const deltaX = e.clientX - startX;
        const newWidth = startWidth + deltaX;
        setSidebarWidth(newWidth);
    }
    
    // Stop resizing
    function stopResize() {
        if (!isResizing) return;
        
        isResizing = false;
        resizeHandle.classList.remove('resizing');
        document.body.style.cursor = '';
        document.body.style.userSelect = '';
    }
    
    // Event listeners
    resizeHandle.addEventListener('mousedown', startResize);
    document.addEventListener('mousemove', resize);
    document.addEventListener('mouseup', stopResize);
    
    // Touch support for mobile
    resizeHandle.addEventListener('touchstart', (e) => {
        startResize({ clientX: e.touches[0].clientX, preventDefault: () => e.preventDefault() });
    });
    
    document.addEventListener('touchmove', (e) => {
        if (isResizing) {
            resize({ clientX: e.touches[0].clientX });
        }
    });
    
    document.addEventListener('touchend', stopResize);
    
    // Initialize
    loadSidebarWidth();
    
    // Reset width when menu is toggled
    const menuToggle = document.getElementById('menu-toggle');
    menuToggle.addEventListener('click', () => {
        setTimeout(() => {
            if (!sidebar.classList.contains('collapsed')) {
                loadSidebarWidth();
            }
        }, 300); // Wait for transition
    });
})();
