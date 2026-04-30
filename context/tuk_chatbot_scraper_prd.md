# Product Requirements Document (PRD)

# TU-K Knowledge Engine & Multimedia Web Scraper

## Project Overview

### Project Name
TU-K Knowledge Engine

### Purpose
Develop a scalable Python-based university knowledge extraction system that crawls and processes data from Technical University of Kenya digital platforms and converts it into structured JSON datasets optimized for chatbot retrieval, semantic search, and Retrieval-Augmented Generation (RAG).

The system will:
- Crawl TU-K web properties
- Extract structured content
- Process multimedia assets
- Normalize information
- Store clean JSON knowledge documents
- Prepare data for chatbot ingestion

---

# Objectives

## Primary Objectives

1. Build a scalable web scraping system
2. Extract university knowledge from multiple subdomains
3. Process multimedia content
4. Convert content into structured JSON datasets
5. Support semantic search and chatbot retrieval
6. Enable periodic automated updates
7. Create a maintainable modular architecture

## Secondary Objectives

1. Enable future vector database integration
2. Support AI-powered university assistants
3. Improve accessibility of university information
4. Centralize distributed university knowledge

---

# Scope

## In Scope

### Data Sources
- Publicly accessible TU-K websites
- Public PDFs
- Public research repositories
- Public admissions documents
- Public course materials
- Public announcements
- Public multimedia assets

### Output Formats
- Structured JSON
- Chunked chatbot-ready documents
- Metadata-enriched datasets
- Search-optimized content

### Multimedia Processing
- PDF extraction
- OCR image extraction
- Video transcript extraction
- Audio transcription
- Table extraction

---

# TU-K Subdomains

## Core University Websites

```text
2024.tukenya.ac.ke
admission.tukenya.ac.ke
admissions.tukenya.ac.ke
alumni.tukenya.ac.ke
analytics.tukenya.ac.ke
ar.tukenya.ac.ke
bb01.tukenya.ac.ke
bb02.tukenya.ac.ke
bb03.tukenya.ac.ke
bb04.tukenya.ac.ke
bb05.tukenya.ac.ke
bb06.tukenya.ac.ke
btl.tukenya.ac.ke
btlconference.tukenya.ac.ke
business.tukenya.ac.ke
careers.tukenya.ac.ke
ciwrm.tukenya.ac.ke
clcs.tukenya.ac.ke
csts.tukenya.ac.ke
dev.tukenya.ac.ke
dicts.tukenya.ac.ke
dqa.tukenya.ac.ke
elearning.tukenya.ac.ke
elibrary.tukenya.ac.ke
fscf.tukenya.ac.ke
intake.tukenya.ac.ke
kaishan-training.tukenya.ac.ke
koha2.tukenya.ac.ke
mail.tukenya.ac.ke
media.tukenya.ac.ke
moodletest.tukenya.ac.ke
part-time.tukenya.ac.ke
portal.tukenya.ac.ke
repository.tukenya.ac.ke
research.tukenya.ac.ke
saae.tukenya.ac.ke
sabe.tukenya.ac.ke
sbls.tukenya.ac.ke
sbms.tukenya.ac.ke
sc.tukenya.ac.ke
scat.tukenya.ac.ke
scbse.tukenya.ac.ke
scit.tukenya.ac.ke
scps.tukenya.ac.ke
scst.tukenya.ac.ke
sest.tukenya.ac.ke
sgas.tukenya.ac.ke
shst.tukenya.ac.ke
shtm.tukenya.ac.ke
sics.tukenya.ac.ke
sire.tukenya.ac.ke
smas.tukenya.ac.ke
smpe.tukenya.ac.ke
spas.tukenya.ac.ke
ssgs.tukenya.ac.ke
staff.tukenya.ac.ke
training.tukenya.ac.ke
tuk-timetable.tukenya.ac.ke
tukcu.tukenya.ac.ke
tusoft.tukenya.ac.ke
tusoftbk.tukenya.ac.ke
webconference.tukenya.ac.ke
welfare.tukenya.ac.ke
www.tukenya.ac.ke
```

---

# Functional Requirements

## 1. Website Crawling

### Requirements
- Crawl all publicly accessible pages
- Respect robots.txt
- Handle pagination
- Handle recursive internal links
- Detect duplicate pages
- Track visited URLs
- Support retry logic

### Supported Content Types
- HTML
- PDFs
- DOCX
- PPTX
- Images
- Videos
- Audio files
- CSV/XLSX

---

# 2. HTML Extraction Engine

## Features
- Extract page title
- Extract body text
- Extract headings
- Extract links
- Extract metadata
- Extract structured tables
- Extract contact information
- Extract announcements

