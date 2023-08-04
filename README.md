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

## Install
Assuming you have a new version of Python 3 and pip installed:
```py
python -m pip install -r requirements.txt
```

If you still get a `ModuleNotFoundError`s, you can forefully install the dependencies using:
```py
python -m pip install pipreqs
python -m pipreqs.pipreqs --force --mode no-pin
python -m pip install --upgrade -r requirements.txt
```

You can also try installing Nova API using `setup.py`:
```py
python setup.py
```

or 

```py
pip install .
```

## `.env` configuration
Create a `.env` file, make sure not to reveal it to anyone, and fill in the required values in the format `KEY=VALUE`. Otherwise, the code won't run.

### Database
- `API_DB_PATH` the path to the databases, e.g. `/etc/nova/db/.` (this way, the database `users` would be saved in `/etc/nova/db/.users.db`.)

### Proxy
- `PROXY_TYPE` (optional, defaults to `socks.PROXY_TYPE_HTTP`): the type of proxy - can be `http`, `https`, `socks4`, `socks5`, `4` or `5`, etc... 
- `PROXY_HOST`: the proxy host (host domain or IP address), without port!
- `PROXY_PORT` (optional)
- `PROXY_USER` (optional)
- `PROXY_PASS` (optional)

### `ACTUAL_IPS` (optional)
This is a security measure to make sure a proxy, VPN, Tor or any other IP hiding service is used by the host when accessing "Closed"AI's API.
It is a space separated list of IP addresses that are allowed to access the API.
You can also just add the *beginning* of an API address, like `12.123.` (without an asterisk!) to allow all IPs starting with `12.123.`.
> To disable the warning if you don't have this feature enabled, set `ACTUAL_IPS` to `None`.

### `CORE_API_KEY`
This specifies the **very secret key** for accessing the entire user database etc.

## Run
> **Warning:** read the according section for production usage!

For developement:

```bash
python run
```

This will run the development server on port `2332`.

You can also specify a port, e.g.:

```bash
python run 1337
```

## Test if it works
`python tests`

## Ports
```yml
2332: Developement (default)
2333: Production
```

## Production
Make sure your server is secure and up to date.
Check everything.

The following command will run the API  __without__ a reloader!

```bash
python run prod
```

or 

```bash
./screen.sh
```