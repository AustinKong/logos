import type { EventSourceMessage } from "eventsource-parser";
import { createParser } from "eventsource-parser";
import type {
  EventRead,
  HTTPValidationError,
  StreamSessionEventsParams,
  StreamSessionTokensParams,
} from "./generated";
import {
  getStreamSessionEventsUrl,
  getStreamSessionTokensUrl,
} from "./generated";

export type { EventRead } from "./generated";

export interface TokenRead {
  stream_id: string;
  content: string;
}

export function streamSessionEvents(
  sessionId: string,
  params?: StreamSessionEventsParams,
  options?: RequestInit,
): AsyncGenerator<EventRead, void, void> {
  return streamSse<EventRead>(
    getStreamSessionEventsUrl(sessionId, params),
    options,
    "Session event stream response did not include a readable body",
  );
}

export function streamSessionTokens(
  sessionId: string,
  params: StreamSessionTokensParams,
  options?: RequestInit,
): AsyncGenerator<TokenRead, void, void> {
  return streamSse<TokenRead>(
    getStreamSessionTokensUrl(sessionId, params),
    options,
    "Session token stream response did not include a readable body",
  );
}

async function* streamSse<T>(
  url: string,
  options: RequestInit | undefined,
  missingBodyMessage: string,
): AsyncGenerator<T, void, void> {
  const res = await fetch(url, {
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
    throw new Error(missingBodyMessage);
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  const items: T[] = [];
  const parser = createParser({
    onEvent(event: EventSourceMessage) {
      items.push(JSON.parse(event.data) as T);
    },
  });

  while (true) {
    const { done, value } = await reader.read();
    if (done) {
      break;
    }

    parser.feed(decoder.decode(value, { stream: true }));
    while (items.length > 0) {
      yield items.shift() as T;
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
