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
  const [selectedModel, setSelectedModel] = useState("");
  const [step, setStep] = useState<"categorie" | "sousCategorie" | "description" | "chat">("categorie");
  const [selectedService, setSelectedService] = useState("");
  const [selectedIssue, setSelectedIssue] = useState("");

  // 🔹 Dictionnaire des sous-catégories selon le service
  const subCategories: Record<string, string[]> = {
    Box: ["Wi-Fi", "TV", "Alimentation", "Internet"],
    Mobile: ["Réseau", "Forfait", "Appels", "Data"],
  };

  // 🔹 Fonction d’envoi au backend LLM
  const sendMessage = async (prompt: string) => {
    setLoading(true);
    setHistory((prev) => [...prev, { question: prompt, answer: "" }]);

    try {
      const res = await fetch("http://192.168.1.173:8000/chat_sav", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          prompt,
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

        partialText += decoder.decode(value, { stream: true });

        setHistory((prev) => {
          const updated = [...prev];
          updated[updated.length - 1].answer = partialText;
          return updated;
        });
      }
    } catch (err) {
      setHistory((prev) => {
        const updated = [...prev];
        updated[updated.length - 1].answer = "❌ Erreur lors de l'appel à l’API.";
        return updated;
      });
    } finally {
      setLoading(false);
    }
  };

  // 🔹 Étape 1 — Choix du service
  const handleCategorieClick = (service: string) => {
    setSelectedService(service);
    setHistory((prev) => [
      ...prev,
      { question: service, answer: `Très bien. Quel type de problème rencontrez-vous avec ${service.toLowerCase()} ?` },
    ]);

    if (service === "Autres") {
      setStep("description");
    } else {
      setStep("sousCategorie");
    }
  };

  // 🔹 Étape 2 — Choix du type de problème
  const handleSousCategorieClick = (issue: string) => {
    setSelectedIssue(issue);
    setStep("description");
    setHistory((prev) => [
      ...prev,
      {
        question: issue,
        answer: `D'accord, vous avez un problème de type **${issue}** sur votre ${selectedService.toLowerCase()}. Pouvez-vous le décrire ?`,
      },
    ]);
  };

  // 🔹 Étape 3 — Saisie du problème et envoi
const handleSend = () => {
  if (!input.trim()) return;

  // 🧠 Prompt complet envoyé à l'API (non affiché côté front)
  const fullPrompt = `
Tu es un assistant technique du support Free.
Voici le contexte utilisateur :
Service : ${selectedService}
Type de problème : ${selectedIssue || "Autres"}
Description : ${input}
Donne une réponse claire, empathique et réaliste (sans inventer).
`;

  // 💬 Message utilisateur visible dans le chat
  const userVisibleMessage = input.trim();

  // Réinitialisation champ + passage au chat
  setInput("");
  setStep("chat");

  // Envoi au backend avec le prompt enrichi
  sendMessage(fullPrompt);

  // Mise à jour historique avec message simple (sans contexte technique)
  setHistory((prev) => [...prev, { question: userVisibleMessage, answer: "" }]);
};
  // 🔹 Initialisation message d’accueil
  useEffect(() => {
    if (history.length === 0) {
      setHistory([{ question: "", answer: "Sur quel type de service avez-vous un problème ?" }]);
    }
  }, []);

  return (
    <main className="min-h-screen bg-white text-black flex flex-col font-['Raleway']">
      {/* HEADER */}
      <header className="border-b px-6 py-4 flex items-center justify-between bg-gray-50 shadow-sm">
        <div className="flex items-center gap-3">
          <a href="https://www.free.fr" target="_blank" rel="noopener noreferrer">
            <Image src="/free.svg" alt="Free logo" width={90} height={32} className="object-contain -mt-1" />
          </a>
          <DropdownTailwind selected={selectedModel} onSelect={(val) => setSelectedModel(val)} />
        </div>
        <div className="flex gap-4 text-gray-500">
          <button title="Langue">🌐</button>
          <button title="Aide">❓</button>
        </div>
      </header>

      {/* CHAT SECTION */}
      <section className="flex-1 max-w-2xl w-full mx-auto px-4 py-8 overflow-y-auto">
        {history.map((entry, i) => (
          <div key={i} className="mb-6">
            {entry.question && (
              <div className="text-right mb-2">
                <div className="inline-block bg-red-50 border border-red-100 px-4 py-2 rounded-xl shadow-sm">
                  {entry.question}
                </div>
              </div>
            )}
            <div className="text-left whitespace-pre-wrap">
              <div className="inline-block bg-gray-50 border px-4 py-3 rounded-xl shadow-sm text-gray-800 prose prose-sm max-w-none">
                <ReactMarkdown>{entry.answer}</ReactMarkdown>
              </div>
            </div>
          </div>
        ))}

        {/* ÉTAPE 1 : CHOIX DU SERVICE */}
        {step === "categorie" && (
          <div className="flex flex-wrap gap-3 justify-center mt-6">
            {["Box", "Mobile", "Autres"].map((cat) => (
              <button
                key={cat}
                onClick={() => handleCategorieClick(cat)}
                className="px-5 py-2 bg-red-500 text-white rounded-full shadow-md hover:bg-red-600 transition text-sm sm:text-base"
              >
                {cat}
              </button>
            ))}
          </div>
        )}

        {/* ÉTAPE 2 : SOUS-CATÉGORIE SELON SERVICE */}
        {step === "sousCategorie" && selectedService in subCategories && (
          <div className="flex flex-wrap gap-3 justify-center mt-6">
            {subCategories[selectedService].map((subCat) => (
              <button
                key={subCat}
                onClick={() => handleSousCategorieClick(subCat)}
                className="px-5 py-2 bg-gray-200 text-gray-800 rounded-full shadow hover:bg-gray-300 transition text-sm sm:text-base"
              >
                {subCat}
              </button>
            ))}
          </div>
        )}
      </section>

      {/* ÉTAPE 3 : DESCRIPTION */}
      {(step === "description" || step === "chat") && (
        <footer className="border-t bg-white p-4 flex items-center justify-center">
          <div className="flex items-center gap-2 w-full max-w-2xl">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") handleSend();
              }}
              placeholder="Décrivez votre problème ici..."
              className="flex-1 border border-gray-300 rounded-full px-4 py-2 text-gray-800 focus:ring-2 focus:ring-red-500 outline-none"
            />
            <button
              onClick={handleSend}
              disabled={loading}
              className="w-10 h-10 flex items-center justify-center rounded-full bg-red-600 hover:bg-red-700 text-white shadow-md transition"
            >
              ➤
            </button>
          </div>
        </footer>
      )}
    </main>
  );
}
