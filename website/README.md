# Open-Assistant NextJS Website

## Purpose

This provides a comprehensive webapp interface for LAION's Open Assistant project. Initially it will support:

1.  User registration using either Discord or Email.
1.  Adding responses to incomplete Open Assistant tasks.
1.  Rating or Ranking responses to Open Assistant tasks.
1.  Viewing an activity leaderboard.
1.  Tracking community wide updates.

This interface compliments the Discord bot and will give access to the same underlying tasks.

## Contributing

### Major Dependencies

This website is built using:

1.  [npm](https://www.npmjs.com/): The node package manager for building.
1.  [React](https://reactjs.org/): The core frontend framework.
1.  [Next.js](https://nextjs.org/): A React scaffolding framework to streamline development.
1.  [Prisma](https://www.prisma.io/): An ORM to interact with a web specific [Postgres](https://www.postgresql.org/)
    database.
1.  [NextAuth.js](https://next-auth.js.org/): A user authentication framework to ensure we handle accounts with best
    practices.
1.  [TailwindCSS](https://tailwindcss.com/): A general purpose framework for styling any component.
1.  [Chakra-UI](https://chakra-ui.com/): A wide collection of pre-built UI components that generally look pretty good.

### Set up your environment

To contribute to the website, make sure you have the following setup and installed:

1.  [NVM](https://github.com/nvm-sh/nvm): The Node Version Manager makes it easy to ensure you have the right NodeJS
    version installed. Once installed, run `nvm use 16` to use Node 16.x. The website is known to be stable with NodeJS
    version 16.x. This will install both Node and NPM.
1.  [Docker](https://www.docker.com/): We use docker to simplify running dependent services.

### Getting everything up and running

If you're doing active development we suggest the following workflow:

1.  Open the terminal, navigate to the project root.
1.  Run `docker compose --profile frontend-dev up --build --attach-dependencies`. You can optionally include `-d` to
    detach and later track the logs if desired.
    - If you want to work on the chat api, you need to run the inference profile as well. Your new command would look
      like: `docker compose --profile frontend-dev --profile inference up --build --attach-dependencies`
    - See [FAQ](https://projects.laion.ai/Open-Assistant/docs/faq#enable-dockers-buildkit-backend) if you face any
      docker problems.
    - Leave this running in the background and continue:
1.  Open another terminal tab, navigate to `${OPEN_ASSISTANT_ROOT/website`.
1.  Run `npm ci`
1.  Run `npx prisma db push` (This is also needed when you restart the docker stack from scratch).
1.  Run `npm run dev`. Now the website is up and running locally at `http://localhost:3000`.
1.  To create an account, login via the user using email authentication and navigate to `http://localhost:1080`. Check
    the email listed and click the log in link. You're now logged in and authenticated.

### Using debug user credentials

You can use the debug credentials provider to log in without fancy emails or OAuth.

1. This feature is automatically on in development mode, i.e. when you run `npm run dev`. In case you want to do the
   same with a production build (for example, the docker image), then run the website with environment variable
   `DEBUG_LOGIN=true`.
1. Use the `Login` button in the top right to go to the login page.
1. You should see a section for debug credentials. Enter any username you wish, you will be logged in as that user.

### Using Storybook

To develop components using [Storybook](https://storybook.js.org/) run `npm run storybook`. Then navigate to in your
browser to `http://localhost:6006`.

To create a new story create a file named `[componentName].stories.js`. An example how such a story could look like, see
`Header.stories.jsx`.

## Code Layout

### React Code

All react code is under `src/` with a few sub directories:

1.  `pages/`: All pages a user could navigate too and API URLs which are under `pages/api/`.
1.  `components/`: All re-usable React components. If something gets used twice we should create a component and put it
    here.
1.  `lib/`: A generic place to store library files that are used anywhere. This doesn't have much structure yet.

NOTE: `styles/` can be ignored for now.

### Database

All database configurations are stored in `prisma/schema.prisma`.

### Static Content

All static images, fonts, svgs, etc are stored in `public/`.

### Styles

We're not really using CSS styles. `styles/` can be ignored.

## Testing the UI

Cypress is used for end-to-end (e2e) and component testing and is configured in `./cypress.config.ts`. The `./cypress`
folder is used for supporting configuration files etc.

- Store e2e tests in the `./cypress/e2e` folder.
- Store component tests adjacent to the component being tested. If you want to wriite a test for
  `./src/components/Layout.tsx` then store the test file at `./src/components/Layout.cy.tsx`.

A few npm scripts are available for convenience:

- `npm run cypress`: Useful for development, it opens Cypress and allows you to explore, run and debug tests. It assumes
  you have the NextJS site running at `localhost:3000`.
- `npm run cypress:run`: Runs all tests. Useful for a quick sanity check before sending a PR or to run in CI pipelines.
- `npm run cypress:image-baseline`: If you have tests failing because of visual changes that was expected, this command
  will update the baseline images stored in `./cypress-visual-screenshots/baseline` with those from the adjacent
  comparison folder. More can be found in the
  [docs of `uktrade/cypress-image-diff`](https://github.com/uktrade/cypress-image-diff/blob/main/docs/CLI.md#update-all-baseline-images-for-failing-tests).

Read more in the [./cypress README](cypress/).

## Unit testing

Jest and React Testing Library are used for unit testing JS/TS/TSX code.

- Store unit test files adjacent to the file being tested and have the filename end with `.test.ts` for non-React code
  or `.test.tsx` for React code.
- `npm run jest`: automatically runs tests and watches for any relevant changes to rerun tests.

Read more in the [./src/README.md](src/README.md).

## Best Practices

When writing code for the website, we have a few best practices:

1.  When importing packages import external dependencies first then local dependencies. Order them alphabetically
    according to the package name.
1.  When trying to implement something new, check if [Chakra-UI](https://chakra-ui.com/) has components that are close
    enough to your need. For example Sliders, Radio Buttons, Progress indicators, etc. They have a lot and we can save
    time by re-using what they have and tweaking the style as needed.
1.  Format everything with [Prettier](https://prettier.io/). This is done by default with pre-submits. We currently
    don't have any custom settings.
1.  Define functional React components (with types for all properties when feasible).

### Developing New Features

When working on new features or making significant changes that can't be done within a single Pull Request, we ask that
you make use of Feature Flags.

We've set up [`react-feature-flags`](https://www.npmjs.com/package/react-feature-flags) to make this easier. To get
started:

1.  Add a new flag entry to `website/src/flags.ts`. We have an example flag you can copy as an example. Be sure to
    `isActive` to true when testing your features but false when submitting your PR.
1.  Use your flag wherever you add a new UI element. This can be done with:

```js
import { Flags } from "react-feature-flags";
...
      <Flags authorizedFlags={["yourFlagName"]}>
        <YourNewComponent />
      </Flags>
```

    You can see an example of how this works by checking `website/src/components/Header/Headers.tsx` where we use `flagTest`.

1.  Once you've finished building out the feature and it is ready for everyone to use, it's safe to remove the `Flag`
    wrappers around your component and the entry in `flags.ts`.

### URL Paths

To use stable and consistent URL paths, we recommend the following strategy for new tasks:

1.  For any task that involves writing a free-form response, put the page under `website/src/pages/create` with a page
    name matching the task type, such as `initial_prompt.tsx`.
1.  For any task that evaluates, rates, or ranks content, put the page under `website/src/pages/evaluate` with a page
    name matching the task type such as `rank_initial_prompts.tsx`.

With this we'll be able to ensure these contribution pages are hidden from logged out users but accessible to logged in
users.

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.
