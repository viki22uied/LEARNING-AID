from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import List, Dict, Any
import json
import logging
import time
import uuid
from app.models.websocket import (
    SearchMessage, AudioChunkMessage, RecommendationsMessage, 
    LiveUpdateMessage, ErrorMessage, WebSocketMessageType
)
from app.models.search import SearchRequest, SearchResponse, LiveTranscript, LiveUpdateResponse
from app.services.search import SearchService
from app.services.ml.stt import stt_service
from app.services.ml.concept_extractor import ConceptExtractor

logger = logging.getLogger(__name__)

router = APIRouter()

# Global services
search_service = SearchService()
concept_extractor = ConceptExtractor()


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            self.disconnect(websocket)

    async def broadcast(self, message: str):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error broadcasting message: {e}")
                disconnected.append(connection)
        
        # Remove disconnected connections
        for connection in disconnected:
            self.disconnect(connection)


manager = ConnectionManager()


@router.websocket("/recommendations/stream")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_text()
            
            try:
                # Parse message
                message_data = json.loads(data)
                message_type = message_data.get("type", "")
                
                if message_type == "search":
                    await handle_search_message(websocket, message_data)
                elif message_type == "audio_chunk":
                    await handle_audio_chunk_message(websocket, message_data)
                elif message_type == "heartbeat":
                    await handle_heartbeat_message(websocket, message_data)
                else:
                    await send_error_message(websocket, f"Unknown message type: {message_type}")
                    
            except json.JSONDecodeError:
                await send_error_message(websocket, "Invalid JSON format")
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                await send_error_message(websocket, f"Processing error: {str(e)}")
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


async def handle_search_message(websocket: WebSocket, message_data: Dict[str, Any]):
    """Handle search request messages"""
    start_time = time.time()
    
    try:
        # Parse search request
        search_request = SearchRequest(**message_data.get("data", {}))
        
        # Perform search
        search_response = await search_service.search(search_request)
        
        # Calculate processing time
        processing_time = int((time.time() - start_time) * 1000)
        search_response.processing_time_ms = processing_time
        
        # Send response
        response_message = RecommendationsMessage(
            data=search_response
        )
        
        await manager.send_personal_message(
            response_message.model_dump_json(),
            websocket
        )
        
        logger.info(f"Search completed in {processing_time}ms")
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        await send_error_message(websocket, f"Search failed: {str(e)}")


async def handle_audio_chunk_message(websocket: WebSocket, message_data: Dict[str, Any]):
    """Handle audio chunk messages for real-time transcription"""
    start_time = time.time()
    
    try:
        audio_data = message_data.get("data", {})
        audio_base64 = audio_data.get("audio_data", "")
        audio_format = audio_data.get("format", "wav")
        is_final = audio_data.get("is_final", False)
        
        if not audio_base64:
            await send_error_message(websocket, "No audio data provided")
            return
        
        # Transcribe audio
        transcription_result = await stt_service.transcribe_base64(audio_base64, audio_format)
        
        # Create live transcript
        transcript = LiveTranscript(
            text=transcription_result["text"],
            confidence=transcription_result.get("language_probability", 0.9),
            is_final=is_final
        )
        
        # Extract concepts for auto-recommendations
        auto_recommendations = None
        if is_final and transcript.text.strip():
            concepts = await concept_extractor.extract_concepts(transcript.text)
            
            if concepts:
                # Get recommendations for the first concept
                search_request = SearchRequest(
                    query=concepts[0],
                    filters=message_data.get("data", {}).get("filters"),
                    preferences=message_data.get("data", {}).get("preferences")
                )
                
                search_response = await search_service.search(search_request)
                
                auto_recommendations = [{
                    "trigger_concept": concepts[0],
                    "resources": search_response.results[:3],  # Top 3 results
                    "confidence": 0.8
                }]
        
        # Calculate processing time
        processing_time = int((time.time() - start_time) * 1000)
        
        # Create live update response
        live_update = LiveUpdateResponse(
            transcript=transcript,
            auto_recommendations=auto_recommendations,
            processing_time_ms=processing_time
        )
        
        # Send response
        response_message = LiveUpdateMessage(data=live_update)
        
        await manager.send_personal_message(
            response_message.model_dump_json(),
            websocket
        )
        
        logger.info(f"Audio transcription completed in {processing_time}ms")
        
    except Exception as e:
        logger.error(f"Audio processing error: {e}")
        await send_error_message(websocket, f"Audio processing failed: {str(e)}")


async def handle_heartbeat_message(websocket: WebSocket, message_data: Dict[str, Any]):
    """Handle heartbeat messages"""
    try:
        response = {
            "type": "heartbeat",
            "data": {
                "timestamp": time.time(),
                "status": "alive"
            }
        }
        
        await manager.send_personal_message(
            json.dumps(response),
            websocket
        )
        
    except Exception as e:
        logger.error(f"Heartbeat error: {e}")


async def send_error_message(websocket: WebSocket, error_message: str):
    """Send error message to client"""
    try:
        error_response = ErrorMessage(
            data={
                "error": error_message,
                "timestamp": time.time()
            }
        )
        
        await manager.send_personal_message(
            error_response.model_dump_json(),
            websocket
        )
        
    except Exception as e:
        logger.error(f"Error sending error message: {e}")
