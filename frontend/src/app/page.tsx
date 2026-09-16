import FileUploader from "@/components/FileUploader";

export default function Home() {
  return (
    <main className="min-h-screen py-16 px-4 sm:px-6 lg:px-8 max-w-4xl mx-auto">
      <div className="text-center space-y-3 mb-10">
        <h1 className="text-4xl font-extrabold tracking-tight sm:text-5xl">
          Translatr
        </h1>
        <p className="text-base sm:text-lg text-zinc-600 dark:text-zinc-400 max-w-xl mx-auto">
          Instant, statutory quote calculation for Polish sworn translations (1,125 characters per page).
        </p>
      </div>

      <FileUploader />
    </main>
  );
}
