"use client";

import { useCallback, useRef, useState } from "react";
import type { SSEEvent } from "../lib/types";

const BACKEND_URL =
  process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

interface UseSSEOptions {
  onEvent: (event: SSEEvent) => void;
  onError?: (error: string) => void;
  onDone?: () => void;
  timeout?: number;
}

export function useSSE({ onEvent, onError, onDone, timeout = 120000 }: UseSSEOptions) {
  const [isConnected, setIsConnected] = useState(false);
  const abortRef = useRef<AbortController | null>(null);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);

  const startResearch = useCallback(
    async (query: string) => {
      // Abort any existing connection
      abortRef.current?.abort();

      const controller = new AbortController();
      abortRef.current = controller;
      setIsConnected(true);

      // Set timeout
      timeoutRef.current = setTimeout(() => {
        controller.abort();
        onError?.("Research timed out");
        setIsConnected(false);
      }, timeout);

      try {
        const resp = await fetch(`${BACKEND_URL}/api/research`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ query }),
          signal: controller.signal,
        });

        if (!resp.ok) {
          const text = await resp.text();
          throw new Error(`Server error ${resp.status}: ${text}`);
        }

        const reader = resp.body?.getReader();
        if (!reader) throw new Error("No response body");

        const decoder = new TextDecoder();
        let buffer = "";

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });

          // Parse SSE lines
          const lines = buffer.split("\n");
          buffer = lines.pop() || "";

          for (const line of lines) {
            const trimmed = line.trim();
            if (trimmed.startsWith("data: ")) {
              try {
                const event: SSEEvent = JSON.parse(trimmed.slice(6));
                onEvent(event);

                if (event.event === "done" || event.event === "error") {
                  onDone?.();
                }
              } catch {
                // Skip malformed events
              }
            }
          }
        }
      } catch (err: any) {
        if (err.name !== "AbortError") {
          onError?.(err.message || "Connection failed");
        }
      } finally {
        if (timeoutRef.current) clearTimeout(timeoutRef.current);
        setIsConnected(false);
        onDone?.();
      }
    },
    [onEvent, onError, onDone, timeout]
  );

  const stopResearch = useCallback(() => {
    abortRef.current?.abort();
    if (timeoutRef.current) clearTimeout(timeoutRef.current);
    setIsConnected(false);
  }, []);

  return { startResearch, stopResearch, isConnected };
}
