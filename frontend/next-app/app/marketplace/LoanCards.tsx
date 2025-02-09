"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

interface LoanPost {
  id: number;
  account_name: string;
  loan_amount: number;
  interest_rate: number;
  payment_schedule: string;
  post_type: string;
}

export default function LoanMarketplace() {
  const [posts, setPosts] = useState<LoanPost[]>([]);
  const [filterType, setFilterType] = useState<string>("all");
  const [sortOption, setSortOption] = useState<string>("none");

  useEffect(() => {
    fetch("http://localhost:5000/api/posts")
      .then((res) => res.json())
      .then((data) => setPosts(data))
      .catch((err) => console.error("Error fetching posts:", err));
  }, []);

  const filteredPosts = posts
    .filter((post) => filterType === "all" || post.post_type === filterType)
    .sort((a, b) => {
      if (sortOption === "loan_amount") {
        return b.loan_amount - a.loan_amount;
      } else if (sortOption === "interest_rate") {
        return b.interest_rate - a.interest_rate;
      }
      return 0;
    });

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <h1 className="text-3xl font-bold text-[#9BB67C] mb-6">Loan Marketplace</h1>

      {/* Filters and Sorting */}
      <div className="flex gap-4 mb-6">
        <select
          onChange={(e) => setFilterType(e.target.value)}
          className="border p-2 rounded bg-white shadow-sm"
        >
          <option value="all">All</option>
          <option value="borrow">Borrow Requests</option>
          <option value="lend">Lend Offers</option>
        </select>

        <select
          onChange={(e) => setSortOption(e.target.value)}
          className="border p-2 rounded bg-white shadow-sm"
        >
          <option value="none">Sort By</option>
          <option value="loan_amount">Loan Amount (High to Low)</option>
          <option value="interest_rate">Interest Rate (High to Low)</option>
        </select>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredPosts.map((post) => (
          <Link key={post.id} href={`/marketplace/${post.id}`}>
            <div className="bg-[#F5F1DA] border-2 border-[#9BB67C] rounded-xl shadow-md p-6 cursor-pointer transform transition-transform duration-300 hover:scale-105 hover:shadow-xl">
              <h2 className="text-xl font-semibold text-[#9BB67C] mb-2">
                {post.account_name}
              </h2>
              <p className="text-gray-700 mb-1">
                💰 Loan Amount: <strong>${post.loan_amount}</strong>
              </p>
              <p className="text-gray-700 mb-1">
                📈 Interest Rate: <strong>{post.interest_rate}%</strong>
              </p>
              <p className="text-gray-700 mb-1">
                📅 Payment Schedule: <strong>{post.payment_schedule}</strong>
              </p>
              <p className="text-gray-700 mb-2">
                🔄 Type: <strong>{post.post_type}</strong>
              </p>
              <button className="mt-4 w-full bg-[#9BB67C] text-white py-2 rounded-lg hover:bg-[#EEBB4D] transition duration-300">
                View Details
              </button>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
