'use client';
import Image from "next/image";
import Link from "next/link";
import { useState, useEffect } from "react";
import { Github, Twitter } from "@/components/shared/icons";
import Card from "../components/home/card";
import WebVitals from "../components/home/web-vitals"; // Add this import


export default function Home() {
  const [user, setUser] = useState(null);

  useEffect(() => {
    const storedUser = sessionStorage.getItem('user');
    if (storedUser) {
      setUser(JSON.parse(storedUser));
    }
  }, []);

  const handleLogout = () => {
    sessionStorage.removeItem('user');
    setUser(null);
  };

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-8">
      <div className="z-10 w-full max-w-xl px-5 xl:px-0">
        <a
          href="#"
          className="mx-auto mb-5 flex max-w-fit animate-fade-up items-center justify-center space-x-2 overflow-hidden rounded-full bg-blue-100 px-7 py-2 transition-colors hover:bg-blue-200"
        >
          <Twitter className="h-5 w-5 text-[#1d9bf0]" />
          <p className="text-sm font-semibold text-[#1d9bf0]">
            Welcome to LoanMe
          </p>
        </a>
        <h1
          className="animate-fade-up bg-gradient-to-br from-black to-stone-500 bg-clip-text text-center font-display text-4xl font-bold tracking-[-0.02em] text-transparent md:text-7xl md:leading-[5rem]"
          style={{ animationDelay: "0.15s" }}
        >
          Private credit public impact
        </h1>
        <p
          className="mt-6 animate-fade-up text-center text-gray-500 md:text-xl"
          style={{ animationDelay: "0.25s" }}
        >
          Decentralized lending platform with average 5.6% APY
        </p>
        
        <div
          className="mx-auto mt-6 flex animate-fade-up items-center justify-center space-x-5"
          style={{ animationDelay: "0.3s" }}
        >
          {user ? (
            <>
              <p className="text-lg text-gray-700">Welcome, {user.email}</p>
              <button
                onClick={handleLogout}
                className="group flex max-w-fit items-center justify-center space-x-2 rounded-full border border-black bg-black px-5 py-2 text-sm text-white transition-colors hover:bg-white hover:text-black"
              >
                Log Out
              </button>
            </>
          ) : (
            <>
              <Link href="/account/create">
                <button className="group flex max-w-fit items-center justify-center space-x-2 rounded-full border border-black bg-black px-5 py-2 text-sm text-white transition-colors hover:bg-white hover:text-black">
                  Create Account
                </button>
              </Link>
              <Link href="/account/login">
                <button className="flex max-w-fit items-center justify-center space-x-2 rounded-full border border-gray-300 bg-white px-5 py-2 text-sm text-gray-600 shadow-md transition-colors hover:border-gray-800">
                  Log In
                </button>
              </Link>
            </>
          )}
        </div>
      </div>
      <div className="my-10 grid w-full max-w-screen-xl animate-fade-up grid-cols-1 gap-5 px-5 md:grid-cols-3 xl:px-0">
      <Card
        title="Average Loan Size"
        description="Our platform facilitates an average loan size of $500+, making credit accessible to everyone."
        demo={<WebVitals percentage={500} prefix="$" />}
        large={true}
      />

      <Card
        title="Competitive APY"
        description="Earn an average of 5.6% APY on your investments while helping others access credit."
        demo={<WebVitals percentage={5.6} suffix="%" />}
      />
       <Card
        title="Secure Platform"
        description="Built on solana's blockchain technology ensuring transparent and secure transactions."
        demo={
          <div className="flex justify-center items-center">
            <Image
              src="/solana-logo.jpg"
              alt="Solana Logo"
              width={100}
              height={100}
            />
          </div>
        }
      />
      </div>
    </main>
  );
}