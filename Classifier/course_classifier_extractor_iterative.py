import google.generativeai as genai
import os
import pathlib
import re
from typing import Dict, Optional  # For type hinting

# --- Configuration ---
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    print("ERROR: The GEMINI_API_KEY environment variable is not set.")
    # ... (error messages) ...
    exit()

genai.configure(api_key=API_KEY)
print("Gemini API configured using the provided key.")

# Consider 'gemini-1.5-pro-latest' for stability with complex tasks if preview gives issues
MODEL_NAME = 'gemini-2.5-pro-preview-05-06'  # Or 'gemini-2.5-pro-preview-05-06' if it's proven stable
model = genai.GenerativeModel(MODEL_NAME)
print(f"Using model: {MODEL_NAME}")

STANDARD_SYLLABUS = """
- Seance 1: Introduction à Python, Présentation de Python et installation de l’environnement (Anaconda, VS Code, Jupyter Notebook), Variables et types de données (entiers, flottants, chaines, booleens), Operateurs arithmetiques, logiques et de comparaison, Structures de controle : conditions (if-else) et boucles (for, while).
- Seance 2: Fonctions et Manipulation des Donnees, Definition et utilisation des fonctions (def, return), Passage de parametres et valeurs de retour, Manipulation des chaines de caracteres et operations sur les listes, Lecture et ecriture dans des fichiers.
- Seance 3: Structures de Donnees et Algorithmes Fondamentaux, Listes et dictionnaires : creation, modification et parcours, Tri et recherche : tri a bulles, tri rapide, recherche lineaire et dichotomique, Complexite algorithmique et optimisation des boucles.
- Seance 4: Programmation Orientee Objet (POO), Definition des classes et des objets, Constructeur (init) et methodes speciales, Heritage et polymorphisme, Gestion des exceptions avec try-except.
- Seance 5: Introduction aux bases de donnees avec SQLite, Interaction avec des APIs et requetes HTTP.
"""

# Define the sections we want to extract iteratively
# file_key: the key used for filenames and in the final parsed_data dictionary
# response_tag_key: the base key for <TAG_START> and <TAG_END> delimiters
# human_readable_name: for prompts and logging
# specific_instructions: unique part of the prompt for this section
SECTIONS_TO_EXTRACT = [
    {
        "file_key": "Nom_du_Cours",
        "response_tag_key": "NOM_DU_COURS",
        "human_readable_name": "le nom du cours",
        "specific_instructions": "Déduis le nom ou titre principal du cours à partir du contenu fourni. Si aucun titre clair n'est identifiable, indique 'Titre de Cours Inconnu'.",
        "syllabus_context_needed": False  # Does this extraction depend on the main syllabus?
    },
    {
        "file_key": "Seance_1_Contenu",
        "response_tag_key": "SEANCE_1_TEXT",
        "human_readable_name": "le contenu de la Séance 1",
        "specific_instructions": "Extrais UNIQUEMENT les portions de texte exactes du CONTENU DU COURS PYTHON qui correspondent aux sujets de la Séance 1 du SYLLABUS STANDARD. Si aucun contenu ne correspond, écris seulement : Contenu Non Couvert pour Seance 1.",
        "syllabus_context_needed": True
    },
    {
        "file_key": "Seance_2_Contenu",
        "response_tag_key": "SEANCE_2_TEXT",
        "human_readable_name": "le contenu de la Séance 2",
        "specific_instructions": "Extrais UNIQUEMENT les portions de texte exactes du CONTENU DU COURS PYTHON qui correspondent aux sujets de la Séance 2 du SYLLABUS STANDARD. Si aucun contenu ne correspond, écris seulement : Contenu Non Couvert pour Seance 2.",
        "syllabus_context_needed": True
    },
    {
        "file_key": "Seance_3_Contenu",
        "response_tag_key": "SEANCE_3_TEXT",
        "human_readable_name": "le contenu de la Séance 3",
        "specific_instructions": "Extrais UNIQUEMENT les portions de texte exactes du CONTENU DU COURS PYTHON qui correspondent aux sujets de la Séance 3 du SYLLABUS STANDARD. Si aucun contenu ne correspond, écris seulement : Contenu Non Couvert pour Seance 3.",
        "syllabus_context_needed": True
    },
    {
        "file_key": "Seance_4_Contenu",
        "response_tag_key": "SEANCE_4_TEXT",
        "human_readable_name": "le contenu de la Séance 4",
        "specific_instructions": "Extrais UNIQUEMENT les portions de texte exactes du CONTENU DU COURS PYTHON qui correspondent aux sujets de la Séance 4 du SYLLABUS STANDARD. Si aucun contenu ne correspond, écris seulement : Contenu Non Couvert pour Seance 4.",
        "syllabus_context_needed": True
    },
    {
        "file_key": "Seance_5_Contenu",
        "response_tag_key": "SEANCE_5_TEXT",
        "human_readable_name": "le contenu de la Séance 5",
        "specific_instructions": "Extrais UNIQUEMENT les portions de texte exactes du CONTENU DU COURS PYTHON qui correspondent aux sujets de la Séance 5 du SYLLABUS STANDARD. Si aucun contenu ne correspond, écris seulement : Contenu Non Couvert pour Seance 5.",
        "syllabus_context_needed": True
    },
    {
        "file_key": "Autres_Sujets_Contenu",
        "response_tag_key": "AUTRES_SUJETS_TEXT",
        "human_readable_name": "le contenu des autres sujets pertinents",
        "specific_instructions": "Extrais UNIQUEMENT les portions de texte exactes du CONTENU DU COURS PYTHON qui ne correspondent à AUCUNE des 5 séances standard mais qui sont néanmoins pertinentes pour le cours. Si aucun contenu de ce type n'est identifié, écris seulement : Aucun autre sujet pertinent identifié.",
        "syllabus_context_needed": True  # Still needs to know what the 5 seances ARE to exclude them
    }
]

