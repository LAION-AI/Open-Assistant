import { Button, Flex, useToast } from "@chakra-ui/react";
import { Check, Copy } from "lucide-react";
import { HTMLAttributes, lazy, MouseEvent, Suspense, useState } from "react";
import { oneDark } from "react-syntax-highlighter/dist/cjs/styles/prism";

const SyntaxHighlighter = lazy(() => import("./SyntaxHighlighter"));

export const RenderedCodeblock = ({
  inline,
  className,
  children,
  ...props
}: HTMLAttributes<HTMLElement> & { inline?: boolean }) => {
  const match = /language-(\w+)/.exec(className || "");
  const lang = match ? match[1] : "";

  const [isCopied, setIsCopied] = useState(false);
  const toast = useToast();

  const handleCopyClick = async (event: MouseEvent) => {
    event.stopPropagation();
    toast.closeAll();

    try {
      await navigator.clipboard.writeText(String(children));

      toast({
        title: "Copied to clipboard",
        status: "info",
        duration: 2000,
        isClosable: true,
      });

      setIsCopied(true);
      setTimeout(() => setIsCopied(false), 2000);
    } catch {
      toast({
        title: "Failed to copy",
        status: "error",
        duration: 2000,
        isClosable: true,
      });
    }
  };

  return !inline ? (
    <Flex pos="relative" flexDir="row" role="group">
      <Suspense
        fallback={
          <code className={className} {...props}>
            {children}
          </code>
        }
      >
        <SyntaxHighlighter language={lang} {...props} style={oneDark}>
          {String(children).replace(/\n$/, "")}
        </SyntaxHighlighter>
      </Suspense>
      <Button
        onClick={handleCopyClick}
        top="0"
        pos="absolute"
        display="none"
        _rtl={{
          left: "0",
          transform: "translate(10px,40%)",
        }}
        _ltr={{
          right: "0",
          transform: "translate(-10px,40%)",
        }}
        _groupHover={{
          display: "flex",
        }}
        colorScheme={isCopied ? "blue" : "gray"}
      >
        {isCopied ? <Check /> : <Copy />}
      </Button>
    </Flex>
  ) : (
    <code className={className} {...props}>
      {children}
    </code>
  );
};
