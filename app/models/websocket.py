from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, Union
from .search import SearchRequest, SearchResponse, LiveUpdateResponse


class WebSocketMessage(BaseModel):
    type: str = Field(..., description="Message type")
    data: Optional[Dict[str, Any]] = None


class SearchMessage(WebSocketMessage):
    type: str = Field(default="search")
    data: SearchRequest


class AudioChunkMessage(WebSocketMessage):
    type: str = Field(default="audio_chunk")
    data: Dict[str, Any] = Field(..., description="Audio data and metadata")


class RecommendationsMessage(WebSocketMessage):
    type: str = Field(default="recommendations")
    data: SearchResponse


class LiveUpdateMessage(WebSocketMessage):
    type: str = Field(default="live_update")
    data: LiveUpdateResponse


class ErrorMessage(WebSocketMessage):
    type: str = Field(default="error")
    data: Dict[str, Any] = Field(..., description="Error details")


class ConnectionMessage(WebSocketMessage):
    type: str = Field(default="connection")
    data: Dict[str, Any] = Field(default_factory=dict, description="Connection info")


class HeartbeatMessage(WebSocketMessage):
    type: str = Field(default="heartbeat")
    data: Dict[str, Any] = Field(default_factory=dict)


# Union type for all possible WebSocket messages
WebSocketMessageType = Union[
    SearchMessage,
    AudioChunkMessage,
    RecommendationsMessage,
    LiveUpdateMessage,
    ErrorMessage,
    ConnectionMessage,
    HeartbeatMessage
]
