import { useColorMode } from "@chakra-ui/react";
import Image from "next/image";
import { useId } from "react";
import { FaLock, FaComment } from "react-icons/fa";
import { useSession } from "next-auth/react";
import { useRouter } from "next/router";
import Link from "next/link";

import { Container } from "./Container";

function BackgroundIllustration(props) {
  const id = useId();

  const { colorMode } = useColorMode();
  const baseRingColor = colorMode === "light" ? "#d4d4d4" : "#005a69";
  const gradStopColor = colorMode === "light" ? "#06b6d4" : "#00f2ff";

  return (
    <div {...props}>
      <svg
        viewBox="0 0 1026 1026"
        fill="none"
        aria-hidden="true"
        className="absolute inset-0 h-full w-full animate-spin-slow"
      >
        <path
          d="M1025 513c0 282.77-229.23 512-512 512S1 795.77 1 513 230.23 1 513 1s512 229.23 512 512Z"
          stroke={baseRingColor}
          strokeOpacity="0.7"
        />
        <path d="M513 1025C230.23 1025 1 795.77 1 513" stroke={`url(#${id}-gradient-1)`} strokeLinecap="round" />
        <defs>
          <linearGradient id={`${id}-gradient-1`} x1="1" y1="513" x2="1" y2="1025" gradientUnits="userSpaceOnUse">
            <stop stopColor={gradStopColor} />
            <stop offset="1" stopColor={gradStopColor} stopOpacity="0" />
          </linearGradient>
        </defs>
      </svg>
      <svg
        viewBox="0 0 1026 1026"
        fill="none"
        aria-hidden="true"
        className="absolute inset-0 h-full w-full animate-spin-reverse-slower"
      >
        <path
          d="M913 513c0 220.914-179.086 400-400 400S113 733.914 113 513s179.086-400 400-400 400 179.086 400 400Z"
          stroke={baseRingColor}
          strokeOpacity="0.7"
        />
        <path d="M913 513c0 220.914-179.086 400-400 400" stroke={`url(#${id}-gradient-2)`} strokeLinecap="round" />
        <defs>
          <linearGradient id={`${id}-gradient-2`} x1="913" y1="513" x2="913" y2="913" gradientUnits="userSpaceOnUse">
            <stop stopColor={gradStopColor} />
            <stop offset="1" stopColor={gradStopColor} stopOpacity="0" />
          </linearGradient>
        </defs>
      </svg>
    </div>
  );
}

function CTA() {
  const { data: session } = useSession();
  const router = useRouter();
  if (session) {
    router.push("/dashboard");
  }
  return (
    <div>
      {!session ? (
        <Link href="/auth/signin">
          <button
            type="button"
            className="mb-2 ml-6 flex items-center rounded-md border border-transparent bg-blue-600 px-6 py-3 text-base font-medium text-white shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          >
            <FaLock />
            <span className="text-lg ml-1"> Login</span>
          </button>
        </Link>
      ) : (
        <Link href="/dashboard">
          <button
            type="button"
            className="mb-2 ml-6 flex items-center rounded-md border border-transparent bg-blue-600 px-6 py-3 text-base font-medium text-white shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          >
            <FaComment />
            <span className="text-lg ml-1"> Start</span>
          </button>
        </Link>
      )}
    </div>
  );
}

export function Hero() {
  const { colorMode } = useColorMode();
  const pTextColor = colorMode === "light" ? "text-gray-600" : "text-white";
  const fancyTextGradientClasses =
    colorMode === "light" ? "from-blue-600 via-sky-400 to-blue-700" : "from-blue-500 via-sky-300 to-blue-400";

  return (
    <div className="overflow-hidden py-20 sm:py-32 lg:pb-32 xl:pb-36">
      <Container className="">
        <div className="lg:grid lg:grid-cols-12 lg:gap-x-8 lg:gap-y-20">
          <div className="relative z-10 mx-auto max-w-2xl lg:col-span-7 lg:max-w-none lg:pt-6 xl:col-span-6">
            <h1 className="text-5xl mb-6 font-bold tracking-tight">Open Assistant</h1>
            <p
              className={`bg-gradient-to-r ${fancyTextGradientClasses} mt-8 text-3xl inline bg-clip-text font-display tracking-tight text-transparent`}
            >
              <b>Conversational AI for everyone.</b>
            </p>
            <p className={`mt-6 text-lg ${pTextColor}`}>We believe we can create a revolution.</p>
            <p className={`mt-6 text-lg ${pTextColor}`}>
              In the same way that Stable Diffusion helped the world make art and images in new ways, we want to improve
              the world by providing amazing conversational AI.
            </p>
          </div>

          <div className="relative mt-10 sm:mt-20 lg:col-span-5 lg:row-span-2 lg:mt-0 xl:col-span-6">
            <BackgroundIllustration className="absolute left-1/2 top-4 h-[1026px] w-[1026px] -translate-x-1/3 stroke-gray-300/70 [mask-image:linear-gradient(to_bottom,white_20%,transparent_75%)] sm:top-16 sm:-translate-x-1/2 lg:-top-16 lg:ml-12 xl:-top-14 xl:ml-0" />
            <div className="-mx-4 h-[448px] px-9 [mask-image:linear-gradient(to_bottom,white_60%,transparent)] sm:mx-0 lg:absolute lg:-inset-x-10 lg:-top-10 lg:-bottom-20 lg:h-auto lg:px-0 lg:pt-10 xl:-bottom-32">
              <Image
                src="/images/logos/logo.svg"
                className="mx-auto mr-6 object-fill"
                width="450"
                height="450"
                alt={""}
              />
            </div>
          </div>
          <CTA />
        </div>
      </Container>
    </div>
  );
}

function componentDidMount() {
  throw new Error("Function not implemented.");
}
