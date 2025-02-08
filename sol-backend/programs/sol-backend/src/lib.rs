use anchor_lang::prelude::*;

declare_id!("66Q3U69jxDRPo9wo1TbiaTWP61NtoGpUw5tqnMjCzQwk");

#[program]
pub mod sol_backend {
    use super::*;

    pub fn initialize(ctx: Context<Initialize>) -> Result<()> {
        msg!("Greetings from: {:?}", ctx.program_id);
        Ok(())
    }
}

#[derive(Accounts)]
pub struct Initialize {}
