from sse_starlette import EventSourceResponse


class ServerSentEventResponse(EventSourceResponse):
    media_type = "text/event-stream"
