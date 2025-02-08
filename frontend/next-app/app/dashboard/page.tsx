'use client';
import { useEffect, useState } from 'react';

export default function Dashboard() {
  const [activity, setActivity] = useState([]);

  useEffect(() => {
    // Replace with actual API endpoint
    fetch('http://localhost:5000/api/activity')
      .then(res => res.json())
      .then(data => setActivity(data));
  }, []);

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
    </div>
  );
}
