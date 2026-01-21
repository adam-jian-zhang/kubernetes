// Menu toggle functionality
(function() {
    const menuToggle = document.getElementById('menu-toggle');
    const sidebar = document.getElementById('sidebar');
    
    // Load saved state or default to expanded
    const savedState = localStorage.getItem('menuCollapsed') === 'true';
    if (savedState) {
        sidebar.classList.add('collapsed');
    }
    
    menuToggle.addEventListener('click', function() {
        sidebar.classList.toggle('collapsed');
        const isCollapsed = sidebar.classList.contains('collapsed');
        localStorage.setItem('menuCollapsed', isCollapsed);
        
        // Update tooltip
        menuToggle.setAttribute('title', isCollapsed ? 'Expand Menu' : 'Collapse Menu');
    });
    
    // Update initial tooltip
    const isCollapsed = sidebar.classList.contains('collapsed');
    menuToggle.setAttribute('title', isCollapsed ? 'Expand Menu' : 'Collapse Menu');
})();

