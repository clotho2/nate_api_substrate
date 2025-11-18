#!/usr/bin/env python3
"""
PDF Reader - Extract text from PDFs (FREE!)

Two modes:
1. ArXiv LaTeX Source (BEST for academic papers!)
2. PyMuPDF (for any PDF)

LaTeX sources are cleaner and preserve formulas!
"""

import os
import logging
import tempfile
from typing import Dict, Any, Optional
from pathlib import Path

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False
    print("⚠️ PyMuPDF not installed. Run: pip install PyMuPDF")

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False
    print("⚠️ httpx not installed. Run: pip install httpx")

import tarfile
import io

logger = logging.getLogger(__name__)


class PDFReader:
    """
    PDF Reader - Extract text from PDFs.
    
    Supports:
    - ArXiv LaTeX source (best for papers!)
    - Any PDF via PyMuPDF
    """
    
    def __init__(self):
        """Initialize PDF reader"""
        if not PYMUPDF_AVAILABLE:
            logger.warning("⚠️ PyMuPDF not available")
        if not HTTPX_AVAILABLE:
            logger.warning("⚠️ httpx not available")
        
        self.client = httpx.Client(timeout=60.0) if HTTPX_AVAILABLE else None
        logger.info("✅ PDF Reader initialized")
    
    def read_arxiv_paper(
        self,
        arxiv_id: str,
        max_chars: Optional[int] = 20000
    ) -> Dict[str, Any]:
        """
        Download and extract ArXiv paper (LaTeX source preferred!).
        
        Args:
            arxiv_id: ArXiv ID (e.g., "2103.14030" or "arXiv:2103.14030")
            max_chars: Max characters to extract (default: 20000)
        
        Returns:
            {
                'status': 'OK' or 'error',
                'arxiv_id': str,
                'text': str,
                'source': 'latex' or 'pdf',
                'length': int
            }
        """
        # Clean ArXiv ID
        clean_id = arxiv_id.replace("arXiv:", "").replace("arxiv:", "").strip()
        
        logger.info(f"📄 Fetching ArXiv paper: {clean_id}")
        
        # Try LaTeX source first (BEST!)
        latex_result = self._download_arxiv_latex(clean_id, max_chars)
        if latex_result['status'] == 'OK':
            return latex_result
        
        logger.info(f"   ⚠️ LaTeX not available, trying PDF...")
        
        # Fallback: Download PDF
        pdf_result = self._download_arxiv_pdf(clean_id, max_chars)
        return pdf_result
    
    def _download_arxiv_latex(
        self,
        arxiv_id: str,
        max_chars: Optional[int]
    ) -> Dict[str, Any]:
        """Download and extract LaTeX source from ArXiv"""
        if not self.client:
            return {"status": "error", "message": "httpx not available"}
        
        try:
            # ArXiv LaTeX source URL
            url = f"https://arxiv.org/e-print/{arxiv_id}"
            
            logger.info(f"   📥 Downloading LaTeX source: {url}")
            
            response = self.client.get(url, follow_redirects=True)
            response.raise_for_status()
            
            # Extract .tar.gz
            with tarfile.open(fileobj=io.BytesIO(response.content), mode='r:gz') as tar:
                # Find main .tex file
                tex_files = [m for m in tar.getmembers() if m.name.endswith('.tex')]
                
                if not tex_files:
                    return {"status": "error", "message": "No .tex files found in archive"}
                
                # Usually main.tex or paper.tex is the main file
                main_tex = None
                for name in ['main.tex', 'paper.tex', f'{arxiv_id}.tex']:
                    matches = [f for f in tex_files if f.name.endswith(name)]
                    if matches:
                        main_tex = matches[0]
                        break
                
                # If no main file found, use first .tex
                if not main_tex:
                    main_tex = tex_files[0]
                
                # Extract text
                tex_file = tar.extractfile(main_tex)
                if not tex_file:
                    return {"status": "error", "message": "Failed to extract .tex file"}
                
                latex_text = tex_file.read().decode('utf-8', errors='ignore')
                
                # Clean LaTeX (remove preamble, comments, etc.)
                cleaned_text = self._clean_latex(latex_text)
                
                # Limit length
                if max_chars and len(cleaned_text) > max_chars:
                    cleaned_text = cleaned_text[:max_chars] + f"\n\n... (truncated, original: {len(latex_text)} chars)"
                
                logger.info(f"   ✅ Extracted LaTeX: {len(cleaned_text)} chars")
                
                return {
                    "status": "OK",
                    "arxiv_id": arxiv_id,
                    "text": cleaned_text,
                    "source": "latex",
                    "length": len(cleaned_text)
                }
        
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 403 or e.response.status_code == 404:
                return {"status": "not_available", "message": "LaTeX source not available (PDF-only submission)"}
            return {"status": "error", "message": f"HTTP error: {e.response.status_code}"}
        
        except Exception as e:
            logger.error(f"   ❌ LaTeX extraction failed: {e}")
            return {"status": "error", "message": str(e)}
    
    def _download_arxiv_pdf(
        self,
        arxiv_id: str,
        max_chars: Optional[int]
    ) -> Dict[str, Any]:
        """Download and extract PDF from ArXiv"""
        if not self.client or not PYMUPDF_AVAILABLE:
            return {"status": "error", "message": "PDF extraction not available"}
        
        try:
            # ArXiv PDF URL
            url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
            
            logger.info(f"   📥 Downloading PDF: {url}")
            
            response = self.client.get(url, follow_redirects=True)
            response.raise_for_status()
            
            # Extract text with PyMuPDF
            text = self._extract_pdf_text(response.content, max_chars)
            
            logger.info(f"   ✅ Extracted PDF: {len(text)} chars")
            
            return {
                "status": "OK",
                "arxiv_id": arxiv_id,
                "text": text,
                "source": "pdf",
                "length": len(text)
            }
        
        except Exception as e:
            logger.error(f"   ❌ PDF extraction failed: {e}")
            return {"status": "error", "message": str(e)}
    
    def _clean_latex(self, latex_text: str) -> str:
        """Clean LaTeX source (remove preamble, comments, etc.)"""
        lines = latex_text.split('\n')
        cleaned_lines = []
        in_document = False
        
        for line in lines:
            # Skip comments
            if line.strip().startswith('%'):
                continue
            
            # Start at \begin{document}
            if '\\begin{document}' in line:
                in_document = True
                continue
            
            # Stop at \end{document}
            if '\\end{document}' in line:
                break
            
            if in_document:
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def _extract_pdf_text(
        self,
        pdf_bytes: bytes,
        max_chars: Optional[int]
    ) -> str:
        """Extract text from PDF bytes using PyMuPDF"""
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        
        text_parts = []
        total_chars = 0
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            page_text = page.get_text()
            
            if max_chars:
                remaining = max_chars - total_chars
                if remaining <= 0:
                    break
                page_text = page_text[:remaining]
            
            text_parts.append(page_text)
            total_chars += len(page_text)
        
        doc.close()
        
        full_text = '\n\n'.join(text_parts)
        
        if max_chars and total_chars >= max_chars:
            full_text += f"\n\n... (truncated at {max_chars} chars)"
        
        return full_text
    
    def read_pdf_file(
        self,
        file_path: str,
        max_chars: Optional[int] = 20000
    ) -> Dict[str, Any]:
        """
        Read any PDF file from disk.
        
        Args:
            file_path: Path to PDF file
            max_chars: Max characters (default: 20000)
        
        Returns:
            {
                'status': 'OK' or 'error',
                'file_path': str,
                'text': str,
                'length': int
            }
        """
        if not PYMUPDF_AVAILABLE:
            return {"status": "error", "message": "PyMuPDF not installed"}
        
        try:
            logger.info(f"📄 Reading PDF: {file_path}")
            
            # Read PDF
            with open(file_path, 'rb') as f:
                pdf_bytes = f.read()
            
            text = self._extract_pdf_text(pdf_bytes, max_chars)
            
            logger.info(f"   ✅ Extracted: {len(text)} chars")
            
            return {
                "status": "OK",
                "file_path": file_path,
                "text": text,
                "length": len(text)
            }
        
        except Exception as e:
            logger.error(f"   ❌ PDF read failed: {e}")
            return {
                "status": "error",
                "message": str(e),
                "file_path": file_path
            }
    
    def __del__(self):
        """Cleanup"""
        try:
            if self.client:
                self.client.close()
        except:
            pass


# Singleton
_pdf_reader: Optional[PDFReader] = None


def get_pdf_reader() -> PDFReader:
    """Get or create PDF reader singleton"""
    global _pdf_reader
    if _pdf_reader is None:
        _pdf_reader = PDFReader()
    return _pdf_reader


def read_arxiv_paper(arxiv_id: str, max_chars: int = 20000) -> Dict[str, Any]:
    """
    Read ArXiv paper (LaTeX or PDF).
    
    Args:
        arxiv_id: ArXiv ID
        max_chars: Max characters (default: 20000)
    
    Returns:
        Paper text
    """
    reader = get_pdf_reader()
    return reader.read_arxiv_paper(arxiv_id, max_chars=max_chars)


if __name__ == "__main__":
    # Test
    print("\n🧪 Testing PDF Reader\n")
    
    # Test ArXiv paper (Attention Is All You Need)
    print("1️⃣ Reading ArXiv Paper: 1706.03762 (Attention Is All You Need)")
    result = read_arxiv_paper("1706.03762", max_chars=5000)
    
    print(f"Status: {result['status']}")
    if result.get('text'):
        print(f"Source: {result['source']}")
        print(f"Length: {result['length']} chars")
        print(f"\nPreview:")
        print(result['text'][:500] + "...")







