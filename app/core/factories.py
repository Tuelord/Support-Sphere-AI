from app.core.interfaces import IContentExtractor
from app.infrastructure.extractors.pdf_extractor import PdfExtractor
from app.infrastructure.extractors.html_extractor import HtmlExtractor

class ExtractorFactory:
    """
    Factory Method Pattern for creating extractors.
    Matches SRS Class Diagram: ExtractorFactory.
    """
    @staticmethod
    def create_extractor(uri: str) -> IContentExtractor:
        if uri.endswith(".pdf"):
            return PdfExtractor()
        elif uri.startswith("http"):
            return HtmlExtractor()
        else:
            raise ValueError(f"No extractor available for URI: {uri}")