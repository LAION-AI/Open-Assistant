import { Progress } from "@chakra-ui/react";

export const LoadingScreen = ({ text }) => (
  <div className="bg-slate-100">
    <Progress size="xs" isIndeterminate />
    {text && (
      <div className="flex h-full">
        <div className="text-xl font-bold text-gray-800  mx-auto my-auto">{text}</div>
      </div>
    )}
  </div>
);
