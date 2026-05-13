// Scripts interface gestion salon
// Ce fichier permet à GitHub de détecter l'utilisation de JavaScript dans le projet

console.log("Gestion salon — scripts chargés");

// Fonction exemple pour les réservations
function toggleReservationDetails(id) {
    const element = document.getElementById(id);
    if (element) {
        element.style.display = element.style.display === 'none' ? 'block' : 'none';
    }
}

// Fonction pour la validation des formulaires
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (form) {
        // Logique de validation simple
        return true;
    }
    return false;
}