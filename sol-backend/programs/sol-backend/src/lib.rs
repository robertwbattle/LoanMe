use anchor_lang::prelude::*;

declare_id!("66Q3U69jxDRPo9wo1TbiaTWP61NtoGpUw5tqnMjCzQwk");

#[program]
pub mod sol_backend {
    use super::*;

    pub fn initialize(ctx: Context<Initialize>) -> Result<()> {
        msg!("Greetings from: {:?}", ctx.program_id);
        Ok(())
    }

    pub fn create_loan(
        ctx: Context<CreateLoan>,
        loan_amount: u64,
        apy: u64,
        duration: i64,
    ) -> Result<()> {
        let loan = &mut ctx.accounts.loan;
        let clock = Clock::get()?;

        loan.lender = ctx.accounts.lender.key();
        loan.borrower = ctx.accounts.borrower.key();
        loan.amount = loan_amount;
        loan.apy = apy;
        loan.paid_amount = 0;
        loan.start_time = clock.unix_timestamp;
        loan.duration = duration;
        loan.is_active = true;

        Ok(())
    }

    pub fn make_payment(
        ctx: Context<MakePayment>,
        payment_amount: u64,
    ) -> Result<()> {
        let loan = &mut ctx.accounts.loan;
        require!(loan.is_active, LoanError::LoanNotActive);
        require!(payment_amount > 0, LoanError::InvalidPaymentAmount);

        // Transfer payment from borrower to lender
        let cpi_context = CpiContext::new(
            ctx.accounts.system_program.to_account_info(),
            anchor_lang::system_program::Transfer {
                from: ctx.accounts.borrower.to_account_info(),
                to: ctx.accounts.lender.to_account_info(),
            },
        );
        anchor_lang::system_program::transfer(cpi_context, payment_amount)?;

        // Update loan state
        loan.paid_amount = loan.paid_amount.checked_add(payment_amount)
            .ok_or(LoanError::CalculationError)?;

        // Check if loan is fully paid
        if loan.paid_amount >= loan.amount {
            loan.is_active = false;
        }

        Ok(())
    }
}

#[derive(Accounts)]
pub struct Initialize {}

#[derive(Accounts)]
pub struct CreateLoan<'info> {
    #[account(
        init,
        payer = lender,
        space = 8 + LoanAccount::SPACE,
        seeds = [b"loan", lender.key().as_ref(), borrower.key().as_ref()],
        bump
    )]
    pub loan: Account<'info, LoanAccount>,
    #[account(mut)]
    pub lender: Signer<'info>,
    /// CHECK: This is safe because we only store the pubkey
    pub borrower: UncheckedAccount<'info>,
    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct MakePayment<'info> {
    #[account(
        mut,
        seeds = [b"loan", loan.lender.as_ref(), loan.borrower.as_ref()],
        bump,
        constraint = loan.borrower == borrower.key()
    )]
    pub loan: Account<'info, LoanAccount>,
    #[account(mut)]
    pub borrower: Signer<'info>,
    /// CHECK: This is safe as we only transfer SOL to this account
    #[account(mut, constraint = loan.lender == lender.key())]
    pub lender: UncheckedAccount<'info>,
    pub system_program: Program<'info, System>,
}

#[account]
pub struct LoanAccount {
    pub lender: Pubkey,
    pub borrower: Pubkey,
    pub amount: u64,
    pub apy: u64,
    pub paid_amount: u64,
    pub start_time: i64,
    pub duration: i64,
    pub is_active: bool,
}

impl LoanAccount {
    pub const SPACE: usize = 32 + // lender pubkey
                            32 + // borrower pubkey
                            8 + // amount
                            8 + // apy
                            8 + // paid_amount
                            8 + // start_time
                            8 + // duration
                            1; // is_active
}

#[error_code]
pub enum LoanError {
    #[msg("Loan is not active")]
    LoanNotActive,
    #[msg("Invalid payment amount")]
    InvalidPaymentAmount,
    #[msg("Calculation error")]
    CalculationError,
}
