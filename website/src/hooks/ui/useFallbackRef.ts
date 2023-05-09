import { ForwardedRef, RefObject, useRef } from "react";

export const useFallbackRef = <T>(maybeRef?: ForwardedRef<T>) => {
  const ref = useRef(null);

  return (maybeRef || ref) as RefObject<T>;
};
