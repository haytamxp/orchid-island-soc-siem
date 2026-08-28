# Playbook : Gestion d'Incidents - Cross-Site Scripting (XSS)

Ce playbook décrit la procédure de réponse à incident en cas de détection d'une tentative ou d'une réussite d'injection de script malveillant (XSS) sur nos applications web.

## 1. Description de la Menace
Le Cross-Site Scripting (XSS) consiste à injecter des scripts côté client (souvent en JavaScript) dans des pages web légitimes afin qu'ils soient exécutés par les navigateurs des utilisateurs cibles. Un XSS réussi peut mener au vol de cookies de session, au détournement de sessions utilisateur, à la défiguration de sites web (defacement), ou à la redirection vers des sites malveillants.

## 2. Procédure de Réponse à Incident

### Phase 1 : Identification & Analyse
1. **Extraction des détails de la requête :** Identifier l'URL ciblée, la méthode HTTP, le paramètre vulnérable et le payload injecté (ex: cherche des balises `<script>`, des attributs HTML d'événement comme `onerror`, `onload`, ou du code JavaScript encodé).
2. **Détermination du type de XSS :**
   - **XSS Réfléchi :** Le script est envoyé par le client et immédiatement retourné dans la réponse (le log montre la charge utile dans les paramètres d'URL ou les requêtes POST).
   - **XSS Stocké :** Le script est enregistré de manière persistante sur le serveur (base de données, fichiers). Vérifier si le contenu a été écrit en base.
   - **XSS DOM-based :** L'exécution a lieu entièrement côté client via la manipulation du DOM par le JavaScript légitime de la page.
3. **Détermination du succès de l'attaque :**
   - Vérifier si l'application renvoie le script non échappé dans sa réponse HTTP (XSS Réfléchi).
   - Si l'attaque est stockée, naviguer sur la page concernée dans un environnement de test sécurisé pour confirmer si le script s'exécute.

### Phase 2 : Confinement
1. **Blocage de l'IP source :** Bannir temporairement l'IP attaquante sur le WAF (Web Application Firewall) ou le pare-feu.
2. **Nettoyage des données (XSS Stocké) :** Si le script malveillant a été enregistré en base de données, isoler et supprimer immédiatement l'enregistrement ou le champ affecté.
3. **Révocation de session :** Si une exécution réussie est suspectée, révoquer immédiatement toutes les sessions actives des utilisateurs ayant visité la page vulnérable durant la fenêtre d'attaque pour neutraliser le vol de session.

### Phase 3 : Éradication & Correction
1. **Échappement contextuel des données (Output Encoding) :** Modifier le code source pour encoder toutes les données provenant des utilisateurs avant de les afficher dans le navigateur. Utiliser l'encodage approprié selon le contexte (HTML body, attribut HTML, JavaScript, CSS, URL).
2. **Validation et filtrage en entrée (Input Validation) :** Implémenter une validation par liste blanche des entrées pour interdire les caractères non autorisés.
3. **Content Security Policy (CSP) :** Déployer des en-têtes HTTP CSP robustes pour restreindre les sources de scripts autorisés et interdire l'exécution de scripts inline (`unsafe-inline`).
4. **Attributs de cookies sécurisés :** Configurer les cookies de session avec les attributs `HttpOnly` (pour empêcher leur lecture via JavaScript) et `Secure` (pour imposer le HTTPS).

### Phase 4 : Rétablissement & Post-Incident
1. **Validation post-correction :** Effectuer un test d'intrusion manuel ou automatisé sur l'endpoint vulnérable pour valider l'absence de régression.
2. **Audit général :** Lancer un scan de vulnérabilités global sur l'ensemble de l'application.
3. **Rapport d'incident :** Rédiger le rapport résumant la cause racine, les utilisateurs potentiellement touchés et les mesures correctives permanentes mises en place.
