'use client';
import Image from "next/image";
import Link from "next/link";
import { useState, useEffect } from "react";

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
    <div className="grid grid-cols-1 sm:grid-cols-2 min-h-screen p-8 sm:p-20 font-[family-name:var(--font-geist-sans)]">
      <div className="flex flex-col items-center justify-center gap-8">
        <h1 className="text-4xl font-bold">Welcome to LoanMe</h1>
        <div className="flex flex-col gap-4 w-full max-w-xs">
          {user ? (
            <>
              <p className="text-lg">Welcome, {user.email}</p>
              <button
                onClick={handleLogout}
                className="rounded-full border border-solid border-transparent transition-colors flex items-center justify-center bg-[#9BB67C] text-[#F5F1DA] gap-2 hover:bg-[#EEBB4D] text-sm sm:text-base h-10 sm:h-12 px-4 sm:px-5"
              >
                Log Out
              </button>
            </>
          ) : (
            <>
              <Link href="/account/create">
                <button className="rounded-full border border-solid border-transparent transition-colors flex items-center justify-center bg-[#9BB67C] text-[#F5F1DA] gap-2 hover:bg-[#EEBB4D] text-sm sm:text-base h-10 sm:h-12 px-4 sm:px-5">
                  Create Account
                </button>
              </Link>
              <Link href="/account/login">
                <button className="rounded-full border border-solid border-[#E3DFC8] transition-colors flex items-center justify-center hover:bg-[#F5F1DA] hover:border-transparent text-sm sm:text-base h-10 sm:h-12 px-4 sm:px-5">
                  Log In
                </button>
              </Link>
            </>
          )}
        </div>
      </div>
      <div className="flex flex-col items-center justify-center gap-8 p-8 sm:p-20 bg-[url('/green-lines.svg')] bg-no-repeat bg-center bg-[length:120%] bg-[#E3DFC8]">
        <h2 className="text-2xl font-semibold">Private credit made public.</h2>
        <ul className="list-none text-left">
          <li className="mb-2">Average loan of <strong>$121</strong>.</li>
          <li className="mb-2"><strong>5.6%</strong> Average APY.</li>
          <li className="mb-2">Decentralized and <strong>secure</strong>.</li>
        </ul>
      </div>
    </div>
  );
}
