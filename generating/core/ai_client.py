import os
import httpx
from typing import Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
import json

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
MONGO_URL = os.getenv("MONGODB_URI")
DB_NAME = "MONGODB_DB_NAME"
COLLECTION_NAME = "your_collection_name"

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]
sessions = db[COLLECTION_NAME]


PROMPTS = {
    "summary": lambda title, content: f"""
Tu es un assistant pédagogique. Je vais te fournir le contenu brut d'une séance intitulée : "{title}".

Le texte peut contenir des lignes vides ou inutiles. Voici ce que tu dois faire :
1. Ignore les lignes vides ou non informatives.
2. Organise le contenu par titres (déjà marqués avec ###).
3. Résume le contenu de façon claire et structurée, en français.
4. Le résumé doit être utile pour un étudiant souhaitant réviser rapidement cette séance.

⛔️ Retourne uniquement le Markdown. Aucun autre texte.
Voici le contenu :
\n\n{content}
""",

    "mindmap": lambda title, content: f"""
Tu es un assistant pédagogique. Je vais te fournir le contenu brut d'une séance intitulée : "{title}".

Je veux que tu génères une **carte mentale** (mind map) à partir de ce contenu.

👉 Format de sortie : JSON.
Structure demandée :
{{
  "title": "Titre de la séance",
  "nodes": [
    {{
      "title": "Titre principal",
      "children": [
        {{"title": "Sous-concept 1"}},
        {{"title": "Sous-concept 2"}}
      ]
    }}
  ]
}}

➡️ Consignes :
- Résume de manière hiérarchique et claire.
- Utilise les titres marqués avec `###` comme racines principales.
- Évite les détails inutiles.
- Utilise un JSON bien formé, sans texte ou explication autour.

Voici le contenu :
\n\n{content}
""",

    "quiz": lambda title, content: f"""
Tu es un assistant pédagogique. Je vais te fournir le contenu brut d'une séance intitulée : "{title}".

Je veux que tu crées un **quiz avec solutions** basé sur ce contenu.

🎯 Format de sortie : JSON uniquement, bien structuré.
Structure demandée :
{{
  "title": "Titre de la séance",
  "questions": [
    {{
      "question": "Quel est le rôle du DNS dans Internet ?",
      "options": [
        "Il stocke les fichiers HTML.",
        "Il convertit les noms de domaine en adresses IP.",
        "Il crypte les communications HTTPS.",
        "Il héberge les bases de données."
      ],
      "answer": "Il convertit les noms de domaine en adresses IP.",
      "explanation": "Le DNS fait correspondre les noms de domaine avec leurs adresses IP respectives."
    }}
  ]
}}

📌 Consignes :
- Génére entre 5 à 10 questions maximum.
- Chaque question doit avoir 4 propositions.
- Une seule réponse correcte par question.
- Ajoute une explication claire et concise pour chaque réponse.
- Le JSON ne doit pas être entouré de texte ni de commentaire.

Voici le contenu :
\n\n{content}
"""
}

# 🔄 Fonction principale
async def process_session_action(session_name: str, action: str) -> Dict[str, Any]:
    if action not in PROMPTS:
        return {"error": f"Action '{action}' non supportée. Choisir parmi {list(PROMPTS.keys())}"}

    # 📦 1. Récupérer la session depuis MongoDB
    session_data = await sessions.find_one({"session_title": session_name})
    if not session_data:
        return {"error": f"Aucune session trouvée avec le titre '{session_name}'."}

    # 📃 2. Extraire le markdown_content
    markdown_blocks = session_data.get("markdown_content", [])
    content = "\n\n".join(markdown_blocks)

    # 🧠 3. Construire le prompt
    prompt = PROMPTS[action](session_name, content)

    # 📤 4. Envoyer le prompt à Gemini
    headers = {
        "Content-Type": "application/json"
    }
    params = {
        "key": GEMINI_API_KEY
    }
    payload = {
        "prompt": {"text": prompt},
        "temperature": 0.7,
        "maxOutputTokens": 1000,
        "candidateCount": 1,
    }

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(GEMINI_API_URL, headers=headers, params=params, json=payload)
            response.raise_for_status()
            data = response.json()

        candidates = data.get("candidates")
        if not candidates:
            return {"error": "Aucune réponse générée par le modèle."}

        result_text = candidates[0].get("output", "").strip()
        if not result_text:
            return {"error": "Réponse vide du modèle."}

        # 🧾 5. Formater la réponse selon l'action
        if action == "summary":
            return {"type": "markdown", "content": result_text}
        elif action in {"mindmap", "quiz"}:
            try:
                parsed_json = json.loads(result_text)
                return {"type": "json", "content": parsed_json}
            except json.JSONDecodeError:
                return {"error": "La réponse du modèle n'est pas un JSON valide.", "raw": result_text}

    except httpx.HTTPStatusError as e:
        return {"error": f"Erreur HTTP: {e.response.status_code} - {e.response.text}"}
    except httpx.RequestError as e:
        return {"error": f"Erreur de requête: {str(e)}"}
    except Exception as e:
        return {"error": f"Erreur inattendue: {str(e)}"}


async def main():
    print("Test Gemini + MongoDB session processing")
    session_name = input("Entrez le titre de la session (ex: Control Structures): ").strip()
    action = input("Entrez l'action à effectuer (summary, mindmap, quiz): ").strip().lower()

    result = await process_session_action(session_name, action)
    if "error" in result:
        print(f"Erreur: {result['error']}")
        if "raw" in result:
            print(f"Réponse brute:\n{result['raw']}")
    else:
        print(f"Résultat ({result['type']}):")
        if result['type'] == "markdown":
            print(result['content'])
        elif result['type'] == "json":
            print(json.dumps(result['content'], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(main())
