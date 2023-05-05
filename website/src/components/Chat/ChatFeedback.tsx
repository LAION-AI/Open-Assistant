import { useState } from "react";

interface FeedbackProps {
  onFeedbackSubmit: (isPositive: boolean) => void;
}

export function ChatFeedback({ onFeedbackSubmit }: FeedbackProps) {
  const [isPositive, setIsPositive] = useState<boolean | null>(null);

  const handleFeedback = (positive: boolean) => {
    setIsPositive(positive);
  };

  const handleSubmit = () => {
    if (isPositive !== null) {
      onFeedbackSubmit(isPositive);
    }
  };

  return (
    <div>
      <h2>Did you find this helpful?</h2>
      <div>
        <button onClick={() => handleFeedback(true)}>👍</button>
        <button onClick={() => handleFeedback(false)}>👎</button>
      </div>
      <button onClick={handleSubmit}>Submit</button>
    </div>
  );
}