# Base prompt template for extracting a single section
SINGLE_SECTION_PROMPT_TEMPLATE = """
Tu es un analyste expert de cursus Python et un extracteur de contenu ultra-précis.
Ta tâche est d'analyser le CONTENU DU COURS PYTHON fourni ci-dessous et d'en extraire une section spécifique.

{syllabus_section_if_needed}

--- CONTENU DU COURS PYTHON COMPLET ---
{{course_content}}
--- FIN DU CONTENU DU COURS PYTHON COMPLET ---

Maintenant, concentre-toi et effectue UNIQUEMENT la tâche suivante :
{specific_instructions_for_section}

Fournis ta réponse PRÉCISÉMENT et UNIQUEMENT avec le contenu demandé, encadré par les délimiteurs suivants. N'ajoute RIEN avant le tag de début ni après le tag de fin.

<{response_tag_key}_START>
[Contenu extrait pour cette section spécifique]
</{response_tag_key}_END>

IMPORTANT (SUIS CES RÈGLES À LA LETTRE):
1.  Ta réponse DOIT commencer par le tag <{response_tag_key}_START> et RIEN d'autre avant.
2.  Ta réponse DOIT se terminer par le tag </{response_tag_key}_END> et RIEN d'autre après.
3.  Reproduis intégralement les portions de texte pertinentes du CONTENU DU COURS PYTHON telles qu'elles apparaissent dans le document original, y compris les titres de section et la mise en forme Markdown (comme les blocs de code avec `).
4.  NE PAS inclure de texte de résumé, d'introduction personnelle, de commentaires ou d'explications, sauf si c'est la phrase exacte demandée (par exemple, "Contenu Non Couvert...").
5.  Si tu ne trouves pas de contenu pour la section demandée selon les instructions, utilise la phrase spécifiée (par exemple, "Contenu Non Couvert pour Seance X.") entre les tags.
"""


