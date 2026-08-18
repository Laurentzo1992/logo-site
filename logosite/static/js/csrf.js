// Lit le jeton CSRF depuis le cookie posé par Django (voir {% csrf_token %} dans base.html)
// et le fournit aux appels fetch() des autres scripts via l'en-tête X-CSRFToken.
function getCsrfToken() {
    const name = 'csrftoken';
    const cookies = document.cookie ? document.cookie.split(';') : [];
    for (let cookie of cookies) {
        cookie = cookie.trim();
        if (cookie.startsWith(name + '=')) {
            return decodeURIComponent(cookie.substring(name.length + 1));
        }
    }
    return '';
}
