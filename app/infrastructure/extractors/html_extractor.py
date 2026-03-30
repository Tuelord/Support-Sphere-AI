import hashlib
import requests
from bs4 import BeautifulSoup
from app.core.domain_models import Document
from app.core.interfaces import IContentExtractor


class HtmlExtractor(IContentExtractor):
    """
    Concrete Strategy for extracting text from Web URLs.
    Matches SRS Class Diagram: HtmlExtractor.
    """

    def extract(self, uri: str) -> Document:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(uri, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.extract()

        text = soup.get_text()

        # Clean leading/trailing whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        clean_text = '\n'.join(chunk for chunk in chunks if chunk)

        content_hash = hashlib.md5(clean_text.encode('utf-8')).hexdigest()

        return Document(
            source_uri=uri,
            content_hash=content_hash,
            raw_content=clean_text,
            metadata={
                "source_type": "web",
                "content_hash": content_hash
            }
        )