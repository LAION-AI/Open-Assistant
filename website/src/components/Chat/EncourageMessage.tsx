import { Box, Button, ButtonProps, Card, Flex } from "@chakra-ui/react";
import { ThumbsDown, ThumbsUp, X } from "lucide-react";
import { useTranslation } from "next-i18next";

import { messageEntryContainerProps } from "./ChatMessageEntry";

export const EncourageMessage = ({
  onClose,
  onThumbsDown,
  onThumbsUp,
}: {
  onThumbsUp: () => void;
  onThumbsDown: () => void;
  onClose: () => void;
}) => {
  const { t } = useTranslation("chat");

  return (
    <Box {...messageEntryContainerProps}>
      <Card
        fontWeight="normal"
        p="4"
        flexDirection="row"
        gap="2"
        alignItems="center"
        justifyContent={{ base: "center", lg: "space-between" }}
        flexWrap="wrap"
        textAlign="center"
        w="fit-content"
        ms={{
          md: "38px",
        }}
        borderRadius="2xl"
      >
        {t("feedback_message")}
        <Flex>
          <FeedBackButton
            leftIcon={<ThumbsUp size="20px" />}
            onClick={() => {
              onThumbsUp();
              onClose();
            }}
          >
            {t("feedback_action_great")}
          </FeedBackButton>
          <FeedBackButton
            leftIcon={<ThumbsDown size="20px" />}
            onClick={() => {
              onThumbsDown();
              onClose();
            }}
          >
            {t("feedback_action_poor")}
          </FeedBackButton>
          <FeedBackButton p="2" onClick={onClose}>
            <X size="20px" />
          </FeedBackButton>
        </Flex>
      </Card>
    </Box>
  );
};

const FeedBackButton = (props: ButtonProps) => {
  return <Button variant="ghost" py="2" px="3" borderRadius="xl" {...props}></Button>;
};
