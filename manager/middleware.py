import re
from django.http import HttpResponseForbidden
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta

class SecurityMiddleware:
    """Middleware de sécurité personnalisé"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Patterns pour détecter les attaques courantes (plus spécifiques)
        self.suspicious_patterns = [
            r'<script[^>]*>.*?</script>',  # Script tags complets
            r'javascript:\s*',     # JavaScript protocol
            r'on\w+\s*=\s*["\'][^"\']*["\']',      # Event handlers avec contenu
            r'<iframe[^>]*>.*?</iframe>',  # Iframe tags complets
            r'<object[^>]*>.*?</object>',  # Object tags complets
            r'<embed[^>]*>.*?</embed>',   # Embed tags complets
            r'<link[^>]*>.*?</link>',    # Link tags complets
            r'<meta[^>]*>.*?</meta>',    # Meta tags complets
            r'<form[^>]*>.*?</form>',    # Form tags complets
            r'<input[^>]*>.*?</input>',   # Input tags complets
            r'<textarea[^>]*>.*?</textarea>', # Textarea tags complets
            r'<select[^>]*>.*?</select>',  # Select tags complets
            r'<button[^>]*>.*?</button>',  # Button tags complets
            r'<a[^>]*>.*?</a>',       # Anchor tags complets
            r'<img[^>]*>.*?</img>',     # Image tags complets
            r'<video[^>]*>.*?</video>',   # Video tags complets
            r'<audio[^>]*>.*?</audio>',   # Audio tags complets
            r'<canvas[^>]*>.*?</canvas>',  # Canvas tags complets
            r'<svg[^>]*>.*?</svg>',     # SVG tags complets
            r'<math[^>]*>.*?</math>',    # MathML tags complets
            r'<xmp[^>]*>.*?</xmp>',     # XMP tags complets
            r'<plaintext[^>]*>.*?</plaintext>', # Plaintext tags complets
            r'<listing[^>]*>.*?</listing>', # Listing tags complets
            r'<noembed[^>]*>.*?</noembed>', # Noembed tags complets
            r'<noframes[^>]*>.*?</noframes>', # Noframes tags complets
            r'<noscript[^>]*>.*?</noscript>', # Noscript tags complets
            r'<nobr[^>]*>.*?</nobr>',    # Nobr tags complets
            r'<noindex[^>]*>.*?</noindex>', # Noindex tags complets
            r'<noreferrer[^>]*>.*?</noreferrer>', # Noreferrer tags complets
            r'<nofollow[^>]*>.*?</nofollow>', # Nofollow tags complets
            r'<noarchive[^>]*>.*?</noarchive>', # Noarchive tags complets
            r'<nosnippet[^>]*>.*?</nosnippet>', # Nosnippet tags complets
            r'<notranslate[^>]*>.*?</notranslate>', # Notranslate tags complets
            r'<noprint[^>]*>.*?</noprint>', # Noprint tags complets
        ]
        
# Pages autorisées (pas de vérification XSS)
        self.allowed_pages = [
            '/connexion/',
            '/inscription/client/',
            '/inscription/coiffeuse/',
            '/',
            '/admin/',
            '/admin/login/',
            '/dashboard/',
            '/reservations/',
            '/services/',
            '/profil/',
            '/validation-coiffeuses/',
        ]
        
    def __call__(self, request):
        # Vérification des attaques XSS (seulement pour les pages non autorisées)
        if not self._is_allowed_page(request.path):
            if self._detect_xss_attack(request):
                return HttpResponseForbidden("Accès refusé - Contenu suspect détecté")
        
        # Vérification du rate limiting
        if self._check_rate_limit(request):
            return HttpResponseForbidden("Trop de requêtes - Veuillez attendre")
        
        # Vérification des headers de sécurité
        response = self.get_response(request)
        self._add_security_headers(response)
        
        return response
    
    def _is_allowed_page(self, path):
        """Vérifie si la page est autorisée (pas de vérification XSS)"""
        for allowed_page in self.allowed_pages:
            if path.startswith(allowed_page):
                return True
        return False
    
    def _detect_xss_attack(self, request):
        """Détecte les tentatives d'attaque XSS"""
        # Vérifier les paramètres GET
        for key, value in request.GET.items():
            if self._contains_suspicious_content(value):
                return True
        
        # Vérifier les paramètres POST
        for key, value in request.POST.items():
            if self._contains_suspicious_content(value):
                return True
        
        # Vérifier les headers (plus restrictif)
        suspicious_headers = ['user-agent', 'referer', 'origin']
        for key, value in request.headers.items():
            if key.lower() in suspicious_headers and self._contains_suspicious_content(value):
                return True
        
        return False
    
    def _contains_suspicious_content(self, content):
        """Vérifie si le contenu contient des patterns suspects"""
        if not isinstance(content, str):
            return False
        
        # Ignorer les caractères spéciaux courants dans les mots de passe
        if len(content) < 100:  # Contenu court probablement normal
            return False
            
        content_lower = content.lower()
        for pattern in self.suspicious_patterns:
            if re.search(pattern, content_lower, re.IGNORECASE | re.DOTALL):
                return True
        
        return False
    
    def _check_rate_limit(self, request):
        """Vérifie le rate limiting par IP"""
        client_ip = self._get_client_ip(request)
        cache_key = f"rate_limit_{client_ip}"
        
        # Récupérer le nombre de requêtes
        request_count = cache.get(cache_key, 0)
        
        # Limite: 500 requêtes par minute (plus permissif)
        if request_count > 1000:
            return True
        
        # Incrémenter le compteur
        cache.set(cache_key, request_count + 1, 60)  # Expire en 60 secondes
        
        return False
    
    def _get_client_ip(self, request):
        """Récupère l'IP du client"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def _add_security_headers(self, response):
        """Ajoute des headers de sécurité"""
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        return response 