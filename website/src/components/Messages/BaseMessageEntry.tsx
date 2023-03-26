import { Avatar, AvatarProps, Box, BoxProps, HStack, useBreakpointValue, useColorModeValue } from "@chakra-ui/react";
import { forwardRef, lazy, Suspense, useMemo } from "react";

const RenderedMarkdown = lazy(() => import("./RenderedMarkdown"));

export type BaseMessageEntryProps = BoxProps & {
  content: string;
  avatarProps: Pick<AvatarProps, "name" | "src">;
};

// eslint-disable-next-line react/display-name
export const BaseMessageEntry = forwardRef<HTMLDivElement, BaseMessageEntryProps>(
  ({ content, avatarProps, children, ...props }, ref) => {
    const inlineAvatar = useBreakpointValue({ base: true, md: false });
    const borderColor = useColorModeValue("blackAlpha.200", "whiteAlpha.200");
    const bg = useColorModeValue("#DFE8F1", "#42536B");

    const avatar = useMemo(
      () => (
        <Avatar
          borderColor={borderColor}
          size={inlineAvatar ? "xs" : "sm"}
          mr={inlineAvatar ? 2 : 0}
          mt={inlineAvatar ? 0 : `6px`}
          mb={inlineAvatar ? 1.5 : 0}
          {...avatarProps}
        />
      ),
      [avatarProps, borderColor, inlineAvatar]
    );
    return (
      <HStack
        ref={ref}
        w={["full", "full", "full", "fit-content"]}
        gap={0.5}
        alignItems="start"
        maxW="full"
        position="relative"
      >
        {!inlineAvatar && avatar}
        <Box
          width={["full", "full", "full", "fit-content"]}
          maxWidth={["full", "full", "full", "2xl"]}
          p={[3, 4]}
          borderRadius="18px"
          bg={bg}
          overflowX="auto"
          {...props}
        >
          {inlineAvatar && avatar}
          <Suspense fallback={content}>
            <RenderedMarkdown markdown={content}></RenderedMarkdown>
          </Suspense>
          {children}
        </Box>
      </HStack>
    );
  }
);
