'use client';
import LoanMarketplace from "./LoanCards";

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