<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-3776AB?style=flat&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-0.100+-009688?style=flat&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat" />
  <img src="https://img.shields.io/badge/Open%20Source-100%25-brightgreen?style=flat" />
  <img src="https://img.shields.io/badge/Docker-Ready-2496ED?style=flat&logo=docker&logoColor=white" />
</p>

<h1 align="center">LEARNING-AID</h1>
<h3 align="center">Open Educational Resources Recommendation Backend</h3>

<p align="center">
  A real-time, fully open-source backend that surfaces free, openly-licensed learning materials the moment students need them — powered by semantic search, speech recognition, and WebSocket streaming.
</p>

---

## What It Does

Students shouldn't have to search for learning materials. LEARNING-AID listens as they speak or type, extracts the concepts they're engaging with, and streams relevant open educational resources back in real time — all from free, openly-licensed sources like Wikipedia, OpenStax, and arXiv.

No proprietary APIs. No paid services. No licensing headaches. Every recommendation is traceable to a source you can legally use, share, and redistribute.

```
[Speech / Text Input]
        ↓
[STT Engine — Whisper]
        ↓
[Concept Extraction — spaCy + KeyBERT]
        ↓
[Vector Search — FAISS / Qdrant]
        ↓
[WebSocket Stream → Client]
        ↑
[Content Harvester] ← [Wikipedia · OpenStax · arXiv · OER Commons · MIT OCW]
```

---

## Features

| Feature | Details |
|---|---|
| 🔍 **Semantic Search** | Vector similarity search via Sentence Transformers — finds conceptually relevant content, not just keyword matches |
| 🎙️ **Real-time Speech-to-Text** | Live audio processing with OpenAI Whisper, streamed over WebSocket |
| ⚡ **WebSocket API** | Bidirectional real-time communication — results stream as concepts are detected |
| 📚 **Multi-source Harvesting** | Pulls from Wikipedia, OpenStax, arXiv, OER Commons, MIT OpenCourseWare |
| ✅ **License Compliance** | Every resource tagged with its open license (CC-BY, CC-BY-SA, Public Domain) — full attribution built in |
| 💰 **Zero Cost** | No paid APIs, no proprietary services — fully reproducible on open infrastructure |
| 🐳 **Docker Ready** | One command to spin up the full stack including vector DB and cache |
| 📊 **Prometheus Metrics** | Built-in observability — health checks, structured logging, request tracing |

---

## Tech Stack

