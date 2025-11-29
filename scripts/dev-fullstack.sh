#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
BACKEND_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FRONTEND_REPO="https://github.com/bijalsanghavi/qrbusinesscard-frontend.git"
FRONTEND_DIR="${BACKEND_DIR}/../qrbusinesscard-frontend"

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}   QR Business Card - Full Stack Local Development   ${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Cleanup function
cleanup() {
    echo ""
    echo -e "${YELLOW}Shutting down...${NC}"

    if [ ! -z "$BACKEND_PID" ]; then
        echo "Stopping backend (PID: $BACKEND_PID)"
        kill $BACKEND_PID 2>/dev/null || true
    fi

    if [ ! -z "$FRONTEND_PID" ]; then
        echo "Stopping frontend (PID: $FRONTEND_PID)"
        kill $FRONTEND_PID 2>/dev/null || true
    fi

    # Also kill any child processes
    pkill -P $$ 2>/dev/null || true

    echo -e "${GREEN}✅ Cleanup complete${NC}"
    exit 0
}

# Set trap for cleanup
trap cleanup EXIT INT TERM

# Step 1: Check if Docker is running (for Postgres)
echo -e "${BLUE}[1/5]${NC} Checking Docker..."
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running!${NC}"
    echo "Please start Docker Desktop and try again."
    exit 1
fi
echo -e "${GREEN}✅ Docker is running${NC}"
echo ""

# Step 2: Start backend
echo -e "${BLUE}[2/5]${NC} Starting backend..."
cd "$BACKEND_DIR"

# Check if Postgres is already running
if docker ps | grep -q qrbusinesscard-db; then
    echo "Postgres already running"
else
    echo "Starting Postgres..."
    docker compose up -d db
    echo "Waiting for Postgres to be ready..."
    sleep 3
fi

# Start backend with run.sh
echo "Starting FastAPI on http://localhost:3001"
./scripts/run.sh > /tmp/qr-backend.log 2>&1 &
BACKEND_PID=$!

# Wait for backend to be ready
echo "Waiting for backend to start..."
for i in {1..30}; do
    if curl -s http://localhost:3001/healthz > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Backend ready at http://localhost:3001${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}❌ Backend failed to start. Check logs at /tmp/qr-backend.log${NC}"
        tail -20 /tmp/qr-backend.log
        exit 1
    fi
    sleep 1
done
echo ""

# Step 3: Setup frontend
echo -e "${BLUE}[3/5]${NC} Setting up frontend..."

if [ ! -d "$FRONTEND_DIR" ]; then
    echo "Frontend repo not found. Cloning..."
    cd "$(dirname "$FRONTEND_DIR")"

    # Check if user wants to clone or if they have a different location
    echo -e "${YELLOW}Frontend repo not found at: $FRONTEND_DIR${NC}"
    echo "Do you want to:"
    echo "  1) Clone from GitHub (default repo)"
    echo "  2) Specify a different local path"
    echo "  3) Skip frontend (backend only)"
    read -p "Choice [1-3]: " choice

    case $choice in
        2)
            read -p "Enter path to frontend directory: " custom_path
            FRONTEND_DIR="$custom_path"
            ;;
        3)
            echo -e "${YELLOW}Skipping frontend. Backend running at http://localhost:3001${NC}"
            echo "Press Ctrl+C to stop"
            wait $BACKEND_PID
            exit 0
            ;;
        *)
            read -p "Enter GitHub repo URL [$FRONTEND_REPO]: " repo_input
            FRONTEND_REPO="${repo_input:-$FRONTEND_REPO}"
            git clone "$FRONTEND_REPO" "$FRONTEND_DIR"
            ;;
    esac
fi

cd "$FRONTEND_DIR"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi

# Create .env.local if it doesn't exist
if [ ! -f ".env.local" ]; then
    echo "Creating .env.local..."
    cat > .env.local << EOF
VITE_API_URL=http://localhost:3001
EOF
fi

echo -e "${GREEN}✅ Frontend setup complete${NC}"
echo ""

# Step 4: Start frontend
echo -e "${BLUE}[4/5]${NC} Starting frontend..."
echo "Starting Vite dev server on http://localhost:5173"
npm run dev > /tmp/qr-frontend.log 2>&1 &
FRONTEND_PID=$!

# Wait for frontend to be ready
echo "Waiting for frontend to start..."
for i in {1..30}; do
    if curl -s http://localhost:5173 > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Frontend ready at http://localhost:5173${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}❌ Frontend failed to start. Check logs at /tmp/qr-frontend.log${NC}"
        tail -20 /tmp/qr-frontend.log
        exit 1
    fi
    sleep 1
done
echo ""

# Step 5: Open in browser
echo -e "${BLUE}[5/5]${NC} Opening browser..."
sleep 2

# Detect OS and open browser
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    open http://localhost:5173
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    xdg-open http://localhost:5173
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
    # Windows
    start http://localhost:5173
fi

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}   🚀 Full Stack Development Environment Ready!      ${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "  ${BLUE}Frontend:${NC} http://localhost:5173"
echo -e "  ${BLUE}Backend:${NC}  http://localhost:3001"
echo -e "  ${BLUE}API Docs:${NC} http://localhost:3001/docs"
echo ""
echo -e "  ${YELLOW}Logs:${NC}"
echo -e "    Backend:  tail -f /tmp/qr-backend.log"
echo -e "    Frontend: tail -f /tmp/qr-frontend.log"
echo ""
echo -e "  ${YELLOW}Press Ctrl+C to stop all services${NC}"
echo ""

# Keep script running
wait $BACKEND_PID $FRONTEND_PID
