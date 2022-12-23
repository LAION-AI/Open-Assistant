import Link from "next/link";
import Image from "next/image";

export function AuthLayout({ children }) {
  return (
    <main className="flex bg-white items-center justify-center min-h-full overflow-hidden pt-16 sm:py-28">
      <div className="flex items-center w-full max-w-2xl flex-col px-4 sm:px-6">
        <Link href="/" aria-label="Home">
          <Image src="/images/logos/oa-logo-2.svg" width="300" height="42" alt="Open Assistant Logo" />
        </Link>
        <div className="flex-auto items-center justify-center w-full py-10 px-4 sm:mx-0 sm:flex-none sm:rounded-2xl sm:p-24">
          {children}
        </div>
      </div>
    </main>
  );
}
