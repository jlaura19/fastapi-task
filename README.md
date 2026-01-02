# URL Shortening Service

A simple and efficient URL shortening service built with FastAPI. This service provides a clean REST API for creating shortened URLs and redirecting to original destinations.

## 🚀 Features

- **Fast & Async**: Built with FastAPI and fully asynchronous operations
- **Clean Architecture**: Layered design with separation of concerns (API → Service → Storage)
- **Type-Safe**: Comprehensive type hints and Pydantic validation
- **Collision-Resistant**: Base62 encoding with SHA256 hashing for unique IDs
- **Well-Tested**: Comprehensive test suite with pytest
- **Production-Ready**: Proper error handling, logging, and extensibility
- **Interactive Docs**: Auto-generated Swagger UI and ReDoc documentation

## 📋 Prerequisites

- Python 3.12 or higher
- pip (Python package manager)

## 🛠️ Installation

1. **Clone the repository** (or download the source code):
```bash
git clone <repository-url>
cd fast-api-task
```

2. **Create a virtual environment**:
```bash
python -m venv venv
```

3. **Activate the virtual environment**:

On Windows:
```bash
venv\Scripts\activate
```

On macOS/Linux:
```bash
source venv/bin/activate
```

4. **Install dependencies**:
```bash
pip install -r requirements.txt
```

## 🏃 Running the Service

Start the development server:
```bash
uvicorn app.main:app --reload
```

The service will be available at:
- **API**: http://localhost:8000
- **Interactive Docs (Swagger)**: http://localhost:8000/docs
- **Alternative Docs (ReDoc)**: http://localhost:8000/redoc

## 📡 API Endpoints

### Create a Shortened URL

**Endpoint**: `POST /`

**Request Body**:
```json
{
  "url": "https://example.com/some/long/path"
}
```

**Response** (201 Created):
```json
{
  "short_id": "abc123"
}
```

**Example using curl**:
```bash
curl -X POST "http://localhost:8000/" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/some/long/path"}'
```

**Example using PowerShell**:
```powershell
$body = @{url = "https://example.com/some/long/path"} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8000/" -Method Post -Body $body -ContentType "application/json"
```

### Redirect to Original URL

**Endpoint**: `GET /{short_id}`

**Response**: 307 Temporary Redirect to the original URL

**Example**:
```bash
curl -L "http://localhost:8000/abc123"
```

**Error Response** (404 Not Found):
```json
{
  "detail": "Short ID 'abc123' not found"
}
```

### Health Check

**Endpoint**: `GET /health`

**Response** (200 OK):
```json
{
  "status": "healthy",
  "service": "url-shortener"
}
```

## 🧪 Running Tests

Run the comprehensive test suite:
```bash
pytest tests/ -v
```

Run tests with coverage:
```bash
pytest tests/ -v --cov=app --cov-report=html
```

The test suite includes:
- ✅ Successful URL creation
- ✅ Redirect functionality
- ✅ 404 error handling
- ✅ Invalid URL validation
- ✅ Duplicate URL handling
- ✅ Concurrent request handling
- ✅ Various URL format validation

## 🏗️ Architecture

The service follows a clean, layered architecture:

```
┌─────────────────────────────────────┐
│         API Layer (main.py)         │
│   FastAPI endpoints & validation    │
└─────────────────┬───────────────────┘
                  │
┌─────────────────▼───────────────────┐
│    Service Layer (url_service.py)   │
│   Business logic & ID generation    │
└─────────────────┬───────────────────┘
                  │
┌─────────────────▼───────────────────┐
│     Storage Layer (storage.py)      │
│   Data persistence abstraction      │
└─────────────────────────────────────┘
```

### Key Components

- **`main.py`**: FastAPI application with endpoint definitions
- **`models.py`**: Pydantic models for request/response validation
- **`url_service.py`**: Business logic for URL shortening
- **`storage.py`**: Storage abstraction (currently in-memory)
- **`utils.py`**: Helper functions (ID generation, validation)

### Short ID Generation

The service generates short IDs using:
- **Base62 encoding** (a-zA-Z0-9) for URL-safe identifiers
- **SHA256 hashing** combined with random data for collision resistance
- **6-character IDs** by default (56.8 billion possible combinations)
- **Collision detection** with automatic retry logic

## 🔧 Configuration

### Changing Short ID Length

Edit `app/url_service.py`:
```python
short_id = generate_short_id(original_url, length=8)  # Change from 6 to 8
```

### Using a Different Storage Backend

The storage layer is abstracted, making it easy to swap implementations:

1. Create a new class implementing the `URLStorage` interface in `storage.py`
2. Update the initialization in `main.py`:
```python
# Example: Redis storage
storage = RedisURLStorage(redis_url="redis://localhost:6379")
url_service = URLShortenerService(storage)
```

## 🚀 Production Considerations

For production deployment, consider:

1. **Persistent Storage**: Replace `InMemoryURLStorage` with Redis, PostgreSQL, or MongoDB
2. **Rate Limiting**: Add rate limiting middleware to prevent abuse
3. **Analytics**: Track click counts, referrers, and geographic data
4. **URL Expiration**: Implement TTL (time-to-live) for shortened URLs
5. **Custom Short IDs**: Allow users to specify custom short IDs
6. **Authentication**: Add API key authentication for URL creation
7. **HTTPS**: Deploy behind a reverse proxy with SSL/TLS
8. **Monitoring**: Add logging, metrics, and health checks

## 📝 Error Handling

The API returns appropriate HTTP status codes:

- **201**: URL successfully created
- **307**: Temporary redirect to original URL
- **404**: Short ID not found
- **422**: Invalid URL format (validation error)
- **500**: Internal server error

All errors return a consistent JSON format:
```json
{
  "detail": "Error message describing what went wrong"
}
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is open source and available under the MIT License.

## 👨‍💻 Author

Created as a technical assessment for Python/FastAPI development skills.

---

**Note**: This implementation uses in-memory storage for simplicity. For production use, implement a persistent storage backend (Redis, PostgreSQL, etc.) by extending the `URLStorage` abstract class.
