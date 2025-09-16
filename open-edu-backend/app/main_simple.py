from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
import logging
from typing import List, Dict, Any
import os
import tempfile

from app.config import settings

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
	title="Open Educational Resources Recommendation Backend",
	description="A fully open-source, real-time educational resource recommendation system",
	version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
	CORSMiddleware,
	allow_origins=settings.cors_origins,
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)


@app.get("/")
async def root():
	"""Root endpoint"""
	return {
		"message": "Open Educational Resources Recommendation Backend",
		"version": "1.0.0",
		"status": "running"
	}


@app.get("/health")
async def health_check():
	"""Basic health check"""
	return {
		"status": "healthy",
		"timestamp": time.time(),
		"services": {
			"api": "running",
			"database": "not_configured",
			"ml_services": "not_configured"
		}
	}


@app.get("/api/v1/status")
async def detailed_status():
	"""Detailed system status"""
	return {
		"status": "operational",
		"timestamp": time.time(),
		"configuration": {
			"api_host": settings.api_host,
			"api_port": settings.api_port,
			"database_url": "not_configured",
			"vector_db_type": settings.vector_db_type
		},
		"services": {
			"api": {
				"status": "running",
				"version": "1.0.0"
			},
			"database": {
				"status": "not_configured",
				"message": "Database not yet implemented"
			},
			"ml_services": {
				"status": "not_configured",
				"message": "ML services not yet implemented"
			}
		}
	}


def _extract_keywords_simple(text: str, max_terms: int = 5) -> List[str]:
	stop = {
		"the","and","a","an","to","of","in","on","for","with","as","by","is","are","be","or","at","that","this","it","from","your","you","we","they","their","our","about","into","can","will","not","have","has","had"
	}
	words: Dict[str,int] = {}
	for raw in text.lower().replace("\n"," ").split():
		w = ''.join(ch for ch in raw if ch.isalnum() or ch=='-')
		if len(w) < 4 or w in stop:
			continue
		words[w] = words.get(w,0)+1
	return [w for w,_ in sorted(words.items(), key=lambda kv: kv[1], reverse=True)[:max_terms]]


async def _fetch_wikipedia_recommendations(keywords: List[str], max_per_kw: int = 2) -> List[Dict[str,Any]]:
	try:
		from app.services.harvester.wikipedia import WikipediaHarvester
	except Exception:
		return []
	recs: List[Dict[str,Any]] = []
	try:
		async with WikipediaHarvester() as wiki:
			for kw in keywords:
				articles = await wiki.search_articles(kw, limit=max_per_kw)
				for art in articles[:max_per_kw]:
					recs.append({
						"id": f"wiki-{art.get('title','').replace(' ','_')}",
						"title": art.get("title",""),
						"description": art.get("description",""),
						"type": "document",
						"url": art.get("url",""),
						"relevanceScore": 80,
						"difficulty": "beginner",
						"source": "Wikipedia",
						"credibilityScore": 90,
						"thumbnail": None,
						"isBookmarked": False,
						"readingTime": 15,
					})
		return recs
	except Exception as e:
		logger.error(f"Wikipedia fetch error: {e}")
		return recs


async def _transcribe_audio_tempfile(file_bytes: bytes, filename: str) -> Dict[str, Any]:
	"""Transcribe using faster-whisper if available; supports wav/webm; mp3 requires ffmpeg installed."""
	try:
		from faster_whisper import WhisperModel
	except Exception:
		return {"text": "", "segments": [], "note": "faster-whisper not installed"}

	suffix = os.path.splitext(filename)[1] or ".wav"
	with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tf:
		tf.write(file_bytes)
		temp_path = tf.name

	try:
		model = WhisperModel("base", device="cpu", compute_type="int8")
		segments, info = model.transcribe(temp_path, beam_size=5)
		seg_list = []
		full = []
		for s in segments:
			seg_list.append({
				"text": s.text.strip(),
				"timestamp": float(getattr(s, 'start', 0.0) or 0.0),
				"confidence": float(getattr(s, 'avg_logprob', -1.0) or -1.0),
			})
			full.append(s.text)
		return {"text": " ".join(full).strip(), "segments": seg_list}
	except Exception as e:
		logger.error(f"STT error: {e}")
		return {"text": "", "segments": [], "note": str(e)}
	finally:
		try:
			os.unlink(temp_path)
		except Exception:
			pass

