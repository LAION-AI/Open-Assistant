import Image from "next/image";
import Link from "next/link";

import { Container } from "./Container";
import { Box, Text, useColorModeValue } from "@chakra-ui/react";

export function Footer() {
  const backgroundColor = useColorModeValue("#FFFFFF", "#000000");
  const foregroundColor = useColorModeValue("#000000", "#FFFFFF");

  return (
    <footer>
      <Box backgroundColor={backgroundColor} className="border-t border-gray-200">
        <main>
          <Container className="">
            <div className="flex flex-wrap justify-between gap-y-12 py-10 lg:items-center lg:py-16">
              <div className="flex items-center text-black pr-8">
                <Link href="/" aria-label="Home" className="flex items-center">
                  <Image
                    src="/images/logos/logo.svg"
                    className="mx-auto object-fill"
                    width="52"
                    height="52"
                    alt="logo"
                  />
                </Link>

                <div className="ml-2">
                  <Text color={foregroundColor} className="text-base font-bold">
                    Open Assistant
                  </Text>
                  <Text color={foregroundColor} className="text-sm">
                    Conversational AI for everyone.
                  </Text>
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
                <div className="flex flex-col text-sm leading-7">
                  <b>Legal</b>
                  <div className="flex flex-col leading-5">
                    <Link href="#" aria-label="Privacy Policy" className="hover:underline underline-offset-2">
                      Privacy Policy
                    </Link>
                    <Link href="#" aria-label="Terms of Service" className="hover:underline underline-offset-2">
                      Terms of Service
                    </Link>
                  </div>
                </div>
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
            </div>
          </Container>
        </main>
      </Box>
    </footer>
  );
}
