"use client";

import { useState, useEffect } from "react";
import TypingLoader from "@/app/components/TypingLoader";
import DropdownTailwind from "@/app/components/DropdownTailwind";
import ReactMarkdown from "react-markdown";
import Image from "next/image";
import remarkGfm from "remark-gfm";


export default function ChatPage() {
  const [input, setInput] = useState("");
  const [history, setHistory] = useState<{ question: string; answer: string }[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedModel, setSelectedModel] = useState("");
  const [step, setStep] = useState<"categorie" | "sousCategorie" | "description" | "chat">("categorie");
  const [selectedService, setSelectedService] = useState("");
  const [selectedIssue, setSelectedIssue] = useState("");
  const [userFeedback, setUserFeedback] = useState<"pending" | "yes" | "no" | null>(null);
  

  const subCategories: Record<string, string[]> = {
    Box: ["Wi-Fi", "TV", "Alimentation", "Internet"],
    Mobile: ["Réseau", "Forfait", "Appels", "Data"],
  };
  const context_model = `Tu es un assistant technique du support Free.
  Tu aides les utilisateurs à résoudre leurs problèmes liés aux services Free (Box, Mobile, etc.).
  Tu fournis des réponses claires et réalistes sans inventer d'informations.
  Tu poses des questions supplémentaires si nécessaire pour mieux comprendre le problème avant de proposer une solution.
  Tu ne dois jamais t'excuser sur ce que l'user a pu vivre avec Free.
  Tu dois toujours répondre en français.`;

const sendMessage = async (apiPrompt: string) => {
    setLoading(true);
    try {
      const res = await fetch("https://saviapi.win/chat_sav", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          prompt: apiPrompt,
          context: context_model,
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
    } catch {
      setHistory((prev) => {
        const updated = [...prev];
        updated[updated.length - 1].answer = "❌ Erreur lors de l'appel à l’API.";
        return updated;
      });
    } finally {
      setLoading(false);
    }
  };

  const formatNumberedAnswer = (raw: string) => {
    if (!raw) return raw;

    let text = raw.replace(/\r\n/g, "\n").trim();
    text = text.replace(/(^|\s)(\d+)\.\s*/g, (match, prefix, num) => {
      if (prefix.includes("\n")) return `${prefix}${num}. `;
      if (prefix === "") return `${num}. `;
      return `${prefix}\n${num}. `;
    });
    text = text.replace(/\n{3,}/g, "");
    return text;
  };

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

  const handleSend = () => {
    if (!input.trim()) return;
    const fullPrompt = `
Tu es un assistant technique du support Free.
Voici le contexte utilisateur :
Service : ${selectedService}
Type de problème : ${selectedIssue || "Autres"}
Description : ${input}
Donne une réponse claire, empathique et réaliste (sans inventer).
`.trim();
    setUserFeedback(null);

    const userVisibleMessage = input.trim();
    setHistory((prev) => [...prev, { question: userVisibleMessage, answer: "" }]);
    setInput("");
    setStep("chat");
    sendMessage(fullPrompt);
  };

  useEffect(() => {
    if (history.length === 0) {
      setHistory([{ question: "", answer: "Sur quel type de service avez-vous un problème ?" }]);
    }
  }, []);

  return (
    <main className="min-h-screen bg-white text-black flex flex-col font-['Raleway']">
      <header className="border-b px-6 py-4 flex items-center justify-between bg-gray-50 shadow-sm">
        <div className="flex items-center gap-3">
          <a href="https://www.free.fr" target="_blank" rel="noopener noreferrer">
            <Image src="/free.svg" alt="Free logo" width={90} height={32} className="object-contain -mt-1" />
          </a>
          <DropdownTailwind selected={selectedModel} onSelect={(val) => setSelectedModel(val)} />
        </div>
        <div className="flex gap-4 text-gray-500">
          <button title="Langue"><Image className="icone" src="/langue.svg" alt="langue logo" width={32} height={32} /></button>
          <button title="Account"><Image className="icone" src="/user-icone.svg" alt="user icone" width={32} height={32} /></button>
        </div> 
      </header>

      <section className="flex-1 max-w-2xl w-full mx-auto px-4 py-8 overflow-y-auto">
        {history.map((entry, i) => (
    <div key={i} className="mb-6">
      {/* Question utilisateur */}
      {entry.question && (
        <div className="text-right mb-2">
          <div className="inline-block bg-red-50 border border-red-100 px-4 py-2 rounded-xl shadow-sm">
            {entry.question}
          </div>
        </div>
      )}

      {/* Réponse LLM */}
      {entry.answer !== undefined && (
  <div className="text-left whitespace-pre-wrap">
    <div className="inline-block bg-gray-50 border px-4 py-3 rounded-xl shadow-sm text-gray-800 prose prose-sm max-w-none">
      {loading && entry.answer === "" ? (
        <div className="flex gap-1 justify-start items-center text-gray-400">
          <span className="w-2 h-2 bg-gray-600 rounded-full animate-bounce [animation-delay:-0.3s]"></span>
          <span className="w-2 h-2 bg-gray-600 rounded-full animate-bounce [animation-delay:-0.15s]"></span>
          <span className="w-2 h-2 bg-gray-600 rounded-full animate-bounce"></span>
        </div>
      ) : (
        <ReactMarkdown remarkPlugins={[remarkGfm]}>
          {formatNumberedAnswer(entry.answer)}
        </ReactMarkdown>
      )}
    </div>
  </div>
)}

      {/* OUI / NON */}
      {i === history.length - 1 &&
        step === "chat" &&
        entry.answer &&
        userFeedback === null && (
          <div className="mt-5 text-center">
            <p className="mb-3 text-gray-700 font-medium">
              Avez-vous résolu votre problème ?
            </p>
            <div className="flex justify-center gap-4">
              <button
                onClick={() => setUserFeedback("yes")}
                className="px-6 py-2 bg-[#0EBE34] text-white rounded-full shadow-md hover:bg-green-600 transition"
              >
                Oui
              </button>
              <button
                onClick={() => setUserFeedback("no")}
                className="px-6 py-2 bg-red-600 text-white rounded-full shadow-md hover:bg-red-700 transition"
              >
                Non
              </button>
            </div>
          </div>
        )}

      {/* Message final */}
      {i === history.length - 1 && userFeedback === "yes" && (
        <div className="mt-4 text-center text-gray-700">
          <p>Parfait 😄 ! Ravi d’avoir pu vous aider.</p>
          <p>N’hésitez pas à poser d’autres questions si besoin.</p>
        </div>
      )}

      {i === history.length - 1 && userFeedback === "no" && (
        <div className="mt-4 text-center text-gray-700">
          <p>Merci pour votre retour 🙏</p>
          <p>
            Un conseiller humain va vous recontacter dans les plus brefs délais.
          </p>
        </div>
      )}
    </div>
  ))}

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
              <Image src="/Arrow-up.svg" alt="arrow icone" width={20} height={20} className="" />
            </button>
          </div>
          <div className="Disclaimer">
              SAVIA peut commettre des erreurs. Il est recommandé de vérifier les informations importantes. 
          </div>
        </footer>
      )}
    </main>
  );
}
