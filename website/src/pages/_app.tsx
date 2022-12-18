import { createBrowserSupabaseClient } from "@supabase/auth-helpers-nextjs";
import { SessionContextProvider } from "@supabase/auth-helpers-react";
import {useEffect, useState} from 'react';


import "../styles/globals.css";
import 'focus-visible'

function MyApp({ Component, pageProps }) {
  const [supabase] = useState(() => createBrowserSupabaseClient());
  useEffect(() => {
    const use = async () => {
      // (await import('tw-elements')).default;
    };
    use();
  }, []);
  return (
    <SessionContextProvider
      supabaseClient={supabase}
      initialSession={pageProps.initialSession}
    >
      <Component {...pageProps} />
    </SessionContextProvider>
  );
}

export default MyApp;
