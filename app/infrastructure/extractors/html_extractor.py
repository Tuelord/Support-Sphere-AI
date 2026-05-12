import hashlib
import logging
import re
import requests
from bs4 import BeautifulSoup
from app.core.domain_models import Document
from app.core.interfaces import IContentExtractor

logger = logging.getLogger(__name__)


class HtmlExtractor(IContentExtractor):
    """
    Concrete Strategy for extracting text from Web URLs.
    Optimized for RAG: removes boilerplate (nav, footer, etc.) and handles network errors.
    """

    # Tags that usually contain boilerplate, non-core content
    NOISE_TAGS = ["script", "style", "nav", "footer", "header", "aside", "noscript", "form", "svg"]

    def extract(self, uri: str) -> Document:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }

        try:
            # Added a reasonable timeout to prevent hanging forever
            response = requests.get(uri, headers=headers, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"Failed to fetch URI: {uri}. Error: {e}")
            raise ValueError(f"Could not extract content from {uri}: {e}")

        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # Try to extract the title for metadata
        title_tag = soup.find('title')
        page_title = title_tag.get_text(strip=True) if title_tag else ""

        # Remove noisy elements that pollute the RAG context
        for element in soup(self.NOISE_TAGS):
            element.decompose()  # decompose is more memory efficient than extract()

        # Extract text using a line break separator and strip surrounding whitespace
        clean_text = soup.get_text(separator='\n', strip=True)

        # Normalize multiple newlines into a maximum of two (paragraph breaks)
        clean_text = re.sub(r'\n{3,}', '\n\n', clean_text)

        if not clean_text:
            logger.warning(f"Extraction yielded empty content for URI: {uri}")

        content_hash = hashlib.md5(clean_text.encode('utf-8')).hexdigest()

        return Document(
            source_uri=uri,
            content_hash=content_hash,
            raw_content=clean_text,
            metadata={
                "source_type": "web",
                "title": page_title,
                "content_hash": content_hash
            }
        )