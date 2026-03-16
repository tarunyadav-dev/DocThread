from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from pathlib import Path

class DocChunker:
    def __init__(self):
        # The Registry: Maps the exact path of the document
        headers_to_split_on = [
            ("#", "h1"),
            ("##", "h2"),
            ("###", "h3"),
            ("####", "h4"),
        ]
        self.md_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=headers_to_split_on,
            strip_headers=False
        )
        
        # Granular Chunking: Small chunks (500) for pinpoint accuracy, 
        # with overlap (100) so we don't lose the flow of code blocks.
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,     
            chunk_overlap=100,   
            separators=["\n\n```", "```\n\n", "\n\n", "\n", " ", ""] 
        )

    def chunk_file(self, file_path: Path, framework: str):
        """Slices a file and attaches the exact metadata 'backpack'."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            header_splits = self.md_splitter.split_text(content)
            final_chunks = self.text_splitter.split_documents(header_splits)
            
            # Add custom metadata to every tiny chunk
            for chunk in final_chunks:
                chunk.metadata["source_file"] = file_path.name
                chunk.metadata["framework"] = framework
                
            return final_chunks
            
        except Exception as e:
            print(f"❌ Error chunking {file_path.name}: {e}")
            return []