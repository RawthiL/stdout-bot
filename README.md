# RawthiL's stdout bot

This is an experimental bot to serve a Telegram-based conversational bot powered by [PNYX](https://pnyx.ai) (using [POKT Network](https://pocket.network/)).

Requirements:
- A telegram bot: https://core.telegram.org/bots
- A PNYX API key: https://pnyx.ai

To test just compile the image:
```bash
cd app
chmod +x build.sh
./build.sh
```

Then execute the bot using:
```bash
docker run -e TELEGRAM_TOKEN="your telegram token" -e LLM_URL="https://testnet-gateway.pnyxai.com/relay/text-to-text/v1" -e LLM_TOKEN="your pnyx gateway token" -e MODEL_NAME="pocket_network" -it rawthil_stdout_bot:latest
```

To communicate just talk to your bot!