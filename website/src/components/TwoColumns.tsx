export const TwoColumns = ({ children }: { children: React.ReactNode[] }) => {
  if (!Array.isArray(children) || children.length !== 2) {
    throw new Error("TwoColumns expects 2 children");
  }

  const [first, second] = children;

  return (
    <section className="mb-8 lt-lg:mb-12 grid lg:gap-x-12 lg:grid-cols-2">
      <div className="rounded-lg shadow-lg h-full block bg-white p-6">{first}</div>
      <div className="rounded-lg shadow-lg h-full block bg-white p-6 mt-6 lg:mt-0">{second}</div>
    </section>
  );
};
