import { QueueInfo } from "src/lib/chat_stream";

// TODO: localize
export const QueueInfoMessage = ({ info }: { info: QueueInfo }) => {
  return <div>Your message is queued, you are at position {info.queuePosition} in the queue</div>;
};
