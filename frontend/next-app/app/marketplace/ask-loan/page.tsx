'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function AskLoan() {
  const [loanAmount, setLoanAmount] = useState('');
  const [interestRate, setInterestRate] = useState('');
  const [paymentSchedule, setPaymentSchedule] = useState('');
  const router = useRouter();

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
        router.push('/marketplace');
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
      <h1 className="text-2xl font-bold mb-4">Ask for a Loan</h1>
      <div className="space-y-4">
        <input
          type="number"
          placeholder="Loan Amount"
          value={loanAmount}
          onChange={(e) => setLoanAmount(e.target.value)}
          className="border p-2 w-full"
        />
        <input
          type="number"
          placeholder="Interest Rate (%)"
          value={interestRate}
          onChange={(e) => setInterestRate(e.target.value)}
          className="border p-2 w-full"
        />
        <input
          type="text"
          placeholder="Payment Schedule"
          value={paymentSchedule}
          onChange={(e) => setPaymentSchedule(e.target.value)}
          className="border p-2 w-full"
        />
        <button onClick={handleAskLoan} className="bg-blue-500 text-white px-4 py-2 rounded">
          Ask for Loan
        </button>
      </div>
    </div>
  );
}
