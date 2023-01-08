import { useColorMode } from "@chakra-ui/react";
import Image from "next/image";
import Link from "next/link";
import { useMemo } from "react";

export function Footer() {
  const { colorMode } = useColorMode();
  const bgColorClass = colorMode === "light" ? "bg-transparent" : "bg-gray-800";
  const borderClass = colorMode === "light" ? "border-slate-200" : "border-transparent";

  return (
    <footer className={bgColorClass}>
      <div className={`flex mx-auto max-w-7xl justify-between border-t p-10 ${borderClass}`}>
        <div className="flex items-center pr-8">
          <Link href="/" aria-label="Home" className="flex items-center">
            <Image src="/images/logos/logo.svg" className="mx-auto object-fill" width="52" height="52" alt="logo" />
          </Link>

          <div className="ml-2">
            <p className="text-base font-bold">Open Assistant</p>
            <p className="text-sm">Conversational AI for everyone.</p>
          </div>
        </div>

        <nav className="grid grid-cols-2 gap-20 leading-5 text-sm">
          <div className="flex flex-col">
            <b className="pb-1">Legal</b>
            <FooterLink href="/privacy-policy" label="Privacy Policy" />
            <FooterLink href="/terms-of-service" label="Terms of Service" />
          </div>
          <div className="flex flex-col">
            <b className="pb-1">Connect</b>
            <FooterLink href="https://github.com/LAION-AI/Open-Assistant" label="Github" />
            <FooterLink href="https://ykilcher.com/open-assistant-discord" label="Discord" />
          </div>
        </nav>
      </div>
    </footer>
  );
}

const FooterLink = ({ href, label }: { href: string; label: string }) =>
  useMemo(
    () => (
      <Link
        href={href}
        rel="noopener noreferrer nofollow"
        target="_blank"
        aria-label={label}
        className="hover:underline underline-offset-2"
      >
        {label}
      </Link>
    ),
    [href, label]
  );
