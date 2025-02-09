import { exec } from 'child_process';

export default function handler(req, res) {
  const { method } = req;

  switch (method) {
    case 'GET':
      // Get user by ID
      const userId = req.query.id;
      exec(`python /c:/Users/Robert/Desktop/LoanMe/backend/db.py get_user ${userId}`, (error, stdout, stderr) => {
        if (error) {
          res.status(500).json({ error: stderr });
          return;
        }
        res.status(200).json(JSON.parse(stdout));
      });
      break;
    case 'POST':
      // Add a new user
      const { username, password_hash, email, score } = req.body;
      exec(`python /c:/Users/Robert/Desktop/LoanMe/backend/db.py add_user ${username} ${password_hash} ${email} ${score}`, (error, stdout, stderr) => {
        if (error) {
          res.status(500).json({ error: stderr });
          return;
        }
        res.status(201).json({ message: 'User added successfully' });
      });
      break;
    default:
      res.setHeader('Allow', ['GET', 'POST']);
      res.status(405).end(`Method ${method} Not Allowed`);
  }
}
