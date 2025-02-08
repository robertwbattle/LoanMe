import type { Metadata } from "next";
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

export const metadata: Metadata = {
  title: "LoanMe - Your Decentralized Loan Platform",
  description: "Securely lend and borrow on the blockchain.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${geistSans.variable} ${geistMono.variable} antialiased`}> 
        {/* Navigation Bar */}
        <nav className="bg-gray-800 text-white p-4 flex justify-around items-center">
          <Link href="/" className="text-lg font-bold hover:text-gray-300">Home</Link>
          <Link href="/dashboard" className="hover:text-gray-300">Dashboard</Link>
          <Link href="/marketplace" className="hover:text-gray-300">Marketplace</Link>
          <Link href="/account" className="hover:text-gray-300">Account</Link>
        </nav>

        {/* Main Content */}
        <main className="p-6">{children}</main>
      </body>
    </html>
  );
}
