import json

import httpx
from fastapi import FastAPI
from google.genai import types

from generating.settings import ALLOWED_USER_ACTIONS, GEMINI_MODEL_NAME


def build_prompt(action: str, title: str, content: str) -> str:
    match action:
        case "summary":
            return f"""
                Tu es un assistant pédagogique. Je vais te fournir le contenu brut d'une séance intitulée : "{title}".
                
                Le texte peut contenir des lignes vides ou inutiles. Voici ce que tu dois faire :
                1. Ignore les lignes vides ou non informatives.
                2. Organise le contenu par titres (déjà marqués avec ###).
                3. Résume le contenu de façon claire et structurée, en français.
                4. Le résumé doit être utile pour un étudiant souhaitant réviser rapidement cette séance.
                
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
                                
                    Voici le contenu:
                    {content}"
                """
            )

        case _:
            raise ValueError("Action non supportée.")


def build_response(action: str, content: str):
    match action:
        case "summary":
            return {
                "type": "markdown", "content": content
            }
        case "mindmap" | "quiz":
            try:
                return {"type": "json", "content": json.loads(content)}
            except json.JSONDecodeError:
                return {"error": "La réponse du modèle n'est pas un JSON valide.", "raw": content}


def process_user_action(app: FastAPI, action: str, collection: str, session: str) -> dict:
    if action not in ALLOWED_USER_ACTIONS:
        return {"error": "Action non supportée."}

    app.state.db.select_topic(collection)

    print("pass")
    session_data = app.state.db.find_session_by_name(session)
    if session_data is None:
        return {"error": "Session non existant."}

    constructed_prompt = build_prompt(action, session_data["session_title"], session_data["markdown_content"])

    try:
        response = app.state.gemini_client.models.generate_content(
            model=GEMINI_MODEL_NAME,
            contents=constructed_prompt,
            config=types.GenerateContentConfig(
                max_output_tokens=1000,
                temperature=0.2
            )
        )

        if not response.text:
            return {"error": "Réponse vide du modèle."}

        return build_response(action, response.text)

    except httpx.HTTPStatusError as e:
        return {"error": f"Erreur HTTP: {e.response.status_code} - {e.response.text}"}
    except httpx.RequestError as e:
        return {"error": f"Erreur de requête: {str(e)}"}
    except Exception as e:
        return {"error": f"Erreur inattendue: {str(e)}"}
