"use client";

import Image from "next/image";
import Link from "next/link";

export default function Home() {
  return (
    <main className="min-h-screen bg-white text-black flex flex-col font-['Raleway']">
      {/* HEADER */}
      <header className="border-b px-6 py-4 flex items-center justify-between bg-gray-50 shadow-sm">
        <div className="flex items-center gap-3">
          <a href="https://www.free.fr" target="_blank" rel="noopener noreferrer">
            <Image
              src="/free.svg"
              alt="Free logo"
              width={90}
              height={32}
              className="object-contain -mt-1"
            />
          </a>
          <h1 className="text-lg font-semibold text-gray-700">Espace Client</h1>
        </div>
        <div className="flex gap-4 text-gray-500">
          <button title="Langue">
            <Image src="/langue.svg" alt="langue logo" width={32} height={32} />
          </button>
          <button title="Account">
            <Image src="/user-icone.svg" alt="user icone" width={32} height={32} />
          </button>
        </div>
      </header>

      {/* HERO SECTION */}
      <section className="flex-1 flex flex-col items-center justify-center text-center px-6 py-20">
        <h1 className="text-4xl font-bold mb-4 text-gray-900">
          Bienvenue chez Free Assistance
        </h1>
        <p className="text-gray-600 max-w-xl mb-8">
          Retrouvez toute l’aide dont vous avez besoin pour vos services Freebox et Mobile.  
          Notre assistant virtuel <span className="font-semibold text-red-600">SAVIA</span> est là pour vous aider 24h/24.
        </p>

        <Link
          href="/chat"
          className="px-8 py-3 bg-red-600 text-white rounded-full shadow-md hover:bg-red-700 transition text-lg"
        >
          Accéder à SAVIA
        </Link>
      </section>

      {/* FOOTER */}
      <footer className="border-t bg-gray-50 p-4 text-center text-sm text-gray-500">
        <p>
          © {new Date().getFullYear()} Free — Tous droits réservés.
        </p>
      </footer>
    </main>
  );
}
