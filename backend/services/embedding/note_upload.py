import pdfplumber
import nltk
from transformers import GPT2TokenizerFast
from sentence_transformers import SentenceTransformer
from sklearn.cluster import AgglomerativeClustering

class NoteClusterer:
    def __init__(self):
        self.tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        nltk.download("punkt_tab")

    def extract_text_from_pdf(self, file_path: str) -> str:
        """returns chunks with the following info, page number, document name, chunk content, and type"""
        extracted_chunks = []
        document_name = file_path.split('/')[-1]

        with pdfplumber.open(file_path) as file:
            for i, page in enumerate(file.pages, start=1):
                page_text = page.extract_text()
                if page_text:
                    extracted_chunks.append({
                        "page_content": page_text.strip(),
                        "metadata": {
                            "document_name": document_name,
                            "page_number": i,
                            "type": "note",
                            "bound_box": None
                        }
                    })
        return extracted_chunks

    def sent_split(self, page_chunk: dict):
        "mutates page_chunk to split the chunk content into sentences"
        sentences = nltk.sent_tokenize(page_chunk["page_content"])
        if sentences:
            page_chunk["page_content"] = sentences

    def raw_cluster_sentences(self, page_chunk: dict):
        """returns rough clusters, not yet processed, only send in page_chunks that are split into sentences"""
        sentences = page_chunk["page_content"]
        embeddings = self.embedding_model.encode(sentences, convert_to_tensor=True).cpu().numpy()

        n_clusters = max(2, len(embeddings) // 5) # 5 selected as an idea is often given 5 sentences
        clustering = AgglomerativeClustering(n_clusters=n_clusters)
        cluster_labels = clustering.fit_predict(embeddings)

        current_cluster = cluster_labels[0]
        current_text = ""
        clusters = []
        for sentence, cluster_label in zip(sentences, cluster_labels):
            if cluster_label == current_cluster:
                current_text += sentence + " "
            else:
                clusters.append(current_text.strip())
                current_cluster = cluster_label
                current_text = sentence + " "

        clusters.append(current_text.strip())
        page_chunk["page_content"] = clusters
    
    def merge_small_clusters(self, chunks, min_tokens=45) -> list:
        """merges clusters that are smaller than min_tokens"""
        merged_chunks = []
        current_chunk = ""
        total_chunk_tokens = 0

        for chunk in chunks:
            chunk_token_count = len(self.tokenizer.encode(chunk, add_special_tokens=False))

            if total_chunk_tokens + chunk_token_count < min_tokens:
                current_chunk += " " + chunk
                total_chunk_tokens += chunk_token_count
            else:
                if current_chunk:
                    merged_chunks.append(current_chunk.strip())
                current_chunk = chunk
                total_chunk_tokens = chunk_token_count

        if current_chunk.strip():
            merged_chunks.append(current_chunk.strip())

        return merged_chunks
    
    def split_large_chunk(self, chunk_tokens, max_tokens=65):
        """splits a singular chunk into smaller chunks until the max length of one chunk is at most 65 tokens"""
        split_chunks = []

        for i in range(0, len(chunk_tokens), max_tokens):
            split_tokens = chunk_tokens[i:i + max_tokens]
            split_text = self.tokenizer.decode(split_tokens, skip_special_tokens=True).strip()
            split_chunks.append(split_text)

        return split_chunks
    
    def process_chunks(self, page_chunk: dict) -> list:
        """return dict that isabella wanted, where each chunk is a dict, returns a list of dicts representing chunks"""
        merged_chunks = self.merge_small_clusters(page_chunk["page_content"])
        processed_chunks = []
        final_chunks = []

        for chunk in merged_chunks:
            chunk_tokens = self.tokenizer.encode(chunk, add_special_tokens=False)
            if len(chunk_tokens) > 65:
                splits = self.split_large_chunk(chunk_tokens)
                processed_chunks.extend(splits)
            else:
                processed_chunks.append(chunk)

        for processed_chunk in processed_chunks:
            final_chunk = {
                "page_content": processed_chunk,
                "metadata": {
                    "type": "note",
                    "bound_box": None,
                    "page_number": page_chunk['metadata']["page_number"],
                    "document_name": page_chunk['metadata']["document_name"],
                }
            }
            final_chunks.append(final_chunk)

        return final_chunks
    
    def process_pdf(self, file_path: str) -> list:
        """processes the pdf file and returns a list of processed chunks"""
        extracted_chunks = self.extract_text_from_pdf(file_path)
        processed_chunks = []

        for page_chunk in extracted_chunks:
            self.sent_split(page_chunk)
            self.raw_cluster_sentences(page_chunk)
            processed_chunks.extend(self.process_chunks(page_chunk))

        return processed_chunks

if __name__ == "__main__":
    # Hardcode your PDF path and document name here
    pdf_path = "backend/services/sample_pdf.pdf"
    document_name = "Sample Document"

    clusterer = NoteClusterer()
    chunks = clusterer.process_pdf(pdf_path)

    print(f"Total chunks: {len(chunks)}")
    for i, chunk in enumerate(chunks, 1):
        print(f"\nChunk {i}:")
        print(chunk)