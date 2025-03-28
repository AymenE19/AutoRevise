import os
import subprocess
from pathlib import Path
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

# Get DOWNLOAD_PATH from environment variables
DOWNLOAD_PATH = os.getenv("DOWNLOAD_PATH")


def test_marker_on_single_pdf():
    # Find the first PDF in the DOWNLOAD_PATH
    pdf_files = []
    for root, _, files in os.walk(DOWNLOAD_PATH):
        for file in files:
            if file.lower().endswith('.pdf'):
                pdf_files.append(os.path.join(root, file))
                break
        if pdf_files:
            break

    if not pdf_files:
        print(f"No PDF files found in {DOWNLOAD_PATH}")
        return

    pdf_path = pdf_files[0]
    print(f"Testing marker_single on: {pdf_path}")

    # Create output directory
    output_dir = os.path.join(os.path.dirname(pdf_path), "marker_test_output")
    os.makedirs(output_dir, exist_ok=True)

    # Run marker_single without a timeout
    try:
        marker_cmd = ["marker_single", pdf_path, "--output_format", "markdown", "--output_dir", output_dir]
        print(f"Executing: {' '.join(marker_cmd)}")

        # Run the command without timeout
        result = subprocess.run(marker_cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print("Success! Marker processed the PDF correctly.")
            output_file = os.path.join(output_dir, f"{Path(pdf_path).stem}.md")

            if os.path.exists(output_file):
                print(f"Output file created: {output_file}")
                print("\nPreview of the first 500 characters:")
                with open(output_file, 'r', encoding='utf-8') as f:
                    preview = f.read(500)
                print(preview + "...")
            else:
                print(f"Output file not found: {output_file}")
        else:
            print(f"Error: {result.stderr}")

    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    test_marker_on_single_pdf()