#!/bin/bash
################################################################################
# Surveillance Detection System - Application Launcher
#
# This script sets up the environment and launches the application.
#
# Requirements:
#   - Python 3.11+
#   - Virtual environment (venv) at ./venv
#
# Usage:
#   ./run.sh
################################################################################

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="$PROJECT_ROOT/venv"
PYTHON_EXEC="$VENV_PATH/bin/python"
PIP_EXEC="$VENV_PATH/bin/pip"

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}Surveillance Detection System v1.0.0${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""

# Check Python installation
echo -e "${YELLOW}Checking Python installation...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}ERROR: Python 3 is not installed${NC}"
    echo "Please install Python 3.11 or later from https://www.python.org"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}✓ Python $PYTHON_VERSION found${NC}"
echo ""

# Create virtual environment if not exists
if [ ! -d "$VENV_PATH" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv "$VENV_PATH"
    if [ $? -ne 0 ]; then
        echo -e "${RED}ERROR: Failed to create virtual environment${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}✓ Virtual environment exists${NC}"
fi

echo ""

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source "$VENV_PATH/bin/activate"
echo -e "${GREEN}✓ Virtual environment activated${NC}"
echo ""

# Install/upgrade requirements
echo -e "${YELLOW}Installing dependencies...${NC}"
$PIP_EXEC install --upgrade pip setuptools wheel > /dev/null 2>&1
$PIP_EXEC install -q -r "$PROJECT_ROOT/requirements.txt"
if [ $? -ne 0 ]; then
    echo -e "${RED}ERROR: Failed to install dependencies${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Dependencies installed${NC}"
echo ""

# Check config file
if [ ! -f "$PROJECT_ROOT/config.yaml" ]; then
    echo -e "${RED}ERROR: config.yaml not found${NC}"
    echo "Please copy config.yaml to the project root directory"
    exit 1
fi
echo -e "${GREEN}✓ Configuration file found${NC}"
echo ""

# Run Phase 1 tests (optional)
read -p "Run Phase 1 tests first? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Running Phase 1 tests...${NC}"
    $PYTHON_EXEC "$PROJECT_ROOT/test_phase1.py"
    if [ $? -ne 0 ]; then
        echo -e "${RED}Phase 1 tests failed. Please fix issues before running.${NC}"
        exit 1
    fi
    echo ""
fi

# Launch application
echo -e "${YELLOW}Launching Surveillance Detection System...${NC}"
echo -e "${GREEN}================================================${NC}"
echo ""

cd "$PROJECT_ROOT"
$PYTHON_EXEC main.py

# Capture exit code
EXIT_CODE=$?

echo ""
echo -e "${GREEN}================================================${NC}"

if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}Application closed successfully${NC}"
else
    echo -e "${RED}Application encountered an error (exit code: $EXIT_CODE)${NC}"
fi

echo ""
echo -e "${BLUE}================================================${NC}"

exit $EXIT_CODE