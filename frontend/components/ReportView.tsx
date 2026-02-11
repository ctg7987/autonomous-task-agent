"use client";

import { useState } from "react";
import {
  FileText,
  Copy,
  Check,
  ChevronDown,
  ChevronRight,
  TrendingUp,
  Info,
} from "lucide-react";
import type { ResearchReport, ReflectionEntry } from "../lib/types";
import SourceCard from "./SourceCard";

interface Props {
  report: ResearchReport;
  reflections: ReflectionEntry[];
}

export default function ReportView({ report, reflections }: Props) {
  const [copied, setCopied] = useState(false);
  const [showMethodology, setShowMethodology] = useState(false);
  const [showReflections, setShowReflections] = useState(false);

  const handleCopy = () => {
    const text = [
      report.summary,
      "",
      "Key Findings:",
      ...report.key_findings.map((f) => `- ${f}`),
      "",
      "Sources:",
      ...report.citations.map((c) => `- ${c.title}: ${c.url}`),
    ].join("\n");

    navigator.clipboard.writeText(text).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <FileText size={20} className="text-violet-600" />
          <h2 className="text-lg font-bold text-gray-900">Research Report</h2>
        </div>
        <div className="flex items-center gap-3">
          {/* Confidence score */}
          <div className="flex items-center gap-1.5">
            <TrendingUp size={14} className="text-gray-500" />
            <span className="text-sm text-gray-600">
              Confidence:{" "}
              <span
                className={`font-semibold ${
                  report.confidence_score >= 0.7
                    ? "text-green-600"
                    : report.confidence_score >= 0.4
                    ? "text-amber-600"
                    : "text-red-600"
                }`}
              >
                {Math.round(report.confidence_score * 100)}%
              </span>
            </span>
          </div>
          <button
            onClick={handleCopy}
            className="flex items-center gap-1.5 text-sm text-gray-500 hover:text-violet-600 transition-colors"
          >
            {copied ? <Check size={14} /> : <Copy size={14} />}
            {copied ? "Copied" : "Copy"}
          </button>
        </div>
      </div>

      {/* Summary */}
      <div className="prose prose-gray max-w-none">
        <p className="text-gray-700 leading-relaxed whitespace-pre-line">
          {report.summary}
        </p>
      </div>

      {/* Key Findings */}
      {report.key_findings.length > 0 && (
        <div>
          <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3">
            Key Findings
          </h3>
          <ul className="space-y-2">
            {report.key_findings.map((finding, i) => (
              <li
                key={i}
                className="flex items-start gap-3 bg-gray-50 rounded-lg px-4 py-3"
              >
                <span className="shrink-0 w-6 h-6 rounded-full bg-violet-100 text-violet-700 text-xs font-bold flex items-center justify-center mt-0.5">
                  {i + 1}
                </span>
                <span className="text-sm text-gray-700 leading-relaxed">
                  {finding}
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Methodology (collapsible) */}
      {report.methodology_note && (
        <button
          onClick={() => setShowMethodology(!showMethodology)}
          className="flex items-center gap-2 text-sm text-gray-500 hover:text-gray-700 transition-colors"
        >
          <Info size={14} />
          <span>Methodology</span>
          {showMethodology ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
        </button>
      )}
      {showMethodology && report.methodology_note && (
        <p className="text-sm text-gray-500 bg-gray-50 rounded-lg px-4 py-3">
          {report.methodology_note}
        </p>
      )}

      {/* Reflections (collapsible) */}
      {reflections.length > 0 && (
        <div>
          <button
            onClick={() => setShowReflections(!showReflections)}
            className="flex items-center gap-2 text-sm text-gray-500 hover:text-gray-700 transition-colors"
          >
            <span>Quality Reviews ({reflections.length})</span>
            {showReflections ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
          </button>
          {showReflections && (
            <div className="mt-2 space-y-2">
              {reflections.map((r, i) => (
                <div key={i} className="bg-pink-50 rounded-lg px-4 py-3 text-sm">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-medium text-pink-700">
                      Review #{r.retry_number + 1}
                    </span>
                    <span className="text-pink-500">
                      Score: {Math.round(r.score * 100)}%
                    </span>
                  </div>
                  <p className="text-gray-600">{r.critique}</p>
                  {r.suggestions.length > 0 && (
                    <ul className="mt-1 text-gray-500">
                      {r.suggestions.map((s, si) => (
                        <li key={si}>&bull; {s}</li>
                      ))}
                    </ul>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Sources */}
      {report.citations.length > 0 && (
        <div>
          <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3">
            Sources ({report.citations.length})
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {report.citations.map((citation, i) => (
              <SourceCard key={i} citation={citation} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
