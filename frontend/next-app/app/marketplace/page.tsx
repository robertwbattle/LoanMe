'use client';
import { useEffect, useState } from 'react';
import Link from 'next/link';

interface Post {
  id: number;
  account_name: string;
  loan_amount: number;
  interest_rate: number;
  payment_schedule: string;
}

export default function Marketplace() {
  const [posts, setPosts] = useState<Post[]>([]);

  useEffect(() => {
    fetch('http://127.0.0.1:5000/api/posts')  // Update this URL if needed
      .then(res => res.json())
      .then(data => setPosts(data));
  }, []);

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Marketplace</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {posts.map((post) => (
          <Link key={post.id} href={`/marketplace/${post.id}`}>
            <div className="border p-4 rounded shadow-md hover:shadow-xl transition-shadow cursor-pointer bg-white">
              <h2 className="text-xl font-semibold">{post.account_name}</h2>
              <p>💰 Loan Amount: <strong>${post.loan_amount}</strong></p>
              <p>📈 Interest Rate: <strong>{post.interest_rate}%</strong></p>
              <p>📅 Payment Schedule: <strong>{post.payment_schedule}</strong></p>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
