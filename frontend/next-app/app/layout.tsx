"use client";

import { Geist, Geist_Mono } from "next/font/google";
import Link from "next/link";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${geistSans.variable} ${geistMono.variable} antialiased relative`}>
        {/* Background gradient - moved to back */}
        <div className="fixed inset-0 bg-gradient-to-br from-indigo-50 via-white to-cyan-100 -z-10" />
        
        {/* Content wrapper - ensure content stays above background */}
        <div className="relative z-0 min-h-screen flex flex-col">
          {/* ✅ Navigation Bar */}
          <nav className="sticky top-0 z-50 p-4 px-8 flex justify-between items-center border-b border-gray-200 bg-white/50 backdrop-blur-xl">
            <Link href="/">
              <h1 className="text-2xl font-extrabold text-gray-800 tracking-wide hover:text-indigo-600 transition-transform duration-300 ease-in-out transform hover:scale-110">
                LoanMe
              </h1>
            </Link>
            <div className="flex space-x-6 text-sm font-medium">
              <Link 
                href="/dashboard" 
                className="text-gray-600 hover:text-indigo-600 transition-transform duration-300 ease-in-out transform hover:scale-110"
              >
                Dashboard
              </Link>
              <Link 
                href="/marketplace" 
                className="text-gray-600 hover:text-indigo-600 transition-transform duration-300 ease-in-out transform hover:scale-110"
              >
                Marketplace
              </Link>
              <Link 
                href="/account" 
                className="text-gray-600 hover:text-indigo-600 transition-transform duration-300 ease-in-out transform hover:scale-110"
              >
                Account
              </Link>
            </div>
          </nav>

          {/* ✅ Main Content */}
          <main className="flex-grow container mx-auto px-4 py-8">
            {children}
          </main>

          {/* ✅ Footer */}
          <footer className="w-full border-t border-gray-200 bg-white/50 backdrop-blur-xl p-8 text-center">
            <p className="text-sm text-gray-600">
              © {new Date().getFullYear()} LoanMe. All rights reserved.
            </p>
          </footer>
        </div>
      </body>
    </html>
  );
}