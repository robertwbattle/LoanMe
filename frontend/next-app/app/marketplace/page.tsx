'use client';
import { useEffect, useState } from 'react';
import Link from 'next/link';

interface Post {
  id: number;
  account_name: string;
  loan_amount: number;
  interest_rate: number;
  payment_schedule: string;
  post_type: string; // Added to differentiate between borrow and lend
}

export default function Marketplace() {
  const [posts, setPosts] = useState<Post[]>([]);
  const [filterType, setFilterType] = useState<string>('all');
  const [minLoan, setMinLoan] = useState<number>(0);
  const [maxLoan, setMaxLoan] = useState<number>(100000);
  const [maxRate, setMaxRate] = useState<number>(10);

  useEffect(() => {
    fetch('http://127.0.0.1:5000/api/posts')
      .then(res => res.json())
      .then(data => setPosts(data));
  }, []);

  const filteredPosts = posts.filter(post => {
    return (
      (filterType === 'all' || post.post_type === filterType) &&
      post.loan_amount >= minLoan &&
      post.loan_amount <= maxLoan &&
      post.interest_rate <= maxRate
    );
  });

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Marketplace</h1>

      {/* Filter Section */}
      <div className="mb-6 flex flex-wrap gap-4">
        <select onChange={(e) => setFilterType(e.target.value)} className="border p-2 rounded">
          <option value="all">All</option>
          <option value="borrow">Borrow</option>
          <option value="lend">Lend</option>
        </select>

        <input
          type="number"
          placeholder="Min Loan Amount"
          value={minLoan}
          onChange={(e) => setMinLoan(Number(e.target.value))}
          className="border p-2 rounded"
        />

        <input
          type="number"
          placeholder="Max Loan Amount"
          value={maxLoan}
          onChange={(e) => setMaxLoan(Number(e.target.value))}
          className="border p-2 rounded"
        />

        <input
          type="number"
          placeholder="Max Interest Rate (%)"
          value={maxRate}
          onChange={(e) => setMaxRate(Number(e.target.value))}
          className="border p-2 rounded"
        />
      </div>

      {/* Display Filtered Posts */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredPosts.map((post) => (
          <Link key={post.id} href={`/marketplace/${post.id}`}>
            <div className="border p-4 rounded shadow-md hover:shadow-xl transition-shadow cursor-pointer bg-white">
              <h2 className="text-xl font-semibold">{post.account_name}</h2>
              <p>💰 Loan Amount: <strong>${post.loan_amount}</strong></p>
              <p>📈 Interest Rate: <strong>{post.interest_rate}%</strong></p>
              <p>📅 Payment Schedule: <strong>{post.payment_schedule}</strong></p>
              <p>🔄 Post Type: <strong>{post.post_type}</strong></p>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
