// JavaScript principal pour la maison connectée

// Fermeture automatique des alertes après 5 secondes
document.addEventListener('DOMContentLoaded', function() {
    // Sélectionner toutes les alertes
    const alerts = document.querySelectorAll('.alert');
    
    // Pour chaque alerte, configurer un délai pour la fermeture
    alerts.forEach(function(alert) {
        setTimeout(function() {
            // Créer un événement de fermeture
            const closeEvent = new Event('close.bs.alert');
            alert.dispatchEvent(closeEvent);
            
            // Ajouter la classe fade-out
            alert.classList.add('fade');
            
            // Après la transition, supprimer l'alerte
            setTimeout(function() {
                alert.remove();
            }, 150);
        }, 5000);
    });
});

// Fonction pour formater une date
function formatDate(dateString) {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    const date = new Date(dateString);
    return date.toLocaleDateString('fr-FR', options);
}

// Fonction pour tronquer un texte
function truncateText(text, maxLength) {
    if (text.length <= maxLength) return text;
    return text.substr(0, maxLength) + '...';
}

// Fonction pour afficher un message de confirmation
function confirmAction(message) {
    return confirm(message);
}
