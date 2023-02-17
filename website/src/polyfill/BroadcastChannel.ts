if (typeof globalThis.BroadcastChannel === "undefined") {
  const noop = () => {
    //noop
  };

  // TODO: this exists to make server side rendering works on node 16.x
  // if we update to node 18, we can remove this
  globalThis.BroadcastChannel = class {
    postMessage = noop;
    addEventListener = noop;
    removeEventListener = noop;
  } as any;
}

export {};
