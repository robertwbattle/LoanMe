'use client';
import { useState } from 'react';

export default function Account() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleUpdate = async () => {
    const response = await fetch('http://localhost:5000/api/account', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
    const result = await response.json();
    alert(result.message);
  };

  return (
    <div className="p-6">
      <h1 className="text-2xl text-black font-bold mb-4">Account Settings</h1>
      <div className="space-y-4">
        <input
          type="email"
          placeholder="New Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="border p-2 w-full"
        />
        <input
          type="password"
          placeholder="New Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="border p-2 w-full"
        />
        <button onClick={handleUpdate} className="bg-blue-500 text-white px-4 py-2 rounded">
          Update Info
        </button>
      </div>
    </div>
  );
}
