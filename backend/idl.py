idl = {
    "version": "0.1.0",
    "name": "sol_backend",
    "instructions": [
        {
            "name": "createLoan",
            "accounts": [
                {
                    "name": "lender",
                    "isMut": True,
                    "isSigner": True
                },
                {
                    "name": "borrower",
                    "isMut": False,
                    "isSigner": False
                },
                {
                    "name": "system_program",
                    "isMut": False,
                    "isSigner": False
                },
                {
                    "name": "loan_account",
                    "isMut": True,
                    "isSigner": False,
                    "pda": {
                        "seeds": [
                            {
                                "kind": "const",
                                "type": "bytes",
                                "value": [108, 111, 97, 110]  // "loan" in bytes
                            },
                            {
                                "kind": "account",
                                "type": "publicKey",
                                "path": "lender"
                            },
                            {
                                "kind": "account",
                                "type": "publicKey",
                                "path": "borrower"
                            },
                            {
                                "kind": "arg",
                                "type": "i64",
                                "path": "timestamp"
                            }
                        ]
                    }
                }
            ],
            "args": [
                {
                    "name": "amount",
                    "type": "u64"
                },
                {
                    "name": "apy",
                    "type": "u16"
                },
                {
                    "name": "duration",
                    "type": "u32"
                },
                {
                    "name": "timestamp",
                    "type": "i64"
                }
            ]
        },
        {
            "name": "makePayment",
            "accounts": [
                {
                    "name": "loanAccount",
                    "isMut": True,
                    "isSigner": False
                },
                {
                    "name": "lender",
                    "isMut": True,
                    "isSigner": False
                },
                {
                    "name": "borrower",
                    "isMut": True,
                    "isSigner": True
                },
                {
                    "name": "system_program",
                    "isMut": False,
                    "isSigner": False
                }
            ],
            "args": [
                {
                    "name": "amount",
                    "type": "u64"
                }
            ]
        }
    ],
    "accounts": [
        {
            "name": "LoanAccount",
            "type": {
                "kind": "struct",
                "fields": [
                    {"name": "lender", "type": "publicKey"},
                    {"name": "borrower", "type": "publicKey"},
                    {"name": "amount", "type": "u64"},
                    {"name": "apy", "type": "u16"},
                    {"name": "paidAmount", "type": "u64"},
                    {"name": "startTime", "type": "i64"},
                    {"name": "duration", "type": "u32"},
                    {"name": "isActive", "type": "bool"}
                ]
            }
        }
    ],
    "metadata": {
        "address": "2LeZgHYfygZeDwg1GRsyAT2HpyB2KnD6zYJYCL4UFMV3"
    }
} 