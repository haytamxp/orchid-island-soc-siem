# Playbook : Gestion d'Incidents - Attaque par Force Brute (Brute Force)

Ce playbook décrit la procédure de réponse à incident en cas de détection d'une tentative ou d'une réussite d'attaque par force brute (Brute Force) ou de bourrage d'identifiants (Credential Stuffing).

## 1. Description de la Menace
L'attaque par force brute consiste à tester de nombreuses combinaisons de mots de passe ou d'identifiants sur un service d'authentification afin de deviner des identifiants valides. Si elle réussit, elle permet à un attaquant d'accéder illégitimement à des comptes d'utilisateurs ou d'administrateurs.

## 2. Procédure de Réponse à Incident

### Phase 1 : Identification & Analyse
1. **Extraction des logs d'authentification :** Récupérer la liste des tentatives de connexion échouées (horodatages, adresses IP sources, comptes visés, codes d'erreur de retour).
2. **Identification de la cible de l'attaque :**
   - Attaque ciblée : Une seule adresse IP teste de nombreux mots de passe sur un seul compte.
   - Attaque par dictionnaire / Credential Stuffing : Une ou plusieurs adresses IP testent de nombreux comptes avec des mots de passe différents.
3. **Détermination du succès de l'attaque :**
   - Rechercher si, après une série de connexions échouées, une tentative de connexion a réussi pour le même compte depuis la même IP ou sous des critères similaires.
   - Analyser le comportement post-connexion (ex: changement soudain d'adresse e-mail, modification de mot de passe, ou actions non habituelles).

### Phase 2 : Confinement
1. **Blocage IP :** Configurer un blocage temporaire ou permanent de l'adresse IP source sur les équipements de sécurité (WAF, IPS, Pare-feu).
2. **Verrouillage de compte (Account Lockout) :** Verrouiller temporairement le ou les comptes cibles afin de stopper l'attaque.
3. **Défi de sécurité (MFA/CAPTCHA) :** Activer ou forcer l'affichage d'un CAPTCHA ou d'une double authentification (MFA) sur la page d'authentification.

### Phase 3 : Éradication & Correction
1. **Politique de verrouillage de compte :** Configurer ou renforcer la politique de verrouillage temporaire des comptes après un nombre prédéfini de tentatives infructueuses (ex: 5 échecs).
2. **Exigence de Mots de Passe Forts :** Mettre en place des règles strictes de complexité et de longueur minimale pour les mots de passe.
3. **Intégration du MFA :** Rendre la double authentification obligatoire pour tous les accès, en particulier pour les comptes dotés de privilèges élevés.
4. **Rate Limiting :** Implémenter une limitation stricte des requêtes sur les endpoints d'authentification (ex: avec Redis, Nginx Rate Limiting, ou au niveau applicatif).

### Phase 4 : Rétablissement & Post-Incident
1. **Réinitialisation des mots de passe :** Si un compte a été compromis avec succès, forcer immédiatement la réinitialisation du mot de passe et révoquer toutes ses sessions actives.
2. **Communication utilisateur :** Informer les utilisateurs concernés de la tentative d'accès illégitime et leur rappeler les consignes de sécurité.
3. **Rapport d'incident :** Rédiger un rapport synthétisant la durée de l'attaque, les comptes visés, le nombre de tentatives, le statut de succès/échec et les mesures de mitigation pérennes appliquées.
