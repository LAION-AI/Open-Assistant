import { Text, useColorMode } from "@chakra-ui/react";
import { AnimatePresence, motion } from "framer-motion";
import Link from "next/link";
import { useState } from "react";
import { colors } from "styles/Theme/colors";

export function NavLinks(): JSX.Element {
  const [hoveredIndex, setHoveredIndex] = useState(null);
  const { colorMode } = useColorMode();

  const linkColor = colorMode === "light" ? "text-gray-700 hover:text-gray-900" : "text-gray-50 hover:text-white";

  const hoverBgColor = colorMode === "light" ? "bg-gray-100" : "bg-gray-800";

  return (
    <>
      {[
        ["FAQ", "/#faq"],
        ["Join Us", "/#join-us"],
      ].map(([label, href], index) => (
        <Link
          key={label}
          href={href}
          className={`${linkColor} relative -my-2 -mx-3 rounded-lg px-3 py-2 text-sm transition-colors delay-150 hover:delay-[0ms]`}
          onMouseEnter={() => setHoveredIndex(index)}
          onMouseLeave={() => setHoveredIndex(null)}
        >
          <AnimatePresence>
            {hoveredIndex === index && (
              <motion.span
                className={`${hoverBgColor} absolute inset-0 rounded-lg`}
                layoutId="hoverBackground"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1, transition: { duration: 0.15 } }}
                exit={{
                  opacity: 0,
                  transition: { duration: 0.15, delay: 0.2 },
                }}
              />
            )}
          </AnimatePresence>
          <Text color={colorMode === "light" ? colors.light.text : colors.dark.text} className="relative z-10">
            {label}
          </Text>
        </Link>
      ))}
    </>
  );
}
