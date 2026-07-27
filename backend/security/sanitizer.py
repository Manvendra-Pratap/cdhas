import re
import html
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from backend.config import settings
from backend.utils.logger import get_logger

logger = get_logger("security.sanitizer")

def sanitize_text(text: str) -> str:
    """Sanitizes user input string by escaping HTML characters and trimming control characters."""
    if not isinstance(text, str):
        return text
    # Escapes <, >, &, ", '
    escaped = html.escape(text.strip())
    # Remove null bytes or non-printable control characters
    sanitized = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", escaped)
    return sanitized

class RequestSanitizerMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_bytes: int = 10_485_760): # 10 MB default max payload size
        super().__init__(app)
        self.max_bytes = max_bytes

    async def dispatch(self, request: Request, call_next):
        # Validate request Content-Length header size
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                length_bytes = int(content_length)
                if length_bytes > self.max_bytes:
                    logger.warning(f"Request payload size {length_bytes} bytes exceeds max limit {self.max_bytes} bytes.")
                    return JSONResponse(
                        status_code=413,
                        content={
                            "status_code": 413,
                            "error_code": "PAYLOAD_TOO_LARGE",
                            "message": f"Request body size exceeds limit of {self.max_bytes} bytes.",
                        }
                    )
            except ValueError:
                pass

        response = await call_next(request)
        return response
