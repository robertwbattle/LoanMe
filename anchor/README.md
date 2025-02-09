# Solana P2P Lending Platform

A decentralized lending platform built on Solana that enables peer-to-peer loans with customizable terms.

## Program ID
Current deployment on Solana devnet:
```
C3xL6yYf9jyCJfthRE2nWYeLS1RLDkaDnUf2zcrGYtMj
```

## Smart Contract Features
- Create loans with custom terms (amount, APY, duration)
- Process loan payments with real-time interest calculation
- Track loan status and repayment progress
- Support multiple active loans between same parties
- Built-in error handling and validation

## Prerequisites
- Solana CLI tools
- Node.js and npm
- Anchor Framework

## Wallet Setup

1. Install Solana CLI tools if you haven't already:
```bash
sh -c "$(curl -sSfL https://release.solana.com/stable/install)"
```

2. Create a new Solana wallet:
```bash
solana-keygen new --outfile ~/.config/solana/devnet.json
```

3. Set the CLI config to use devnet:
```bash
solana config set --url devnet
solana config set --keypair ~/.config/solana/devnet.json
```

4. Get some devnet SOL:
```bash
solana airdrop 2
```

You can check your balance with:
```bash
solana balance
```

## Installation & Setup

1. Clone the repository and install dependencies:
```bash
cd anchor
npm install
```

2. Create `.env` file in `anchor/app`:
```bash
WALLET_PRIVATE_KEY=["your","wallet","private","key","array"]
PROGRAM_ID="your_program_id_here"  # You'll get this after deployment
```

## Deployment Steps

1. Clean the existing build:
```bash
rm -rf target/
```

2. Build the program:
```bash
anchor build
```

3. Get your program ID:
```bash
anchor keys list
```

4. Update the program ID in three places:
   - At the top of `programs/sol-backend/src/lib.rs`:
   ```rust
   declare_id!("your_program_id_here");
   ```
   - In `Anchor.toml`:
   ```toml
   [programs.devnet]
   sol_backend = "your_program_id_here"
   ```
   - In your `.env` file as shown above

5. Rebuild with updated program ID:
```bash
anchor build
```

6. Deploy to devnet:
```bash
anchor deploy --provider.cluster devnet
```

7. Start the server:
```bash
npm start
```

## Smart Contract Structure

### Loan Account Structure
```rust
#[account]
pub struct LoanAccount {
    pub lender: Pubkey,
    pub borrower: Pubkey,
    pub amount: u64,
    pub apy: u16,
    pub paid_amount: u64,
    pub start_time: i64,
    pub duration: u32,
    pub is_active: bool,
}
```

## API Endpoints

### 1. Create Loan
```http
POST http://localhost:3000/loans
```

Request Body:
```json
{
    "borrowerPublicKey": "5FHwkrdxkjPmL7SMrU3mH9uXtZXAuH5NKiaXEGwdF9eZ",
    "loanAmount": 1000000000,  // 1 SOL
    "apy": 1000,               // 10%
    "duration": 31536000       // 1 year
}
```

Response:
```json
{
    "success": true,
    "transaction": "transaction_signature",
    "loanPDA": "loan_account_address"
}
```

### 2. Make Payment
```http
POST http://localhost:3000/loans/:loanPDA/payments
```

Request Body:
```json
{
    "paymentAmount": 100000000,  // 0.1 SOL
    "borrowerPrivateKey": [...]  // Borrower's private key array
}
```

Response:
```json
{
    "success": true,
    "transaction": "tx_signature",
    "loanStatus": {
        "originalAmount": "1000000000",
        "paidAmount": "100000000",
        "remainingAmount": "900000000",
        "interestAccrued": "50000000",
        "isActive": true,
        "completionPercentage": "10.00"
    }
}
```

## Testing
Run the test suite:
```bash
npm run test
```

## Development Scripts
Available in package.json:
```json
{
    "scripts": {
        "lint:fix": "prettier */**/*.{js,ts} -w",
        "lint": "prettier */**/*.{js,ts} --check",
        "build": "anchor build",
        "test": "anchor test",
        "start": "ts-node app/server.ts"
    }
}
```

## Security Considerations

1. **Private Key Management**
   - Never share private keys
   - Use proper key management in production
   - Store sensitive data securely

2. **Amount Calculations**
   - All amounts are in lamports (1 SOL = 1,000,000,000 lamports)
   - APY is in basis points (1000 = 10%)
   - Duration is in seconds

3. **Error Handling**
   - All transactions are validated
   - Comprehensive error checks included
   - Failed transactions return detailed error messages

## License
MIT