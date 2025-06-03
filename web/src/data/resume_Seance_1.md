Okay, je vais traiter ce contenu pour en faire un résumé de révision structuré et clair pour un étudiant.

Voici le résumé de la "🟠 Séance 1 : Bases d’HTML et CSS, Structure d’une page web, Introduction à CSS" :

---

## Résumé de la Séance 1 : Bases d’HTML et CSS, Structure d’une page web, Introduction à CSS

### I. Les Fondements du Web Statique

1.  **Concepts Clés :**
    *   **Internet :** Réseau mondial interconnecté d'ordinateurs utilisant le protocole TCP/IP pour échanger des données.
    *   **Web (World Wide Web - WWW) :** Système d'information multimédia sur Internet basé sur l'hypertexte. Permet de naviguer entre des documents (pages web) via un navigateur.
    *   **Page Web :** Document électronique (texte, son, images, liens) accessible via un navigateur.
    *   **Site Web :** Ensemble de pages web reliées par des hyperliens, hébergées sur un serveur web, et structurées autour d'une page d'accueil.
    *   **Protocoles :** HTTP (pour le web), FTP (pour l'échange de fichiers).
    *   **Création d'un site web :** Comprend 3 phases : conception, réalisation, hébergement.

2.  **Site Web Statique vs. Dynamique :**
    *   **Statique :** Pages créées avec HTML et CSS. Le contenu est fixe et ne change que si le webmaster modifie le code source manuellement. Ne peut pas s'adapter au visiteur ou utiliser une base de données dynamiquement.
    *   **Dynamique :** Pages générées à la volée par des programmes (ex: PHP, ASP). Le contenu peut changer sans intervention manuelle, permettant interactivité et personnalisation.
    *   **Extensions de fichiers :** `.htm` ou `.html` (HTML), `.php` (PHP), `.asp` (ASP).

3.  **Types de Sites Web :**
    *   Carte de visite, site vitrine, e-commerce, site mobile, application web, blog, etc.

4.  **Outils et Technologies du Développement Web :**
    *   **Serveur web :** Logiciel qui délivre les pages web (ex: Apache, IIS).
    *   **Navigateur web :** Logiciel qui affiche les pages web (ex: Firefox, Chrome).
    *   **CSS (Cascading Style Sheets) :** Langage pour formater et mettre en page le contenu HTML. Sépare la structure (HTML) de la présentation (CSS).
    *   **Langages de scripts côté serveur :** PHP, Perl, Java (exécutés sur le serveur).
    *   **Langages de scripts côté client :** JavaScript, VBScript (exécutés dans le navigateur).

5.  **HTML (HyperText Markup Language) :**
    *   Langage de balisage pour structurer le contenu d'une page web.
    *   Les **balises** indiquent comment présenter le document et créent des liens.
    *   **HTML5 :** Version actuelle recommandée par le W3C.
        *   Déclaration `<!DOCTYPE html>` simplifiée.
        *   Balises fonctionnent par paires : `<balise_ouvrante>contenu</balise_ouvrante>`. La casse n'est pas stricte (mais la convention est minuscule).
        *   Balises impaires (auto-fermantes) : `<balise />` (ex: `<img />`, `<br />`).
        *   Commentaires : `<!-- commentaire -->`.
        *   **Attributs :** Propriétés supplémentaires d'une balise, sous la forme `nom="valeur"`, placés dans la balise ouvrante.
    *   **Éditeurs HTML :**
        *   **Texte :** (Notepad++, VS Code) éditent directement le code source.
        *   **WYSIWYG :** (Dreamweaver) montrent un aperçu visuel pendant l'édition.

### II. Structure de Base d'une Page HTML (HTML Basics)

1.  **Éléments et Balises (Tags) :**
    *   Un élément HTML est composé d'une balise d'ouverture, d'un contenu, et d'une balise de fermeture (ex: `<p>Ceci est un paragraphe.</p>`).
    *   Les éléments peuvent être imbriqués.
    *   Les balises peuvent avoir des **attributs** qui spécifient des propriétés (ex: `<img src="image.jpg" alt="description">`).
        *   Attributs communs : `id` (unique), `class`, `style`, `title` (infobulle).

2.  **Structure Fondamentale :**
    *   Doit commencer par `<!DOCTYPE html>`.
    *   L'élément racine est `<html>`.
    *   Comprend deux sections principales : `<head>` et `<body>`.

    ```html
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Titre de la Page</title>
        <!-- Autres méta-informations, liens CSS, scripts -->
    </head>
    <body>
        <!-- Contenu visible de la page -->
    </body>
    </html>
    ```

3.  **La Section `<head>` :**
    *   Contient des méta-informations non visibles directement sur la page.
    *   ` <title> ` : Titre affiché dans l'onglet du navigateur et utilisé par les moteurs de recherche. (Obligatoire)
    *   ` <meta> ` : Décrit le contenu (ex: `charset`, `description`, `keywords`).
    *   ` <link> ` : Pour lier des feuilles de style externes (CSS). Ex: `<link rel="stylesheet" href="style.css">`.
    *   ` <style> ` : Pour inclure du code CSS directement dans la page HTML.
    *   ` <script> ` : Pour inclure du code JavaScript.

4.  **La Section `<body>` :**
    *   Contient tout le contenu visible de la page.
    *   **Titres :** `<h1>` à `<h6>` (du plus important au moins important).
    *   **Paragraphes :** `<p>`.
    *   **Formatage de Texte :**
        *   `<b>` ou `<strong>` (gras/important)
        *   `<i>` ou `<em>` (italique/emphase)
        *   `<u>` (souligné - usage déconseillé pour éviter confusion avec liens)
        *   `<sup>` (exposant), `<sub>` (indice)
        *   `<pre>` (texte préformaté, conserve les espaces et sauts de ligne)
        *   `<blockquote>` (bloc de citation)
        *   `<del>` (texte barré)
    *   **Liens Hypertextes (`<a>`) :**
        *   ` <a href="url">Texte du lien</a> `
        *   `href` peut pointer vers une autre page, un fichier, une ancre dans la page (`#id`), une adresse email (`mailto:`).
        *   `target="_blank"` ouvre le lien dans un nouvel onglet.
        *   `title` fournit une information supplémentaire au survol.
    *   **Images (`<img>`) :**
        *   ` <img src="chemin/vers/image.jpg" alt="description de l'image"> `
        *   `src` : source de l'image.
        *   `alt` : texte alternatif (important pour l'accessibilité et si l'image ne charge pas).
    *   **Divisions (`<div>` et `<span>`) :**
        *   `<div>` : Conteneur de type bloc, pour grouper et structurer des sections.
        *   `<span>` : Conteneur de type en-ligne, pour appliquer des styles à une partie de texte.
    *   **Commentaires HTML :** `<!-- Ceci est un commentaire -->`

5.  **Bonnes Pratiques HTML :**
    *   Indenter le code pour la lisibilité.
    *   Utiliser des balises sémantiques (qui décrivent leur contenu).
    *   Valider son code (HTML est tolérant aux erreurs, mais un code valide est préférable).
    *   **HTML vs. XHTML :** XHTML est une formulation plus stricte de HTML (balises en minuscules, toujours fermées, attributs avec guillemets). HTML5 est plus flexible mais encourage les bonnes pratiques.

### III. Introduction à CSS (Cascading Style Sheets)

1.  **Rôle de CSS :**
    *   CSS est utilisé pour décrire la présentation (apparence, mise en page) des documents HTML.
    *   Sépare le contenu (HTML) de la forme (CSS).

2.  **Méthodes d'intégration du CSS :**
    *   **CSS Externe :** Dans un fichier `.css` séparé, lié via la balise `<link>` dans le `<head>`. C'est la méthode recommandée pour la majorité des styles.
        ```html
        <link rel="stylesheet" type="text/css" href="styles.css">
        ```
    *   **CSS Interne :** Directement dans la page HTML, à l'intérieur de balises `<style>` dans le `<head>`.
        ```html
        <head>
            <style>
                p {
                    color: blue;
                    font-size: 14px;
                }
            </style>
        </head>
        ```
    *   **CSS en Ligne (Inline) :** Directement sur un élément HTML via l'attribut `style`. À utiliser avec parcimonie car moins maintenable.
        ```html
        <p style="color: red; font-size: 16px;">Texte en rouge.</p>
        ```
    *   **Importation (`@import`) :** Permet d'importer une feuille de style depuis une autre feuille de style ou dans une balise `<style>`. Doit être la première règle.
        ```css
        /* Dans un fichier CSS ou une balise <style> */
        @import url("autre-style.css");
        ```

3.  **Syntaxe de Base d'une Règle CSS :**
    *   `sélecteur { propriété: valeur; }`
    *   Exemple : `p { color: blue; text-align: center; }`
        *   `p` est le sélecteur (cible les éléments `<p>`).
        *   `color` et `text-align` sont des propriétés.
        *   `blue` et `center` sont leurs valeurs respectives.

### IV. Création d'un Formulaire HTML

1.  **Balise `<form>` :**
    *   Conteneur principal pour les éléments de formulaire.
    *   Attributs importants :
        *   `action` : URL de la page ou du script qui traitera les données du formulaire.
        *   `method` : Méthode HTTP pour envoyer les données :
            *   **`get` :** Ajoute les données du formulaire à l'URL (`page.php?nom=valeur&autre=valeur2`). Visible, limité en taille, bookmarkable.
            *   **`post` :** Envoie les données dans le corps de la requête HTTP. Non visible dans l'URL, pas de limite de taille (pratique), plus sécurisé pour les données sensibles.

2.  **Éléments de Formulaire (principalement avec `<input>`) :**
    *   Tous les champs de saisie doivent avoir un attribut `name` pour que leurs données soient envoyées. L'attribut `value` peut définir une valeur par défaut.

    *   **Champ de texte (`<input type="text">`) :**
        ```html
        <label for="nom">Nom :</label>
        <input type="text" id="nom" name="utilisateur_nom" size="30" maxlength="50">
        ```
        *   `size` : largeur visible du champ.
        *   `maxlength` : nombre maximal de caractères.

    *   **Champ de mot de passe (`<input type="password">`) :**
        ```html
        <label for="mdp">Mot de passe :</label>
        <input type="password" id="mdp" name="utilisateur_mdp">
        ```

    *   **Boutons Radio (`<input type="radio">`) :** Pour un choix unique parmi plusieurs options. Tous les boutons radio d'un même groupe doivent avoir le même `name`.
        ```html
        <input type="radio" id="homme" name="sexe" value="H" checked>
        <label for="homme">Masculin</label>
        <input type="radio" id="femme" name="sexe" value="F">
        <label for="femme">Féminin</label>
        ```
        *   `checked` : présélectionne une option.

    *   **Cases à Cocher (`<input type="checkbox">`) :** Pour sélection multiple.
        ```html
        <input type="checkbox" id="musique" name="interet_musique" value="oui">
        <label for="musique">Musique</label>
        <input type="checkbox" id="sport" name="interet_sport" value="oui" checked>
        <label for="sport">Sport</label>
        ```
        * Si plusieurs checkboxes partagent le même `name` (ex: `name="interets[]"` en PHP), le serveur les recevra comme un tableau.

    *   **Liste Déroulante (`<select>` et `<option>`) :**
        ```html
        <label for="age">Âge :</label>
        <select id="age" name="tranche_age">
            <option value="moins30">Moins de 30 ans</option>
            <option value="trenteSoixante" selected>Entre 30 et 60 ans</option>
            <option value="plus60">Plus de 60 ans</option>
        </select>
        ```
        *   `selected` : présélectionne une option.
        *   L'attribut `multiple` sur `<select>` permet la sélection multiple.

    *   **Zone de Texte Multiligne (`<textarea>`) :**
        ```html
        <label for="commentaires">Commentaires :</label>
        <textarea id="commentaires" name="texte_commentaires" rows="5" cols="40"></textarea>
        ```
        *   `rows` : nombre de lignes visibles.
        *   `cols` : nombre de colonnes visibles.

    *   **Bouton d'Envoi (`<input type="submit">`) :**
        ```html
        <input type="submit" value="Envoyer les données">
        ```
        *   `value` : texte affiché sur le bouton.

    *   **Bouton de Réinitialisation (`<input type="reset">`) :**
        ```html
        <input type="reset" value="Effacer">
        ```

3.  **Organisation et Présentation :**
    *   Utiliser des balises `<label>` associées aux champs (via l'attribut `for` qui correspond à l'`id` du champ) pour l'accessibilité et l'ergonomie.
    *   Les listes (`<ul>`, `<ol>`, `<dl>`) ou les tableaux (`<table>`) peuvent être utilisés pour structurer la présentation des formulaires (bien que CSS soit préférable pour la mise en page complexe).

### V. Intégration PHP et HTML (Aperçu)

*   PHP est un langage exécuté côté serveur. L'interpréteur PHP traite le code PHP contenu entre des balises spécifiques (ex: `<?php ... ?>`).
*   Le code PHP peut générer du HTML qui est ensuite envoyé au navigateur.
*   L'interpréteur PHP "saute" les balises HTML et ne traite que le code PHP.
*   On peut insérer du HTML dans des instructions PHP `echo` ou `print`.
*   Pour créer des sauts de ligne dans le rendu HTML à partir de PHP, on peut utiliser `echo "<br>\n";` ou insérer `\n` dans des chaînes entre guillemets doubles pour formater le code source HTML (pas l'affichage).
*   Les commentaires en PHP : `// commentaire sur une ligne`, `# commentaire style shell`, `/* commentaire sur plusieurs lignes */`.

*(Note : La séance contient des éléments sur PHP qui dépassent l'introduction à HTML/CSS, comme le traitement détaillé de formulaires en PHP (`$_POST`), la gestion des sessions (`PHPSESSID`), et des fonctions PHP spécifiques comme `stripslashes()`, `isset()`, `substr()`, `count()`. Ces aspects seront approfondis dans des séances dédiées à PHP.)*

---