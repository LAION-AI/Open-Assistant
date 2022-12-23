import Link from "next/link";
import Image from "next/image";

export function AuthLayout({ children }) {
  return (
    <main className="flex items-center justify-center min-h-full overflow-hidden pt-16 sm:py-28">
      <div className="flex items-center w-full max-w-2xl flex-col px-4 sm:px-6">
        <Link href="/" aria-label="Home" className="flex items-center text-3xl font-extrabold text-black">
          <Image src="/images/logos/logo.svg" width="100" height="100" alt="Open Assistant Logo" /> Open Assistant
        </Link>
        <div className="flex-auto items-center justify-center w-full py-10 px-4 sm:mx-0 sm:flex-none sm:rounded-2xl sm:p-20">
          {children}
        </div>
      </div>
    </main>
  );
}
