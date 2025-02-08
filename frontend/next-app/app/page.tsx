import Image from "next/image";

export default function Home() {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 min-h-screen p-8 sm:p-20 font-[family-name:var(--font-geist-sans)]">
      <div className="flex flex-col items-center justify-center gap-8">
        <h1 className="text-4xl font-bold">Welcome to LoanMe</h1>
        <div className="flex flex-col gap-4 w-full max-w-xs">
          <button className="rounded-full border border-solid border-transparent transition-colors flex items-center justify-center bg-foreground text-background gap-2 hover:bg-[#383838] dark:hover:bg-[#ccc] text-sm sm:text-base h-10 sm:h-12 px-4 sm:px-5">
            Create Account
          </button>
          <button className="rounded-full border border-solid border-black/[.08] dark:border-white/[.145] transition-colors flex items-center justify-center hover:bg-[#f2f2f2] dark:hover:bg-[#1a1a1a] hover:border-transparent text-sm sm:text-base h-10 sm:h-12 px-4 sm:px-5">
            Log In
          </button>
        </div>
      </div>
      <div className="flex flex-col items-center justify-center gap-8 p-8 sm:p-20 bg-[url('/green-lines.svg')] bg-no-repeat bg-center bg-[length:120%]">
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
