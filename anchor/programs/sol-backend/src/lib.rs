use anchor_lang::prelude::*;

declare_id!("HpEWLU7hUuDasqiVvZaL6bQAnyUTY9SUhHWTL9uz4kc4");

#[account]
#[derive(Default)]
pub struct LoanAccount {
    pub lender: Pubkey,
    pub borrower: Pubkey,
    pub amount: u64,
    pub apy: u16,
    pub paid_amount: u64,
    pub start_time: i64,
    pub duration: u32,
    pub is_active: bool,
    pub is_funded: bool,
}

const DISCRIMINATOR_LENGTH: usize = 8;
const PUBKEY_LENGTH: usize = 32;
const BOOL_LENGTH: usize = 1;

impl LoanAccount {
    pub const SPACE: usize = DISCRIMINATOR_LENGTH +
        (PUBKEY_LENGTH * 2) +  // lender + borrower
        8 + 2 + 8 + 8 + 4 + 1 + 1;  // amount + apy + paid_amount + start_time + duration + is_active + is_funded
}

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
        apy: u16,
        duration: u32,
        timestamp: i64,
    ) -> Result<()> {
        let loan_account = &mut ctx.accounts.loan_account;
        let clock = Clock::get()?;

        loan_account.lender = ctx.accounts.lender.key();
        loan_account.borrower = ctx.accounts.borrower.key();
        loan_account.amount = loan_amount;
        loan_account.apy = apy;
        loan_account.paid_amount = 0;
        loan_account.start_time = clock.unix_timestamp;
        loan_account.duration = duration;
        loan_account.is_active = true;
        loan_account.is_funded = false;

        Ok(())
    }

    pub fn fund_loan(ctx: Context<FundLoan>) -> Result<()> {
        let loan_account = &ctx.accounts.loan_account;
        require!(loan_account.is_active, LoanError::LoanNotActive);
        
        // Transfer the loan amount from lender to borrower
        let cpi_context = CpiContext::new(
            ctx.accounts.system_program.to_account_info(),
            anchor_lang::system_program::Transfer {
                from: ctx.accounts.lender.to_account_info(),
                to: ctx.accounts.borrower.to_account_info(),
            },
        );
        
        anchor_lang::system_program::transfer(cpi_context, loan_account.amount)?;
        
        Ok(())
    }

    pub fn make_payment(
        ctx: Context<MakePayment>,
        payment_amount: u64,
    ) -> Result<()> {
        let loan_account = &mut ctx.accounts.loanAccount;
        require!(loan_account.is_active, LoanError::LoanNotActive);
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
        loan_account.paid_amount = loan_account.paid_amount.checked_add(payment_amount)
            .ok_or(LoanError::CalculationError)?;

        // Check if loan is fully paid
        if loan_account.paid_amount >= loan_account.amount {
            loan_account.is_active = false;
        }

        Ok(())
    }
}

#[derive(Accounts)]
pub struct Initialize {}

#[derive(Accounts)]
#[instruction(timestamp: i64)]
pub struct CreateLoan<'info> {
    #[account(
        init,
        payer = lender,
        space = LoanAccount::SPACE,
        seeds = [
            b"loan",
            lender.key().as_ref(),
            borrower.key().as_ref(),
            timestamp.to_le_bytes().as_ref()
        ],
        bump
    )]
    pub loan_account: Account<'info, LoanAccount>,
    
    #[account(mut)]
    pub lender: Signer<'info>,
    
    pub borrower: Signer<'info>,
    
    pub system_program: Program<'info, System>,
}

impl<'info> CreateLoan<'info> {
    fn validate(&self) -> Result<()> {
        Ok(())
    }
}

#[derive(Accounts)]
#[instruction(payment_amount: u64)]
pub struct MakePayment<'info> {
    #[account(mut)]
    pub loanAccount: Account<'info, LoanAccount>,
    #[account(mut)]
    pub borrower: Signer<'info>,
    /// CHECK: Safe as we only transfer SOL
    #[account(mut)]
    pub lender: UncheckedAccount<'info>,
    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct FundLoan<'info> {
    #[account(
        mut,
        constraint = loan_account.lender == lender.key(),
        constraint = loan_account.borrower == borrower.key(),
        constraint = loan_account.is_active == true
    )]
    pub loan_account: Account<'info, LoanAccount>,
    
    #[account(mut)]
    pub lender: Signer<'info>,
    
    #[account(mut)]
    /// CHECK: This is safe because we verify it matches the loan account
    pub borrower: UncheckedAccount<'info>,
    
    pub system_program: Program<'info, System>,
}

#[error_code]
pub enum LoanError {
    #[msg("Loan is not active")]
    LoanNotActive,
    #[msg("Invalid payment amount")]
    InvalidPaymentAmount,
    #[msg("Calculation error")]
    CalculationError,
    #[msg("Invalid borrower")]
    InvalidBorrower,
    #[msg("Loan has already been funded")]
    LoanAlreadyFunded,
}
