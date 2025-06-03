import json

import httpx
from fastapi import FastAPI
from google.genai import types

from generating.settings import ALLOWED_USER_ACTIONS, GEMINI_MODEL_NAME
from utils.strings import clean_code_block


def build_action_prompt(action: str, title: str, content: str) -> str:
    match action:
        case "summary":
            return f"""
                Tu es un assistant pédagogique. Je vais te fournir le contenu brut d'une séance intitulée : "{title}".
                
                Le texte peut contenir des lignes vides ou inutiles. Voici ce que tu dois faire :
                1. Ignore les lignes vides ou non informatives.
                2. Organise le contenu par titres (déjà marqués avec ###).
                3. Résume le contenu de façon claire et structurée, en français.
                4. Le résumé doit être utile pour un étudiant souhaitant réviser rapidement cette séance.
                5. Gardez la réponse sous 2500 caractères
                
                Retourne uniquement le Markdown. Aucun autre texte.
                Voici le contenu :
                {content}
            """

        case "mind-map":
            return (
                f"""
                Tu es un assistant pédagogique. Je vais te fournir le contenu brut d'une séance intitulée : "{title}".
                
                Je veux que tu génères une **carte mentale** (mind map) à partir de ce contenu.
                Format de sortie : JSON
                Structure demandée :
                """
                """
                    {
                      "title": "Titre de la séance",
                      "nodes": [
                        {
                          "title": "Titre principal",
                          "children": [
                            {
                              "title": "Sous-concept 1"
                            },
                            {
                              "title": "Sous-concept 2"
                            }
                          ]
                        }
                      ]
                    }
                """
                f"""
                Consignes :
                - Résume de manière hiérarchique et claire.
                - Utilise les titres marqués avec `###` comme racines principales.
                - Évite les détails inutiles.
                - Utilise un JSON bien formé, sans texte ou explication autour.
                - Gardez la réponse sous 2500 caractères
                
                Voici le contenu :
                {content}
            """
            )

        case "quiz":
            return (
                f"""
                    Tu es un assistant pédagogique.Je vais te fournir le contenu brut d'une séance intitulée : "{title}\n".
                    
                    Je veux que tu crées un ** quiz avec solutions ** basé sur ce contenu.
                    
                    Format de sortie: JSON uniquement, bien structuré.
                    Structure demandée:
                """
                """
                    {{
                      "title": "Titre de la séance",
                      "questions": [
                        {
                        {
                          "question": "Quel est le rôle du DNS dans Internet ?",
                          "options": [
                            "Il stocke les fichiers HTML.",
                            "Il convertit les noms de domaine en adresses IP.",
                            "Il crypte les communications HTTPS.",
                            "Il héberge les bases de données."
                          ],
                          "answer": "Il convertit les noms de domaine en adresses IP.",
                          "explanation": "Le DNS fait correspondre les noms de domaine avec leurs adresses IP respectives."
                        }
                        }
                      ]
                    }}
                """
                f"""        
                    Consignes:
                    - Génére entre 5 à 10 questions maximum.
                    - Chaque question doit avoir 4 propositions.
                    - Une seule réponse correcte par question.
                    - Ajoute une explication claire et concise pour chaque réponse.
                    - Le JSON ne doit pas être entouré de texte ni de commentaire.
                    - Gardez la réponse sous 2500 caractères
                                
                    Voici le contenu:
                    {content}"
                """
            )

        case _:
            raise ValueError("Action non supportée.")


def send_prompt(app: FastAPI, prompt: str, max_output_tokens: int = 500, temperature: float = 0.1):
    try:
        return app.state.gemini_client.models.generate_content(
            model=GEMINI_MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                max_output_tokens=max_output_tokens,
                temperature=temperature
            )
        )
    except Exception as e:
        app.state.logger.error(e)
        return None


def match_user_prompt(app: FastAPI, user_prompt: str) -> dict | None:
    topics = app.state.db.get_all_topics()

    topic_samples = {
        topic: [
            {
                "session_title": s["session_title"],
                "session_order": s["session_order"],
                "session_description": s["session_description"],
            }
            for s in app.state.db.select_topic(topic) or app.state.db.get_all_sessions()
        ]
        for topic in topics
    }

    prompt = (
        f'You are given a user prompt: "{user_prompt}".\n'
        f"Based on the following available topics and sample sessions, "
        f"extract the most relevant topic and session title.\n\n"
        f"Topics and sessions:\n{topic_samples}\n\n"
        'Return your answer in JSON: { "topic": "<topic>", "session_order": "<session_order>" }'
    )

    response = send_prompt(app, prompt, max_output_tokens=400, temperature=0.1)
    if response:
        app.state.logger.info(f"At match_user_prompt(), Gemini responded with {response.text}")
        try:
            return clean_code_block(app, response.text)
        except ValueError:
            raise ValueError(response.text)

    raise ValueError(response.text)


