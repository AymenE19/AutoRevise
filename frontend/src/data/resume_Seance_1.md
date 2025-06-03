
# Résumé - Séance 1: Bases d'HTML et CSS, Structure d'une page web, Introduction à CSS

## Introduction
Cette première séance couvre les fondamentaux du développement web, en se concentrant sur HTML et CSS comme technologies de base pour créer des pages web structurées et stylisées.

## 1. Bases d'HTML

### Structure de base d'un document HTML
```html
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Titre de la page</title>
</head>
<body>
    <!-- Contenu de la page -->
</body>
</html>
```

### Balises HTML essentielles
- **Titres** : `<h1>` à `<h6>` pour hiérarchiser le contenu
- **Paragraphes** : `<p>` pour le texte
- **Conteneurs** : `<div>` et `<span>` pour structurer
- **Liens** : `<a href="">` pour la navigation
- **Images** : `<img src="" alt="">` pour les médias

## 2. Structure sémantique d'une page web

### Éléments structurels
- `<header>` : En-tête de la page ou d'une section
- `<nav>` : Menu de navigation
- `<main>` : Contenu principal
- `<section>` : Sections thématiques
- `<article>` : Contenu autonome
- `<aside>` : Contenu complémentaire
- `<footer>` : Pied de page

### Métadonnées importantes
- `<meta charset="UTF-8">` : Encodage des caractères
- `<meta name="viewport">` : Responsive design
- `<title>` : Titre dans l'onglet du navigateur

## 3. Introduction à CSS

### Méthodes d'intégration CSS
1. **CSS inline** : `style="color: red;"`
2. **CSS interne** : `<style>` dans `<head>`
3. **CSS externe** : `<link rel="stylesheet" href="style.css">`

### Sélecteurs CSS de base
- **Élément** : `h1 { color: blue; }`
- **Classe** : `.ma-classe { font-size: 16px; }`
- **ID** : `#mon-id { background: yellow; }`

### Propriétés CSS fondamentales
- **Couleurs** : `color`, `background-color`
- **Typographie** : `font-size`, `font-family`, `font-weight`
- **Espacement** : `margin`, `padding`
- **Bordures** : `border`
- **Dimensions** : `width`, `height`

## Points clés à retenir

1. **HTML** structure le contenu de manière sémantique
2. **CSS** s'occupe de la présentation et du style
3. La **séparation des préoccupations** est essentielle
4. L'**accessibilité** doit être prise en compte dès le début
5. La **validation** du code HTML/CSS est importante

## Exercices pratiques recommandés

1. Créer une page HTML avec structure sémantique complète
2. Appliquer des styles CSS de base
3. Expérimenter avec différents sélecteurs
4. Valider le code avec les outils W3C

## Ressources supplémentaires

- [MDN Web Docs](https://developer.mozilla.org/)
- [W3C Validator](https://validator.w3.org/)
- [Can I Use](https://caniuse.com/) pour la compatibilité des navigateurs
