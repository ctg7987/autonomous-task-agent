"use client";

import { ExternalLink, Shield, ShieldAlert, ShieldCheck } from "lucide-react";
import type { Citation } from "../lib/types";

interface Props {
  citation: Citation;
}

function CredibilityBadge({ score }: { score: number }) {
  if (score >= 0.7) {
    return (
      <span className="inline-flex items-center gap-1 text-xs font-medium text-green-700 bg-green-100 px-2 py-0.5 rounded-full">
        <ShieldCheck size={12} />
        High
      </span>
    );
  }
  if (score >= 0.4) {
    return (
      <span className="inline-flex items-center gap-1 text-xs font-medium text-amber-700 bg-amber-100 px-2 py-0.5 rounded-full">
        <Shield size={12} />
        Medium
      </span>
    );
  }
  return (
    <span className="inline-flex items-center gap-1 text-xs font-medium text-red-700 bg-red-100 px-2 py-0.5 rounded-full">
      <ShieldAlert size={12} />
      Low
    </span>
  );
}

function getDomain(url: string): string {
  try {
    return new URL(url).hostname.replace("www.", "");
  } catch {
    return url;
  }
}

export default function SourceCard({ citation }: Props) {
  return (
    <a
      href={citation.url}
      target="_blank"
      rel="noopener noreferrer"
      className="block rounded-lg border border-gray-200 bg-white p-4 hover:border-violet-300 hover:shadow-md transition-all group"
    >
      <div className="flex items-start justify-between gap-2 mb-2">
        <h4 className="text-sm font-semibold text-gray-800 group-hover:text-violet-700 line-clamp-2 transition-colors">
          {citation.title}
        </h4>
        <ExternalLink
          size={14}
          className="shrink-0 text-gray-400 group-hover:text-violet-500 mt-0.5"
        />
      </div>

      <div className="flex items-center gap-2 mb-2">
        <img
          src={`https://www.google.com/s2/favicons?domain=${getDomain(citation.url)}&sz=16`}
          alt=""
          className="w-4 h-4 rounded-sm"
          onError={(e) => {
            (e.target as HTMLImageElement).style.display = "none";
          }}
        />
        <span className="text-xs text-gray-500 truncate">{getDomain(citation.url)}</span>
        <CredibilityBadge score={citation.credibility_score} />
      </div>

      {citation.relevant_claims.length > 0 && (
        <div className="mt-2 space-y-1">
          {citation.relevant_claims.slice(0, 2).map((claim, i) => (
            <p key={i} className="text-xs text-gray-500 leading-relaxed line-clamp-1">
              &bull; {claim}
            </p>
          ))}
        </div>
      )}
    </a>
  );
}
