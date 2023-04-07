import { InferenceEvent, InferenceMessage } from "src/types/Chat";

export interface QueueInfo {
  queuePosition: number;
  queueSize: number;
}

export interface ChatStreamHandlerOptions {
  stream: ReadableStream<Uint8Array>;
  onError: (err: unknown) => unknown;
  onPending: (info: QueueInfo) => unknown;
  onToken: (partialMessage: string) => unknown;
}

export async function handleChatEventStream({
  stream,
  onError,
  onPending,
  onToken,
}: ChatStreamHandlerOptions): Promise<InferenceMessage | null> {
  let tokens = "";
  for await (const { event, data } of iteratorSSE(stream)) {
    if (event === "error") {
      await onError(data);
    } else if (event === "ping") {
      continue;
    }
    try {
      const chunk: InferenceEvent = JSON.parse(data);
      if (chunk.event_type === "pending") {
        await onPending({ queuePosition: chunk.queue_position, queueSize: chunk.queue_size });
      } else if (chunk.event_type === "token") {
        tokens += chunk.text;
        await onToken(tokens);
      } else if (chunk.event_type === "message") {
        // final message
        return chunk.message;
      } else if (chunk.event_type === "error") {
        // handle error
        await onError(chunk.error);
        return chunk.message;
      } else {
        console.error("Unexpected event", chunk);
      }
    } catch (e) {
      console.error(`Error parsing data: ${data}, error: ${e}`);
    }
  }
}

export async function* iteratorSSE(stream: ReadableStream<Uint8Array>) {
  const reader = stream.pipeThrough(new TextDecoderStream()).getReader();

  let done = false,
    value: string | undefined = "";
  while (!done) {
    ({ value, done } = await reader.read());
    if (done) {
      break;
    }
    if (!value) {
      continue;
    }

    const fields = value
      .split(/\r?\n/)
      .filter(Boolean)
      .map((line) => {
        const colonIdx = line.indexOf(":");
        return [line.slice(0, colonIdx), line.slice(colonIdx + 1).trimStart()];
      });

    yield Object.fromEntries(fields);
  }
}
