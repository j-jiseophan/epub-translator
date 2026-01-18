#!/bin/bash

# EPUB Translator - Start Script
# Starts both backend and frontend servers

cd "$(dirname "$0")"

echo "Starting EPUB Translator..."

# Start backend
echo "Starting backend server..."
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!
cd ..

# Wait for backend to be ready
sleep 2

# Start frontend
echo "Starting frontend server..."
cd frontend
npm run dev -- --port 5173 &
FRONTEND_PID=$!
cd ..

echo ""
echo "========================================="
echo "  EPUB Translator is running!"
echo "========================================="
echo "  Frontend: http://localhost:5173"
echo "  Backend:  http://localhost:8000"
echo "========================================="
echo ""
echo "Press Ctrl+C to stop all servers"

# Handle Ctrl+C to kill both processes
trap "echo 'Stopping servers...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" SIGINT SIGTERM

# Wait for both processes
wait
