function AfficherFormulaire(id) {
    const form = document.getElementById(id);
    form.style.display = (form.style.display === 'block') ? 'none' : 'block';
  }