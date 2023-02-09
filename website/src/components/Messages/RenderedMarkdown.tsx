import { ReactMarkdown } from "react-markdown/lib/react-markdown";
import remarkGfm from "remark-gfm";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { dark } from "react-syntax-highlighter/dist/cjs/styles/prism";

interface RenderedMarkdownProps {
  markdown: string;
}

const RenderedMarkdown = ({ markdown }: RenderedMarkdownProps) => {
  return (
    <ReactMarkdown
      className="prose"
      remarkPlugins={[remarkGfm]}
      components={{
        code({ node, inline, className, children, style, ...props }) {
          const match = /language-(\w+)/.exec(className || "");
          const lang = match ? match[1] : "";
          return !inline ? (
            <SyntaxHighlighter style={dark} language={lang} PreTag="div" {...props}>
              {String(children).replace(/\n$/, "")}
            </SyntaxHighlighter>
          ) : (
            <code className={className} {...props}>
              {children}
            </code>
          );
        },
      }}
    >
      {markdown}
    </ReactMarkdown>
  );
};

export default RenderedMarkdown;
