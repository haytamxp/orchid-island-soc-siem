# Playbook : Gestion d'Incidents - Injection SQL (SQLi)

Ce playbook décrit la procédure de réponse à incident en cas de détection d'une tentative ou d'une réussite d'injection SQL sur nos applications web.

## 1. Description de la Menace
L'injection SQL (SQLi) consiste à insérer des commandes SQL malveillantes dans les champs de saisie ou les paramètres d'une requête HTTP afin d'interférer avec les requêtes exécutées par l'application sur la base de données. Une SQLi réussie peut mener à la fuite de données confidentielles, à la modification de données, voire à la prise de contrôle du serveur de base de données.

## 2. Procédure de Réponse à Incident

### Phase 1 : Identification & Analyse
1. **Extraction des logs applicatifs :** Récupérer la requête HTTP complète ayant déclenché l'alerte (URL, en-têtes, méthode, adresse IP source).
2. **Détermination du succès de l'attaque :**
   - Analyser le code HTTP de réponse : une réponse `500 Internal Server Error` ou `200 OK` avec un volume de données anormalement élevé ou une signature d'erreur SQL indique un risque de succès.
   - Analyser le volume des réponses : comparer avec les requêtes normales de l'utilisateur.
3. **Recherche de persistance :** Examiner la base de données pour détecter d'éventuelles modifications de schémas, création de comptes administrateurs factices ou insertion de scripts malveillants.

### Phase 2 : Confinement
1. **Blocage de la source :** Bannir temporairement l'adresse IP source sur le Pare-feu Applicatif Web (WAF) ou le pare-feu réseau.
2. **Isolation applicative :** Si la vulnérabilité est exploitée activement et qu'aucun WAF ne peut la bloquer, mettre l'application en mode maintenance afin de stopper l'exposition.
3. **Révocation de sessions :** Révoquer toutes les sessions actives associées à l'IP ou aux comptes potentiellement compromis par l'injection.

### Phase 3 : Éradication & Correction
1. **Utilisation de requêtes préparées (Prepared Statements) :** Modifier le code source applicatif pour remplacer toutes les requêtes SQL concaténées par des requêtes paramétrées avec liaison de variables (Prepared Statements / Parameterized Queries).
2. **Validation & Assainissement des entrées :** Implémenter des listes blanches de caractères autorisés pour toutes les entrées utilisateur.
3. **Principe du moindre privilège :** Restreindre les privilèges du compte de connexion à la base de données utilisé par l'application (supprimer les droits de modification de schéma `ALTER`, `DROP` ou d'exécution de commandes système comme `xp_cmdshell`).

### Phase 4 : Rétablissement & Post-Incident
1. **Vérification de l'intégrité :** Effectuer un scan de vulnérabilités ciblé (ex: avec OWASP ZAP ou sqlmap) sur l'endpoint corrigé avant la remise en ligne.
2. **Restauration :** Si des données ont été altérées, restaurer la base de données à partir d'une sauvegarde saine connue.
3. **Rapport d'incident :** Rédiger un rapport post-incident résumant la vulnérabilité exploitée, les données compromises et les actions correctives menées.
