#!/bin/bash

# Create the "secrets" directory if it doesn't exist
mkdir -p secrets

# Check if 'secrets/soiree-demo-loop.yaml' exists
if [ -f "secrets/soiree-demo-loop.yaml" ]; then
    read -p "'secrets/soiree-demo-loop.yaml' already exists. Do you want to overwrite it? (y/N) " decision
    if [[ ! "$decision" =~ ^[Yy]$ ]]; then
        echo "Aborting."
        exit 1
    fi
fi

# Generate a random 32 bytes in base64 format
RANDOM_STRING=$(head -c 16 /dev/urandom | od -An -tx1 | tr -d ' \n')

# Create the YAML content with the generated random string
cat <<EOF > secrets/soiree-demo-loop.yaml
apiVersion: itllib/v1
kind: LoopSecret
metadata:
  name: soiree-demo-loop
  creationTimestamp: null
spec:
  loopName: soiree-$RANDOM_STRING
  authenticationType: PASSWORD
  secretBasicAuth:
    endpoint: streams.thatone.ai:30000
    username: usernameGoesHere
    password: passwordGoesHere
  protocols: [basicAuth]
EOF

# Print a message to let the user know it's done
echo "Content written to secrets/soiree-demo-loop.yaml"


