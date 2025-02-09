import * as anchor from "@coral-xyz/anchor";
import { Program } from "@coral-xyz/anchor";
import { SolBackend } from "../target/types/sol_backend";
import { PublicKey, SystemProgram } from '@solana/web3.js';
import { expect } from 'chai';
import { describe, it } from 'mocha';
describe("sol-backend", () => {
  // Configure the client to use the local cluster.
  const provider = anchor.AnchorProvider.env();
  anchor.setProvider(provider);

  const program = anchor.workspace.SolBackend as Program<SolBackend>;
  const lender = provider.wallet;

  it("Is initialized!", async () => {
    // Add your test here.
    const tx = await program.methods.initialize().rpc();
    console.log("Your transaction signature", tx);
  });

  it("Creates a loan", async () => {
    const borrower = anchor.web3.Keypair.generate();
    
    const signature = await provider.connection.requestAirdrop(
      borrower.publicKey,
      1000000000
    );
    await provider.connection.confirmTransaction(signature);

    const [loanPDA] = await PublicKey.findProgramAddress(
      [
        Buffer.from("loan"),
        lender.publicKey.toBuffer(),
        borrower.publicKey.toBuffer(),
      ],
      program.programId
    );

    const loanAmount = new anchor.BN(100000000);
    const apy = new anchor.BN(1000).toNumber();
    const duration = new anchor.BN(365 * 24 * 60 * 60).toNumber();

    await program.methods
      .createLoan(loanAmount, apy, duration)
      .accounts({
        lender: lender.publicKey,
        borrower: borrower.publicKey,
      })
      .rpc();

    const loanAccount = await program.account.loanAccount.fetch(loanPDA);
    expect(loanAccount.lender.toString()).to.equal(lender.publicKey.toString());
    expect(loanAccount.borrower.toString()).to.equal(borrower.publicKey.toString());
    expect(loanAccount.amount.toNumber()).to.equal(loanAmount.toNumber());
  });

  it("Full loan lifecycle - create and repay", async () => {
    // Generate a new borrower for this test
    const borrower = anchor.web3.Keypair.generate();
    
    // Airdrop 2 SOL to borrower for testing
    const signature = await provider.connection.requestAirdrop(
      borrower.publicKey,
      2_000_000_000 // 2 SOL
    );
    await provider.connection.confirmTransaction(signature);

    // Create loan PDA
    const [loanPDA] = PublicKey.findProgramAddressSync(
      [
        Buffer.from("loan"),
        lender.publicKey.toBuffer(),
        borrower.publicKey.toBuffer(),
      ],
      program.programId
    );

    // Create a loan for 1 SOL with 10% APY
    const loanAmount = new anchor.BN(1_000_000_000); // 1 SOL
    const apy = new anchor.BN(1000).toNumber(); // Convert to number since we're using u16
    const duration = new anchor.BN(365 * 24 * 60 * 60).toNumber(); // Convert to number since we're using u32

    console.log("Creating loan...");
    await program.methods
      .createLoan(loanAmount, apy, duration)
      .accounts({
        lender: lender.publicKey,
        borrower: borrower.publicKey,
      })
      .rpc();

    // Verify loan creation
    let loanAccount = await program.account.loanAccount.fetch(loanPDA);
    console.log("Loan created with details:", {
      amount: loanAccount.amount.toString(),
      apy: loanAccount.apy.toString(),
      paidAmount: loanAccount.paidAmount.toString(),
      isActive: loanAccount.isActive
    });

    // Make first payment of 0.6 SOL
    console.log("Making first payment...");
    const firstPayment = new anchor.BN(600_000_000); // 0.6 SOL
    await program.methods
      .makePayment(firstPayment)
      .accounts({
        loanAccount: loanPDA,
        borrower: borrower.publicKey,
        lender: lender.publicKey,
      })
      .signers([borrower])
      .rpc();

    // Verify first payment
    loanAccount = await program.account.loanAccount.fetch(loanPDA);
    console.log("After first payment:", {
      paidAmount: loanAccount.paidAmount.toString(),
      isActive: loanAccount.isActive
    });

    // Make final payment of 0.4 SOL
    console.log("Making final payment...");
    const finalPayment = new anchor.BN(400_000_000); // 0.4 SOL
    await program.methods
      .makePayment(finalPayment)
      .accounts({
        loanAccount: loanPDA,
        borrower: borrower.publicKey,
        lender: lender.publicKey,
      })
      .signers([borrower])
      .rpc();

    // Verify loan is fully paid
    loanAccount = await program.account.loanAccount.fetch(loanPDA);
    console.log("After final payment:", {
      paidAmount: loanAccount.paidAmount.toString(),
      isActive: loanAccount.isActive
    });

    // Assertions
    expect(loanAccount.paidAmount.toString()).to.equal(loanAmount.toString());
    expect(loanAccount.isActive).to.be.false;
  });
});
