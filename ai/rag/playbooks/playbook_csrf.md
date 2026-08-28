# Playbook : Gestion d'Incidents - Cross-Site Request Forgery (CSRF)

Ce playbook décrit la procédure de réponse à incident en cas de détection d'une tentative ou d'une réussite d'attaque par falsification de requête intersites (CSRF) sur nos applications web.

## 1. Description de la Menace
Le Cross-Site Request Forgery (CSRF) consiste à forcer le navigateur d'un utilisateur authentifié à envoyer une requête HTTP malveillante vers une application web vulnérable sur laquelle il dispose de privilèges actifs. L'application exécute alors l'action involontaire (ex: changement de mot de passe, transfert de fonds, modification de profil) sous l'identité de la victime, car celle-ci est déjà authentifiée (les cookies de session sont automatiquement transmis par le navigateur).

## 2. Procédure de Réponse à Incident

### Phase 1 : Identification & Analyse
1. **Extraction et vérification des en-têtes :** Examiner la requête HTTP ayant généré l'alerte. Vérifier l'absence ou l'invalidité du jeton anti-CSRF. Examiner les en-têtes `Origin` et `Referer` pour déterminer la provenance de la requête (site tiers suspect).
2. **Détermination du succès de l'attaque :**
   - Analyser si l'action d'écriture (POST, PUT, DELETE) initiée a été exécutée avec succès côté base de données (ex: modifications de données sur le compte utilisateur sans sa participation active).
   - Confirmer si la victime a visité un site externe suspect ou a cliqué sur un lien externe juste avant l'exécution de la requête.

### Phase 2 : Confinement
1. **Blocage réseau et WAF :** Ajouter une règle de blocage ou d'alerte sur le pare-feu ou le WAF pour le domaine référent tiers (`Referer`) malveillant identifié.
2. **Suspension des comptes affectés :** Si des comptes utilisateurs spécifiques sont identifiés comme ayant été altérés de manière frauduleuse, les désactiver temporairement pour empêcher d'autres actions.
3. **Révocation générale des sessions :** En cas d'attaque généralisée ou de campagne malveillante active, forcer la déconnexion de tous les utilisateurs afin de réinitialiser les identifiants de session et cookies de navigation.

### Phase 3 : Éradication & Correction
1. **Jetons Anti-CSRF (Synchronizer Token Pattern) :** Implémenter des jetons cryptographiques uniques, secrets et imprévisibles pour chaque session utilisateur. Ce jeton doit être requis pour toute requête modifiant l'état de l'application (POST, PUT, DELETE) et être validé côté serveur.
2. **Attribut de Cookie `SameSite` :** Configurer l'attribut `SameSite` à `Lax` ou `Strict` sur tous les cookies de session pour empêcher leur transmission automatique lors de requêtes cross-site.
3. **Validation des en-têtes `Origin` et `Referer` :** Compléter la défense en validant systématiquement que l'en-tête `Origin` ou `Referer` provient bien d'un domaine autorisé de l'agence.
4. **Double authentification (2FA) / Ré-authentification :** Exiger la saisie du mot de passe actuel ou une confirmation double facteur pour les actions critiques (changement de mot de passe, d'e-mail ou d'administration).

### Phase 4 : Rétablissement & Post-Incident
1. **Validation post-correction :** Retester les formulaires et endpoints d'écriture en tentant de soumettre des requêtes sans jetons ou depuis un domaine tiers pour s'assurer que les barrières fonctionnent.
2. **Audit et monitoring :** Surveiller les logs applicatifs pour toute anomalie d'en-tête `Referer` ou de validation de jeton.
3. **Rapport d'incident :** Documenter l'incident et informer les utilisateurs si des données de profil ou des actions critiques ont été réalisées à leur insu (obligation RGPD).
