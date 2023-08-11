# ☄️ NovaOSS API Server
Reverse proxy server for "Closed"AI's API.

> "*OpenAI is very closed*"
> 
> — [ArsTechnica (July 2023)](https://arstechnica.com/information-technology/2023/07/is-chatgpt-getting-worse-over-time-study-claims-yes-but-others-arent-sure/)

We aim to fix that!

## NovaOSS APIs
Our infrastructure might seem a bit confusing, but it's actually quite simple. Just the first one really matters for you, if you want to access our AI API. The other ones are just for the team.

### AI API
**Public** (everyone can use it with a valid API key)

Official endpoints: `https://api.nova-oss.com/v1/...`
Documentation & info: [nova-oss.com](https://nova-oss.com)

- Access to AI models

***

### User/Account management API
**Private** (NovaOSS operators only!)

Official endpoints: `https://api.nova-oss.com/...`
Documentation: [api.nova-oss.com/docs](https://api.nova-oss.com/docs)

- Access to user accounts
- Implemented in [NovaCord](https://nova-oss.com/novacord)

### Website API
**Private** (NovaOSS operators only!)

Official endpoints: `https://nova-oss.com/api/...`

This one's code can be found in the following repository: [github.com/novaoss/nova-web](https://github.com/novaoss/nova-web)

- Used for the Terms of Service (ToS) verification for the Discord bot.
- In a different repository and with a different domain because it needs to display codes on the website.
- Implemented in [NovaCord](https://nova-oss.com/novacord)

## Install & self-host
See [setup.md](setup.md)
