import Image from "next/image";
import Link from "next/link";

import { Container, Text, useColorModeValue } from "@chakra-ui/react";

export function Footer() {
  return (
    <footer>
      <Container className="flex justify-evenly py-10 px-10 border-t">
        <div className="flex items-center pr-8">
          <Link href="/" aria-label="Home" className="flex items-center">
            <Image src="/images/logos/logo.svg" className="mx-auto object-fill" width="52" height="52" alt="logo" />
          </Link>

          <div className="ml-2">
            <p className="text-base font-bold">Open Assistant</p>
            <p className="text-sm">Conversational AI for everyone.</p>
          </div>
        </div>
        <nav className="flex justify-center gap-20">
          <div className="flex flex-col text-sm leading-7">
            <b>Information</b>
            <div className="flex flex-col leading-5">
              <Link href="#" aria-label="Our Team" className="hover:underline underline-offset-2">
                Our Team
              </Link>
              <Link href="#join-us" aria-label="Join Us" className="hover:underline underline-offset-2">
                Join Us
              </Link>
            </div>
          </div>
          <nav className="flex justify-center gap-20">
            <div className="flex flex-col text-sm leading-7">
              <b>Information</b>
              <div className="flex flex-col leading-5">
                <Link href="#" aria-label="Our Team" className="hover:underline underline-offset-2">
                  Our Team
                </Link>
                <Link href="/#join-us" aria-label="Join Us" className="hover:underline underline-offset-2">
                  Join Us
                </Link>
              </div>
            </div>
          </nav>
          <div className="flex flex-col text-sm leading-7">
            <b>Connect</b>
            <div className="flex flex-col leading-5">
              <Link
                href="https://github.com/LAION-AI/Open-Assistant"
                rel="noopener noreferrer nofollow"
                target="_blank"
                aria-label="Privacy Policy"
                className="hover:underline underline-offset-2"
              >
                Github
              </Link>
              <Link
                href="https://discord.gg/pXtnYk9c"
                rel="noopener noreferrer nofollow"
                target="_blank"
                aria-label="Terms of Service"
                className="hover:underline underline-offset-2"
              >
                Discord
              </Link>
            </div>
          </div>
        </nav>
      </Container>
    </footer>
  );
}
