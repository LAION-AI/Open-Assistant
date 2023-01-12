export function AuthLayout({ children }) {
  return (
    <div className="flex items-center justify-center sm:py-4 subpixel-antialiased">
      <div className="flex items-center w-full max-w-2xl flex-col px-4 sm:px-6">
        <div className="flex-auto items-center justify-center w-full py-10 px-4 sm:mx-0 sm:flex-none sm:rounded-2xl sm:p-4">
          {children}
        </div>
      </div>
    </div>
  );
}
