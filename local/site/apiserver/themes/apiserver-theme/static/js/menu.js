// Menu Toggle Functionality
(function() {
    const MENU_STATE_KEY = 'apiserver-menu-collapsed';
    const sidebar = document.getElementById('sidebar');
    const menuToggle = document.getElementById('menu-toggle');
    
    // Load saved menu state
    function loadMenuState() {
        const isCollapsed = localStorage.getItem(MENU_STATE_KEY) === 'true';
        if (isCollapsed) {
            sidebar.classList.add('collapsed');
        }
    }
    
    // Toggle menu
    function toggleMenu() {
        sidebar.classList.toggle('collapsed');
        const isCollapsed = sidebar.classList.contains('collapsed');
        localStorage.setItem(MENU_STATE_KEY, isCollapsed);
        
        // Update tooltip
        menuToggle.setAttribute('title', 
            isCollapsed ? 'Expand Menu' : 'Collapse Menu'
        );
    }
    
    // Event listener
    menuToggle.addEventListener('click', toggleMenu);
    
    // Initialize
    loadMenuState();
    
    // Add tooltips to menu items when collapsed
    const menuItems = document.querySelectorAll('.menu-item a');
    menuItems.forEach(item => {
        const text = item.querySelector('.menu-text');
        if (text) {
            item.setAttribute('title', text.textContent);
        }
    });
})();
