import { Center, Text, useColorMode, useColorModeValue } from "@chakra-ui/react";
import { FiFileText } from "react-icons/fi";
import { IconType } from "react-icons/lib";

type EmptyStateProps = {
  text: string;
  icon: IconType;
};

export const EmptyState = (props: EmptyStateProps) => {
  const { colorMode } = useColorMode();
  const mainBgClasses = colorMode === "light" ? "bg-slate-300 text-gray-900" : "bg-slate-900 text-white";

  const widgetClasses = useColorModeValue("border-gray-700 text-gray-700", "border-gray-300 text-gray-300");

  return (
    <div className={`p-12 ${mainBgClasses}`}>
      <Center>
        <div className={`block border-2 border-dotted rounded-lg p-24 text-center ${widgetClasses}`}>
          <props.icon className="mx-auto h-16 w-16" />
          <Text fontFamily="inter" fontSize="2xl">
            {props.text}
          </Text>
        </div>
      </Center>
    </div>
  );
};

export const TaskEmptyState = () => {
  return <EmptyState text="No tasks found!" icon={FiFileText} />;
};