def build_response(app: FastAPI, action: str, content: str) -> dict:
    if action not in ALLOWED_USER_ACTIONS:
        return {"error": "Unrecognized action", "raw": content}

    try:
        content = clean_code_block(app, content)
        return {
            "type": "markdown" if action == "summary" else "json",
            "content": content
        }
    except json.JSONDecodeError:
        return {"error": "La réponse du modèle n'est pas un JSON valide.", "raw": content}


def process_user_action(app: FastAPI, action: str, user_prompt: str) -> dict:
    if action not in ALLOWED_USER_ACTIONS:
        return {"error": "Action non supportée."}

    try:
        matched = match_user_prompt(app, user_prompt)  # Logging
        app.state.logger.info(f"At process_user_action(), match_user_prompt returned {matched}")
    except ValueError:
        return {"error": "Action non reconnue."}

    topic = matched.get("topic")
    session_order = matched.get("session_order")

    if not topic:
        return {"error": "Topic non existant"}
    if not session_order:
        return {"error": "Session non existant"}

    app.state.db.select_topic(topic)
    session = app.state.db.find_session_by_order(int(session_order))
    if session is None:
        return {"error": "Session non existant."}

    prompt = build_action_prompt(action, session["session_title"], session["markdown_content"])

    try:
        response = send_prompt(app, prompt, max_output_tokens=3000, temperature=0.2)

        if not response or not response.text:
            return {"error": "Réponse vide du modèle."}

        return build_response(app, action, response.text)

    except httpx.HTTPStatusError as e:
        return {"error": f"Erreur HTTP: {e.response.status_code} - {e.response.text}"}

    except httpx.RequestError as e:
        return {"error": f"Erreur de requête: {str(e)}"}

    except Exception as e:
        return {"error": f"Erreur inattendue: {str(e)}"}


