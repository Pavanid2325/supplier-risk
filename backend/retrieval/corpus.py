import os
import re
from typing import List, Dict, Any

class ContractChunk:
    def __init__(
        self,
        document_id: str,
        section: str,
        tenant_id: str,
        text: str,
        metadata: Dict[str, Any]
    ):
        self.document_id = document_id
        self.section = section
        self.tenant_id = tenant_id
        self.text = text
        self.metadata = metadata

    def to_dict(self) -> Dict[str, Any]:
        return {
            "document_id": self.document_id,
            "section": self.section,
            "tenant_id": self.tenant_id,
            "text": self.text,
            "metadata": self.metadata
        }

def parse_frontmatter(content: str) -> tuple[Dict[str, Any], str]:
    metadata = {}
    body = content
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            raw_meta = parts[1].strip()
            body = parts[2].strip()
            for line in raw_meta.split("\n"):
                if ":" in line:
                    key, val = line.split(":", 1)
                    metadata[key.strip()] = val.strip()
    return metadata, body

def load_and_chunk_corpus(corpus_dir: str) -> List[ContractChunk]:
    chunks: List[ContractChunk] = []
    if not os.path.exists(corpus_dir):
        return chunks

    for filename in os.listdir(corpus_dir):
        if not filename.endswith(".md"):
            continue

        filepath = os.path.join(corpus_dir, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        meta, body = parse_frontmatter(content)
        doc_id = meta.get("document_id", filename)
        tenant_id = meta.get("tenant_id", "tenant-alpha")

        # Split body by markdown section headers (## or #)
        sections = re.split(r'\n(?=#{1,3}\s)', body)
        for sec in sections:
            sec_clean = sec.strip()
            if not sec_clean:
                continue

            lines = sec_clean.split("\n", 1)
            title_line = lines[0].lstrip("#").strip()
            sec_body = sec_clean

            chunk_meta = dict(meta)
            chunk_meta["filename"] = filename

            chunks.append(
                ContractChunk(
                    document_id=doc_id,
                    section=title_line,
                    tenant_id=tenant_id,
                    text=sec_body,
                    metadata=chunk_meta
                )
            )

    return chunks
