Running the example shimmer-chatgpt agent:
```bash
# I don't have dns or a local instance set up yet for communication.
# streams.thatone.ai is essentially kafka-over-websockets.
docker run --rm -it --add-host streams.thatone.ai:216.153.52.171 synthbot/eqmesh:v0.2.0

# Create an isolated communication environment
./eqmesh/examples/sunset-shimmer/create-secrets.sh

# Run the chatbot
export OPENAI_API_KEY='openai-api-key-goes-here'
python3 eqmesh/examples/sunset-shimmer/shimmer_agent-chatgpt.py

# NOTE: Right now, this will invoke the GPT-4 API every 60 seconds, unless the LLM
# decides to check at a different interval.
```

To connect:
```bash
docker exec -it $(docker ps  --filter ancestor=synthbot/eqmesh:v0.2.0 -n1 -q) bash

python3 -m itlmon --config eqmesh/examples/sunset-shimmer/config.yaml
```

Interacting with the chatbot:
- Click on a channel name on the left to open it. (Or use Ctrl+Up, Ctrl+Down to navigate).
- Send a message in the user-messages channel.
- Receive messages in the sunset-shimmer channel.
- `/quit` in any channel to close the chat interface.

To connect to the chatbot remotely:
```bash
# copy config.yaml from the container to the remote machine
# copy the secrets/ folder from the container to the remote machine

pip install --upgrade "git+https://github.com/ThatOneAI/itlmon"

python3 -m itlmon --config config.yaml --secrets ./secrets/
```
