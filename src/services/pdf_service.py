import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

class PDFProcessor:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            is_separator_regex=False,
        )

    def load_and_split(self, file_path: str) -> list[Document]:
        """
        Loads a PDF, splits it into chunks, and ensures metadata contains 
        file_name and page_label.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDF file not found: {file_path}")

        loader = PyPDFLoader(file_path)
        # load() returns a list of Documents (one per page)
        pages = loader.load()
        
        # Split documents into chunks
        chunks = self.text_splitter.split_documents(pages)
        
        file_name = os.path.basename(file_path)
        
        # Ensure metadata consistency as per ADR-003
        for i, chunk in enumerate(chunks):
            chunk.metadata["source_file"] = file_name
            # page_label is often available in PyPDFLoader metadata or we use 'page'
            chunk.metadata["page_number"] = chunk.metadata.get("page", 0) + 1
            chunk.metadata["chunk_id"] = f"{file_name}_p{chunk.metadata['page_number']}_c{i}"
            
        return chunks
