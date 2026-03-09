"use client";

import { SessionProvider, useSession } from "next-auth/react";
import { useEffect } from "react";
import { initAnalytics } from "@/lib/analytics";

function TokenSync() {
  const { data: session } = useSession();

  useEffect(() => {
    const s = session as Record<string, unknown> | null;
    const idToken = s?.id_token;
    if (typeof idToken === "string" && idToken) {
      sessionStorage.setItem("id_token", idToken);
    } else {
      sessionStorage.removeItem("id_token");
    }

    const email = session?.user?.email;
    if (email) {
      sessionStorage.setItem("user_email", email);
    } else {
      sessionStorage.removeItem("user_email");
    }
  }, [session]);

  return null;
}

export default function Providers({ children }: { children: React.ReactNode }) {
  useEffect(() => {
    initAnalytics();
  }, []);

  return (
    <SessionProvider>
      <TokenSync />
      {children}
    </SessionProvider>
  );
}
