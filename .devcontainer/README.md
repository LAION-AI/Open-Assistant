# devcontainer

## example usage

Below are some example use cases you might want to run from within the
devcontainer (either within VSCode or GitHub Codespaces).

### Run pre-commit

```bash
# run pre-commit
pre-commit run --all-files
```

### Docker compose

```bash
# build the image
docker compose up --build
```

You should see some docker containers being pulled and activated.

Once you see the line
`open-assistant-web-1 | Listening on port 3000 url: http://localhost:3000` you
should be able to access that port like below:

![port_forwarding](https://user-images.githubusercontent.com/2178292/210395676-e9c2aab5-cb54-4ae6-b1eb-ac929fd73607.png)

![website_example](https://user-images.githubusercontent.com/2178292/210396207-1b2e259f-4d5d-475d-b225-91e2bd004071.png)
