# UW5 v5 Retrieval Indexer — vektör indeksini oluşturur/günceller
# Görev: SKILL.md + KAIROS kayıtları + UW5_CORE.md'yi vector store'a dönüştür
# L03 (KAIROS Recall) / L04 (Knowledge Graph) alt bileşeni — bağımsız modül değil

import os, json, re, hashlib, glob, time
from pathlib import Path

try:
    import numpy as np
except ImportError:
    np = None

class UW5RetrievalIndexer:
    def __init__(self, uw5_root):
        self.uw5_root = Path(uw5_root)
        self.vector_dir = self.uw5_root / "memory" / "vector-index"
        self.vector_dir.mkdir(parents=True, exist_ok=True)
        
        # Skill dizinleri
        self.skill_dirs = [
            Path(os.environ.get("USERPROFILE", "")) / ".config" / "opencode" / "skills",
            Path(os.environ.get("USERPROFILE", "")) / ".claude" / "skills",
        ]
        # KAIROS kayıtları
        self.kairos_dir = Path(os.environ.get("USERPROFILE", "")) / ".config" / "opencode" / ".kairos" / "records"
        # UW5_CORE.md
        self.core_path = self.uw5_root / "UW5_CORE.md"
        
        self.documents = []  # {id, text, source, source_type, domain, timestamp}
        self.embeddings = None
        self.vocab = {}  # word -> index for TF-IDF
    
    def load_all_sources(self):
        """Tüm kaynaklardan metin topla"""
        self.documents = []
        
        # 1. SKILL.md dosyaları
        for skill_dir in self.skill_dirs:
            if not skill_dir.exists():
                continue
            skill_files = list(skill_dir.rglob("SKILL.md"))
            for sf in skill_files:
                try:
                    text = sf.read_text(encoding="utf-8")
                    # Her SKILL.md'yi chunk'lara böl
                    chunks = self._chunk_skill(text, sf)
                    self.documents.extend(chunks)
                except Exception as e:
                    print(f"[INDEXER] Warning: Can't read {sf}: {e}")
        
        # 2. KAIROS kayıtları
        if self.kairos_dir.exists():
            for jf in self.kairos_dir.glob("*.json"):
                try:
                    data = json.loads(jf.read_text(encoding="utf-8"))
                    doc = {
                        "id": f"kairos_{jf.stem}",
                        "text": json.dumps(data, indent=2),
                        "source": jf.name,
                        "source_type": "kairos",
                        "domain": data.get("domain", "unknown"),
                        "error_signature": data.get("error_signature", ""),
                        "timestamp": data.get("timestamp", ""),
                    }
                    self.documents.append(doc)
                except Exception as e:
                    print(f"[INDEXER] Warning: Can't read KAIROS {jf}: {e}")
        
        # 3. UW5_CORE.md
        if self.core_path.exists():
            try:
                text = self.core_path.read_text(encoding="utf-8")
                chunks = self._chunk_text(text, "UW5_CORE.md", "uw5_core", "core")
                self.documents.extend(chunks)
            except Exception as e:
                print(f"[INDEXER] Warning: Can't read UW5_CORE.md: {e}")
        
        # 4. Pine Script hard kuralları (her zaman index'te olsun)
        pine_rules = (
            "Pine Script Hard Rules: "
            "1. 64-plot limit: Total plot() calls per script cannot exceed 64. "
            "2. plot() scope: plot() MUST be called at script-level (global) scope only. "
            "3. linewidth: Must reference an input.int() variable directly. "
            "4. Library rules: export functions do pure computation only (no plot/input/strategy). "
            "5. Change scope: numeric values/logic unchanged unless specified — only color/cosmetic changes."
        )
        self.documents.append({
            "id": "pine_hard_rules",
            "text": pine_rules,
            "source": "pine-architect SKILL.md",
            "source_type": "pine_rules",
            "domain": "pine",
            "timestamp": "",
        })
        
        print(f"[INDEXER] Loaded {len(self.documents)} documents")
        return self.documents
    
    def _chunk_skill(self, text, filepath):
        """SKILL.md'yi anlamlı chunk'lara böl — çok kısa chunk'ları birleştir"""
        chunks = []
        source_name = filepath.stem if filepath.parent.name == "skills" else filepath.parent.name
        
        # Metadata'yı ayır
        meta = {}
        meta_match = re.search(r'^---\n(.+?)\n---', text, re.DOTALL)
        if meta_match:
            for line in meta_match.group(1).split('\n'):
                if ':' in line:
                    k, v = line.split(':', 1)
                    meta[k.strip()] = v.strip()
        
        # Ana metni böl (metadata sonrası)
        main_text = re.sub(r'^---\n.+?\n---\n?', '', text, flags=re.DOTALL)
        
        # Section başlıklarına göre böl (## ile başlayan)
        sections = re.split(r'\n(?=## )', main_text)
        merged = []
        pending = ""
        for sec in sections:
            if not sec.strip():
                continue
            if pending:
                pending += "\n\n" + sec
            else:
                pending = sec
            # Eğer yeterince uzunsa veya son section'sa, kes
            if len(pending) >= 800:
                merged.append(pending)
                pending = ""
        if pending.strip():
            merged.append(pending)
        
        for i, section in enumerate(merged):
            sub_chunks = self._split_long_text(section.strip(), max_chars=2000)
            for j, sub in enumerate(sub_chunks):
                chunk_id = f"{source_name}_s{i}_c{j}"
                chunks.append({
                    "id": chunk_id,
                    "text": sub,
                    "source": str(filepath),
                    "source_type": "skill",
                    "domain": meta.get("name", source_name),
                    "timestamp": str(filepath.stat().st_mtime) if filepath.exists() else "",
                })
        return chunks
    
    def _chunk_text(self, text, source, source_type, domain):
        """Genel metni chunk'lara böl — çok kısa chunk'ları birleştir"""
        chunks = []
        sections = re.split(r'\n(?=#{1,3} )', text)
        merged = []
        pending = ""
        for sec in sections:
            if not sec.strip():
                continue
            if pending:
                pending += "\n\n" + sec
            else:
                pending = sec
            if len(pending) >= 800:
                merged.append(pending)
                pending = ""
        if pending.strip():
            merged.append(pending)
        
        for i, section in enumerate(merged):
            sub_chunks = self._split_long_text(section.strip(), max_chars=2000)
            for j, sub in enumerate(sub_chunks):
                chunks.append({
                    "id": f"{Path(source).stem}_s{i}_c{j}",
                    "text": sub,
                    "source": source,
                    "source_type": source_type,
                    "domain": domain,
                    "timestamp": "",
                })
        return chunks
    
    def _split_long_text(self, text, max_chars=2000):
        """Uzun metni alt chunk'lara böl (paragraf sınırından)"""
        if len(text) <= max_chars:
            return [text]
        chunks = []
        paragraphs = text.split('\n\n')
        current = ""
        for para in paragraphs:
            if len(current) + len(para) + 1 < max_chars:
                current += para + '\n\n'
            else:
                if current.strip():
                    chunks.append(current.strip())
                current = para + '\n\n'
        if current.strip():
            chunks.append(current.strip())
        return chunks if chunks else [text[:max_chars]]
    
    def _build_vocab(self):
        """TF-IDF vektörleri için vokabüler oluştur"""
        word_counts = {}
        for doc in self.documents:
            words = self._tokenize(doc["text"])
            for w in set(words):
                word_counts[w] = word_counts.get(w, 0) + 1
        
        # Stop words + çok nadir/çok yaygın kelimeleri filtrele
        total_docs = len(self.documents)
        self.vocab = {}
        idx = 0
        for word, freq in word_counts.items():
            if 2 <= freq <= total_docs * 0.8:  # en az 2 dokümanda, en fazla %80'inde geçsin
                self.vocab[word] = idx
                idx += 1
        print(f"[INDEXER] Vocabulary size: {len(self.vocab)}")
    
    def _tokenize(self, text):
        """Tokenize + normalize"""
        text = text.lower()
        text = re.sub(r'[^a-z0-9\s_\-]', ' ', text)
        tokens = text.split()
        # Stop words
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
    
    def _tfidf_vectorize(self, text):
        """Tek bir metni TF-IDF vektörüne dönüştür"""
        if not self.vocab:
            return np.array([], dtype=np.float32)
        vec = np.zeros(len(self.vocab), dtype=np.float32)
        words = self._tokenize(text)
        word_counts = {}
        for w in words:
            if w in self.vocab:
                word_counts[w] = word_counts.get(w, 0) + 1
        
        total_words = len(words) or 1
        for w, count in word_counts.items():
            tf = count / total_words
            idx = self.vocab[w]
            vec[idx] = tf
        
        return vec
    
    def build_index(self):
        """İndeksi oluştur ve kaydet"""
        print("[INDEXER] Building UW5 retrieval index...")
        self.load_all_sources()
        self._build_vocab()
        
        if len(self.vocab) == 0:
            print("[INDEXER] ERROR: Empty vocabulary — check source files")
            return False
        
        if np is None:
            print("[INDEXER] ERROR: numpy required but not available")
            return False
        
        # Her doküman için TF-IDF vektörü
        vectors = []
        for doc in self.documents:
            vec = self._tfidf_vectorize(doc["text"])
            vectors.append(vec)
        
        self.embeddings = np.array(vectors, dtype=np.float32)
        
        # Normalize (cosine similarity için)
        norms = np.linalg.norm(self.embeddings, axis=1, keepdims=True)
        norms[norms == 0] = 1
        self.embeddings = self.embeddings / norms
        
        # Kaydet
        np.save(str(self.vector_dir / "embeddings.npy"), self.embeddings)
        
        # Dokümanları JSON olarak kaydet (sadece id, source, domain, text)
        slim_docs = []
        for d in self.documents:
            slim_docs.append({
                "id": d["id"],
                "source": d["source"],
                "source_type": d["source_type"],
                "domain": d["domain"],
                "text": d["text"][:500],  # Önizleme için ilk 500 karakter
                "error_signature": d.get("error_signature", ""),
            })
        
        (self.vector_dir / "documents.json").write_text(
            json.dumps(slim_docs, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        
        # Metadata
        meta = {
            "version": "1.0",
            "built_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "num_documents": len(self.documents),
            "vocab_size": len(self.vocab),
            "embedding_dim": len(self.vocab),
            "method": "tfidf_cosine",
            "uw5_component": "L03_KAIROS_RECALL__L04_KNOWLEDGE_GRAPH__sub_component",
            "source_types": list(set(d["source_type"] for d in self.documents)),
        }
        (self.vector_dir / "index.json").write_text(
            json.dumps(meta, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        
        # Vocabulary kaydet
        vocab_list = [{"word": w, "idx": i} for w, i in sorted(self.vocab.items(), key=lambda x: x[1])]
        (self.vector_dir / "vocab.json").write_text(
            json.dumps(vocab_list, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        
        print(f"[INDEXER] Index built: {len(self.documents)} docs, {len(self.vocab)} terms, {self.embeddings.shape}")
        return True
    
    def get_file_hashes(self):
        """Kaynak dosyaların hash'lerini al (watcher için)"""
        hashes = {}
        sources = []
        
        # SKILL.md
        for skill_dir in self.skill_dirs:
            if skill_dir.exists():
                sources.extend(skill_dir.rglob("SKILL.md"))
        
        # KAIROS
        if self.kairos_dir.exists():
            sources.extend(self.kairos_dir.glob("*.json"))
        
        # UW5_CORE
        if self.core_path.exists():
            sources.append(self.core_path)
        
        for src in sources:
            try:
                stat = src.stat()
                key = str(src.relative_to(src.anchor) if src.is_absolute() else str(src))
                hashes[key] = f"{stat.st_mtime}_{stat.st_size}"
            except:
                pass
        
        return hashes


if __name__ == "__main__":
    import sys
    uw5_root = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".."
    )
    indexer = UW5RetrievalIndexer(uw5_root)
    success = indexer.build_index()
    sys.exit(0 if success else 1)
