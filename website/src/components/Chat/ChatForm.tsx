import { Button, Grid, Textarea, Box, useBreakpointValue } from "@chakra-ui/react";
import { useTranslation } from "next-i18next";
import { forwardRef, KeyboardEvent, SyntheticEvent, useCallback } from "react";
import TextareaAutosize from "react-textarea-autosize";
import { QueueInfo } from "src/lib/chat_stream";

import { ChatConfigDrawer } from "./ChatConfigDrawer";
import { QueueInfoMessage } from "./QueueInfoMessage";
import { PluginsChooser } from "./PluginsChooser";

type ChatFormProps = {
  isSending: boolean;
  onSubmit: () => void;
  queueInfo: QueueInfo | null;
};

// eslint-disable-next-line react/display-name
export const ChatForm = forwardRef<HTMLTextAreaElement, ChatFormProps>((props, ref) => {
  const { isSending, onSubmit: onSubmit, queueInfo } = props;
  const { t } = useTranslation("common");
  const handleSubmit = useCallback(
    (e: SyntheticEvent) => {
      e.preventDefault();
      onSubmit();
    },
    [onSubmit]
  );
  const handleKeydown = useCallback(
    (e: KeyboardEvent) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault(); // Prevents the addition of a new line
        onSubmit();
      }
    },
    [onSubmit]
  );
  return (
    <form onSubmit={handleSubmit}>
      <Textarea
        as={TextareaAutosize}
        ref={ref}
        bg="gray.100"
        borderRadius="xl"
        onKeyDown={handleKeydown}
        _dark={{
          bg: "gray.800",
        }}
      />
      <Grid
        gridTemplateColumns="1fr 350px"
        gap={2}
        mt="4"
        gridTemplateColumns={useBreakpointValue({ base: "1fr", md: "1fr 350px" })}
      >
        <Button
          type="submit"
          onClick={handleSubmit}
          isLoading={isSending}
          overflow="hidden"
          spinner={queueInfo ? <QueueInfoMessage info={queueInfo} /> : undefined}
          size="lg"
          borderRadius="xl"
        >
          {t("submit")}
        </Button>
        <Box display="flex" justifyContent="flex-end" gap={2}>
          <PluginsChooser />
          <ChatConfigDrawer />
        </Box>
      </Grid>
    </form>
  );
});
