import express from 'express';
import cors from 'cors';
import * as anchor from "@coral-xyz/anchor";
import { Program } from "@coral-xyz/anchor";
import { PublicKey, Connection, Keypair, SystemProgram } from '@solana/web3.js';
import { SolBackend } from "../target/types/sol_backend";
import * as dotenv from 'dotenv';
import { workspace } from "@coral-xyz/anchor";

dotenv.config();

const app = express();
app.use(cors());
app.use(express.json());

// Initialize Solana connection and program
const connection = new Connection("https://api.devnet.solana.com");
console.log("🌐 Connected to Solana devnet");

const wallet = Keypair.fromSecretKey(
  Buffer.from(JSON.parse(process.env.WALLET_PRIVATE_KEY || '[]'))
);
console.log("👛 Wallet loaded with public key:", wallet.publicKey.toString());

const provider = new anchor.AnchorProvider(
  connection,
  new anchor.Wallet(wallet),
  { commitment: 'processed' }
);

// Initialize anchor provider
anchor.setProvider(provider);
console.log("🔗 Anchor provider set up");

const programId = new PublicKey(process.env.PROGRAM_ID || 'C3xL6yYf9jyCJfthRE2nWYeLS1RLDkaDnUf2zcrGYtMj');
console.log("📝 Program ID:", programId.toString());
const idl = require('../target/idl/sol_backend.json');
const program = workspace.SolBackend as Program<SolBackend>;

// Create a new loan
app.post('/loans', async (req, res) => {
  console.log("\n🏁 Creating new loan...");
  console.log("📥 Request body:", req.body);
  
  try {
    const { borrowerPublicKey, loanAmount, apy, duration } = req.body;
    const borrower = new PublicKey(borrowerPublicKey);
    console.log("👥 Borrower public key:", borrower.toString());
    console.log("💰 Loan amount:", loanAmount);
    console.log("📈 APY:", apy);
    console.log("⏱️ Duration:", duration);
    
    const [loanPDA] = PublicKey.findProgramAddressSync(
      [
        Buffer.from("loan"),
        wallet.publicKey.toBuffer(),
        borrower.toBuffer(),
      ],
      program.programId
    );
    console.log("🔑 Generated loan PDA:", loanPDA.toString());

    console.log("📝 Sending transaction to create loan...");
    const tx = await program.methods
      .createLoan(
        new anchor.BN(loanAmount),
        apy,
        duration
      )
      .accounts({
        lender: wallet.publicKey,
        borrower: borrower,
      })
      .rpc();
    console.log("✅ Loan created successfully!");
    console.log("📜 Transaction signature:", tx);

    res.json({
      success: true,
      transaction: tx,
      loanPDA: loanPDA.toString()
    });
  } catch (error: unknown) {
    console.error("❌ Error creating loan:", error);
    res.status(500).json({ 
      success: false, 
      error: error instanceof Error ? error.message : 'Unknown error occurred'
    });
  }
});

// Make a payment
app.post('/loans/:loanPDA/payments', async (req, res) => {
  console.log("\n💸 Processing payment...");
  console.log("📥 Request body:", req.body);
  
  try {
    const { loanPDA } = req.params;
    const { paymentAmount, borrowerPrivateKey } = req.body;
    console.log("🔑 Loan PDA:", loanPDA);
    console.log("💰 Payment amount:", paymentAmount);

    const borrower = Keypair.fromSecretKey(
      Buffer.from(JSON.parse(borrowerPrivateKey))
    );
    console.log("👤 Borrower public key:", borrower.publicKey.toString());

    console.log("📝 Sending payment transaction...");
    const tx = await program.methods
      .makePayment(new anchor.BN(paymentAmount))
      .accounts({
        loanAccount: new PublicKey(loanPDA),
        borrower: borrower.publicKey,
        lender: wallet.publicKey,
      })
      .signers([borrower])
      .rpc();
    console.log("✅ Payment transaction successful!");
    console.log("📜 Transaction signature:", tx);

    console.log("📊 Fetching updated loan details...");
    const loanAccount = await program.account.loanAccount.fetch(
      new PublicKey(loanPDA)
    );

    // Calculate interest accrued
    const currentTime = Math.floor(Date.now() / 1000);
    const timeElapsed = currentTime - Number(loanAccount.startTime);
    const yearInSeconds = 365 * 24 * 60 * 60;
    const interestRate = Number(loanAccount.apy) / 10000;
    const interestAccrued = Math.floor(
      (Number(loanAccount.amount) * interestRate * timeElapsed) / yearInSeconds
    );

    const totalOwed = Number(loanAccount.amount) + interestAccrued;
    const remainingAmount = totalOwed - Number(loanAccount.paidAmount);

    console.log("📈 Loan status:", {
      originalAmount: loanAccount.amount.toString(),
      paidAmount: loanAccount.paidAmount.toString(),
      remainingAmount: remainingAmount.toString(),
      interestAccrued: interestAccrued.toString(),
      isActive: loanAccount.isActive,
      completionPercentage: ((Number(loanAccount.paidAmount) / totalOwed) * 100).toFixed(2)
    });

    res.json({
      success: true,
      transaction: tx,
      loanStatus: {
        originalAmount: loanAccount.amount.toString(),
        paidAmount: loanAccount.paidAmount.toString(),
        remainingAmount: remainingAmount.toString(),
        interestAccrued: interestAccrued.toString(),
        isActive: loanAccount.isActive,
        completionPercentage: ((Number(loanAccount.paidAmount) / totalOwed) * 100).toFixed(2)
      }
    });
  } catch (error: unknown) {
    console.error("❌ Error processing payment:", error);
    res.status(500).json({ 
      success: false, 
      error: error instanceof Error ? error.message : 'Unknown error occurred'
    });
  }
});

// Get loan details
app.get('/loans/:loanPDA', async (req, res) => {
  try {
    const { loanPDA } = req.params;
    const loanAccount = await program.account.loanAccount.fetch(
      new PublicKey(loanPDA)
    );

    res.json({
      success: true,
      loan: {
        lender: loanAccount.lender.toString(),
        borrower: loanAccount.borrower.toString(),
        amount: loanAccount.amount.toString(),
        apy: loanAccount.apy.toString(),
        paidAmount: loanAccount.paidAmount.toString(),
        startTime: loanAccount.startTime.toString(),
        duration: loanAccount.duration.toString(),
        isActive: loanAccount.isActive
      }
    });
  } catch (error: unknown) {
    console.error(error);
    res.status(500).json({ 
      success: false, 
      error: error instanceof Error ? error.message : 'Unknown error occurred'
    });
  }
});

// Add this after your create loan endpoint
app.post('/loans/payment', async (req, res) => {
  try {
    const { loanPDA, paymentAmount } = req.body;

    const tx = await program.methods
      .makePayment(new anchor.BN(paymentAmount))
      .accounts({
        loanAccount: new PublicKey(loanPDA),
        borrower: wallet.publicKey,
        lender: wallet.publicKey,
      })
      .rpc();

    res.json({
      success: true,
      transaction: tx
    });
  } catch (error: unknown) {
    console.error(error);
    res.status(500).json({ 
      success: false, 
      error: error instanceof Error ? error.message : 'Unknown error occurred'
    });
  }
});

app.get('/test', (req, res) => {
  console.log("🧪 Test endpoint hit!");
  res.json({ message: "Server is working!" });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`\n🚀 Server running on port ${PORT}`);
  console.log('================================================');
});
