<a href="https://github-com.translate.goog/LAION-AI/Open-Assistant/blob/main/docs/README.md?_x_tr_sl=auto&_x_tr_tl=en&_x_tr_hl=en&_x_tr_pto=wapp">![Translate](https://img.shields.io/badge/Translate-blue)</a>

# Docs Site

https://laion-ai.github.io/Open-Assistant/

This [site](https://laion-ai.github.io/Open-Assistant/) is built using
[Docusaurus 2](https://docusaurus.io/), a modern static website generator.

### Contributing

#### Changes to existing docs

You can just make a PR on whatever .md file you would like to update.

#### Changes to docs structure

If you would like to add a new category:

1. Create a new folder under `/docs/docs/` for the category you want to add.
1. Include any `.md` files you want to live under this new category.
1. Update the order or hierarchy in `/docs/sidebars.js` as needed.

If you would like to add a new page into an existing category:

1. Create the `.md` file you want in the relevant folder within `/docs/docs/`.
1. Update the hierarchy in `/docs/sidebars.js` as needed.

### Installation

From within the `/docs/` folder.

```
$ yarn
```

### Local Development

```
$ yarn start
```

This command starts a local development server and opens up a browser window.
Most changes are reflected live without having to restart the server.

### Browser Development

If you would like to work on the docs from within your browser you can create a
github codespace on your fork or branch. Then from within that codespace you can
run below commands to launch the docs site on port 3000 within your codespace.

```bash

# cd to docs dir
cd docs

# start dev server to work on your changes
yarn start
```

Once you port forward to port 3000 within your codespace you will be able to see
all changes reflected as soon as you make them.
