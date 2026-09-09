# UpMarket Frontend

React + Vite + TypeScript + Tailwind CSS v4 — RTL Persian UI.

## Pages

- `/login`, `/register` — JWT auth
- `/` — dashboard: store list + create store
- `/stores/:id` — brand profile editing, product creation, product list
- `/products/:id` — product editing, image upload/delete, attributes, **AI intelligence panel**
  (analyze button → job progress polling → structured result display)

## Run (dev)

```powershell
cd frontend
npm install
npm run dev        # http://localhost:5173
```

The dev server proxies `/api` and `/media` to the Django backend at
`http://localhost:8000` (see `vite.config.ts`) — start the backend first.
If the backend runs on another host, change the proxy `target` accordingly.

## Build check

```powershell
npm run build      # type-check + production bundle in dist/
```

## Notes

- Tokens are stored in localStorage; the axios client auto-refreshes the access
  token on 401 and redirects to `/login` if refresh fails.
- The AI analyze flow needs the main system (Ollama + Redis + Celery worker) —
  on the dev machine the backend honestly returns 503 `queue_unavailable`.
