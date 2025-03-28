import os
import requests
import fitz
import json
from .marker_extractor import MarkerExtractor


def download_pdf(url, output_dir="temp_downloads"):
    """Download a PDF from a URL and save it to a temporary directory."""
    os.makedirs(output_dir, exist_ok=True)
    file_name = os.path.basename(url)
    file_path = os.path.join(output_dir, file_name)

    try:
        # Stream the PDF to disk in chunks (avoids loading the entire file into RAM)
        response = requests.get(url, stream=True)
        response.raise_for_status()

        with open(file_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:  # Filter out keep-alive chunks
                    f.write(chunk)

        print(f"PDF temporarily downloaded: {file_path}")
        return file_path

    except Exception as e:
        print(f"Download failed: {e}")
        return None


def extract_text_from_pdf(pdf_path, use_marker=False, output_format="markdown", keep_pdf=False):
    """
    Extract text and potentially images from a PDF file.

    Args:
        pdf_path (str): Path to the PDF file
        use_marker (bool): Whether to use Marker for better extraction with formatting
        output_format (str): When using marker, format to extract to ("markdown", "html", "json")
        keep_pdf (bool): Whether to keep the PDF after extraction

    Returns:
        dict: Content and metadata from the PDF
    """
    try:
        result = {}

        if use_marker:
            # Use Marker for enhanced extraction with images and formatting
            marker = MarkerExtractor()

            # Extract to requested format
            content, img_dir = marker.extract_with_format(
                pdf_path,
                output_format=output_format,
                output_dir=os.path.dirname(pdf_path)
            )

            result = {
                "content": content,
                "format": output_format,
                "has_images": os.path.exists(img_dir) and len(os.listdir(img_dir)) > 0,
                "images_dir": img_dir if os.path.exists(img_dir) and len(os.listdir(img_dir)) > 0 else None
            }

            # If content is JSON, ensure it's returned as a Python dict
            if output_format.lower() == "json" and isinstance(content, str):
                try:
                    result["content"] = json.loads(content)
                except json.JSONDecodeError:
                    pass  # Leave as string if not valid JSON
        else:
            # Use original PyMuPDF extraction (text only)
            doc = fitz.open(pdf_path)
            text = ""
            for page in doc:
                text += page.get_text()

            result = {
                "content": text,
                "format": "text",
                "has_images": False,
                "images_dir": None
            }

        print("Content extracted successfully.")
        return result

    except Exception as e:
        print(f"Extraction failed: {e}")
        return {"content": None, "error": str(e)}

    finally:
        # Clean up: Delete the PDF after extraction to save disk space, unless keep_pdf is True
        if not keep_pdf and os.path.exists(pdf_path):
            os.remove(pdf_path)
            print(f"Deleted temporary PDF: {pdf_path}")