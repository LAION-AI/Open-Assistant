# Fill Database

## Requirements

For filling the database with mock data, you should first turn off the checkers
that we have about for ensuring correct data in our database.

So go inside of the **oasst_backend.config**: _DEBUG_SKIP_API_KEY_CHECK: bool =
False_.

## Script

With the backend environment working, we could run this script to fill the
database.

We have the following arguments:

- _api_clients_: amount of api clients that we want to create
- _users_: amount of users that we want to create
- _use_seed_: use a seed for the random generation of the data

So an example would be:

```bash
    python3 filldb.py --api_clients=10 --users=10 --use_seed=False
```
