import os
import json
import markdown
from bs4 import BeautifulSoup
import google.generativeai as genai
import re

# --- PART 1: Markdown Extraction ---

def extract_nested_headings(markdown_text):
    lines = markdown_text.splitlines()
    in_code_block = False
    valid_lines = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            continue
        if not in_code_block:
            valid_lines.append(stripped)

    html = markdown.markdown('\n'.join(valid_lines))
    soup = BeautifulSoup(html, 'html.parser')

    structure = {}
    current_main = None
    current_sub = None

    for tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
        level = int(tag.name[1])
        text = tag.get_text(strip=True)
        if not text:
            continue

        if level == 1:
            current_main = f"🔹 {text}"
            structure[current_main] = {}
            current_sub = None

        elif level == 2 and current_main:
            current_sub = f"🔸 {text}"
            structure[current_main][current_sub] = []

        elif level >= 3 and current_main and current_sub:
            structure[current_main][current_sub].append(f"🔻 {text}")

    return structure

def process_markdown_directory(directory_path):
    output = {"marker_output_python": []}

    if not os.path.exists(directory_path):
        print(f"❌ Error: Directory does not exist -> {directory_path}")
        return output

    for filename in os.listdir(directory_path):
        if filename.endswith(".md"):
            filepath = os.path.join(directory_path, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                markdown_text = f.read()
                headings = extract_nested_headings(markdown_text)
                if headings:
                    output["marker_output_python"].append({f"📄 {filename}": headings})

    return output

# --- PART 2: Send to Gemini ---

def send_structure_to_gemini(input_json_path, output_json_path):
    # Load structured data
    with open(input_json_path, 'r', encoding='utf-8') as f:
        structure = json.load(f)

    # Prompt setup
    prompt = f"""Voici la structure d’un document Markdown analysé en JSON. Je souhaite que tu regroupes chaque partie (🔹, 🔸 et 🔻) sous l'une des cinq séances suivantes, en fonction du contenu traité dans le titre. Utilise les mots-clés associés à chaque séance pour effectuer un regroupement intelligent et pertinent. Si un titre semble correspondre à plusieurs séances, choisis celle qui semble la plus dominante.
    Si une partie ne correspond à aucune séance (par exemple : Avant-propos, Remerciements, Présentation du livre, etc.), place-la dans une section à part nommée "🟤 Autres".

    En plus du regroupement, je veux aussi que tu me donnes le **nom du document** si tu peux le déduire d’après la structure (par exemple à partir des premières sections comme couverture, titre, etc.).

    Voici les séances avec des mots-clés pour t'aider :
    🟠 Séance 1 : Introduction à Python, installation, types, variables, boucles  
    Mots-clés : Python, introduction, présentation, installation, Anaconda, Miniconda, VS Code, Jupyter, types de données, entiers, flottants, chaînes, booléens, variables, assignation, opérateurs, comparaison, arithmétique, logique, conditions, if, else, boucles, while, for, shell, terminal, premier programme, script, print  
    🟠 Séance 2 : Fonctions et manipulation des données  
    Mots-clés : fonction, def, return, appel, paramètres, valeurs de retour, chaînes de caractères, string, concaténation, méthodes, slicing, listes, append, remove, split, input, fichier, ouverture, lecture, écriture, read, write, open, with, chemin, txt  
    🟠 Séance 3 : Structures de données et algorithmes fondamentaux  
    Mots-clés : liste, dictionnaire, dict, clés, valeurs, boucle sur dictionnaire, parcours, itération, tri, trier, tri à bulles, tri rapide, sort, recherche, linéaire, dichotomique, binary search, complexité, optimisation, efficacité, algorithme  
    🟠 Séance 4 : Programmation orientée objet (POO)  
    Mots-clés : classe, objet, POO, object oriented, init, constructeur, méthode, attribut, self, héritage, inheritance, polymorphisme, encapsulation, instance, exception, try, except, gestion des erreurs, raise, erreur  
    🟠 Séance 5 : Bases de données, SQLite, APIs  
    Mots-clés : SQLite, base de données, requête, insert, select, cursor, connexion, table, SQL, interroger, API, HTTP, GET, POST, requêtes, json, REST, fetch, communication, endpoint  
    🟤 Autres : Tout ce qui ne correspond pas aux mots-clés précédents ou qui relève de l’introduction, avant-propos, remerciements, information générale, ou annexes.

    ⚡ IMPORTANT :
    - Donne ta réponse en JSON strictement valide.
    - Ne mets pas de texte avant ou après.
    - Juste un seul objet JSON final.
    - Structure du JSON attendu :
       {{
      "🟠 Séance X : nom de la séance": [
        {{
          "📄 nom_du_document.md": {{
            "🔹 Titre 1": {{}},
            "🔹 Titre 2": {{}},
            ...
          }}
        }},
        ...
      ],
      ...
    }}
    Here is the structure:
    {json.dumps(structure, indent=2, ensure_ascii=False)}

    Give a summarized or enriched output if needed.
    """


    # Configure Gemini
    genai.configure(api_key="AIzaSyC_do7KMqoHBbGKxMGws4fRjw0ViJl2LrU")
    model = genai.GenerativeModel('gemini-2.5-pro-exp-03-25')

    # Generate
    # response = model.generate_content(prompt)
    # generated_text = response.text.strip()
    #
    # # Try parsing JSON
    # try:
    #     generated_json = json.loads(generated_text)
    # except json.JSONDecodeError as e:
    #     print("❌ Failed to parse Gemini output as JSON!")
    #     print(f"Error: {e}")
    #     print("Generated text:\n", generated_text)
    #     else:
    #     try:
    #         # Clean and extract the actual JSON inside any code block
    #         fixed_text = generated_text.strip()
    #
    #         # If Gemini put ```json or ``` at the start
    #         if fixed_text.startswith("```json"):
    #             fixed_text = fixed_text[len("```json"):].strip()
    #         elif fixed_text.startswith("```"):
    #             fixed_text = fixed_text[len("```"):].strip()
    #
    #         # If Gemini put ``` at the end
    #         if fixed_text.endswith("```"):
    #             fixed_text = fixed_text[:-len("```")].strip()
    #
    #         # Now parse it safely
    #         data = json.loads(fixed_text)
    #
    #         with open(output_json_path, 'w', encoding='utf-8') as f:
    #             json.dump(data, f, ensure_ascii=False, indent=2)
    #         print("✅ Gemini response cleaned and saved as valid JSON.")
    #
    #     except json.JSONDecodeError as e:
    #         with open(output_json_path, 'w', encoding='utf-8') as f:
    #             f.write(generated_text)
    #         print("⚠️ Gemini response was not valid JSON even after cleaning, saved as text.")
    #         print(f"Error details: {e}")
    #
    # # except json.JSONDecodeError:
    # #     generated_json = None
    #
    # if generated_json:
    #     with open(output_json_path, 'w', encoding='utf-8') as f:
    #         json.dump(generated_json, f, indent=2, ensure_ascii=False)
    #     print("✅ Gemini response saved as JSON.")
    # else:
    #     # try:
    #     #     # 1. Remove code block markers using regex
    #     #     fixed_text = re.sub(r'^```json\s*|\s*```$', '', generated_text.strip(), flags=re.MULTILINE).strip()
    #     #
    #     #     # 2. Parse as JSON
    #     #     data = json.loads(fixed_text)
    #     #
    #     #     # 3. Save JSON
    #     #     with open(output_json_path, 'w', encoding='utf-8') as f:
    #     #         json.dump(data, f, ensure_ascii=False, indent=2)
    #     #     print("✅ Gemini response cleaned and saved as valid JSON.")
    #     #
    #     # except json.JSONDecodeError as e:
    #     #     with open(output_json_path, 'w', encoding='utf-8') as f:
    #     #         f.write(generated_text)
    #     #     print("⚠️ Gemini response was not valid JSON even after cleaning, saved as text.")
    #     #     print(f"Error details: {e}")
    #     # Save the raw text (even if it has ```json ... ```)
    #     with open(output_json_path, 'w', encoding='utf-8') as f:
    #         f.write(generated_text)
    #     print("📝 Saved Gemini raw output as text file.")
    #
    # print("\n--- Gemini Output Preview ---\n")
    # print(generated_text)
    # print("\n------------------------------\n")

    # Generate
    response = model.generate_content(prompt)
    generated_text = response.text.strip()

    # Initialize
    generated_json = None

    # Try parsing JSON
    try:
        generated_json = json.loads(generated_text)
    except json.JSONDecodeError as e:
        print("❌ Failed to parse Gemini output as JSON!")
        print(f"Error: {e}")
        print("Generated text:\n", generated_text)

        # Try to clean the text and parse again
        try:
            # Clean and extract the actual JSON inside any code block
            fixed_text = generated_text.strip()

            # If Gemini put ```json or ``` at the start
            if fixed_text.startswith("```json"):
                fixed_text = fixed_text[len("```json"):].strip()
            elif fixed_text.startswith("```"):
                fixed_text = fixed_text[len("```"):].strip()

            # If Gemini put ``` at the end
            if fixed_text.endswith("```"):
                fixed_text = fixed_text[:-len("```")].strip()

            # Now parse it safely
            generated_json = json.loads(fixed_text)

            print("✅ Gemini response cleaned and saved as valid JSON.")

        except json.JSONDecodeError as e:
            print("⚠️ Gemini response was not valid JSON even after cleaning.")
            print(f"Error details: {e}")

    # Now check if generated_json is ready
    if generated_json:
        with open(output_json_path, 'w', encoding='utf-8') as f:
            json.dump(generated_json, f, indent=2, ensure_ascii=False)
        print("✅ Gemini response saved as JSON.")
    else:
        # Save the raw text if JSON failed
        with open(output_json_path, 'w', encoding='utf-8') as f:
            f.write(generated_text)
        print("📝 Saved Gemini raw output as text file.")

    print("\n--- Gemini Output Preview ---\n")
    print(generated_text)
    print("\n------------------------------\n")


def clean_gemini_text(raw_text):
    """Clean Gemini output: remove ```json and ``` markers and parse as JSON."""
    # Step 1: Remove the ```json ... ``` markers
    cleaned_text = re.sub(r'^```json\s*', '', raw_text.strip(), flags=re.MULTILINE)
    cleaned_text = re.sub(r'\s*```$', '', cleaned_text.strip(), flags=re.MULTILINE)

    # Step 2: Parse cleaned text as JSON
    try:
        parsed_json = json.loads(cleaned_text)
        return parsed_json
    except json.JSONDecodeError as e:
        print("❌ Failed to parse cleaned text as JSON!")
        print(f"Error: {e}")
        return None


# --- PART 3: Enrich the JSON with real Markdown Content ---

def extract_content_from_markdown(filepath, needed_titles):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    content_map = {}
    current_title = None
    buffer = []

    needed_titles_set = set(needed_titles)

    def save():
        if current_title and buffer:
            content_map[current_title] = "\n".join(buffer).strip()

    for line in lines:
        line = line.rstrip()
        if line.startswith("#"):
            save()
            clean_title = line.lstrip("#").strip()
            marker = f"{'🔹' if line.startswith('# ') else '🔸' if line.startswith('## ') else '🔻'} {clean_title}"
            if marker in needed_titles_set:
                current_title = marker
                buffer = []
            else:
                current_title = None
                buffer = []
        else:
            if current_title is not None:
                buffer.append(line)
    save()
    return content_map

def enrich_json_with_markdown_only_titles(json_path, markdown_folder):
    with open(json_path, 'r', encoding='utf-8') as f:
        structure = json.load(f)

    enriched = {}

    for séance, files in structure.items():
        enriched[séance] = []
        for file_obj in files:
            for filename, headings in file_obj.items():
                real_filename = filename.replace("📄 ", "")
                file_path = os.path.join(markdown_folder, real_filename)

                if not os.path.exists(file_path):
                    continue

                needed_titles = []
                for h1, h2s in headings.items():
                    needed_titles.append(h1)
                    if isinstance(h2s, dict):
                        for h2, h3s in h2s.items():
                            needed_titles.append(h2)
                            if isinstance(h3s, list):
                                needed_titles.extend(h3s)

                extracted_content = extract_content_from_markdown(file_path, needed_titles)

                enriched_file = {}
                for h1, h2s in headings.items():
                    enriched_h1 = {}
                    if isinstance(h2s, dict):
                        for h2, h3s in h2s.items():
                            if isinstance(h3s, list):
                                enriched_h2 = []
                                for h3 in h3s:
                                    enriched_h2.append({h3: extracted_content.get(h3, "")})
                                enriched_h1[h2] = enriched_h2
                            else:
                                enriched_h1[h2] = extracted_content.get(h2, "")
                    enriched_h1["🔹_content"] = extracted_content.get(h1, "")
                    enriched_file[h1] = enriched_h1
                enriched[séance].append({filename: enriched_file})

    return enriched

# --- MAIN PROGRAM ---

def main():
    # CONFIG paths
    markdown_folder_path = r"C:\Users\OUSSAMA MDJ\Downloads\marker_output_python"
    extracted_structure_json_path = r"C:\Users\OUSSAMA MDJ\Downloads\structure.json"
    gemini_output_path = r"C:\Users\OUSSAMA MDJ\Downloads\intilaform.txt"
    enriched_output_path = r"C:\Users\OUSSAMA MDJ\Downloads\enriched_output.json"

    # STEP 1 - Extract headings structure
    print("\n🛠️ Extracting structure from markdown files...")
    structure = process_markdown_directory(markdown_folder_path)
    with open(extracted_structure_json_path, "w", encoding="utf-8") as f:
        json.dump(structure, f, indent=2, ensure_ascii=False)
    print("✅ Structure extraction completed.")

    # STEP 2 - Send structure to Gemini
    print("\n🤖 Sending structure to Gemini for categorization...")
    send_structure_to_gemini(extracted_structure_json_path, gemini_output_path)

    # STEP 3 - Enrich categorized structure with markdown content
    print("\n🛠️ Enriching Gemini output with real markdown content...")
    result = enrich_json_with_markdown_only_titles(gemini_output_path, markdown_folder_path)

    # Save enriched result
    with open(enriched_output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print("✅ Enrichment complete. Output saved to:", enriched_output_path)

    print("\n🎯 All steps completed successfully!")

if __name__ == "__main__":
    main()