## Output
Structured JSON objects.

---

# 3. PDF Processing Engine

## Features
- Detect text-based PDFs
- OCR scanned PDFs
- Extract tables
- Extract metadata
- Extract paragraphs
- Chunk large documents

## Supported Libraries
- pdfplumber
- PyMuPDF
- Camelot
- pytesseract

---

# 4. Image Processing Engine

## Features
- OCR posters
- Extract captions
- Detect contextual text
- Store image metadata

## Use Cases
- Admission posters
- Timetable images
- Event flyers
- Fee notices

---

# 5. Video Processing Engine

## Features
- Extract audio
- Generate transcripts
- Detect timestamps
- Extract topics
- Store transcript chunks

## Supported Tools
- OpenAI Whisper
- ffmpeg

---

# 6. Audio Processing Engine

## Features
- Speech-to-text conversion
- Transcript generation
- Topic extraction
- Metadata extraction

---

# 7. Data Normalization Layer

## Features
- Remove duplicate whitespace
- Remove HTML artifacts
- Standardize dates
- Standardize phone numbers
- Normalize URLs
- Remove navigation clutter

---

# 8. JSON Knowledge Store

## Features
- Categorized datasets
- Metadata support
- Chunked content
- Semantic-search-ready structure
- Version tracking

---

# 9. Metadata System

## Required Metadata
- Source URL
- Date scraped
- Content type
- Subdomain source
- Category
- Department
- Last modified date
- Chunk ID

---

# 10. Scheduler System

## Features
- Daily crawling
- Incremental updates
- Failed job retry
- Change detection
- Scheduled re-indexing

---

# Non-Functional Requirements

## Scalability
- Modular worker architecture
- Queue-based processing
- Parallel scraping support

## Reliability
- Retry mechanisms
- Error logging
- Failure isolation

## Maintainability
- Modular architecture
- Clear directory structure
- Config-driven scraping

## Security
- Respect authentication boundaries
- Avoid private student data
- Avoid scraping restricted resources

## Performance
- Async crawling
- Concurrent downloads
- Efficient chunking
- Incremental scraping

---

# System Architecture

## High-Level Architecture

```text
                 TU-K Websites
                        ↓
                 URL Discovery Engine
                        ↓
                  Recursive Crawler
                        ↓
                 Content-Type Detector
                        ↓
       ┌─────────────────────────────────┐
       │                                 │
 HTML Worker                      Multimedia Workers
       │                                 │
       │               ┌───────────────────────────────┐
       │               │            │          │       │
       ↓               ↓            ↓          ↓       ↓
HTML Parser       PDF Worker   OCR Worker  Video Worker Audio Worker
       │               │            │          │       │
       └───────────────────────────────────────────────┘
                               ↓
                    Data Cleaning & Normalization
                               ↓
                        Chunking Engine
                               ↓
                     JSON Knowledge Generator
                               ↓
                    Structured Knowledge Store
                               ↓
                         Chatbot / RAG Layer
```

---

# Recommended Technology Stack

## Scraping Layer

| Component | Technology |
|---|---|
| Static scraping | requests |
| HTML parsing | BeautifulSoup4 |
| Dynamic rendering | Playwright |
| Async requests | aiohttp |

---

## Multimedia Layer

| Component | Technology |
|---|---|
| PDF extraction | pdfplumber |
| Advanced PDF parsing | PyMuPDF |
| OCR | pytesseract |
| Table extraction | Camelot |
| Speech-to-text | Whisper |
| Video/audio handling | ffmpeg |

---

## Processing Layer

| Component | Technology |
|---|---|
| Validation | Pydantic |
| Queue system | Celery |
| Broker | Redis |
| Logging | loguru |

---

## Storage Layer

| Component | Technology |
|---|---|
| Structured storage | JSON |
| Future vector DB | ChromaDB |
| Optional DB | PostgreSQL |

---

## Backend Layer

| Component | Technology |
|---|---|
| API | FastAPI |
| Background jobs | APScheduler |

---

# Directory Structure

```text
tuk_knowledge_engine/
│
├── crawler/
│   ├── url_discovery.py
│   ├── crawler.py
│   └── robots.py
│
├── workers/
│   ├── html_worker.py
│   ├── pdf_worker.py
│   ├── image_worker.py
│   ├── video_worker.py
│   └── audio_worker.py
│
├── parsers/
│   ├── html_parser.py
│   ├── pdf_parser.py
│   └── metadata_parser.py
│
├── normalizers/
│   ├── text_cleaner.py
│   └── metadata_cleaner.py
│
├── chunkers/
│   └── semantic_chunker.py
│
├── models/
│   └── schemas.py
│
├── storage/
│   ├── json_writer.py
│   └── vector_writer.py
│
├── queue/
│   └── tasks.py
│
├── scheduler/
│   └── scheduler.py
│
├── output/
│   ├── admissions/
│   ├── academics/
│   ├── research/
│   ├── events/
│   └── multimedia/
│
└── main.py
```

