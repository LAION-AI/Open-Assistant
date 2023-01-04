# Website

This website is built using [Docusaurus 2](https://docusaurus.io/), a modern
static website generator.

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

### Build

```
$ yarn build
```

This command generates static content into the `build` directory and can be
served using any static contents hosting service.
