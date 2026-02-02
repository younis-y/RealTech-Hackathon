# Domus Frontend

Next.js web application for the Domus housing recommendation platform.

## Features

- 🎯 Persona-based recommendations (Student, Parent, Developer)
- 🏘️ Real-time London area data
- 🤖 AI-powered explanations
- 📊 Transparent factor breakdowns
- ⚡ Fast, responsive UI

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Backend**: Python tools via API routes

## Getting Started

1. Install dependencies:
   ```bash
   npm install
   ```

2. Run development server:
   ```bash
   npm run dev
   ```

3. Open http://localhost:3000

## Project Structure

```
frontend/
├── app/
│   ├── page.tsx              # Homepage with input form
│   ├── results/page.tsx      # Results display
│   ├── api/
│   │   └── recommendations/
│   │       └── route.ts      # API route to Python backend
│   ├── layout.tsx            # Root layout
│   └── globals.css           # Global styles
├── components/               # Reusable components (future)
└── lib/                      # Utilities (future)
```

## API Integration

The frontend calls Python tools through Next.js API routes:
- Form data → `/api/recommendations` → Python `demo_pipeline.py` → Results

## Deployment

Ready to deploy to Vercel:
```bash
npm run build
vercel deploy
```

## Development Notes

- API route spawns Python process to run recommendations
- Results are cached in sessionStorage for navigation
- Tailwind CSS for rapid styling
- TypeScript for type safety
