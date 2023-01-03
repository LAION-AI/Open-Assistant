import { SurveyCard } from "src/components/Survey/SurveyCard";

export const TwoColumnsWithCards = ({ children }: { children: React.ReactNode[] }) => {
  if (!Array.isArray(children) || children.length !== 2) {
    throw new Error("TwoColumns expects 2 children");
  }

  const [first, second] = children;

  return (
    <div className="mb-8 mx-auto max-w-7xl lt-lg:mb-12 grid lg:gap-x-12 lg:grid-cols-2">
      <SurveyCard>{first}</SurveyCard>
      <SurveyCard className="lg:mt-0 lt-lg:mt-6">{second}</SurveyCard>
    </div>
  );
};
