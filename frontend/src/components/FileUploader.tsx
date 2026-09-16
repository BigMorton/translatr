"use client";

import { useState, useTransition } from "react";
import { UploadCloud, FileText, CheckCircle2, AlertCircle, Loader2 } from "lucide-react";

interface FileQuoteResponse {
  filename: string;
  source_type: "digital_pdf" | "scanned_pdf" | "image" | "text";
  used_ocr: boolean;
  physical_pages: number;
  raw_character_count: number;
  sworn_page_count: number;
  word_count: number;
  is_empty: boolean;
}

const BASE_PRICE_PER_PAGE_PLN = 55.0; // Statutory sworn translation baseline estimate

export default function FileUploader() {
  const [result, setResult] = useState<FileQuoteResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();
  const [isDragging, setIsDragging] = useState(false);

  const handleUpload = (selectedFile: File) => {
    setError(null);
    setResult(null);

    const formData = new FormData();
    formData.append("file", selectedFile);

    startTransition(async () => {
      try {
        const response = await fetch("http://localhost:8000/api/v1/quote/file", {
          method: "POST",
          body: formData,
        });

        if (!response.ok) {
          const errData = await response.json().catch(() => ({}));
          throw new Error(errData.detail || `Upload failed with status ${response.status}`);
        }

        const data: FileQuoteResponse = await response.json();
        setResult(data);
      } catch (err: unknown) {
        if (err instanceof Error) {
          setError(err.message);
        } else {
          setError("An unexpected error occurred while processing the document.");
        }
      }
    });
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleUpload(e.dataTransfer.files[0]);
    }
  };

  return (
    <div className="w-full max-w-2xl mx-auto space-y-6">
      {/* Dropzone Area */}
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
        className={`border-2 border-dashed rounded-xl p-8 text-center transition-colors cursor-pointer ${
          isDragging
            ? "border-blue-500 bg-blue-50/10"
            : "border-zinc-300 dark:border-zinc-700 hover:border-zinc-400 dark:hover:border-zinc-600"
        }`}
      >
        <input
          type="file"
          id="file-upload"
          className="hidden"
          accept=".pdf,.txt,.png,.jpg,.jpeg"
          onChange={(e) => {
            if (e.target.files && e.target.files[0]) {
              handleUpload(e.target.files[0]);
            }
          }}
        />
        <label htmlFor="file-upload" className="cursor-pointer flex flex-col items-center gap-3">
          {isPending ? (
            <Loader2 className="w-10 h-10 animate-spin text-blue-500" />
          ) : (
            <UploadCloud className="w-10 h-10 text-zinc-400" />
          )}

          <div>
            <p className="text-base font-medium">
              {isPending ? "Analyzing document..." : "Drag and drop your document here, or browse"}
            </p>
            <p className="text-sm text-zinc-500 mt-1">
              Supports PDF, PNG, JPG, or TXT (Max 10 MB)
            </p>
          </div>
        </label>
      </div>

      {/* Error Banner */}
      {error && (
        <div className="flex items-center gap-2 p-4 text-sm text-red-700 bg-red-50 dark:bg-red-950/40 dark:text-red-300 rounded-lg border border-red-200 dark:border-red-900">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          <p>{error}</p>
        </div>
      )}

      {/* Quote Summary Results Card */}
      {result && (
        <div className="border border-zinc-200 dark:border-zinc-800 rounded-xl p-6 bg-zinc-50/50 dark:bg-zinc-900/50 space-y-6">
          <div className="flex items-start justify-between border-b border-zinc-200 dark:border-zinc-800 pb-4">
            <div className="flex items-center gap-3">
              <FileText className="w-6 h-6 text-blue-500" />
              <div>
                <h3 className="font-semibold text-lg">{result.filename}</h3>
                <p className="text-xs text-zinc-500 uppercase tracking-wider font-mono">
                  Type: {result.source_type.replace("_", " ")} {result.used_ocr && "• OCR applied"}
                </p>
              </div>
            </div>
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-emerald-50 text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-300">
              <CheckCircle2 className="w-3.5 h-3.5" /> Ready
            </span>
          </div>

          {/* Pricing & Key Metrics */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="p-3 bg-white dark:bg-zinc-800/80 rounded-lg border border-zinc-200/60 dark:border-zinc-700/60">
              <p className="text-xs text-zinc-500">Sworn Pages</p>
              <p className="text-2xl font-bold mt-1 text-blue-600 dark:text-blue-400">
                {result.sworn_page_count}
              </p>
              <p className="text-[10px] text-zinc-400 mt-0.5">1,125 chars / page</p>
            </div>

            <div className="p-3 bg-white dark:bg-zinc-800/80 rounded-lg border border-zinc-200/60 dark:border-zinc-700/60">
              <p className="text-xs text-zinc-500">Total Characters</p>
              <p className="text-2xl font-bold mt-1">
                {result.raw_character_count.toLocaleString()}
              </p>
              <p className="text-[10px] text-zinc-400 mt-0.5">With spaces</p>
            </div>

            <div className="p-3 bg-white dark:bg-zinc-800/80 rounded-lg border border-zinc-200/60 dark:border-zinc-700/60">
              <p className="text-xs text-zinc-500">Source Pages</p>
              <p className="text-2xl font-bold mt-1">{result.physical_pages}</p>
              <p className="text-[10px] text-zinc-400 mt-0.5">Physical sheet count</p>
            </div>

            <div className="p-3 bg-white dark:bg-zinc-800/80 rounded-lg border border-zinc-200/60 dark:border-zinc-700/60">
              <p className="text-xs text-zinc-500">Est. Price</p>
              <p className="text-2xl font-bold mt-1 text-emerald-600 dark:text-emerald-400">
                {(result.sworn_page_count * BASE_PRICE_PER_PAGE_PLN).toFixed(2)} zł
              </p>
              <p className="text-[10px] text-zinc-400 mt-0.5">55 zł / page base</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
