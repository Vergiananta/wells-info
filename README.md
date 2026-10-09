# Wells Information & Glossary QA System

Aplikasi Retrieval-Augmented Generation (RAG) berbasis web dan CLI untuk menjawab pertanyaan seputar data operasional sumur migas (Daily Geological Operations Summary / DGOS dan Daily Operation Report / DDR) serta Glosarium istilah Oil and Gas.

---

## 1. Prasyarat Sistem

* Sistem Operasi: Windows, Linux, atau macOS
* Python: Versi 3.10 atau lebih baru
* OpenAI API Key yang aktif

---

## 2. Struktur Direktori dan Penempatan Data

Sesuai dengan ketentuan kerahasiaan data, dataset dan file output hasil parsing diabaikan dari git repository melalui `.gitignore`.

### Penempatan File Input
Letakkan dokumen pada lokasi berikut sebelum menjalankan aplikasi:
* Dokumen Glosarium: Letakkan file `Glossaries.docx` di root direktori project (`./Glossaries.docx`).
* Dokumen Laporan Sumur: Letakkan file PDF pada folder `Datasets/` dengan struktur:
  * `Datasets/Daily Geological Operations Summary/` (untuk file PDF DGOS)
  * `Datasets/Daily Operation Report/` (untuk file PDF DDR / Daily Drilling Report)

### Lokasi Output Data Terstruktur
Hasil parsing dan indeksasi akan otomatis dihasilkan dan disimpan pada folder `output/`:
* File JSON: `output/parsed_wells_data.json`
* File Database SQLite: `output/wells_data.db`
* File Cache Vektor Embedding: `output/embeddings_cache.npz`

---

## 3. Instalasi

1. Clone repositori ke komputer lokal:
```bash
git clone https://github.com/Vergiananta/wells-info.git
cd wells-info
```

2. (Opsional) Buat dan aktifkan virtual environment:
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

3. Pasang dependensi yang diperlukan:
```bash
pip install -r requirements.txt
```

---

## 4. Konfigurasi Lingkungan (.env)

1. Salin template `.env.example` menjadi `.env`:
```bash
# Windows (PowerShell)
Copy-Item .env.example .env

# Linux / macOS
cp .env.example .env
```

2. Buka file `.env` dan masukkan API Key OpenAI Anda:
```env
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxx
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_CHAT_MODEL=gpt-4o-mini
```

---

## 5. Perintah Menjalankan Program

### A. Menjalankan Antarmuka Web (Streamlit UI)
Untuk menjalankan aplikasi dengan antarmuka web interaktif:
```bash
python run.py
```
Aplikasi web akan otomatis terbuka di browser pada alamat `http://localhost:8501`.

### B. Menjalankan Mode CLI
Untuk menjalankan pengujian benchmark langsung melalui terminal:
```bash
python run.py --cli
```

### C. Memproses Ulang Dokumen (Force Reparse)
Jika Anda menambahkan file PDF baru berformat serupa ke dalam folder `Datasets/` atau memperbarui glosarium, jalankan perintah reparse tanpa mengubah kode:
```bash
python run.py --cli --reparse
```
Atau klik tombol **"Proses Ulang Dokumen (Reparse)"** pada sidebar antarmuka web.

---

## 6. Dokumentasi Struktur JSON Hasil Parsing

Hasil parsing disimpan dalam file `output/parsed_wells_data.json` dengan format array objek JSON.

### Penjelasan Skema Field JSON:
* `id` (string): Identifikator unik untuk setiap potongan/dokumen (misal: `BARAKUDA-1_DGOS_72_20260829_p1` atau `glossary_chunk_1`).
* `source_file` (string): Nama file dokumen asli (`.pdf` atau `.docx`).
* `doc_type` (string): Tipe dokumen (`DGOS`, `DDR`, `Glossary`, atau `Document Summary`).
* `page` (integer): Nomor halaman dokumen (nilai `0` untuk summary atau docx).
* `total_pages` (integer): Total halaman pada dokumen sumber.
* `title` (string | null): Judul atau topik bagian.
* `category` (string | null): Kategori konten.
* `content` (string): Teks lengkap hasil ekstraksi yang telah dibersihkan.
* `metadata` (object): Metadata terstruktur seperti `well_name`, `region`, `country`, `npt_info`, `wireline_info`, atau daftar istilah glosarium.

### Contoh Data Dummy JSON:
```json
[
  {
    "id": "BARAKUDA-1_DGOS_72_20260829_summary",
    "source_file": "BARAKUDA-1_DGOS_72_20260829.pdf",
    "doc_type": "Document Summary",
    "page": 0,
    "total_pages": 1,
    "title": null,
    "category": null,
    "content": "Dokumen: BARAKUDA-1_DGOS_72_20260829.pdf\nWell Name: BARAKUDA-1\nLokasi / Region / Country: Malaysia (PM Block PM515)\nRingkasan Isi & Metadata:\nDAILY UPDATES Report No. 72 Mud Weight 14.1 SBM Next Update: Perform WL Run #1: PEX-QAIT. Perform WL Run #2: MDT (QS-Saturn).",
    "metadata": {
      "well_name": "BARAKUDA-1",
      "region": "PM (Peninsular Malaysia)",
      "country": "Malaysia",
      "wireline_info": [
        "WL Run #1: PEX-QAIT",
        "WL Run #2: MDT (QS-Saturn)"
      ]
    }
  },
  {
    "id": "glossary_chunk_1",
    "source_file": "Glossaries.docx",
    "doc_type": "Glossary",
    "page": 0,
    "total_pages": 0,
    "title": "Glosarium Istilah Part 1",
    "category": "Oil and Gas Terms",
    "content": "- AFE: Authorization for Expenditure - Approved budget and plan for the well.\n- AMSL: Above Mean Sea Level - Height above average sea level.\n- BHA: Bottom Hole Assembly - Tools at the bottom of the drill string (bit, motor, MWD).",
    "metadata": {
      "terms": [
        "AFE",
        "AMSL",
        "BHA"
      ]
    }
  }
]
```

