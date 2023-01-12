# Script to Fill DB with Mock Data

Currently, script is capable of generating random users and messagetrees with
supported dependencies. A root message tree can have at most 5 children each of
which can have from 0 to 3 messages.

Usage is simple as:

```
python3 main.py --users 100 --trees 50
```

Script is aligned with DB schema as of 11 Jan 2023.
