# EventConnect

EventConnect is a web application that helps users discover and manage events from their email. It uses AI to summarize event details and provides a clean interface for viewing and managing events.

## Features

- Email event scraping
- AI-powered event summarization
- Clean and modern UI
- Event management dashboard

## Tech Stack

- Backend: FastAPI, PostgreSQL, OpenAI
- Frontend: Next.js, TailwindCSS
- Deployment: Render (Backend), Vercel (Frontend)

## Setup

1. Clone the repository
2. Set up the backend:
   - Install Python dependencies: `pip install -r requirements.txt`
   - Configure environment variables (see .env.example)
   - Run the server: `uvicorn main:app --reload`

3. Set up the frontend:
   - Install Node.js dependencies: `npm install`
   - Configure environment variables
   - Run the development server: `npm run dev`

## Deployment

The application is deployed on:
- Backend: Render
- Frontend: Vercel 