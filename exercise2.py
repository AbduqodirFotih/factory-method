from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum


class DocumentType(Enum):
    TEXT = "text"
    PDF = "pdf"
    SPREADSHEET = "spreadsheet"


class Document(ABC):
    def __init__(self, title: str, author: str):
        self.title = title
        self.author = author
        self.created_at = datetime.now()
        self.modified_at = datetime.now()
        self.content = ""

    @abstractmethod
    def open(self) -> str:
        pass

    @abstractmethod
    def save(self, content: str) -> None:
        pass

    @abstractmethod
    def get_metadata(self) -> dict:
        pass


class TextDocument(Document):
    def __init__(self, title: str, author: str, encoding: str = "utf-8"):
        super().__init__(title, author)
        self.encoding = encoding
        self.line_count = 0

    def open(self) -> str:
        return f"Opening text document: {self.title}"

    def save(self, content: str) -> None:
        self.content = content
        self.line_count = len(content.split('\n'))
        self.modified_at = datetime.now()

    def get_metadata(self) -> dict:
        return {
            "type": "Text Document",
            "encoding": self.encoding,
            "line_count": self.line_count
        }


class PDFDocument(Document):
    def __init__(self, title: str, author: str, page_size: str = "A4", security_level: int = 0):
        super().__init__(title, author)
        self.page_size = page_size
        self.security_level = security_level
        self.pages = []

    def open(self) -> str:
        return f"Opening PDF document: {self.title}"

    def save(self, content: str) -> None:
        self.pages = content.split('\n---\n')
        self.modified_at = datetime.now()

    def get_metadata(self) -> dict:
        return {
            "type": "PDF Document",
            "page_size": self.page_size,
            "security_level": self.security_level,
            "page_count": len(self.pages)
        }


class SpreadsheetDocument(Document):
    def __init__(self, title: str, author: str, rows: int = 100, columns: int = 26):
        super().__init__(title, author)
        self.rows = rows
        self.columns = columns
        self.sheets = []

    def open(self) -> str:
        return f"Opening spreadsheet: {self.title}"

    def save(self, content: str) -> None:
        self.sheets = content.split('\n###\n')
        self.modified_at = datetime.now()

    def get_metadata(self) -> dict:
        return {
            "type": "Spreadsheet",
            "dimensions": f"{self.rows}x{self.columns}",
            "sheet_count": len(self.sheets)
        }


class DocumentFactory:
    _documents = {
        DocumentType.TEXT: TextDocument,
        DocumentType.PDF: PDFDocument,
        DocumentType.SPREADSHEET: SpreadsheetDocument,
    }

    @staticmethod
    def create_document(
        doc_type: DocumentType,
        title: str,
        author: str,
        **kwargs
    ) -> Document:
        document_class = DocumentFactory._documents.get(doc_type)
        if document_class is None:
            raise ValueError(f"Unknown document type: {doc_type}")
        return document_class(title, author, **kwargs)


def test_document_factory():
    factory = DocumentFactory()

    text_doc = factory.create_document(
        DocumentType.TEXT, "My Novel", "Jane Author", encoding="utf-16"
    )

    pdf_doc = factory.create_document(
        DocumentType.PDF, "Annual Report", "Company Inc",
        page_size="Legal", security_level=2
    )

    spreadsheet = factory.create_document(
        DocumentType.SPREADSHEET, "Sales Data", "Data Team",
        rows=1000, columns=50
    )

    documents = [text_doc, pdf_doc, spreadsheet]

    for doc in documents:
        print(f"\n{doc.open()}")
        print(f"Metadata: {doc.get_metadata()}")


if __name__ == "__main__":
    test_document_factory()
