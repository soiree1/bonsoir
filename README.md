Running the example shimmer-chatgpt agent:
```bash
# I don't have dns or a local instance set up yet for communication.
# streams.thatone.ai is essentially kafka-over-websockets.
docker run --rm -it --add-host streams.thatone.ai:216.153.52.171 synthbot/eqmesh:v0.1.0

export OPENAI_API_KEY='openai-api-key-goes-here'
python3 eqmesh/src/examples/sunset-shimmer/shimmer_agent-chatgpt.py
# NOTE: Right now, this will invoke the GPT-4 API every 60 seconds, unless the LLM
# decides to check at a different interval.
```

That will create a config.yaml file to connect to the bot.

To connect:
```bash
docker exec -it $(docker ps  --filter ancestor=synthbot/eqmesh:v0.1.0 -n1 -q) bash

python3 -m itlmon --config config.yaml
# IMPORTANT: if you restart the chatbot, it will regenerate a new config.yaml
# and you'll need to re-run the itlmon command.
```

Interacting with the chatbot:
- Click on a channel name on the left to open it. (Or use Ctrl+Up / Ctrl+Down to navigate).
- Send a message in the user-messages channel.
- Receive messages in the sunset-shimmer channel.
- `/quit` in any channel to close the chat interface.

To connect through a different machine:
```bash
# copy config.yaml to the target machine
pip install 'git+https://github.com/ThatOneAI/itlmon'
python3 -m itlmon --config config.yaml
# NOTE: Right now, all user messages are sent as if from the same user. The chatbot
# will not differentiate between messages sent by different people.
```
