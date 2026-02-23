#!/bin/bash

echo "========================================"
echo "   Environment Variables Setup"
echo "========================================"
echo

echo "Setting up environment variables for 01Agent..."
echo

# Set default API URL
export 01AGENT_API_URL="http://localhost:8000"
echo "✓ 01AGENT_API_URL set to: $01AGENT_API_URL"

# Prompt for Thread ID
read -p "Enter your Thread ID: " 01AGENT_THREAD_ID
if [ -z "$01AGENT_THREAD_ID" ]; then
    export 01AGENT_THREAD_ID="default-thread-id"
    echo "⚠ Using default Thread ID: $01AGENT_THREAD_ID"
else
    export 01AGENT_THREAD_ID
    echo "✓ 01AGENT_THREAD_ID set to: $01AGENT_THREAD_ID"
fi

# Prompt for Access Token
read -p "Enter your Access Token: " 01AGENT_USER_ACCESS_TOKEN
if [ -z "$01AGENT_USER_ACCESS_TOKEN" ]; then
    export 01AGENT_USER_ACCESS_TOKEN="default-access-token"
    echo "⚠ Using default Access Token: $01AGENT_USER_ACCESS_TOKEN"
else
    export 01AGENT_USER_ACCESS_TOKEN
    echo "✓ 01AGENT_USER_ACCESS_TOKEN set"
fi

# Save to .env file for persistence
cat > .env << EOF
01AGENT_API_URL=$01AGENT_API_URL
01AGENT_THREAD_ID=$01AGENT_THREAD_ID
01AGENT_USER_ACCESS_TOKEN=$01AGENT_USER_ACCESS_TOKEN
EOF

echo
echo "========================================"
echo "Environment Setup Complete!"
echo "========================================"
echo
echo "Current settings:"
echo "API URL: $01AGENT_API_URL"
echo "Thread ID: $01AGENT_THREAD_ID"
echo "Access Token: [HIDDEN]"
echo
echo "Settings saved to .env file"
echo "You can now run: ./start-all-services.sh"
echo