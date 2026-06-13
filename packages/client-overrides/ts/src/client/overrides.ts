import type { EventSourceMessage } from "eventsource-parser";
import { createParser } from "eventsource-parser";
import type {
  HTTPValidationError,
  ParticipantMessageEventRead,
  ParticipantRemovedEventRead,
  ParticipantVoteEventRead,
  SessionCompletedEventRead,
  SessionStartedEventRead,
} from "./generated";
import { getStreamSessionEventsUrl } from "./generated";

export type EventRead =
  | SessionStartedEventRead
  | SessionCompletedEventRead
  | ParticipantMessageEventRead
  | ParticipantVoteEventRead
  | ParticipantRemovedEventRead;

export async function* streamSessionEvents(
  sessionId: string,
  options?: RequestInit,
): AsyncGenerator<EventRead, void, void> {
  const res = await fetch(getStreamSessionEventsUrl(sessionId), {
    ...options,
    method: "GET",
    headers: {
      Accept: "text/event-stream",
      ...options?.headers,
    },
  });

  if (!res.ok) {
    throw await createApiError(res);
  }

  if (!res.body) {
    throw new Error(
      "Session event stream response did not include a readable body",
    );
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  const events: EventRead[] = [];
  const parser = createParser({
    onEvent(event: EventSourceMessage) {
      events.push(JSON.parse(event.data) as EventRead);
    },
  });

  while (true) {
    const { done, value } = await reader.read();
    if (done) {
      break;
    }

    parser.feed(decoder.decode(value, { stream: true }));
    while (events.length > 0) {
      yield events.shift() as EventRead;
    }
  }
}

async function createApiError(
  res: Response,
): Promise<Error & { info?: HTTPValidationError | string; status?: number }> {
  const body = [204, 205, 304].includes(res.status) ? null : await res.text();
  const contentType = (res.headers.get("content-type") ?? "").toLowerCase();
  const error: Error & {
    info?: HTTPValidationError | string;
    status?: number;
  } = new Error(`Request failed with status ${res.status}`);

  error.info = body
    ? contentType.includes("json")
      ? (JSON.parse(body) as HTTPValidationError)
      : body
    : {};
  error.status = res.status;

  return error;
}
