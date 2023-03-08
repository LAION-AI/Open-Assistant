import Image from "next/image";
import { useState } from "react";
export function UserAvatar(options: { displayName: string; avatarUrl?: string }) {
  const { displayName, avatarUrl } = options;
  const [src, setSrc] = useState(
    avatarUrl
      ? avatarUrl
      : `https://api.dicebear.com/5.x/initials/png?seed=${displayName}&radius=50&backgroundType=gradientLinear`
  );
  return (
    <>
      <Image
        src={src}
        onError={() =>
          setSrc(
            `https://api.dicebear.com/5.x/initials/png?seed=${displayName}&radius=50&backgroundType=gradientLinear`
          )
        }
        alt={`${displayName}'s avatar`}
        width={30}
        height={30}
        className="rounded-full"
      />
    </>
  );
}
