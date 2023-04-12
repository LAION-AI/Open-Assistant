import { iteratorSSE } from "./chat_stream";

function streamFromIt(it) {
  return new ReadableStream({
    async pull(controller) {
      const { value, done } = await it.next();

      if (done) {
        controller.close();
      } else {
        controller.enqueue(value);
      }
    },
  });
}

async function* generatorFromList(inpList: Array<string>) {
  for (const inp of inpList) {
    yield new TextEncoder().encode(inp);
  }
}

describe("iteratorSSE", () => {
  it("iteratorSSE line-buffering", async () => {
    const inputs = ["dat", "a: {", '"test": "123"}\n'];
    const outputs = [{ data: '{"test": "123"}' }];
    let idx = 0;

    for await (const res of iteratorSSE(streamFromIt(generatorFromList(inputs)))) {
      expect(res).toEqual(outputs[idx]);
      idx += 1;
    }
    expect(idx).toBe(outputs.length);
  });

  it("iteratorSSE line-buffering \\r\\n", async () => {
    const inputs = ["dat", "a: {", '"test": "123"}\r\n'];
    const outputs = [{ data: '{"test": "123"}' }];
    let idx = 0;

    for await (const res of iteratorSSE(streamFromIt(generatorFromList(inputs)))) {
      expect(res).toEqual(outputs[idx]);
      idx += 1;
    }
    expect(idx).toBe(outputs.length);
  });

  it("iteratorSSE line-buffering2", async () => {
    const inputs = ["test:", "\n"];
    const outputs = [{ test: "" }];
    let idx = 0;

    for await (const res of iteratorSSE(streamFromIt(generatorFromList(inputs)))) {
      expect(res).toEqual(outputs[idx]);
      idx += 1;
    }
    expect(idx).toBe(outputs.length);
  });

  it("iteratorSSE multiple lines ", async () => {
    const inputs = ['data: {"test": "123"}\ndata: {"test": "234"}\n'];
    const outputs = [{ data: '{"test": "123"}' }, { data: '{"test": "234"}' }];
    let idx = 0;

    for await (const res of iteratorSSE(streamFromIt(generatorFromList(inputs)))) {
      expect(res).toEqual(outputs[idx]);
      idx += 1;
    }
    expect(idx).toBe(outputs.length);
  });

  it("iteratorSSE multiple lines - unfinished line ", async () => {
    const inputs = ['data: {"test": "123"}\ndata: {"test": "234"}\ndata: {"test": "', '345"}\n'];
    const outputs = [{ data: '{"test": "123"}' }, { data: '{"test": "234"}' }, { data: '{"test": "345"}' }];
    let idx = 0;

    for await (const res of iteratorSSE(streamFromIt(generatorFromList(inputs)))) {
      expect(res).toEqual(outputs[idx]);
      idx += 1;
    }
    expect(idx).toBe(outputs.length);
  });

  it("iteratorSSE multiple lines - unfinished line no end", async () => {
    const inputs = ['data: {"test": "123"}\ndata: {"test": "234"}\ndata: {"test": "', '345"}'];
    const outputs = [{ data: '{"test": "123"}' }, { data: '{"test": "234"}' }];
    let idx = 0;

    for await (const res of iteratorSSE(streamFromIt(generatorFromList(inputs)))) {
      expect(res).toEqual(outputs[idx]);
      idx += 1;
    }
    expect(idx).toBe(outputs.length);
  });
});