def _extract_keywords_simple(text: str, max_terms: int = 5) -> List[str]:
	stop = {
		"the","and","a","an","to","of","in","on","for","with","as","by","is","are","be","or","at","that","this","it","from","your","you","we","they","their","our","about","into","can","will","not","have","has","had"
	}
	words: Dict[str,int] = {}
	for raw in text.lower().replace("\n"," ").split():
		w = ''.join(ch for ch in raw if ch.isalnum() or ch=='-')
		if len(w) < 4 or w in stop:
			continue
		words[w] = words.get(w,0)+1
	return [w for w,_ in sorted(words.items(), key=lambda kv: kv[1], reverse=True)[:max_terms]]


async def _fetch_wikipedia_recommendations(keywords: List[str], max_per_kw: int = 2) -> List[Dict[str,Any]]:
	try:
		from app.services.harvester.wikipedia import WikipediaHarvester
	except Exception:
		return []
	recs: List[Dict[str,Any]] = []
	try:
		async with WikipediaHarvester() as wiki:
			for kw in keywords:
				articles = await wiki.search_articles(kw, limit=max_per_kw)
				for art in articles[:max_per_kw]:
					recs.append({
						"id": f"wiki-{art.get('title','').replace(' ','_')}",
						"title": art.get("title",""),
						"description": art.get("description",""),
						"type": "document",
						"url": art.get("url",""),
						"relevanceScore": 80,
						"difficulty": "beginner",
						"source": "Wikipedia",
						"credibilityScore": 90,
						"thumbnail": None,
						"isBookmarked": False,
						"readingTime": 15,
					})
		return recs
	except Exception as e:
		logger.error(f"Wikipedia fetch error: {e}")
		return recs


@app.post("/api/v1/analyze")
async def analyze_audio(audio: UploadFile = File(...)):
	"""Analyze uploaded audio: real STT if available, else quick fallback; then Wikipedia resources by keywords."""
	try:
		data = await audio.read()
		# Try real STT
		stt = await _transcribe_audio_tempfile(data, audio.filename or "audio.wav")
		transcript_text = (stt.get("text") or "").strip()
		segments: List[Dict[str,Any]] = stt.get("segments", [])
		# Fallback to filename if STT unavailable
		if not transcript_text:
			base = os.path.splitext(os.path.basename(audio.filename or "audio"))[0]
			transcript_text = base.replace("_"," ").replace("-"," ")[:500]

		# Extract keywords and fetch Wikipedia
		keywords = _extract_keywords_simple(transcript_text) if transcript_text else []
		if not keywords:
			keywords = ["machine learning", "neural networks"]
		recommendations = await _fetch_wikipedia_recommendations(keywords, max_per_kw=3)
		concepts = [{"term": kw.title(), "category": "keyword", "relevance": 80 - i*5, "confidence": 0.8} for i,kw in enumerate(keywords[:5])]

		return {
			"transcript": {"text": transcript_text},
			"segments": segments,
			"concepts": concepts,
			"recommendations": recommendations,
		}
	except Exception as e:
		logger.error(f"Analyze error: {e}")
		raise HTTPException(status_code=500, detail="Analyze failed")


@app.get("/api/v1/resources")
async def list_resources():
	"""List resources (placeholder)"""
	return {
		"resources": [],
		"total": 0,
		"message": "Resource database not yet implemented"
	}


@app.post("/api/v1/resources/search")
async def search_resources():
	"""Search resources (placeholder)"""
	return {
		"results": [],
		"total_results": 0,
		"message": "Search functionality not yet implemented"
	}


if __name__ == "__main__":
	import uvicorn
	uvicorn.run(
		"app.main_simple:app",
		host=settings.api_host,
		port=settings.api_port,
		reload=True
	)
