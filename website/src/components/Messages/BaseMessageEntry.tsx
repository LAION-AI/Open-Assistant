import { Avatar, AvatarProps, Box, BoxProps, HStack, useBreakpointValue, useColorModeValue } from "@chakra-ui/react";
import { forwardRef, lazy, Suspense, useMemo } from "react";

const RenderedMarkdown = lazy(() => import("./RenderedMarkdown"));

export type BaseMessageEntryProps = BoxProps & {
  content: string;
  avatarProps: Pick<AvatarProps, "name" | "src">;
  containerProps?: BoxProps;
};

// eslint-disable-next-line react/display-name
export const BaseMessageEntry = forwardRef<HTMLDivElement, BaseMessageEntryProps>(
  ({ content, avatarProps, children, ...props }, ref) => {
    const inlineAvatar = useBreakpointValue({ base: true, md: false });
    const bg = useColorModeValue("#DFE8F1", "#42536B");

    const avatar = useMemo(
      () => (
        <Avatar
          borderColor="blackAlpha.200"
          _dark={{
            borderColor: "whiteAlpha.200",
          }}
          size={{ base: "xs", md: "sm" }}
          mr={{ base: 2, md: 0 }}
          mt={{ base: 0, md: `6px` }}
          mb={{ base: 1.5, md: 0 }}
          {...avatarProps}
        />
      ),
      [avatarProps]
    );
    return (
      <HStack ref={ref} gap={0.5} alignItems="start" maxW="full" position="relative">
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
