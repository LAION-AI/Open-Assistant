import { Progress } from "@chakra-ui/react";
import { useColorMode } from "@chakra-ui/react";

export const LoadingScreen = ({ text = "Loading..." } = {}) => {
  const { colorMode } = useColorMode();
  const mainClasses = colorMode === "light" ? "bg-slate-300 text-gray-800" : "bg-slate-900 text-white";

  return (
    <div className={`h-full ${mainClasses}`}>
      <Progress size="sm" isIndeterminate />
      {text && (
        <div className="flex h-full">
          <div className="text-xl font-bold  mx-auto my-auto">{text}</div>
        </div>
      )}
    </div>
  );
};
