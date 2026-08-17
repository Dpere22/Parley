# Parley - a messaging application

## Frontend

The frontend of the application is written in TypeScript using

- [react](https://react.dev/)
- [tailwind](https://tailwindcss.com/)
- [vite](https://vite.dev/)

### Setup

- Ensure you have modern version of Node.js installed, at least version 20. (I am using
  Node version 23.8.0.)

- If you are using `npm` on the command line, you can install the dependencies from within
  the `frontend` folder by running

  ```bash
  npm install
  ```

- If you are using `npm` in your IDE, follow your IDE instructions for installing Node
  dependencies.

### Development

Start the frontend server from within the `frontend` folder by running

```bash
npm run dev
```

Once the server is running, you can visit the site at `http://localhost:5173`.

### Type checking

Types for the API live in `src/types.ts` and mirror the pydantic models in
`backend/models.py`. Check them with

```bash
npm run typecheck
```

`npm run build` runs the same check before bundling.

### Tailwind CSS

The project is set up to use TailwindCSS. The only styles applied initially are in
the `body` and `div#root` components in `index.html` and the headers in `App.tsx`.
You may change these styles as you see fit.

### Routing

The project is set up to use `react-router` to define routes, in `App.tsx`. Routes that
need a logged in user are wrapped in `RequireAuth`, which redirects anonymous visitors
to the login page.

### Queries

The project is set up to use `react-query` for managing queries, mutations, and query
data. The query client and query client provider are in use in `App.tsx`, and the read
hooks are collected in `src/queries.ts`.

### Realtime

`src/useChatSocket.ts` opens a WebSocket to `/chats/{id}/ws` and writes incoming events
straight into the react-query cache, so an open chat updates without polling. The socket
reconnects with backoff, and refetches the message list on reconnect to pick up anything
missed.
