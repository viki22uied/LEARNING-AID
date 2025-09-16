# Open Educational Resources Recommendation Backend

A fully open-source, real-time educational resource recommendation system that provides free, openly-licensed learning materials through semantic search and WebSocket-based streaming recommendations.

## 🚀 Features

- **100% Open Source**: All components, data sources, and recommendations are free and redistributable
- **Real-time Intelligence**: Provides contextual learning resources as users speak or type
- **Legal Compliance**: Strict adherence to open licenses with full attribution and transparency
- **Zero Cost**: No proprietary APIs or paid services required
- **Semantic Search**: Advanced vector-based search using sentence transformers
- **Speech-to-Text**: Real-time audio processing with Whisper
- **WebSocket API**: Real-time bidirectional communication
- **Multi-source Harvesting**: Content from Wikipedia, OpenStax, arXiv, and more

## 🏗️ Architecture

```
[Speech Input] → [STT Engine] → [Concept Extraction] → [Vector Search] → [Recommendation API] → [WebSocket Client]
                                        ↓
[Open Content Sources] → [Harvester] → [Text Processor] → [Embeddings] → [FAISS/Qdrant Index]
```

## 🛠️ Technology Stack

### Core Framework
- **Backend**: FastAPI (Python 3.9+)
- **WebSocket**: FastAPI WebSockets + uvicorn ASGI server
- **Database**: PostgreSQL (primary) + SQLite (development/testing)
- **Caching**: Redis (optional, for session management)

### ML/AI Stack
- **Speech-to-Text**: OpenAI Whisper (`whisper` or `faster-whisper`)
- **Embeddings**: Sentence Transformers (`sentence-transformers`)
- **Vector Database**: Qdrant (persistent, scalable) + FAISS (local development)
- **NLP**: spaCy + KeyBERT for concept extraction

### Content Processing
- **PDF Processing**: PyMuPDF (fitz) + pdfminer.six
- **Web Scraping**: BeautifulSoup4 + newspaper3k + readability-lxml
- **HTTP Client**: aiohttp (async) + requests (sync fallback)

## 📦 Installation

### Prerequisites
- Python 3.9+
- PostgreSQL (or SQLite for development)
- Redis (optional)
- Qdrant (optional, can use FAISS for development)

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd open-edu-backend
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements/dev.txt
   ```

4. **Configure environment**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize database**
   ```bash
   alembic upgrade head
   ```

6. **Start the server**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Docker Setup

1. **Build and run with Docker Compose**
   ```bash
   docker-compose -f docker/docker-compose.yml up --build
   ```

2. **Access the application**
   - API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Database connection string | `postgresql://user:pass@localhost:5432/open_edu_db` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` |
| `EMBEDDINGS_MODEL` | Sentence transformer model | `all-MiniLM-L6-v2` |
| `STT_MODEL` | Whisper model | `whisper-base` |
| `VECTOR_DB_TYPE` | Vector database type | `qdrant` |
| `QDRANT_URL` | Qdrant server URL | `http://localhost:6333` |
| `API_HOST` | API host | `0.0.0.0` |
| `API_PORT` | API port | `8000` |

### Content Sources

The system supports harvesting from multiple open educational sources:

- **Wikipedia/Wikibooks/Wikiversity**: Public Domain/CC-BY-SA
- **OpenStax**: CC-BY 4.0 textbooks
- **OER Commons**: Curated open educational resources
- **arXiv**: Academic preprints
- **MIT OpenCourseWare**: Various open licenses

## 📡 API Usage

### WebSocket API

Connect to the WebSocket endpoint for real-time recommendations:

```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/recommendations/stream');

// Search request
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

// Audio chunk for STT
ws.send(JSON.stringify({
  type: "audio_chunk",
  data: {
    audio_data: "base64_encoded_audio",
    format: "wav",
    is_final: false
  }
}));
```

### REST API

#### Search Resources
```bash
curl -X POST "http://localhost:8000/api/v1/resources/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "machine learning algorithms",
    "filters": {
      "license_types": ["CC-BY-4.0"],
      "max_results": 5
    }
  }'
```

#### List Resources
```bash
curl "http://localhost:8000/api/v1/resources/?limit=10&resource_type=document"
```

#### Get Resource Details
```bash
curl "http://localhost:8000/api/v1/resources/{resource_id}"
```

### Admin API

#### Trigger Content Harvest
```bash
curl -X POST "http://localhost:8000/api/v1/admin/harvest" \
  -H "X-Admin-API-Key: your_admin_key" \
  -H "Content-Type: application/json" \
  -d '{"source": "wikipedia", "subjects": ["mathematics", "physics"]}'
```

#### Get System Stats
```bash
curl "http://localhost:8000/api/v1/admin/stats" \
  -H "X-Admin-API-Key: your_admin_key"
```

## 🔍 Search Features

### Semantic Search
- Vector-based similarity search using sentence transformers
- Support for multiple embedding models
- Configurable similarity thresholds

### Filters
- License type filtering
- Resource type filtering
- Difficulty level filtering
- Language filtering
- Source platform filtering

### Real-time Processing
- Live speech-to-text transcription
- Automatic concept extraction
- Instant recommendation generation

## 📊 Monitoring

### Health Checks
- `/health` - Basic health check
- `/api/v1/status` - Detailed system status
- `/metrics` - Prometheus metrics

### Logging
- Structured JSON logging
- Configurable log levels
- Request/response logging
- Error tracking

## 🧪 Testing

### Run Tests
```bash
pytest tests/
```

### Run with Coverage
```bash
pytest --cov=app tests/
```

### Load Testing
```bash
# Install locust
pip install locust

# Run load test
locust -f tests/load_test.py
```

## 🚀 Deployment

### Production Deployment

1. **Set up production environment**
   ```bash
   pip install -r requirements/prod.txt
   ```

2. **Configure production settings**
   - Set `DATABASE_URL` to production PostgreSQL
   - Configure `QDRANT_URL` for production Qdrant
   - Set `ADMIN_API_KEY` for admin access
   - Configure logging and monitoring

3. **Run with Gunicorn**
   ```bash
   gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker \
     --bind 0.0.0.0:8000 --timeout 300
   ```

### Docker Production
```bash
docker build -f docker/Dockerfile -t open-edu-backend .
docker run -p 8000:8000 open-edu-backend
```

## 📈 Performance

### Response Times
- **WebSocket Connection**: < 100ms
- **Search Query Processing**: < 500ms
- **STT Processing**: < 2s for 10s audio clip
- **Vector Search**: < 200ms for 10k+ embeddings

### Throughput
- **Concurrent WebSocket Connections**: 100+
- **Search Requests per Second**: 50+
- **Harvest Rate**: 1000+ resources per hour

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

### Development Setup
```bash
# Install development dependencies
pip install -r requirements/dev.txt

# Install pre-commit hooks
pre-commit install

# Run code formatting
black app/
isort app/

# Run linting
flake8 app/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) for the web framework
- [Sentence Transformers](https://www.sbert.net/) for semantic search
- [OpenAI Whisper](https://github.com/openai/whisper) for speech recognition
- [Qdrant](https://qdrant.tech/) for vector database
- All open educational content providers

## 📞 Support

For questions, issues, or contributions:
- Create an issue on GitHub
- Join our community discussions
- Check the documentation at `/docs` when running the server

---

**Built with ❤️ for open education**
#   L E A R N I N G - A I D  
 