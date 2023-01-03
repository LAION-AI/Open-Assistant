import { useColorMode } from "@chakra-ui/react";
import { CiDark } from "react-icons/ci";
import { CiLight } from "react-icons/ci";

export function ColorModeIconToggle(props) {
  const { colorMode, toggleColorMode } = useColorMode();
  const propsClassName = props.className ?? "";

  return (
    <button
      type="button"
      className={`flex h-6 w-6 items-center justify-center rounded-md transition hover:bg-zinc-900/5 dark:hover:bg-white/5 ${propsClassName}`}
      aria-label="Toggle dark mode"
      onClick={toggleColorMode}
    >
      {colorMode === "light" ? (
        <CiDark className="h-5 w-5 stroke-zinc-900 dark:hidden" />
      ) : (
        <CiLight className="h-5 w-5 stroke-white" />
      )}
    </button>
  );
}
