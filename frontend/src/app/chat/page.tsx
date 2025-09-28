"use client";

import { useState, useEffect } from "react";
import TypingLoader from "@/app/components/TypingLoader";
import DropdownTailwind from "@/app/components/DropdownTailwind";
import ReactMarkdown from "react-markdown";
import Image from "next/image";

export default function ChatPage() {
  const [input, setInput] = useState("");
  const [history, setHistory] = useState<{ question: string; answer: string }[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedModel, setSelectedModel] = useState(""); // dropdown
  const [currentAnswer, setCurrentAnswer] = useState(""); // affichage en cours

  // 🚀 Fonction principale d’envoi (stream incluse)
const handleSend = async () => {
  if (!input.trim()) return;

  const userMessage = input;
  setInput("");
  setLoading(true);

  // Ajoute le message vide du bot pour mise à jour progressive
  setHistory((prev) => [...prev, { question: userMessage, answer: "" }]);

  try {
    const res = await fetch("http://192.168.1.173:8000/chat_sav", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        prompt: userMessage,
        model_selected: selectedModel || "Mistral-medium",
      }),
    });

    if (!res.body) throw new Error("Pas de flux de réponse.");

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let partialText = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      // Décodage et ajout
      partialText += decoder.decode(value, { stream: true });

      // 🔹 Mise à jour progressive du dernier message dans l’historique
      setHistory((prev) => {
        const updated = [...prev];
        updated[updated.length - 1].answer = partialText;
        return updated;
      });
    }
  } catch (error) {
    console.error("Erreur lors de l’appel API :", error);
    setHistory((prev) => {
      const updated = [...prev];
      updated[updated.length - 1].answer = "❌ Erreur lors de l’appel à l’API.";
      return updated;
    });
  } finally {
    setLoading(false);
  }
};


  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  useEffect(() => {
    window.scrollTo({ top: document.body.scrollHeight, behavior: "smooth" });
  }, [history, currentAnswer]);

  return (
    <main className="min-h-screen bg-white text-black flex flex-col font-['Raleway']">
      {/* HEADER */}
      <header className="border-b px-6 py-4 flex items-center justify-between bg-gray-50 shadow-sm">
        <div className="flex items-center gap-3">
            {/* ✅ Lien autour du logo uniquement */}
            <a href="https://www.free.fr" target="_blank" rel="noopener noreferrer">
                <Image
                src="/free.svg"
                alt="Free logo"
                width={90}
                height={32}
                priority
                className="object-contain -mt-1 cursor-pointer hover:opacity-80 transition"
                />
            </a>

            {/* 🔽 Menu de sélection du modèle */}
            <DropdownTailwind
                selected={selectedModel}
                onSelect={(val: string) => setSelectedModel(val)}
            />
        </div>


        <div className="flex gap-4 text-gray-500">
          <button title="Langue">🌐</button>
          <button title="Aide">❓</button>
        </div>
      </header>

      {/* CHAT */}
      <section className="flex-1 max-w-2xl w-full mx-auto px-4 py-8 overflow-y-auto">
        <p className="mb-6 text-center text-gray-600 text-base">
          Posez votre question et notre assistant SAV s’occupe du reste !
        </p>

        {history.map((entry, i) => (
          <div key={i} className="mb-6">
            {/* Message utilisateur */}
            <div className="text-right mb-2">
              <div className="inline-block bg-red-50 border border-red-100 px-4 py-2 rounded-xl shadow-sm">
                {entry.question}
              </div>
            </div>

            {/* Réponse assistant */}
            <div className="text-left whitespace-pre-wrap">
              <div className="inline-block bg-gray-50 border px-4 py-3 rounded-xl shadow-sm text-gray-800 prose prose-sm max-w-none">
                <ReactMarkdown
                  components={{
                    p: ({ children }) => <p className="my-1 leading-snug">{children}</p>,
                    strong: ({ children }) => <strong className="text-gray-800">{children}</strong>,
                    ul: ({ children }) => <ul className="my-1 ml-4 list-disc">{children}</ul>,
                    li: ({ children }) => <li className="my-0">{children}</li>,
                  }}
                >
                  {entry.answer}
                </ReactMarkdown>
              </div>
            </div>
          </div>
        ))}

        {/* 🔴 Affichage temporaire du flux en direct */}
        {currentAnswer && (
          <div className="mb-6 text-left">
            <div className="inline-block bg-gray-50 border px-4 py-3 rounded-xl shadow-sm text-gray-800">
              <ReactMarkdown>{currentAnswer}</ReactMarkdown>
            </div>
          </div>
        )}

        {loading && !currentAnswer && (
          <div className="flex items-center text-gray-500 mt-2">
            <TypingLoader />
            <span className="ml-2 text-sm">L’assistant rédige une réponse...</span>
          </div>
        )}
      </section>

      {/* FOOTER */}
      <footer className="border-t bg-white p-4 flex items-center justify-center">
        <div className="flex items-center gap-2 w-full max-w-2xl">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Décrivez votre problème ou demandez de l’aide..."
            className="
              flex-1 border border-gray-300 rounded-full
              px-4 py-2 text-gray-800 font-medium
              focus:ring-2 focus:ring-red-500 outline-none
              transition
            "
          />
          <button
            onClick={handleSend}
            disabled={loading}
            className="
              w-10 h-10 flex items-center justify-center
              rounded-full bg-red-600 hover:bg-red-700
              text-white shadow-md transition
            "
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth="2"
              stroke="currentColor"
              className="w-5 h-5"
            >
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 19V5m0 0l-7 7m7-7l7 7" />
            </svg>
          </button>
        </div>
      </footer>
    </main>
  );
}
