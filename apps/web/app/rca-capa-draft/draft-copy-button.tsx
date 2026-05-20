"use client";

import { useState } from "react";

type DraftCopyButtonProps = {
  draftText: string;
};

export function DraftCopyButton({ draftText }: DraftCopyButtonProps) {
  const [copyState, setCopyState] = useState<"idle" | "copied" | "failed">("idle");

  async function copyDraft() {
    try {
      await navigator.clipboard.writeText(draftText);
      setCopyState("copied");
    } catch {
      setCopyState("failed");
    }
  }

  return (
    <div className="draft-copy">
      <button onClick={copyDraft} type="button">
        Copy draft text
      </button>
      <span role="status">
        {copyState === "copied" ? "Copied" : null}
        {copyState === "failed" ? "Copy unavailable" : null}
      </span>
    </div>
  );
}
