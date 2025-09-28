"use client";
import { useState } from "react";
import { ChevronDown } from "lucide-react";

export default function DropdownTailwind({
  selected,
  onSelect,
}: {
  selected: string;
  onSelect: (value: string) => void;
}) {
  const [open, setOpen] = useState(false);
  const options = [
    {
      value: "Mistral-medium",
      title: "Mistral-medium",
      desc: "Modèle stable et rapide – recommandé pour la plupart des usages.",
    },
    {
      value: "Mistral-7B-Instruct",
      title: "Mistral-7B-Instruct (Bêta)",
      desc: "Version expérimentale, plus créative mais moins cohérente.",
    },
  ];

  const current = options.find((opt) => opt.value === selected);

  return (
    <div className="relative">
      {/* Bouton principal */}
      <button
        onClick={() => setOpen(!open)}
        className="
          flex items-center justify-between
          bg-white border border-gray-200
          text-gray-800 text-sm font-medium
          rounded-lg px-3 py-2 w-64
          shadow-sm hover:shadow-md
          focus:ring-2 focus:ring-red-400
          transition-all duration-150
        "
      >
        <div className="text-left">
          <p className="font-semibold text-20px] leading-tight">
            {current ? current.title : "Mistral-medium"}
          </p>
        </div>

        <ChevronDown
          className={`w-4 h-4 text-gray-500 ml-2 transition-transform duration-200 ${
            open ? "rotate-180" : ""
          }`}
        />
      </button>

      {/* Menu déroulant */}
      {open && (
        <div
          className="
            absolute mt-2 w-64 bg-white border border-gray-200 rounded-lg shadow-lg
            z-50 animate-fadeIn
          "
        >
          {options.map((opt) => (
            <button
              key={opt.value}
              onClick={() => {
                onSelect(opt.value);
                setOpen(false);
              }}
              className={`
                w-full text-left px-4 py-2.5 rounded-md transition-colors duration-100
                hover:bg-gray-100
                ${selected === opt.value ? "bg-gray-50 text-red-600" : "text-gray-800"}
              `}
            >
              <p className="font-semibold text-[13px] leading-tight">{opt.title}</p>
              <p className="text-xs text-gray-500 leading-snug">{opt.desc}</p>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
