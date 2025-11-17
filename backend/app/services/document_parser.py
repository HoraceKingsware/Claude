import os
from typing import List, Dict, Any
from pathlib import Path
import logging

import PyPDF2
from docx import Document as DocxDocument
from pptx import Presentation
import markdown
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class DocumentParser:
    """Parse various document formats and extract text content."""

    @staticmethod
    def parse_pdf(file_path: str) -> str:
        """Parse PDF file and extract text."""
        try:
            text = []
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text.append(page_text)
            return "\n\n".join(text)
        except Exception as e:
            logger.error(f"Error parsing PDF {file_path}: {str(e)}")
            raise

    @staticmethod
    def parse_docx(file_path: str) -> str:
        """Parse DOCX file and extract text."""
        try:
            doc = DocxDocument(file_path)
            paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
            return "\n\n".join(paragraphs)
        except Exception as e:
            logger.error(f"Error parsing DOCX {file_path}: {str(e)}")
            raise

    @staticmethod
    def parse_pptx(file_path: str) -> str:
        """Parse PPTX file and extract text."""
        try:
            prs = Presentation(file_path)
            text = []

            for slide in prs.slides:
                slide_text = []
                for shape in slide.shapes:
                    if hasattr(shape, "text") and shape.text.strip():
                        slide_text.append(shape.text)
                if slide_text:
                    text.append("\n".join(slide_text))

            return "\n\n".join(text)
        except Exception as e:
            logger.error(f"Error parsing PPTX {file_path}: {str(e)}")
            raise

    @staticmethod
    def parse_txt(file_path: str) -> str:
        """Parse TXT file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:
            # Try with different encoding
            with open(file_path, 'r', encoding='latin-1') as file:
                return file.read()

    @staticmethod
    def parse_markdown(file_path: str) -> str:
        """Parse Markdown file and extract text."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                md_content = file.read()
            # Convert to HTML and then extract text
            html = markdown.markdown(md_content)
            soup = BeautifulSoup(html, 'html.parser')
            return soup.get_text(separator='\n\n')
        except Exception as e:
            logger.error(f"Error parsing Markdown {file_path}: {str(e)}")
            raise

    @staticmethod
    def parse_html(file_path: str) -> str:
        """Parse HTML file and extract text."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                html_content = file.read()
            soup = BeautifulSoup(html_content, 'html.parser')
            return soup.get_text(separator='\n\n')
        except Exception as e:
            logger.error(f"Error parsing HTML {file_path}: {str(e)}")
            raise

    def parse(self, file_path: str) -> str:
        """
        Parse document based on file extension.

        Args:
            file_path: Path to the document file

        Returns:
            Extracted text content
        """
        file_ext = Path(file_path).suffix.lower()

        parsers = {
            '.pdf': self.parse_pdf,
            '.docx': self.parse_docx,
            '.doc': self.parse_docx,
            '.pptx': self.parse_pptx,
            '.ppt': self.parse_pptx,
            '.txt': self.parse_txt,
            '.md': self.parse_markdown,
            '.markdown': self.parse_markdown,
            '.html': self.parse_html,
            '.htm': self.parse_html,
        }

        parser = parsers.get(file_ext)
        if not parser:
            raise ValueError(f"Unsupported file type: {file_ext}")

        return parser(file_path)


class TextChunker:
    """Split text into chunks for embedding."""

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_text(self, text: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Split text into overlapping chunks.

        Args:
            text: Text content to chunk
            metadata: Additional metadata to attach to each chunk

        Returns:
            List of chunks with metadata
        """
        if not text or not text.strip():
            return []

        chunks = []
        start = 0
        text_length = len(text)

        while start < text_length:
            end = start + self.chunk_size

            # Try to break at sentence boundary
            if end < text_length:
                # Look for sentence endings
                for separator in ['. ', '.\n', '! ', '!\n', '? ', '?\n']:
                    last_sep = text.rfind(separator, start, end)
                    if last_sep != -1:
                        end = last_sep + len(separator)
                        break

            chunk_text = text[start:end].strip()
            if chunk_text:
                chunk_data = {
                    'content': chunk_text,
                    'metadata': {
                        **(metadata or {}),
                        'chunk_index': len(chunks),
                        'start_char': start,
                        'end_char': end,
                    }
                }
                chunks.append(chunk_data)

            start = end - self.chunk_overlap if end < text_length else text_length

        return chunks
