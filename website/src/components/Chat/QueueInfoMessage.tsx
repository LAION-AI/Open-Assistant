import { useTranslation } from "next-i18next";
import { QueueInfo } from "src/lib/chat_stream";

export const QueueInfoMessage = ({ info }: { info: QueueInfo }) => {
  const { t } = useTranslation("chat");
  return <>{t("queue_info", info)}</>;
};
