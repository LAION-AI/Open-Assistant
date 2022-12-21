# End to End Demo

This sets up an entire stack needed to run Open Assistant, including the
website, backend, and associated dependent services.

To start the service, do the following:

```sh
docker compose up --build
```

Then, navigate to `http://localhost:3000` and interact with the website. When
logging in, navigate to `http://localhost:1080` to get the magic email login
link.
