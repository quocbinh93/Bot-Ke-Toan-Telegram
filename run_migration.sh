#!/bin/bash

echo "=================================="
echo "DATABASE MIGRATION v1.0 → v2.0"
echo "=================================="
echo ""

# Check if accounting.db exists
if [ ! -f "accounting.db" ]; then
    echo "❌ Error: accounting.db not found!"
    echo "Please run the bot first to create database"
    exit 1
fi

# Backup
echo "📦 Creating backup..."
cp accounting.db accounting.db.backup_$(date +%Y%m%d_%H%M%S)
echo "✅ Backup created"
echo ""

# Run migration
echo "🔄 Running migration..."
python migrate_database.py

if [ $? -eq 0 ]; then
    echo ""
    echo "=================================="
    echo "✅ MIGRATION SUCCESSFUL!"
    echo "=================================="
    echo ""
    echo "Next steps:"
    echo "1. Restart bot: python main.py"
    echo "2. Test new features:"
    echo "   - /admin"
    echo "   - /pending"
    echo "   - /search_date 01/12/2025 31/12/2025"
    echo ""
else
    echo ""
    echo "=================================="
    echo "❌ MIGRATION FAILED!"
    echo "=================================="
    echo "Database has been restored from backup"
    echo "Please check errors and try again"
fi
