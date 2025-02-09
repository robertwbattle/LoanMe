import * as anchor from "@coral-xyz/anchor";
import { Program } from "@coral-xyz/anchor";
import { SolBackend } from "../target/types/sol_backend";
import { PublicKey } from '@solana/web3.js';
import { expect } from 'chai';

describe("SolBackend", () => {
  const provider = anchor.AnchorProvider.env();
  anchor.setProvider(provider);
  const program = anchor.workspace.SolBackend as Program<SolBackend>;

  it("Creates a loan account", async () => {
    // Setup with fixed values for debugging
    const borrower = new PublicKey("HrAhp4tFjQcPQGfXW2uMddRhTd97yN4n2WNTRScmDG9w");
    const timestamp = new anchor.BN(1234567890);
    
    // Create Buffer directly from number to match Rust's to_le_bytes()
    const timestampBuffer = Buffer.alloc(8);
    timestampBuffer.writeBigInt64LE(BigInt(timestamp.toString()));
    
    // Generate PDA
    const [loanPDA] = PublicKey.findProgramAddressSync(
      [
        Buffer.from("loan"),
        provider.wallet.publicKey.toBuffer(),
        borrower.toBuffer(),
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
          loanAccount: loanPDA,
          lender: provider.wallet.publicKey,
          borrower: borrower,
          systemProgram: anchor.web3.SystemProgram.programId,
        })
        .rpc();
    } catch (error) {
      console.error("Transaction failed:", error);
      throw error;
    }
  });
});