---

## 7. Planning: Pendekatan, Arsitektur, dan Pemilihan Teknologi

### Pendekatan RAG
* **Hybrid Search (Vektor + Keyword Boost):** Mengombinasikan pencarian vektor semantik (*cosine similarity* pada embedding `text-embedding-3-small`) dengan pencarian kata kunci eksak. Hal ini penting pada domain migas karena kueri pengguna sering memuat kode alat spesifik (seperti *PEX-QAIT*, *MDT (QS-Saturn)*) atau singkatan (*NPT*, *BHA*).
* **Grounding & Guardrails:** Prompt sistem dikonfigurasi ketat agar hanya menjawab berdasarkan dokumen yang diberikan, menyertakan sitasi sumber file rujukan `[Sumber: <nama_file>]`, dan secara konsisten menolak pertanyaan di luar topik migas (*out-of-scope*).

### Arsitektur Clean Code (Uncle Bob)
Sistem backend disusun di dalam direktori `src/backend` dengan pemisahan tanggung jawab yang modular:
* `config.py`: Pengaturan variabel lingkungan dan path file.
* `models.py`: Data Transfer Object domain (`DocumentChunk`, `RetrievalItem`, `ChatAnswer`).
* `parsers/`: Abstraksi parser untuk mengekstrak file PDF sumur dan file DOCX glosarium secara modular dan dapat digunakan kembali (*reusable*).
* `repositories/`: Akses penyimpanan terpisah untuk format JSON (`json_repository.py`), database relasional SQLite dan FTS5 (`database_repository.py`), serta penyimpanan cache vektor (`embedding_repository.py`).
* `services/`: Layer logika bisnis yang terdiri dari `embedding_service.py`, `retrieval_service.py`, `chat_service.py`, dan orkestrator `pipeline_service.py`.

### Alasan Pemilihan Teknologi
* **OpenAI (GPT-4o-mini & text-embedding-3-small):** Memberikan kombinasi optimal antara kecepatan respon (< 2 detik), pemahaman konteks teknis, dan efisiensi biaya/token.
* **SQLite (FTS5):** Menyediakan database relasional tanpa memerlukan setup infrastruktur tambahan (*zero-configuration*), memenuhi kriteria *Nice to have*.
* **Streamlit:** Memungkinkan pembuatan antarmuka web yang responsif, interaktif, dan mudah dioperasikan.
* **PyPDF & Python-docx:** Library parsing dokumen standar yang ringan dan dapat diandalkan tanpa dependensi biner eksternal.

---

## 8. Resolution: Kendala, Solusi, dan Rencana Pengembangan

### Kendala yang Dihadapi & Solusinya
1. **Variasi Format Dokumen PDF Operasional:** Laporan harian sumur (DGOS dan DDR) memiliki format visual berbasis tabel dan blok teks yang padat.
   * *Solusi:* Implementasi ekstraksi berbasis layout halaman dan ekstraksi metadata otomatis (*regular expression pattern matcher*) untuk menangkap entitas penting seperti Nama Sumur, Wilayah, Nilai NPT, dan Rencana Wireline.
2. **Efisiensi Waktu dan Token Embedding:** Menghindari pemanggilan API embedding berulang kali setiap kali aplikasi dijalankan.
   * *Solusi:* Menyimpan cache vektor embedding ke dalam file numpy terkompresi (`embeddings_cache.npz`). Embedding hanya dibuat ulang saat dokumen diparsing ulang (*force reparse*).
3. **Filter Pertanyaan Di Luar Cakupan (Out-of-Scope):**
   * *Solusi:* Menetapkan instruksi guardrail deterministik pada prompt sistem LLM dan menyaring retrieval score agar model menolak pertanyaan di luar topik dengan pesan konsisten.

### Rencana Perbaikan ke Depan (Future Improvements)
1. **Cross-Encoder Re-Ranking:** Menambahkan model re-ranker (misal: Cohere Re-rank atau BGE-Reranker) untuk meningkatkan presisi peringkat dokumen pada kueri yang sangat ambigu.
2. **Optical Character Recognition (OCR):** Menambahkan modul Tesseract / EasyOCR untuk mendukung pembacaan file PDF hasil scan dokumen fisik.
3. **Multi-turn Conversation Memory:** Menyimpan riwayat percakapan dinamis dengan teknik *summary buffer memory* untuk obrolan multi-konteks.
