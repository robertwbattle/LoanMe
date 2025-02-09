'use client';
import { useEffect, useState } from 'react';

interface ActivityItem {
  type: string;
  details: string;
}

interface Loan {
  id: number;
  loan_amount: number;
  interest_rate: number;
  payment_schedule: string;
  amount_due: number;
  amount_paid: number;
  payment_status: string;
}

export default function Dashboard() {
  const [activity, setActivity] = useState<ActivityItem[]>([]);
  const [loans, setLoans] = useState<Loan[]>([]);
  const [user, setUser] = useState(null);

  useEffect(() => {
    fetch('http://127.0.0.1:5000/api/activity')
      .then(res => res.json())
      .then(data => setActivity(data));
  }, []);

  useEffect(() => {
    const storedUser = sessionStorage.getItem('user');
    if (storedUser) {
      setUser(JSON.parse(storedUser));
    }
  }, []);

  useEffect(() => {
    if (user) {
      fetch(`http://127.0.0.1:5000/api/user/${user.user_id}/loans`)
        .then(res => res.json())
        .then(data => setLoans(data));
    }
  }, [user]);

  const handlePayLoan = async (loanId: number, amount: number) => {
    try {
      const response = await fetch(`http://127.0.0.1:5000/api/loans/${loanId}/pay`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ amount }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      if (result.success) {
        alert('Payment successful!');
        fetch(`http://127.0.0.1:5000/api/user/${user.user_id}/loans`)
          .then(res => res.json())
          .then(data => setLoans(data));
      } else {
        alert(result.message);
      }
    } catch (error) {
      console.error('Error paying loan:', error);
      alert('Failed to pay loan. Please try again.');
    }
  };

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Your Activity</h1>
      {activity.length === 0 ? (
        <p>No recent activity.</p>
      ) : (
        <ul>
          {activity.map((item, index) => (
            <li key={index} className="p-4 border-b">
              <strong>{item.type}</strong> - {item.details}
            </li>
          ))}
        </ul>
      )}
      <h1 className="text-2xl font-bold mb-4">Your Loans</h1>
      {loans.length === 0 ? (
        <p>No loans found.</p>
      ) : (
        <ul>
          {loans.map((loan) => (
            <li key={loan.id} className="p-4 border-b">
              <p>💰 Loan Amount: <strong>${loan.loan_amount}</strong></p>
              <p>📈 Interest Rate: <strong>{loan.interest_rate}%</strong></p>
              <p>📅 Payment Schedule: <strong>{loan.payment_schedule}</strong></p>
              <p>💸 Amount Due: <strong>${loan.amount_due}</strong></p>
              <p>💵 Amount Paid: <strong>${loan.amount_paid}</strong></p>
              <p>📅 Payment Status: <strong>{loan.payment_status}</strong></p>
              <button
                onClick={() => handlePayLoan(loan.id, loan.amount_due)}
                className="mt-2 bg-blue-500 text-white px-4 py-2 rounded"
              >
                Pay Loan
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
