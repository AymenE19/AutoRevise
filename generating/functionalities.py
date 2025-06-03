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

        case "mindmap":
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
