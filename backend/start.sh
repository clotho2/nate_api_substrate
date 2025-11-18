#!/bin/bash
# Start the Substrate AI backend server

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}Starting Substrate AI Backend...${NC}"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${RED}Virtual environment not found!${NC}"
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "${GREEN}Activating virtual environment...${NC}"
source venv/bin/activate

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${RED}.env file not found!${NC}"
    echo "Copying .env.example to .env..."
    cp config/.env.example .env
    echo -e "${BLUE}Please edit .env and add your OPENROUTER_API_KEY${NC}"
    exit 1
fi

# Install/update dependencies
echo -e "${GREEN}Installing dependencies...${NC}"
pip install -q -r requirements.txt

# Create data directories if they don't exist
mkdir -p data/db data/chromadb

# Start the server
echo -e "${GREEN}Starting server on http://localhost:8284${NC}"
python api/server.py

