# ☄️ NovaOSS API Server
Reverse proxy server for "Closed"AI's API.

![Badge showing the most used language](https://img.shields.io/github/languages/top/novaoss/nova-api)
![Badge showing the code size](https://img.shields.io/github/languages/code-size/novaoss/nova-api)
![Discord Badge](https://img.shields.io/discord/1120037287300976640)
![Badge showing the number of issues](https://img.shields.io/github/issues/novaoss/nova-api)
![Badge showing the number of pull requests](https://img.shields.io/github/issues-pr/novaoss/nova-api)
![Badge showing the license](https://img.shields.io/github/license/novaoss/nova-api)

![Badge showing the number of stars](https://img.shields.io/github/stars/novaoss/nova-api?style=social)
![Badge showing the number of forks](https://img.shields.io/github/forks/novaoss/nova-api?style=social)
![Badge showing the number of watchers](https://img.shields.io/github/watchers/novaoss/nova-api?style=social)

![Nova-API Conver/Banner Image - a picture of a galaxy with the caption "the core API server"](https://i.ibb.co/ZBhkS56/nova-api.png)

> "*OpenAI is very closed*"
> 
> — [ArsTechnica (July 2023)](https://arstechnica.com/information-technology/2023/07/is-chatgpt-getting-worse-over-time-study-claims-yes-but-others-arent-sure/)

We aim to fix that!

## Star History


###### *I founded FoxGPT (called *NovaGPT* back then)
Old, slow, deprecated* FoxGPT vs new NovaAI repository star count:

<a href="https://star-history.com/#NovaOSS/nova-api&FoxGPT/gpt&Date">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=NovaOSS/nova-api,FoxGPT/gpt&type=Date&theme=dark" />
    <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=NovaOSS/nova-api,FoxGPT/gpt&type=Date" />
    <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=NovaOSS/nova-api,FoxGPT/gpt&type=Date" />
  </picture>
</a>

<img alt="'Emotional damage' meme, with a man with a worried face and the yellow caption 'emotional damage'" src="https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Findianmemetemplates.com%2Fwp-content%2Fuploads%2Femotional-damage-1024x575.jpg&f=1&nofb=1&ipt=b325721ee0a7b9e11603a9bd484c8042b82e1704e639887107c6ce3e0d9b389e&ipo=images" height=100>

## NovaOSS APIs
Our infrastructure might seem a bit confusing, but it's actually quite simple. Just the first one really matters for you, if you want to access our AI API. The other ones are just for the team.

### AI API
**Public** (everyone can use it with a valid API key)

Endpoint: `https://api.nova-oss.com/v1/...`
Documentation & info: [nova-oss.com](https://nova-oss.com)

- Access to AI models

***

### User/Account management API
**Private** (NovaOSS operators only!)

Endpoint: `https://api.nova-oss.com/...`
Documentation: [api.nova-oss.com/docs](https://api.nova-oss.com/docs)

- Access to user accounts
- Implemented in [NovaCord](https://nova-oss.com/novacord)

### NovaCord Bot API
**Private** (NovaOSS operators only!)

Endpoint: `http://0.0.0.0:3224/...`

- acess to Discord server member roles (for receiving the Discord level, ...)
- hosted using [NovaCord](https://nova-oss.com/novacord)

### Website API
**Private** (NovaOSS operators only!)

Endpoint: `https://nova-oss.com/api/...`

This one's code can be found in the following repository: [github.com/novaoss/nova-web](https://github.com/novaoss/nova-web)

- Used for the Terms of Service (ToS) verification for the Discord bot.
- In a different repository and with a different domain because it needs to display codes on the website.
- Implemented in [NovaCord](https://nova-oss.com/novacord)

## Install & self-host
See [setup.md](setup.md)
