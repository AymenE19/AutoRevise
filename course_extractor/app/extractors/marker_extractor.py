import os
import subprocess
import json
from pathlib import Path
import tempfile


class MarkerExtractor:
    """
    Class for extracting content from PDFs using the Marker tool.
    Supports Markdown, HTML, and JSON outputs with image extraction.
    """

    def __init__(self, marker_path="marker"):
        """
        Initialize the MarkerExtractor.

        Args:
            marker_path (str): Path to the Marker binary or command name if in PATH
        """
        self.marker_path = marker_path

    def _check_marker_installed(self):
        """Check if Marker is installed and accessible."""
        try:
            result = subprocess.run([self.marker_path, "--version"],
                                    capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False

    def extract_to_markdown(self, pdf_path, output_dir=None):
        """
        Extract PDF content to Markdown format.

        Args:
            pdf_path (str): Path to the PDF file
            output_dir (str, optional): Directory to save output files. If None, uses a temp dir.

        Returns:
            tuple: (markdown_text, image_dir_path)
        """
        if not self._check_marker_installed():
            raise RuntimeError(
                "Marker is not installed or not found in PATH. Please install it from https://github.com/VikParuchuri/marker")

        use_temp = output_dir is None
        if use_temp:
            output_dir = tempfile.mkdtemp()
        else:
            os.makedirs(output_dir, exist_ok=True)

        pdf_name = Path(pdf_path).stem
        output_path = os.path.join(output_dir, f"{pdf_name}.md")
        img_dir = os.path.join(output_dir, f"{pdf_name}_images")

        # Run marker to extract PDF to markdown
        cmd = [
            self.marker_path,
            "-i", pdf_path,
            "-o", output_path,
            "--extract-images",
            "--image-dir", img_dir
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            raise RuntimeError(f"Marker extraction failed: {result.stderr}")

        # Read the markdown file
        with open(output_path, 'r', encoding='utf-8') as f:
            markdown_text = f.read()

        return markdown_text, img_dir

    def extract_to_html(self, pdf_path, output_dir=None):
        """
        Extract PDF content to HTML format.

        Args:
            pdf_path (str): Path to the PDF file
            output_dir (str, optional): Directory to save output files

        Returns:
            tuple: (html_text, image_dir_path)
        """
        if not self._check_marker_installed():
            raise RuntimeError("Marker is not installed or not found in PATH")

        use_temp = output_dir is None
        if use_temp:
            output_dir = tempfile.mkdtemp()
        else:
            os.makedirs(output_dir, exist_ok=True)

        pdf_name = Path(pdf_path).stem
        output_path = os.path.join(output_dir, f"{pdf_name}.html")
        img_dir = os.path.join(output_dir, f"{pdf_name}_images")

        # Run marker to extract PDF to HTML
        cmd = [
            self.marker_path,
            "-i", pdf_path,
            "-o", output_path,
            "--html",
            "--extract-images",
            "--image-dir", img_dir
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            raise RuntimeError(f"Marker extraction failed: {result.stderr}")

        # Read the HTML file
        with open(output_path, 'r', encoding='utf-8') as f:
            html_text = f.read()

        return html_text, img_dir

    def extract_to_json(self, pdf_path, output_dir=None):
        """
        Extract PDF content to JSON format with structure information.

        Args:
            pdf_path (str): Path to the PDF file
            output_dir (str, optional): Directory to save output files

        Returns:
            tuple: (json_data, image_dir_path)
        """
        if not self._check_marker_installed():
            raise RuntimeError("Marker is not installed or not found in PATH")

        use_temp = output_dir is None
        if use_temp:
            output_dir = tempfile.mkdtemp()
        else:
            os.makedirs(output_dir, exist_ok=True)

        pdf_name = Path(pdf_path).stem
        output_path = os.path.join(output_dir, f"{pdf_name}.json")
        img_dir = os.path.join(output_dir, f"{pdf_name}_images")

        # Run marker to extract PDF to JSON
        cmd = [
            self.marker_path,
            "-i", pdf_path,
            "-o", output_path,
            "--json",
            "--extract-images",
            "--image-dir", img_dir
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            raise RuntimeError(f"Marker extraction failed: {result.stderr}")

        # Read the JSON file
        with open(output_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)

        return json_data, img_dir

    def extract_with_format(self, pdf_path, output_format="markdown", output_dir=None):
        """
        Extract PDF content in the specified format.

        Args:
            pdf_path (str): Path to the PDF file
            output_format (str): One of "markdown", "html", or "json"
            output_dir (str, optional): Directory to save output files

        Returns:
            tuple: (content, image_dir_path)
        """
        if output_format.lower() == "markdown" or output_format.lower() == "md":
            return self.extract_to_markdown(pdf_path, output_dir)
        elif output_format.lower() == "html":
            return self.extract_to_html(pdf_path, output_dir)
        elif output_format.lower() == "json":
            return self.extract_to_json(pdf_path, output_dir)
        else:
            raise ValueError(f"Unsupported format: {output_format}. Use 'markdown', 'html', or 'json'.")