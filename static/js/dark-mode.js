// Dans votre fichier static/js/dark-mode.js
document.addEventListener('DOMContentLoaded', function() {
    // Vérifier si le mode sombre était précédemment activé
    const isDarkMode = localStorage.getItem('darkMode') === 'true';
    
    // Fonction pour mettre à jour l'interface
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
    
    // Initialiser le thème
    updateTheme(isDarkMode);
    
    // Ajouter l'écouteur d'événements pour le bouton
    const darkModeToggle = document.getElementById('darkModeToggle');
    if (darkModeToggle) {
        darkModeToggle.addEventListener('click', function() {
            const currentMode = document.body.classList.contains('dark-mode');
            const newMode = !currentMode;
            
            // Mettre à jour le localStorage
            localStorage.setItem('darkMode', newMode);
            
            // Mettre à jour l'interface
            updateTheme(newMode);
        });
    }
});