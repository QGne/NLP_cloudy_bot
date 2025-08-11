#!/bin/bash

echo "🧹 Cleaning up ChatBot SaaS Prototype..."
echo "======================================="

read -p "Are you sure you want to destroy all resources? (yes/no): " confirmation

if [ "$confirmation" != "yes" ]; then
    echo "Cleanup cancelled."
    exit 0
fi

cd terraform

echo "🗑️  Destroying infrastructure..."
terraform destroy -auto-approve

echo "🧽 Cleaning up local files..."
rm -f chat_handler.zip
rm -f tfplan
rm -f terraform.tfstate.backup

cd ..

# Reset CLI config
echo "⚙️  Resetting CLI configuration..."
git checkout cli/config.py 2>/dev/null || echo "No git repo found, skipping config reset"

echo "✅ Cleanup complete!"