document.addEventListener('DOMContentLoaded', function() {
    const isDarkMode = localStorage.getItem('darkMode') === 'true';
    
    function updateTheme(isDark) {
        const body = document.body;
        const themeText = document.getElementById('themeModeText');
        const themeIcon = document.querySelector('#darkModeToggle i');
        
        if (isDark) {
            body.classList.add('dark-mode');
            themeText.textContent = 'Mode clair';
            themeIcon.classList.remove('fa-moon');
            themeIcon.classList.add('fa-sun');
        } else {
            body.classList.remove('dark-mode');
            themeText.textContent = 'Mode sombre';
            themeIcon.classList.remove('fa-sun');
            themeIcon.classList.add('fa-moon');
        }
    }
    
    updateTheme(isDarkMode);
    
    const darkModeToggle = document.getElementById('darkModeToggle');
    if (darkModeToggle) {
        darkModeToggle.addEventListener('click', function() {
            const currentMode = document.body.classList.contains('dark-mode');
            const newMode = !currentMode;
            
            localStorage.setItem('darkMode', newMode);
            
            updateTheme(newMode);
        });
    }
});