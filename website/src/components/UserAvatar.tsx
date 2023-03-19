import Image from "next/image";
import { useEffect, useState } from "react";
export function UserAvatar({ displayName, avatarUrl }: { displayName: string; avatarUrl?: string }) {
  const diceBearURL = `https://api.dicebear.com/5.x/initials/png?seed=${displayName}&radius=50&backgroundType=gradientLinear`;

  const [src, setSrc] = useState(avatarUrl ?? diceBearURL);
  useEffect(() => {
    setSrc(avatarUrl ?? diceBearURL);
  }, [avatarUrl, diceBearURL]);

  return (
    <Image
      src={src}
      onError={() => setSrc(diceBearURL)}
      alt={`${displayName}'s avatar`}
      width={30}
      height={30}
      className="rounded-full"
    />
  );
}
