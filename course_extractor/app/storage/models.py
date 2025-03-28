from datetime import datetime, UTC


class CourseDocument:
    def __init__(self, doc_id, file_name, file_path, file_type="pdf", title=None, url=None,
                 pages=None, views=None, content=None, content_format="text",
                 has_images=False, images_dir=None, tags=None):
        """
        Initialize a CourseDocument object with support for different content formats.

        Args:
            doc_id (int/str): Unique ID of the document.
            file_name (str): Name of the file.
            file_path (str): Path to the file relative to download directory.
            file_type (str): Type of the file (default: "pdf").
            title (str): Title of the document.
            url (str): Original URL of the document.
            pages (int): Number of pages in the document.
            views (int): Number of views for the document.
            content (str/dict): Extracted content from the document (text, markdown, html, or json).
            content_format (str): Format of the content ("text", "markdown", "html", "json").
            has_images (bool): Whether images were extracted along with content.
            images_dir (str): Path to extracted images directory, if applicable.
            tags (list): List of tags for categorization.
        """
        self._id = doc_id
        self.file_name = file_name
        self.file_path = file_path
        self.file_type = file_type
        self.title = title
        self.url = url
        self.pages = pages
        self.views = views
        self.content = content
        self.content_format = content_format
        self.has_images = has_images
        self.images_dir = images_dir
        self.tags = tags or []
        self.creation_date = datetime.now(UTC)

    def to_dict(self):
        """
        Convert the CourseDocument object to a dictionary for MongoDB storage.

        Returns:
            dict: A dictionary representation of the document.
        """
        return {
            "_id": self._id,
            "file_name": self.file_name,
            "file_path": self.file_path,
            "file_type": self.file_type,
            "title": self.title,
            "url": self.url,
            "pages": self.pages,
            "views": self.views,
            "content": self.content,
            "content_format": self.content_format,
            "has_images": self.has_images,
            "images_dir": self.images_dir,
            "tags": self.tags,
            "creation_date": self.creation_date
        }

    @classmethod
    def from_scraper_data(cls, doc_data, extraction_result=None):
        """
        Create a CourseDocument instance from data structure used in scraper.py.

        Args:
            doc_data (dict): Document data from scraper.
            extraction_result (dict, optional): Result from extract_text_from_pdf or Marker extraction.

        Returns:
            CourseDocument: A new CourseDocument instance.
        """
        content = None
        content_format = "text"
        has_images = False
        images_dir = None

        if extraction_result:
            content = extraction_result.get("content")
            content_format = extraction_result.get("format", "text")
            has_images = extraction_result.get("has_images", False)
            images_dir = extraction_result.get("images_dir")

        return cls(
            doc_id=doc_data["_id"],
            file_name=doc_data["file_name"],
            file_path=doc_data["file_path"],
            file_type=doc_data.get("file_type", "pdf"),
            title=doc_data.get("title"),
            url=doc_data.get("url"),
            pages=doc_data.get("pages"),
            views=doc_data.get("views"),
            content=content,
            content_format=content_format,
            has_images=has_images,
            images_dir=images_dir
        )

    @property
    def text(self):
        """
        Backward compatibility for older code expecting a 'text' attribute.

        Returns:
            str: The content as text, regardless of original format
        """
        if self.content is None:
            return None

        if self.content_format == "json" and isinstance(self.content, dict):
            # Pour JSON content, try to extract text from the structure
            try:
                # Extract text from a typical Marker JSON structure
                text_parts = []
                for block in self.content.get("blocks", []):
                    if "text" in block:
                        text_parts.append(block["text"])
                return "\n".join(text_parts)
            except (AttributeError, KeyError):
                # If we can't extract in the expected format, convert to string
                return str(self.content)
        else:
            # For text, markdown, html - return as is
            return self.content