# DoctorOS AI Frontend

React 18 + TypeScript + Vite + Tailwind. Talks to the FastAPI backend (see FRONTEND_API_CONTRACT).

## Run
1. Start the backend (http://localhost:8000). CORS allows localhost:5173.
2. `npm install`
3. `cp .env.example .env`  (set VITE_API_BASE_URL if your backend is elsewhere)
4. `npm run dev`  ->  http://localhost:5173

## Notes
- Login is form-data (username = email). Token lives in localStorage; any 401 redirects to /login.
- AI tabs (Assistant, Summary) need a scheduled/completed appointment with the patient (else 403 message).
- Not available in backend, shown as "Coming Soon": patient edit, medical history, allergies, appointment/visit/document lists, file viewer.

## Design (v2)
Vintage-anatomy "3D" theme built from the supplied artwork (public/images). Fonts are bundled via @fontsource
(Fraunces = headings, Manrope = UI text, Cinzel = small caps labels, JetBrains Mono = medical values).
3D effects are pure CSS (tilt cards, rotating caduceus coin, rotating print ring, login parallax) and switch off
automatically on touch screens and when "reduce motion" is enabled.

## Deploy
`npm run build` -> upload `dist/`. SPA rewrites are included for Vercel (vercel.json) and Netlify (public/_redirects).
Set `VITE_API_BASE_URL` to your HTTPS backend URL in the host's environment settings, and add your deployed
frontend origin to the backend CORS allow-list.
