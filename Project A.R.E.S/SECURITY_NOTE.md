# ARES Security Note

This repository is intended to be a public showcase build of Project ARES.
Sensitive local data, prompt tuning, model routing experiments, and any proprietary logic
should be stored in the ignored `private_overrides/` directory or in a separate private repository.

Before publishing:
- make sure `.env` is not committed
- make sure `ares.db` is not committed
- keep private strategy files outside the public repo or inside `private_overrides/`
- review every commit before pushing
