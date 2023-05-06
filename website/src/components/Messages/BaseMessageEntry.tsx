import { Avatar, AvatarProps, Box, BoxProps, Flex, useColorModeValue } from "@chakra-ui/react";
import { forwardRef, lazy, Suspense } from "react";
import { colors } from "src/styles/Theme/colors";
import { StrictOmit } from "ts-essentials";
import { PluginUsageDetails } from "./PluginUsageDetails";
const RenderedMarkdown = lazy(() => import("./RenderedMarkdown"));

export type BaseMessageEntryProps = StrictOmit<BoxProps, "bg" | "backgroundColor"> & {
  content: string;
  avatarProps: Pick<AvatarProps, "name" | "src">;
  bg?: string;
  highlight?: boolean;
  usedPlugin?: object;
  isAssistant?: boolean;
  containerProps?: BoxProps;
};

export const BaseMessageEntry = forwardRef<HTMLDivElement, BaseMessageEntryProps>(function BaseMessageEntry(
  { content, avatarProps, children, highlight, usedPlugin, isAssistant, containerProps, ...props },
  ref
) {
  const bg = useColorModeValue("#DFE8F1", "#42536B");
  const actualBg = props.bg ?? bg;

  return (
    <Flex
      ref={ref}
      gap={0.5}
      flexDirection={{ base: "column", md: "row" }}
      alignItems="start"
      maxWidth="full"
      position="relative"
      p={{ base: 3, md: 0 }}
      borderRadius={{ base: "18px", md: 0 }}
      bg={{ base: actualBg, md: "transparent" }}
      outline={highlight ? { base: `2px solid black`, md: "0px" } : undefined}
      outlineColor={colors.light.active}
      _dark={{ outlineColor: colors.dark.active }}
      {...containerProps}
    >
      <Avatar
        borderColor="blackAlpha.200"
        _dark={{
          borderColor: "whiteAlpha.200",
        }}
        size={{ base: "xs", md: "sm" }}
        mr={{ base: 0, md: 2 }}
        mt={{ base: 0, md: `6px` }}
        mb={{ base: 1.5, md: 0 }}
        {...avatarProps}
      />
      <Box
        width={["full", "full", "full", "fit-content"]}
        maxWidth={["full", "full", "full", "2xl"]}
        p={{ base: 0, md: 4 }}
        borderRadius={{ base: 0, md: "18px" }}
        bg={bg}
        overflowX="auto"
        outline={highlight ? { base: "0px", md: `2px solid black` } : undefined}
        outlineColor={{ md: colors.light.active }}
        {...props}
        _dark={{ outlineColor: { md: colors.dark.active }, ...props._dark }}
      >
        <Suspense fallback={content}>
          {isAssistant ? <PluginUsageDetails usedPlugin={usedPlugin} /> : null}
          <RenderedMarkdown markdown={content} disallowedElements={[]}></RenderedMarkdown>
        </Suspense>
        {children}
      </Box>
    </Flex>
  );
});
