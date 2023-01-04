import { useColorMode } from "@chakra-ui/react";

interface SurveyCardProps {
  className?: string;
  children: React.ReactNode;
}

export const SurveyCard = (props: SurveyCardProps) => {
  const extraClases = props.className || "";
  const { colorMode } = useColorMode();

  const baseCardClasses = "rounded-lg h-full block p-6";
  const cardClases =
    colorMode === "light"
      ? `${baseCardClasses} bg-slate-50 text-gray-800 shadow-lg ${extraClases}`
      : // `${baseCardClasses} bg-slate-800 text-white shadow-xl${extraClases}`;
        `${baseCardClasses} bg-slate-800 text-slate-400 shadow-xl ring-1 ring-white/10 ring-inset ${extraClases}`;

  return <div className={cardClases}>{props.children}</div>;
};
