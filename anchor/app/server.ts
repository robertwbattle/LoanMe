import express from 'express';
import cors from 'cors';
import * as anchor from "@coral-xyz/anchor";
import { Program } from "@coral-xyz/anchor";
import { PublicKey, Connection, Keypair, SystemProgram } from '@solana/web3.js';
import { SolBackend } from "../target/types/sol_backend";
import * as dotenv from 'dotenv';

dotenv.config();

const app = express();
app.use(cors());
app.use(express.json());

// Initialize Solana connection and program
const connection = new Connection("https://api.devnet.solana.com");
const wallet = Keypair.fromSecretKey(
  Buffer.from(JSON.parse(process.env.WALLET_PRIVATE_KEY || '[]'))
);

const provider = new anchor.AnchorProvider(
  connection,
  new anchor.Wallet(wallet),
  { commitment: 'processed' }
);

const programId = new PublicKey(process.env.PROGRAM_ID || '66Q3U69jxDRPo9wo1TbiaTWP61NtoGpUw5tqnMjCzQwk');

// Initialize the program with the correct parameter order
const program = new Program<SolBackend>(
  {
    idl: require('../target/idl/sol_backend.json'),
    provider: provider,
    programId: programId
  }
);

// Create a new loan
app.post('/loans', async (req, res) => {
  try {
    const { borrowerPublicKey, loanAmount, apy, duration } = req.body;

    const borrower = new PublicKey(borrowerPublicKey);
    
    const [loanPDA] = PublicKey.findProgramAddressSync(
      [
        Buffer.from("loan"),
        wallet.publicKey.toBuffer(),
        borrower.toBuffer(),
      ],
      program.programId
    );

    const tx = await program.methods
      .createLoan(
        new anchor.BN(loanAmount),
        new anchor.BN(apy),
        new anchor.BN(duration)
      )
      .accounts({
        loanAccount: loanPDA,
        lender: wallet.publicKey,
        borrower: borrower,
        systemProgram: SystemProgram.programId,
      })
      .rpc();

    res.json({
      success: true,
      transaction: tx,
      loanPDA: loanPDA.toString()
    });
  } catch (error: unknown) {
    console.error(error);
    res.status(500).json({ 
      success: false, 
      error: error instanceof Error ? error.message : 'Unknown error occurred'
    });
  }
});

// Make a payment
app.post('/loans/:loanPDA/payments', async (req, res) => {
  try {
    const { loanPDA } = req.params;
    const { paymentAmount, borrowerPrivateKey } = req.body;

    const borrower = Keypair.fromSecretKey(
      Buffer.from(JSON.parse(borrowerPrivateKey))
    );

    const tx = await program.methods
      .makePayment(new anchor.BN(paymentAmount))
      .accounts({
        loanAccount: new PublicKey(loanPDA),
        borrower: borrower.publicKey,
        lender: wallet.publicKey,
        systemProgram: SystemProgram.programId,
      })
      .signers([borrower])
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

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
