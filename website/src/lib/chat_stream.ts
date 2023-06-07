import { InferenceEvent, InferenceMessage } from "src/types/Chat";

export interface QueueInfo {
  queuePosition: number;
  queueSize: number;
}

export interface PluginIntermediateResponse {
  currentPluginThought: string;
  currentPluginAction: string;
  currentPluginActionResponse: string;
  currentPluginActionInput: string;
}

export interface ChatStreamHandlerOptions {
  stream: ReadableStream<Uint8Array>;
  onError: (err: unknown) => unknown;
  onPending: (info: QueueInfo) => unknown;
  onToken: (partialMessage: string) => unknown;
  onPluginIntermediateResponse: (pluginIntermediateResponse: PluginIntermediateResponse) => unknown;
}

export async function handleChatEventStream({
  stream,
  onError,
  onPending,
  onToken,
  onPluginIntermediateResponse,
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
      } else if (chunk.event_type === "plugin_intermediate") {
        await onPluginIntermediateResponse({
          currentPluginThought: chunk.current_plugin_thought,
          currentPluginAction: chunk.current_plugin_action_taken,
          currentPluginActionResponse: chunk.current_plugin_action_response,
          currentPluginActionInput: chunk.current_plugin_action_input,
        });
      } else {
        console.log("Unexpected event", chunk);
      }
    } catch (e) {
      console.error(`Error parsing data: ${data}, error: ${e}`);
    }
  }
  return null;
}

export async function* iteratorSSE(stream: ReadableStream<Uint8Array>) {
  const reader = stream.pipeThrough(new TextDecoderStream()).getReader();

  let done = false,
    value: string | undefined = "";
  let unfinished_line = "";
  while (!done) {
    ({ value, done } = await reader.read());
    if (done) {
      break;
    }
    if (!value) {
      continue;
    }
    const full_value = unfinished_line + value;
    const lines = full_value.split(/\r?\n/).filter(Boolean);
    // do line buffering - otherwise leads to parsing errors
    if (full_value[full_value.length - 1] !== "\n") {
      unfinished_line = lines.pop();
    } else {
      unfinished_line = "";
    }
    const fields = lines.map((line) => {
      const colonIdx = line.indexOf(":");
      return [line.slice(0, colonIdx), line.slice(colonIdx + 1).trimStart()];
    });
    // yield multiple messages distinctly
    for (const field of fields) {
      yield Object.fromEntries([field]);
    }
  }
}
