import Image from "next/image";
import { useEffect, useState } from "react";
export function UserAvatar({ displayName, avatarUrl }: { displayName: string; avatarUrl?: string }) {
  const diceBearURL = `https://api.dicebear.com/5.x/initials/png?seed=${encodeURIComponent(
    displayName
  )}&radius=50&backgroundType=gradientLinear`;

  const [src, setSrc] = useState(avatarUrl ? avatarUrl : diceBearURL);
  useEffect(() => {
    setSrc(avatarUrl ? avatarUrl : diceBearURL);
  }, [avatarUrl, diceBearURL]);

  return (
    <Image
      src={src}
      onError={() => setSrc(diceBearURL)}
      alt={`${displayName}'s avatar`}
      width={30}
      height={30}
      referrerPolicy="no-referrer"
      className="rounded-full"
    />
  );
}
