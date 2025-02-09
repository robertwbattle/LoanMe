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
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased bg-[#E3DFC8] text-gray-900`}
      >
        {/* ✅ Navigation Bar */}
        <nav className="bg-[#9BB67C] shadow-md sticky top-0 z-50 p-4 px-8 flex justify-between items-center border-b border-gray-300">
          <Link href="/">
            <h1 className="text-2xl font-extrabold text-white tracking-wide hover:text-[#EEBB4D] transition-transform duration-300 ease-in-out transform hover:scale-110">
              LoanMe
            </h1>
          </Link>
          <div className="flex space-x-6 text-sm font-medium">
            <Link 
              href="/dashboard" 
              className="text-white hover:text-[#EEBB4D] transition-transform duration-300 ease-in-out transform hover:scale-110"
            >
              Dashboard
            </Link>
            <Link 
              href="/marketplace" 
              className="text-white hover:text-[#EEBB4D] transition-transform duration-300 ease-in-out transform hover:scale-110"
            >
              Marketplace
            </Link>
            <Link 
              href="/account" 
              className="text-white hover:text-[#EEBB4D] transition-transform duration-300 ease-in-out transform hover:scale-110"
            >
              Account
            </Link>
          </div>
        </nav>

        {/* ✅ Main Content with Responsive Layout */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 bg-[#F5F1DA] rounded-xl shadow-md">
          {children}
        </main>

        {/* ✅ Footer */}
        <footer className="bg-[#9BB67C] text-white text-center p-4 mt-10 rounded-t-xl shadow-inner">
          <p className="text-sm font-medium">
            © {new Date().getFullYear()} LoanMe. All rights reserved.
          </p>
        </footer>
      </body>
    </html>
  );
}
