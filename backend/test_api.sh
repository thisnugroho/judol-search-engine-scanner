#!/bin/bash

echo "=== Testing API ==="
echo ""

# Test 1: Valid domain
echo "1. Testing with valid domain (example.com):"
curl -X POST http://localhost:5000/search \
  -H "Content-Type: application/json" \
  -d '{"domain": "ejurnal.iainpare.ac.id"}' \
  -w "\nStatus: %{http_code}\n\n"
