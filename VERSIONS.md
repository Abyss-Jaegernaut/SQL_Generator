# Historique des Versions - SQL Generator CRUD

## v1.3.1 - La Mise à Jour "Quality of Life" (Actuelle)
**Date :** Janvier 2026
**Statut :** Stable
**Description :** Une série de correctifs ergonomiques et visuels basés sur les retours utilisateurs pour polir l'expérience v1.3.

### 🎨 & Ergonomie
- **Thèmes** : Correction définitive de l'illisibilité des listes déroulantes (SGBD) dans les thèmes sombres.
- **Ajout Colonne** : Fenêtre compactée et stylisée (plus d'espace vide blanc en bas).
- **Validation** : Les espaces dans les noms de colonnes sont automatiquement remplacés par des tirets bas `_` pour garantir un SQL valide.
- **Types SQL** : Ajout explicite de `CHAR`, `DATE`, `DATETIME`, `BOOLEAN` dans la liste des choix.

### 💾 Gestion
- **Sécurité** : Demande de confirmation explicite avant d'écraser un projet existant.
- **Nettoyage** : Ajout d'un bouton pour vider intégralement l'historique des générations.

---

## v1.3.0 - La Mise à Jour "Data Intelligence"
**Description :** Introduction majeure de la génération automatique de données et consolidation de l'architecture de sécurité.

### ✨ Nouvelles Fonctionnalités
- **Génération Fake Data (Faker)** : Remplissage automatique et intelligent des tables avec des données réalistes (Noms, Emails, Adresses, Dates...) via un bouton "✨ Remplir auto".
- **Migration de Licence Transparente** : Système de mise à jour automatique des clés d'activation (Rolling Update) pour assurer la compatibilité future sans déconnecter les utilisateurs.

---

## v1.2.3 - La Mise à Jour "Structure & Freemium"
**Date :** Janvier 2026
**Description :** Transformation du modèle économique et ajout des relations SGBD.

### 🏗️ Core & SQL
- **Foreign Keys (FK)** : Support complet des clés étrangères dans l'interface et génération SQL (CONSTRAINT FK...) pour SQL Server, MySQL, PostgreSQL.
- **Visualisation** : Ajout de la colonne "F.KEY (Ref)" dans la liste des colonnes.

### 💎 Modèle Économique
- **Version Standard (Gratuite)** : Accès limité (Thème Clair, pas d'export, pas d'historique).
- **Version Premium** : Débloquée par Clé Hardware, accès aux Thèmes Sombres (Abyss/Violet...), Export .sql, Historique.

### 🎨 UI/UX
- **Retour à l'ergonomie v1.1** : Restauration du layout robuste pour l'ajout de tables (Spinbox + Boutons alignés).
- **Correctifs Thèmes** : Correction des glitchs au démarrage et lisibilité des Spinbox/Listbox.
- **Compilation** : Passage en mode "Fichier Unique" (.exe autonome).

---

## v1.2.0 - La Mise à Jour "Design Abyss"
**Description :** Refonte esthétique complète.

### 🎨 Design
- **Nouveaux Thèmes** : Introduction du moteur de thèmes avancé avec le thème phare "Abyss" (Bleu nuit profond) et ses variantes.
- **Glassmorphism** : Légère transparence et effets modernes sur les conteneurs.

---

## v1.1.0 - La Version "Fondation Robuste"
**Description :** La version de référence pour la stabilité.

### ⚙️ Fonctionnalités
- **Génération CRUD Complète** : Création tables, procédures stockées (Insert, Select, Update, Delete).
- **Interface Intuitive** : Gestion efficace des tables et colonnes.
- **Multi-SGBD** : Abstraction initiale pour supporter différents moteurs SQL.
