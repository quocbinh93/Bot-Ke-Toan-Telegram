#!/bin/bash
# Web Admin Panel Startup Script for Git Bash/Linux

echo "=================================="
echo "WEB ADMIN PANEL"
echo "=================================="
echo ""
echo "Starting web server..."
echo ""
echo "URL: http://localhost:5000"
echo "Default Password: admin123"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=================================="
echo ""

python webapp/app.py
