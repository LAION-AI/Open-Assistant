import type { SyntaxHighlighterProps } from "react-syntax-highlighter";
import { PrismAsyncLight } from "react-syntax-highlighter";
import { oneDark } from "react-syntax-highlighter/dist/cjs/styles/prism";

export default function SyntaxHighlighter({ children, lang, ...props }: SyntaxHighlighterProps) {
  return (
    <PrismAsyncLight language={lang} {...props} style={oneDark}>
      {String(children).replace(/\n$/, "")}
    </PrismAsyncLight>
  );
}
