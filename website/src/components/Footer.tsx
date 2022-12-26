import Image from "next/image";
import Link from "next/link";

import { Container } from "./Container";
import { NavLinks } from "./NavLinks";

export function Footer() {
  return (
    <footer className="border-t border-gray-200">
      <Container className="">
        <div className="flex flex-col items-start justify-between gap-y-12 pt-16 pb-6 lg:flex-row lg:items-center lg:py-16">
          <div>
            <div className="flex items-center text-gray-900">
              <Link href="/" aria-label="Home" className="flex items-center">
                <Image
                  src="/images/logos/logo.svg"
                  className="mx-auto object-fill"
                  width="50"
                  height="50"
                  alt="logo"
                />
              </Link>

              <div className="ml-4">
                <p className="text-base font-semibold">Open Assistant</p>
                <p className="mt-1 text-sm">Conversational AI for everyone.</p>
              </div>
            </div>
            <nav className="mt-11 flex gap-8">{/* <NavLinks /> */}</nav>
          </div>
        </div>
      </Container>
    </footer>
  );
}