def extract_single_section_with_llm(
        full_course_content: str,
        section_definition: Dict,
        course_filename_for_logging: str
) -> Optional[str]:
    """
    Calls the LLM to extract a single, specific section of the course.
    Returns the content *between* the specific start and end tags, or None on error/no content.
    """
    section_name = section_definition["human_readable_name"]
    tag_key = section_definition["response_tag_key"]

    print(f"\n--- Attempting to extract: {section_name} for {course_filename_for_logging} ---")

    syllabus_text_for_prompt = ""
    if section_definition["syllabus_context_needed"]:
        syllabus_text_for_prompt = f"Voici le SYLLABUS STANDARD DE 5 SÉANCES pour référence :\n{STANDARD_SYLLABUS}\n"

    prompt = SINGLE_SECTION_PROMPT_TEMPLATE.format(
        syllabus_section_if_needed=syllabus_text_for_prompt,
        course_content=full_course_content,
        specific_instructions_for_section=section_definition["specific_instructions"],
        response_tag_key=tag_key
    )

    try:
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            # ... other safety settings ...
        ]
        generation_config = genai.types.GenerationConfig(
            temperature=0.2,  # Low temperature for precise extraction
            max_output_tokens=65536  # Should be ample for a single section
        )
        request_options = {"timeout": 400.0}  # 5 min timeout per section; adjust if needed

        response = model.generate_content(
            prompt,
            generation_config=generation_config,
            safety_settings=safety_settings,
            request_options=request_options
        )

        raw_llm_response = "Error: No usable text in LLM response."
        if response.parts:
            raw_llm_response = "".join(part.text for part in response.parts)
        elif hasattr(response, 'text') and response.text:
            raw_llm_response = response.text
        elif response.candidates and response.candidates[0].content.parts:
            raw_llm_response = "".join(part.text for part in response.candidates[0].content.parts)
        else:
            print(f"  Warning: Could not extract text directly for {section_name}. Full response object: {response}")
            if response.prompt_feedback: print(f"  Prompt Feedback: {response.prompt_feedback}")
            return None

        raw_llm_response = raw_llm_response.strip()
        print(f"  Raw LLM response preview for {section_name} (first 100 chars): '{raw_llm_response[:100]}...'")

        # --- Strict Parsing for the single expected section ---
        start_tag = f"<{tag_key}_START>"
        end_tag = f"</{tag_key}_END>"

        if not raw_llm_response.startswith(start_tag):
            print(f"  ERROR: LLM response for {section_name} did not start with expected tag {start_tag}.")
            print(f"  Full LLM response was: {raw_llm_response}")  # Print full response on error
            return f"Erreur de formatage: Réponse LLM pour {section_name} ne commence pas par {start_tag}."

        if not raw_llm_response.endswith(end_tag):
            print(f"  ERROR: LLM response for {section_name} did not end with expected tag {end_tag}.")
            print(f"  Full LLM response was: {raw_llm_response}")  # Print full response on error
            return f"Erreur de formatage: Réponse LLM pour {section_name} ne finit pas par {end_tag}."

        # Extract content between the tags
        # Add len(start_tag) to start index, and use negative slicing for end_tag
        content_start_index = len(start_tag)
        content_end_index = -len(end_tag)

        extracted_content = raw_llm_response[content_start_index:content_end_index].strip()

        if not extracted_content:
            print(f"  Warning: Extracted content for {section_name} is empty after stripping tags.")
            # Return specific "not covered" messages if the LLM was supposed to provide them.
            # This check can be enhanced based on expected "empty" responses.
            if "Contenu Non Couvert" in extracted_content or "Aucun autre sujet pertinent identifié" in extracted_content:
                return extracted_content  # It correctly said it's not covered

        print(f"  Successfully extracted content for {section_name}.")
        return extracted_content

    except Exception as e:
        print(f"  An error occurred while calling LLM for {section_name}: {e}")
        if hasattr(e, 'response') and hasattr(e.response, 'prompt_feedback'):
            print(f"  Prompt Feedback: {e.response.prompt_feedback}")
        return f"Erreur API lors de l'extraction de {section_name}: {e}"


# --- Main Test Logic ---
if __name__ == "__main__":
    project_root = pathlib.Path(__file__).parent.resolve()
    course_file_to_test = project_root / "python9_clean.md"  # Your input course file

    if not course_file_to_test.exists():
        print(f"ERROR: Course file not found at {course_file_to_test}")
        exit()

    print(f"Reading course file: {course_file_to_test.name}")
    try:
        with open(course_file_to_test, "r", encoding="utf-8") as f:
            full_course_content = f.read()
        if not full_course_content.strip():
            print(f"ERROR: The course file '{course_file_to_test.name}' is empty.")
            exit()

        all_extracted_data = {}
        print("\nStarting iterative extraction process...")

        for section_def in SECTIONS_TO_EXTRACT:
            file_key = section_def["file_key"]
            extracted_content_for_section = extract_single_section_with_llm(
                full_course_content,
                section_def,
                course_file_to_test.name
            )
            if extracted_content_for_section is not None:
                all_extracted_data[file_key] = extracted_content_for_section
            else:
                # Handle cases where extraction failed or returned None definitively
                all_extracted_data[file_key] = f"Échec de l'extraction pour {file_key} ou contenu non applicable."
                print(f"  Extraction failed or no content for {file_key}, using placeholder.")

        print("\n--- All iterative extractions attempted. ---")

        # Create a dedicated output directory
        course_specific_output_dir_name = f"{course_file_to_test.stem}_iterative_extracted_content"
        course_output_dir = project_root / course_specific_output_dir_name
        course_output_dir.mkdir(parents=True, exist_ok=True)
        print(f"\nSaving extracted content to directory: {course_output_dir}")

        for file_key, content in all_extracted_data.items():
            output_file_path = course_output_dir / f"{file_key}.txt"  # Saving as .md
            try:
                with open(output_file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"  Successfully saved: {output_file_path.name}")
            except Exception as e:
                print(f"  Error saving {output_file_path.name}: {e}")

        print("\n--- Iterative extraction and saving process complete. ---")

    except Exception as e:
        print(f"An unexpected error occurred in the main process for {course_file_to_test.name}: {e}")

    print("\n--- Script finished. ---")