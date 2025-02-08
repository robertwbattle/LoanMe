'use client';
import { useEffect, useState } from 'react';

// ✅ Define the Activity Type
interface ActivityItem {
  type: string;
  details: string;
}

export default function Dashboard() {
  const [activity, setActivity] = useState<ActivityItem[]>([]);  // ✅ Set the correct type

  useEffect(() => {
    fetch('http://127.0.0.1:5000/api/activity')
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
