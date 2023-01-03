import { AnimatePresence, motion } from "framer-motion";
import Link from "next/link";
import { useState } from "react";

import { useColorMode } from "@chakra-ui/react";

export function NavLinks(): JSX.Element {
  const [hoveredIndex, setHoveredIndex] = useState(null);
  const { colorMode } = useColorMode();

  const linkColor = colorMode === "light" ? "text-gray-700 hover:text-gray-900" : "text-gray-50 hover:text-white";

  const hoverBgColor = colorMode === "light" ? "bg-gray-100" : "bg-gray-800";

  return (
    <>
      {[
        ["Join Us", "/#join-us"],
        ["FAQ", "/#faq"],
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
          <span className="relative z-10">{label}</span>
        </Link>
      ))}
    </>
  );
}
