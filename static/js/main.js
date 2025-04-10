document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert');
    
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const closeEvent = new Event('close.bs.alert');
            alert.dispatchEvent(closeEvent);
            
            alert.classList.add('fade');
            
            setTimeout(function() {
                alert.remove();
            }, 150);
        }, 5000);
    });
});

function formatDate(dateString) {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    const date = new Date(dateString);
    return date.toLocaleDateString('fr-FR', options);
}

function truncateText(text, maxLength) {
    if (text.length <= maxLength) return text;
    return text.substr(0, maxLength) + '...';
}

function confirmAction(message) {
    return confirm(message);
}