---

# Program Flow

# Phase 1 — URL Discovery

```text
Seed Subdomains
       ↓
Fetch HTML
       ↓
Extract Internal Links
       ↓
Validate URLs
       ↓
Add New URLs to Queue
       ↓
Continue Recursively
```

---

# Phase 2 — Content Detection

```text
Downloaded Resource
        ↓
Detect MIME Type
        ↓
Route to Correct Worker
```

Examples:

```text
text/html → HTML Worker
application/pdf → PDF Worker
image/png → OCR Worker
video/mp4 → Video Worker
```

---

# Phase 3 — Processing Pipeline

```text
Raw Content
      ↓
Parser
      ↓
Cleaner
      ↓
Normalizer
      ↓
Metadata Extraction
      ↓
Chunking
      ↓
JSON Generation
```

---

# Phase 4 — Knowledge Storage

```text
Generated JSON
      ↓
Categorize by Domain
      ↓
Store in Output Directories
      ↓
Optional Embedding Generation
```

---

# Multimedia Handling Strategy

## PDFs

### Workflow

```text
PDF Download
      ↓
Determine if OCR Needed
      ↓
Extract Text
      ↓
Extract Tables
      ↓
Chunk Content
      ↓
Generate JSON
```

---

## Images

### Workflow

```text
Image Download
      ↓
OCR Processing
      ↓
Extract Text
      ↓
Extract Metadata
      ↓
Generate JSON
```

---

## Videos

### Workflow

```text
Video Download
      ↓
Extract Audio
      ↓
Speech-to-Text
      ↓
Transcript Cleaning
      ↓
Chunking
      ↓
Generate JSON
```

---

# JSON Schema Design

## Generic Knowledge Object

```json
{
  "id": "doc_001",
  "title": "Admission Requirements",
  "content": "Students applying for...",
  "category": "admissions",
  "source_type": "pdf",
  "source_url": "https://admissions.tukenya.ac.ke",
  "subdomain": "admissions.tukenya.ac.ke",
  "metadata": {
    "department": "Admissions",
    "last_updated": "2026-04-30"
  }
}
```

---

# Chunking Strategy

## Requirements
- 500–1000 word chunks
- Overlapping chunk boundaries
- Semantic chunking where possible
- Preserve metadata per chunk

## Purpose
- Improve chatbot retrieval
- Improve semantic search
- Improve embedding quality

---

# Data Categorization

## Suggested Categories

```text
admissions/
academics/
research/
departments/
contacts/
events/
multimedia/
fees/
student_services/
announcements/
```

---

# Future Enhancements

## Phase 2 Features

- Vector embeddings
- Semantic search
- Real-time updates
- Knowledge graphs
- AI summarization
- Duplicate semantic detection
- Advanced OCR
- Multi-language support

---

# Risks & Mitigation

| Risk | Mitigation |
|---|---|
| Broken pages | Retry mechanisms |
| Duplicate content | Hash detection |
| Large PDFs | Chunked processing |
| Dynamic JS pages | Playwright rendering |
| OCR inaccuracies | Confidence scoring |
| Massive datasets | Queue workers |
| Site structure changes | Config-driven parsers |

---

# Recommended Development Phases

## Phase 1
- Basic crawler
- HTML extraction
- JSON generation

## Phase 2
- PDF support
- OCR support
- Multimedia extraction

## Phase 3
- Queue workers
- Async crawling
- Scheduler

## Phase 4
- Vector database
- Chatbot integration
- Semantic retrieval

---

# Success Metrics

## Technical Metrics
- Successful crawl rate
- Processing speed
- JSON validation success
- OCR accuracy
- Transcript quality

## Chatbot Metrics
- Retrieval accuracy
- Response relevance
- Reduced hallucinations
- Semantic search quality

---

# Conclusion

The TU-K Knowledge Engine is designed as a scalable multimedia-aware university knowledge extraction system capable of transforming distributed university content into structured AI-ready datasets.

The system architecture prioritizes:
- scalability
- maintainability
- semantic retrieval quality
- multimedia handling
- modular processing
- chatbot optimization

The final output will serve as the foundational knowledge layer for a future AI-powered Technical University of Kenya assistant.

