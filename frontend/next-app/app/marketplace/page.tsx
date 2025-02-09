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
  const [showOfferLoanModal, setShowOfferLoanModal] = useState(false);
  const [showAskLoanModal, setShowAskLoanModal] = useState(false);
  const [loanAmount, setLoanAmount] = useState('');
  const [interestRate, setInterestRate] = useState('');
  const [paymentSchedule, setPaymentSchedule] = useState('');

  useEffect(() => {
    fetch('http://127.0.0.1:5000/api/posts')  // Update this URL if needed
      .then(res => res.json())
      .then(data => setPosts(data));
  }, []);

  const handleOfferLoan = async () => {
    try {
      const response = await fetch('http://127.0.0.1:5000/api/posts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          post_type: 'lend',
          loan_amount: parseFloat(loanAmount),
          interest_rate: parseFloat(interestRate),
          payment_schedule: paymentSchedule,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      if (result.success) {
        setShowOfferLoanModal(false);
        fetch('http://127.0.0.1:5000/api/posts')
          .then(res => res.json())
          .then(data => setPosts(data));
      } else {
        alert(result.message);
      }
    } catch (error) {
      console.error('Error offering loan:', error);
      alert('Failed to offer loan. Please try again.');
    }
  };

  const handleAskLoan = async () => {
    try {
      const response = await fetch('http://127.0.0.1:5000/api/posts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          post_type: 'borrow',
          loan_amount: parseFloat(loanAmount),
          interest_rate: parseFloat(interestRate),
          payment_schedule: paymentSchedule,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      if (result.success) {
        setShowAskLoanModal(false);
        fetch('http://127.0.0.1:5000/api/posts')
          .then(res => res.json())
          .then(data => setPosts(data));
      } else {
        alert(result.message);
      }
    } catch (error) {
      console.error('Error asking for loan:', error);
      alert('Failed to ask for loan. Please try again.');
    }
  };

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Marketplace</h1>
      <div className="flex justify-between mb-4">
        <button onClick={() => setShowOfferLoanModal(true)} className="bg-green-500 text-white px-4 py-2 rounded">Offer a Loan</button>
        <button onClick={() => setShowAskLoanModal(true)} className="bg-blue-500 text-white px-4 py-2 rounded">Ask for a Loan</button>
      </div>
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

      {showOfferLoanModal && (
        <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50">
          <div className="bg-white p-6 rounded shadow-md">
            <h2 className="text-xl font-bold mb-4">Offer a Loan</h2>
            <input
              type="number"
              placeholder="Loan Amount"
              value={loanAmount}
              onChange={(e) => setLoanAmount(e.target.value)}
              className="border p-2 w-full mb-4"
            />
            <input
              type="number"
              placeholder="Interest Rate (%)"
              value={interestRate}
              onChange={(e) => setInterestRate(e.target.value)}
              className="border p-2 w-full mb-4"
            />
            <input
              type="text"
              placeholder="Payment Schedule (e.g., weekly, bi-weekly, monthly)"
              value={paymentSchedule}
              onChange={(e) => setPaymentSchedule(e.target.value)}
              className="border p-2 w-full mb-4"
            />
            <div className="text-sm text-gray-500 mb-4">
              Please enter the payment schedule in one of the following formats: weekly, bi-weekly, monthly.
            </div>
            <div className="flex justify-end gap-4">
              <button onClick={() => setShowOfferLoanModal(false)} className="bg-gray-500 text-white px-4 py-2 rounded">Cancel</button>
              <button onClick={handleOfferLoan} className="bg-green-500 text-white px-4 py-2 rounded">Offer Loan</button>
            </div>
          </div>
        </div>
      )}

      {showAskLoanModal && (
        <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50">
          <div className="bg-white p-6 rounded shadow-md">
            <h2 className="text-xl font-bold mb-4">Ask for a Loan</h2>
            <input
              type="number"
              placeholder="Loan Amount"
              value={loanAmount}
              onChange={(e) => setLoanAmount(e.target.value)}
              className="border p-2 w-full mb-4"
            />
            <input
              type="number"
              placeholder="Interest Rate (%)"
              value={interestRate}
              onChange={(e) => setInterestRate(e.target.value)}
              className="border p-2 w-full mb-4"
            />
            <input
              type="text"
              placeholder="Payment Schedule (e.g., weekly, bi-weekly, monthly)"
              value={paymentSchedule}
              onChange={(e) => setPaymentSchedule(e.target.value)}
              className="border p-2 w-full mb-4"
            />
            <div className="text-sm text-gray-500 mb-4">
              Please enter the payment schedule in one of the following formats: weekly, bi-weekly, monthly.
            </div>
            <div className="flex justify-end gap-4">
              <button onClick={() => setShowAskLoanModal(false)} className="bg-gray-500 text-white px-4 py-2 rounded">Cancel</button>
              <button onClick={handleAskLoan} className="bg-blue-500 text-white px-4 py-2 rounded">Ask for Loan</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
