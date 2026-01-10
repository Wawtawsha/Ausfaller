"""
Social Scraper - Entry point

Run the FastAPI server:
    python main.py

Or use uvicorn directly:
    uvicorn src.api.server:app --reload --host 0.0.0.0 --port 8080

API docs available at:
    http://localhost:8080/docs
"""

import uvicorn
from config.settings import settings


def main():
    print("=" * 50)
    print("Social Scraper API v0.2.0")
    print("=" * 50)
    print(f"Server: http://{settings.host}:{settings.port}")
    print(f"Docs:   http://localhost:{settings.port}/docs")
    print(f"Gemini: {'configured' if settings.gemini_api_key else 'NOT configured'}")
    print("=" * 50)

    uvicorn.run(
        "src.api.server:app",
        host=settings.host,
        port=settings.port,
        reload=True,
    )


if __name__ == "__main__":
    main()
