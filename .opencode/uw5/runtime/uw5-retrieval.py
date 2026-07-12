# UW5 v5 Retrieval — sorgu anında RAG context toplar
# Görev: kullanıcı task'ini vektör indeksinde ara, en alakalı 3-5 chunk'ı döndür
# L03 (KAIROS Recall) alt bileşeni — <200ms hedef, threshold 0.45

import os, json, sys, time
from pathlib import Path

try:
    import numpy as np
except ImportError:
    np = None

class UW5Retrieval:
    def __init__(self, uw5_root):
        self.uw5_root = Path(uw5_root)
        self.vector_dir = self.uw5_root / "memory" / "vector-index"
        self.embeddings = None
        self.documents = None
        self.vocab = None
        self.vocab_rev = {}  # idx -> word
        self.meta = None
        self._loaded = False
    
    def load_index(self):
        """İndeksi hafızaya yükle"""
        try:
            # Metadata
            meta_file = self.vector_dir / "index.json"
            if not meta_file.exists():
                return False
            self.meta = json.loads(meta_file.read_text(encoding="utf-8"))
            
            # Embeddings
            emb_file = self.vector_dir / "embeddings.npy"
            if not emb_file.exists():
                return False
            self.embeddings = np.load(str(emb_file))
            
            # Documents (slim)
            doc_file = self.vector_dir / "documents.json"
            if not doc_file.exists():
                return False
            self.documents = json.loads(doc_file.read_text(encoding="utf-8"))
            
            # Vocabulary
            vocab_file = self.vector_dir / "vocab.json"
            if vocab_file.exists():
                vocab_list = json.loads(vocab_file.read_text(encoding="utf-8"))
                self.vocab = {item["word"]: item["idx"] for item in vocab_list}
                self.vocab_rev = {item["idx"]: item["word"] for item in vocab_list}
            
            self._loaded = True
            return True
        except Exception as e:
            print(f"[RETRIEVAL] Index load failed: {e}", file=sys.stderr)
            return False
    
    def _tokenize(self, text):
        """Tokenize + normalize — indexer ile aynı"""
        import re
        text = text.lower()
        text = re.sub(r'[^a-z0-9\s_\-]', ' ', text)
        tokens = text.split()
        stops = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
                 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'can', 'could',
                 'shall', 'should', 'may', 'might', 'must', 'to', 'of', 'in', 'for', 'on',
                 'with', 'at', 'by', 'from', 'as', 'into', 'through', 'during', 'before',
                 'after', 'above', 'below', 'between', 'out', 'off', 'over', 'under',
                 'again', 'further', 'then', 'once', 'and', 'but', 'or', 'nor', 'not',
                 'so', 'yet', 'both', 'either', 'neither', 'each', 'every', 'all', 'any',
                 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'only', 'own',
                 'same', 'this', 'that', 'these', 'those', 'i', 'me', 'my', 'myself',
                 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours', 'yourself',
                 'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself',
                 'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves',
                 'what', 'which', 'who', 'whom', 'whose', 'when', 'where', 'why', 'how',
                 've', 're', 'll', 't', 's', 'don', 'doesn', 'didn', 'isn', 'aren',
                 'won', 'wouldn', 'shan', 'shouldn', 'can', 'couldn', 'mightn', 'mustn',
                 'bir', 've', 'ile', 'icin', 'bu', 'su', 'o', 'da', 'de', 'den', 'dan',
                 'mi', 'mu', 'mı', 'olarak', 'gibi', 'kadar', 'sonra', 'once', 'ama',
                 'fakat', 'ancak', 'veya', 'ya da', 'çok', 'daha', 'en', 'her'}
        return [t for t in tokens if t not in stops and len(t) > 1]
    
    def _vectorize(self, text):
        """Sorguyu vektöre dönüştür (indexer ile aynı yöntem)"""
        if not self.vocab:
            return np.array([], dtype=np.float32)
        vec = np.zeros(len(self.vocab), dtype=np.float32)
        words = self._tokenize(text)
        word_counts = {}
        for w in words:
            if w in self.vocab:
                word_counts[w] = word_counts.get(w, 0) + 1
        total = len(words) or 1
        for w, c in word_counts.items():
            vec[self.vocab[w]] = c / total
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec
    
    def query(self, query_text, top_k=5, threshold=0.45):
        """En alakalı chunk'ları bul"""
        if not self._loaded:
            if not self.load_index():
                return []
        
        if self.embeddings is None or len(self.documents) == 0:
            return []
        
        t0 = time.time()
        
        # Sorguyu vektöre çevir
        query_vec = self._vectorize(query_text)
        if len(query_vec) == 0:
            return []
        
        # Cosine similarity
        scores = np.dot(self.embeddings, query_vec)
        
        # En yüksek top_k
        top_indices = np.argsort(scores)[-top_k:][::-1]
        
        results = []
        for idx in top_indices:
            score = float(scores[idx])
            if score < threshold:
                continue
            doc = self.documents[idx]
            results.append({
                "score": round(score, 4),
                "source": doc["source"],
                "source_type": doc["source_type"],
                "domain": doc["domain"],
                "text": doc["text"],
                "error_signature": doc.get("error_signature", ""),
            })
        
        elapsed = (time.time() - t0) * 1000  # ms
        
        return {
            "results": results,
            "query_time_ms": round(elapsed, 1),
            "total_docs": len(self.documents),
            "threshold": threshold,
        }


if __name__ == "__main__":
    import sys
    
    uw5_root = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(os.path.abspath(__file__)), ".."
    )
    query_text = sys.argv[2] if len(sys.argv) > 2 else ""
    
    if not query_text:
        print("Usage: python uw5-retrieval.py <uw5_root> <query_text> [top_k] [threshold]")
        sys.exit(1)
    
    top_k = int(sys.argv[3]) if len(sys.argv) > 3 else 5
    threshold = float(sys.argv[4]) if len(sys.argv) > 4 else 0.45
    
    retriever = UW5Retrieval(uw5_root)
    result = retriever.query(query_text, top_k=top_k, threshold=threshold)
    
    print(json.dumps(result, indent=2, ensure_ascii=False))