### Backend
- **[FastAPI](https://fastapi.tiangolo.com/)** — async Python web framework with built-in OpenAPI docs
- **[uvicorn](https://www.uvicorn.org/)** — ASGI server for WebSocket and async support
- **PostgreSQL** — primary database · **SQLite** for development/testing
- **Redis** — optional session management and caching

### ML / AI
- **[OpenAI Whisper](https://github.com/openai/whisper)** (`whisper` or `faster-whisper`) — speech-to-text
- **[Sentence Transformers](https://www.sbert.net/)** — semantic embeddings (`all-MiniLM-L6-v2` default)
- **[Qdrant](https://qdrant.tech/)** — persistent vector database for production
- **[FAISS](https://faiss.ai/)** — local vector search for development
- **[spaCy](https://spacy.io/) + [KeyBERT](https://github.com/MaartenGr/KeyBERT)** — NLP concept extraction

### Content Processing
- **PyMuPDF (fitz) + pdfminer.six** — PDF parsing
- **BeautifulSoup4 + newspaper3k + readability-lxml** — web content extraction
- **aiohttp** — async HTTP client for harvesting

---

## Performance

| Metric | Target |
|---|---|
| WebSocket connection latency | < 100ms |
| Search query processing | < 500ms |
| STT processing (10s audio) | < 2s |
| Vector search (10k+ embeddings) | < 200ms |
| Concurrent WebSocket connections | 100+ |
| Search requests per second | 50+ |
| Content harvest rate | 1,000+ resources/hour |

---

## Getting Started

### Prerequisites

- Python 3.9+
- PostgreSQL (or SQLite for development)
- Redis *(optional)*
- Qdrant *(optional — FAISS used as fallback in development)*

### Local Setup

**1. Clone the repository**
```bash
git clone <repo-url>
cd open-edu-backend
```

**2. Create and activate virtual environment**
```bash
python -m venv venv
source venv/bin/activate       # macOS / Linux
venv\Scripts\activate          # Windows
```

**3. Install dependencies**
```bash
pip install -r requirements/dev.txt
```

**4. Configure environment**
```bash
cp env.example .env
# Edit .env with your local configuration
```

**5. Initialize the database**
```bash
alembic upgrade head
```

**6. Start the server**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be live at `http://localhost:8000`
Interactive docs at `http://localhost:8000/docs`

---

### Docker Setup *(recommended)*

```bash
docker-compose -f docker/docker-compose.yml up --build
```

| Service | URL |
|---|---|
| API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |
| Health Check | http://localhost:8000/health |

---

## Configuration

### Environment Variables

| Variable | Description | Default |
|---|---|---|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@localhost:5432/open_edu_db` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` |
| `EMBEDDINGS_MODEL` | Sentence Transformer model name | `all-MiniLM-L6-v2` |
| `STT_MODEL` | Whisper model size | `whisper-base` |
| `VECTOR_DB_TYPE` | Vector DB backend (`qdrant` or `faiss`) | `qdrant` |
| `QDRANT_URL` | Qdrant server URL | `http://localhost:6333` |
| `API_HOST` | Server bind host | `0.0.0.0` |
| `API_PORT` | Server bind port | `8000` |
| `ADMIN_API_KEY` | Admin endpoint authentication key | *(required in production)* |

### Content Sources

| Source | License | Content Type |
|---|---|---|
| Wikipedia / Wikibooks / Wikiversity | Public Domain · CC-BY-SA | Encyclopedia, textbooks, courses |
| OpenStax | CC-BY 4.0 | Peer-reviewed textbooks |
| OER Commons | Various open licenses | Curated educational resources |
| arXiv | Various open licenses | Academic preprints and papers |
| MIT OpenCourseWare | CC-BY-NC-SA | University course materials |

---

## API Reference

### WebSocket API

Connect to `/api/v1/recommendations/stream` for real-time recommendations.

**Semantic search request:**
```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/recommendations/stream');

ws.send(JSON.stringify({
  type: "search",
  data: {
    query: "neural networks and machine learning",
    filters: {
      license_types: ["CC-BY", "CC-BY-SA", "Public Domain"],
      resource_types: ["document", "video"],
      max_results: 10
    }
  }
}));
```

**Live audio streaming (speech-to-text):**
```javascript
ws.send(JSON.stringify({
  type: "audio_chunk",
  data: {
    audio_data: "<base64_encoded_audio>",
    format: "wav",
    is_final: false
  }
}));
```

---

### REST API

**Search resources**
```bash
POST /api/v1/resources/search
```
```json
{
  "query": "machine learning algorithms",
  "filters": {
    "license_types": ["CC-BY-4.0"],
    "max_results": 5
  }
}
```

**List resources**
```bash
GET /api/v1/resources/?limit=10&resource_type=document
```

**Get resource by ID**
```bash
GET /api/v1/resources/{resource_id}
```

---

### Admin API

All admin endpoints require the `X-Admin-API-Key` header.

**Trigger content harvest**
```bash
POST /api/v1/admin/harvest
```
```json
{
  "source": "wikipedia",
  "subjects": ["mathematics", "physics"]
}
```

**Get system stats**
```bash
GET /api/v1/admin/stats
```

---

## Monitoring

### Health Endpoints

| Endpoint | Purpose |
|---|---|
| `GET /health` | Basic liveness check |
| `GET /api/v1/status` | Detailed system status (DB, vector DB, cache) |
| `GET /metrics` | Prometheus-compatible metrics |

### Logging

Structured JSON logging across all services. Configure via `LOG_LEVEL` in `.env`. Request/response logging and error tracking included out of the box.

---

## Testing

**Run the full test suite**
```bash
pytest tests/
```

**Run with coverage report**
```bash
pytest --cov=app tests/
```

**Load testing with Locust**
```bash
pip install locust
locust -f tests/load_test.py
```

---

## Deployment

### Production with Gunicorn

```bash
pip install -r requirements/prod.txt

gunicorn app.main:app \
  -w 4 \
  -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 300
```

### Production Checklist

- [ ] Set `DATABASE_URL` to production PostgreSQL instance
- [ ] Set `QDRANT_URL` to production Qdrant instance
- [ ] Set a strong `ADMIN_API_KEY`
- [ ] Configure Redis for session management
- [ ] Set `LOG_LEVEL=INFO` and point logs to your observability stack
- [ ] Run `alembic upgrade head` on first deploy

### Docker (Production)

```bash
docker build -f docker/Dockerfile -t learning-aid .
docker run -p 8000:8000 --env-file .env learning-aid
```

---

## Contributing

Contributions are welcome. Please follow the standard fork → branch → PR flow.

```bash
# Install dev dependencies and pre-commit hooks
pip install -r requirements/dev.txt
pre-commit install

# Format and lint before committing
black app/
isort app/
flake8 app/
```

For significant changes, open an issue first to discuss the approach. All new functionality should include tests.

---

## License

MIT — see [LICENSE](LICENSE) for details.

---

## Acknowledgements

- [FastAPI](https://fastapi.tiangolo.com/) — the web framework powering this backend
- [Sentence Transformers](https://www.sbert.net/) — semantic search embeddings
- [OpenAI Whisper](https://github.com/openai/whisper) — open speech recognition
- [Qdrant](https://qdrant.tech/) — vector database
- Every open educational content provider making knowledge freely available

---

## About (GitHub Repository Settings)

- **Description:** Real-time open-education recommendation backend + Next.js frontend — semantic search, Whisper STT, vector search (FAISS/Qdrant) over Wikipedia/OpenStax/arXiv.
- **Website:** `http://localhost:8000/docs` (or your deployed URL)
- **Topics:** `nextjs` `fastapi` `open-education` `oer` `whisper` `vector-search` `faiss` `qdrant` `ai` `education` `typescript` `python`
- **Tags:** See `RECONSTRUCTED_HISTORY` — `v0.1.0`, `v0.5.0`, `v1.0.0`

> To set these on GitHub: Repo → Settings → General → About → Edit (add description/website/topics) and `git push --tags`.

---

<p align="center">Built for open education · MIT Licensed · PRs welcome</p>
