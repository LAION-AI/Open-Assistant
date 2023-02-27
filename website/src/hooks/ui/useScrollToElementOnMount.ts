import { RefObject, useEffect, useState } from "react";

/**
 *  This is a custom hook that returns a ref that can be used to focus an element.
 *
 *   Use like:
 *
 *   ```
 *   const ref = useRef();
 *   useScrollToElementOnMount(ref);
 *   return <div ref={ref} />
 *   ```
 */
export const useScrollToElementOnMount = (ref: RefObject<HTMLElement> | undefined) => {
  const [scrolled, setScrolled] = useState(false);
  useEffect(() => {
    if (!ref?.current || scrolled) {
      return;
    }

    ref.current.scrollIntoView();
    setScrolled(true);
  }, [ref, scrolled]);
};
