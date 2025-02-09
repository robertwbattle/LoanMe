import * as anchor from "@coral-xyz/anchor";
import { Program } from "@coral-xyz/anchor";
import { SolBackend } from "../target/types/sol_backend";
import { PublicKey, Keypair } from '@solana/web3.js';
import { expect } from 'chai';

describe("SolBackend", () => {
  const provider = anchor.AnchorProvider.env();
  anchor.setProvider(provider);
  const program = anchor.workspace.SolBackend as Program<SolBackend>;

  it("Creates a loan account", async () => {
    // Generate a new keypair instead of using a hardcoded public key
    const borrowerKeypair = Keypair.generate();
    const timestamp = new anchor.BN(1234567890);
    
    // Create Buffer directly from number to match Rust's to_le_bytes()
    const timestampBuffer = Buffer.alloc(8);
    timestampBuffer.writeBigInt64LE(BigInt(timestamp.toString()));
    
    // Generate PDA
    const [loanPDA] = PublicKey.findProgramAddressSync(
      [
        Buffer.from("loan"),
        provider.wallet.publicKey.toBuffer(),
        borrowerKeypair.publicKey.toBuffer(),
        timestampBuffer
      ],
      program.programId
    );

    // Test parameters
    const loanAmount = new anchor.BN(100000000);
    const apy = 1000;
    const duration = 365 * 24 * 60 * 60;

    try {
      await program.methods
        .createLoan(
          loanAmount,
          apy,
          duration,
          timestamp
        )
        .accounts({
          lender: provider.wallet.publicKey,
          borrower: borrowerKeypair.publicKey,
        })
        .signers([borrowerKeypair])  // Add the borrower's keypair as a signer
        .rpc();

      const loanAccount = await program.account.loanAccount.fetch(loanPDA);
      expect(loanAccount.lender.toString()).to.equal(provider.wallet.publicKey.toString());
      expect(loanAccount.borrower.toString()).to.equal(borrowerKeypair.publicKey.toString());
      expect(loanAccount.amount.toNumber()).to.equal(loanAmount.toNumber());
    } catch (error) {
      console.error("Transaction failed:", error);
      throw error;
    }
  });

  it("Fails to create loan with invalid APY", async () => {
    const borrowerKeypair = Keypair.generate();
    const timestamp = new anchor.BN(Date.now());
    const loanAmount = new anchor.BN(100000000);
    const invalidApy = 10001; // Above 100%
    const duration = 365 * 24 * 60 * 60;

    try {
      await program.methods
        .createLoan(
          loanAmount,
          invalidApy,
          duration,
          timestamp
        )
        .accounts({
          lender: provider.wallet.publicKey,
          borrower: borrowerKeypair.publicKey,
        })
        .signers([borrowerKeypair])
        .rpc();
      expect.fail("Expected transaction to fail");
    } catch (error) {
      expect(error).to.be.an('error');
    }
  });

  it("Makes a payment on a loan", async () => {
    // Create loan first
    const borrowerKeypair = Keypair.generate();
    const timestamp = new anchor.BN(Date.now());
    const loanAmount = new anchor.BN(100000000);
    const apy = 1000;
    const duration = 365 * 24 * 60 * 60;

    const timestampBuffer = Buffer.alloc(8);
    timestampBuffer.writeBigInt64LE(BigInt(timestamp.toString()));
    
    const [loanPDA] = PublicKey.findProgramAddressSync(
      [
        Buffer.from("loan"),
        provider.wallet.publicKey.toBuffer(),
        borrowerKeypair.publicKey.toBuffer(),
        timestampBuffer
      ],
      program.programId
    );

    await program.methods
      .createLoan(loanAmount, apy, duration, timestamp)
      .accounts({
        lender: provider.wallet.publicKey,
        borrower: borrowerKeypair.publicKey,
      })
      .signers([borrowerKeypair])
      .rpc();

    // Make payment
    const paymentAmount = new anchor.BN(10000000);
    await program.methods
      .makePayment(paymentAmount)
      .accounts({
        loanAccount: loanPDA,
        borrower: borrowerKeypair.publicKey,
        lender: provider.wallet.publicKey,
      })
      .signers([borrowerKeypair])
      .rpc();

    // Verify payment was recorded
    const loanAccount = await program.account.loanAccount.fetch(loanPDA);
    expect(loanAccount.paidAmount.toNumber()).to.equal(paymentAmount.toNumber());
  });

  it("Fails to make payment with wrong borrower", async () => {
    const borrowerKeypair = Keypair.generate();
    const wrongBorrowerKeypair = Keypair.generate();
    const timestamp = new anchor.BN(Date.now());
    const loanAmount = new anchor.BN(100000000);
    
    const timestampBuffer = Buffer.alloc(8);
    timestampBuffer.writeBigInt64LE(BigInt(timestamp.toString()));
    
    const [loanPDA] = PublicKey.findProgramAddressSync(
      [
        Buffer.from("loan"),
        provider.wallet.publicKey.toBuffer(),
        borrowerKeypair.publicKey.toBuffer(),
        timestampBuffer
      ],
      program.programId
    );

    // Create loan
    await program.methods
      .createLoan(
        loanAmount,
        1000,
        365 * 24 * 60 * 60,
        timestamp
      )
      .accounts({
        lender: provider.wallet.publicKey,
        borrower: borrowerKeypair.publicKey,
      })
      .signers([borrowerKeypair])
      .rpc();

    // Try to make payment with wrong borrower
    try {
      await program.methods
        .makePayment(new anchor.BN(10000000))
        .accounts({
          loanAccount: loanPDA,
          borrower: wrongBorrowerKeypair.publicKey,
          lender: provider.wallet.publicKey,
        })
        .signers([wrongBorrowerKeypair])
        .rpc();
      expect.fail("Expected transaction to fail");
    } catch (error) {
      expect(error).to.be.an('error');
    }
  });
});