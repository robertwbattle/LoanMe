'use client';
import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';

interface LoanDetail {
  id: number;
  account_name: string;
  loan_amount: number;
  interest_rate: number;
  payment_schedule: string;
  description: string;  // Optional: Add more fields as needed
}

export default function LoanDetailPage() {
  const { id } = useParams();
  const [loan, setLoan] = useState<LoanDetail | null>(null);

  useEffect(() => {
    fetch(`http://127.0.0.1:5000/api/posts/${id}`)
      .then(res => res.json())
      .then(data => setLoan(data));
  }, [id]);
  

  if (!loan) return <p>Loading loan details...</p>;

  return (
    <div className="p-6 max-w-2xl mx-auto bg-white rounded shadow-md">
      <h1 className="text-3xl font-bold mb-4">{loan.account_name}'s Loan</h1>
      <p className="mb-2">💰 Loan Amount: <strong>${loan.loan_amount}</strong></p>
      <p className="mb-2">📈 Interest Rate: <strong>{loan.interest_rate}%</strong></p>
      <p className="mb-2">📅 Payment Schedule: <strong>{loan.payment_schedule}</strong></p>
      <p className="mt-4">{loan.description}</p>

      <button className="mt-6 bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition">
        Apply for this Loan
      </button>
    </div>
  );
}