def test(action: str, user_prompt: str) -> dict:
    if action not in ALLOWED_USER_ACTIONS:
        return {"error": "Action non supportée."}

    if action == "summary":
        return {
            "type": "markdown",
            "content": "## Python : Résumé de Séance\n\n### Fonctions\n*   Définition avec `def nom_fonction(paramètres):`.\n*   Appel : `nom_fonction(arguments)`.\n*   `return` renvoie une valeur (sinon `None`).\n*   Paramètres : positionnels, nommés, par défaut.\n*   Fonctions lambda : `lambda arguments: expression` (anonymes, courtes).\n\n### Chaînes de Caractères (Strings)\n*   Immuables.\n*   Concaténation (`+`), répétition (`*`), indexation (`[]`), slicing (`[:]`).\n*   Méthodes : `len()`, `upper()`, `lower()`, `strip()`, `split()`, `join()`, `find()`, `replace()`, `startswith()`, `endswith()`, `count()`, `isalpha()`, `isdigit()`, `isalnum()`, `isspace()`.\n*   Formatage : f-strings (recommandé), `format()`.\n\n### Listes\n*   Mutables, ordonnées.\n*   Création : `[element1, element2, ...]`.\n*   Accès/Modification : index, slicing.\n*   Méthodes : `append()`, `insert()`, `pop()`, `remove()`, `sort()`, `reverse()`, `extend()`, `count()`, `index()`, `copy()`.\n*   `sort()` vs `sorted()`.\n*   Compréhensions de listes : `[expression for item in iterable if condition]`.\n\n### Lecture/Écriture de Fichiers\n*   `open(nom_fichier, mode, encoding='utf-8')`.\n*   Modes : `'r'` (lecture), `'w'` (écriture, écrase), `'a'` (ajout), `'x'` (création exclusive), `'b'` (binaire).\n*   `with open(...) as f:` (gestionnaire de contexte, fermeture auto).\n*   Lecture : `read()`, `readline()`, `readlines()`.\n*   Écriture : `write()`, `writelines()`."
        }

    elif action == "quiz":
        return {
            "type": "json",
            "content": {
                "title": "Quiz Python",
                "questions": [
                    {
                        "question": "Quelle est la syntaxe correcte pour définir une fonction en Python?",
                        "options": [
                            "function nom_fonction():",
                            "def nom_fonction():",
                            "nom_fonction = function():",
                            "define nom_fonction():"
                        ],
                        "answer": "def nom_fonction():",
                        "explanation": "En Python, on utilise le mot-clé 'def' suivi du nom de la fonction et de parenthèses pour définir une fonction."
                    },
                    {
                        "question": "Quelle instruction est utilisée pour renvoyer une valeur depuis une fonction?",
                        "options": [
                            "print",
                            "return",
                            "yield",
                            "exit"
                        ],
                        "answer": "return",
                        "explanation": "L'instruction 'return' est utilisée pour spécifier la valeur que la fonction doit renvoyer."
                    },
                    {
                        "question": "Qu'est-ce qu'une fonction lambda en Python?",
                        "options": [
                            "Une fonction qui ne prend aucun argument.",
                            "Une fonction courte et anonyme.",
                            "Une fonction qui ne peut pas être appelée.",
                            "Une fonction qui est toujours récursive."
                        ],
                        "answer": "Une fonction courte et anonyme.",
                        "explanation": "Les fonctions lambda sont des fonctions anonymes courtes, définies en utilisant le mot-clé 'lambda'."
                    },
                    {
                        "question": "Quelle méthode est utilisée pour ajouter un élément à la fin d'une liste en Python?",
                        "options": [
                            "insert()",
                            "add()",
                            "append()",
                            "extend()"
                        ],
                        "answer": "append()",
                        "explanation": "La méthode 'append()' ajoute un élément à la fin de la liste."
                    },
                    {
                        "question": "Quelle méthode est utilisée pour supprimer un élément d'une liste en connaissant sa valeur?",
                        "options": [
                            "pop()",
                            "remove()",
                            "delete()",
                            "discard()"
                        ],
                        "answer": "remove()",
                        "explanation": "La méthode 'remove()' supprime la première occurrence de la valeur spécifiée dans la liste."
                    },
                    {
                        "question": "Comment ouvrir un fichier en mode lecture en Python en s'assurant qu'il soit fermé après utilisation?",
                        "options": [
                            "file = open('fichier.txt', 'r'); file.close()",
                            "open('fichier.txt', 'r').close()",
                            """with open('fichier.txt', 'r') as file:""",
                            "open('fichier.txt', 'r')"
                        ],
                        "answer": "with open('fichier.txt', 'r') as file:",
                        "explanation": "L'instruction 'with open()' garantit que le fichier est correctement fermé après utilisation, même en cas d'erreur."
                    },
                    {
                        "question": "Quel est le rôle du mode 'w' lors de l'ouverture d'un fichier en Python?",
                        "options": [
                            "Ouvrir le fichier en mode lecture.",
                            "Ouvrir le fichier en mode ajout.",
                            "Ouvrir le fichier en mode écriture, en écrasant le contenu existant.",
                            "Ouvrir le fichier en mode binaire."
                        ],
                        "answer": "Ouvrir le fichier en mode écriture, en écrasant le contenu existant.",
                        "explanation": "Le mode 'w' ouvre le fichier en mode écriture. Si le fichier existe, son contenu est écrasé. S'il n'existe pas, un nouveau fichier est créé."
                    },
                    {
                        "question": "Quelle méthode de chaîne de caractères permet de supprimer les espaces au début et à la fin d'une chaîne?",
                        "options": [
                            "trim()",
                            "strip()",
                            "clean()",
                            "remove()"
                        ],
                        "answer": "strip()",
                        "explanation": "La méthode 'strip()' supprime les espaces (ou d'autres caractères spécifiés) au début et à la fin d'une chaîne de caractères."
                    },
                    {
                        "question": "Quelle est la différence entre `append()` et `extend()` pour les listes?",
                        "options": [
                            "`append()` ajoute un seul élément à la fin de la liste, tandis que `extend()` ajoute plusieurs éléments à la fois.",
                            "`append()` ajoute tous les éléments d'une autre liste à la fin, tandis que `extend()` ajoute un seul élément.",
                            "`append()` et `extend()` font la même chose.",
                            "`append()` ne fonctionne qu'avec des nombres, tandis que `extend()` fonctionne avec n'importe quel type de données."
                        ],
                        "answer": "`append()` ajoute un seul élément à la fin de la liste, tandis que `extend()` ajoute plusieurs éléments à la fois.",
                        "explanation": "`append()` ajoute l'élément tel quel à la fin de la liste, tandis que `extend()` prend un itérable (comme une autre liste) et ajoute chaque élément de cet itérable à la fin de la liste."
                    }
                ]
            }
        }

    elif action == "mind-map":
        return {
            "type": "json",
            "content": {
                "title": "Python",
                "nodes": [
                    {
                        "title": "Fonctions",
                        "children": [
                            {
                                "title": "Définition (def)"
                            },
                            {
                                "title": "Appel"
                            },
                            {
                                "title": "Paramètres (positionnels, nommés, défaut)"
                            },
                            {
                                "title": "Valeur de retour (return)"
                            },
                            {
                                "title": "Lambda (anonymes)"
                            }
                        ]
                    },
                    {
                        "title": "Chaînes (Strings)",
                        "children": [
                            {
                                "title": "Opérations (concat, slice)"
                            },
                            {
                                "title": "Méthodes (upper, lower, strip, split, join, find, replace)"
                            },
                            {
                                "title": "Formatage (f-strings)"
                            }
                        ]
                    },
                    {
                        "title": "Listes (Lists)",
                        "children": [
                            {
                                "title": "Création, accès, modification"
                            },
                            {
                                "title": "Méthodes (append, insert, pop, remove, sort, reverse, len, count, index)"
                            },
                            {
                                "title": "Boucles et compréhensions"
                            }
                        ]
                    },
                    {
                        "title": "Fichiers",
                        "children": [
                            {
                                "title": "Lecture (open 'r', read, readline, readlines)"
                            },
                            {
                                "title": "Écriture (open 'w'/'a', write, writelines)"
                            },
                            {
                                "title": "Gestionnaire de contexte (with)"
                            }
                        ]
                    }
                ]
            }
        }
