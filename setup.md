
## Install
Assuming you have a new version of Python 3.9+ and pip installed:
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
Create a `.env` file, make sure not to reveal any of its contents to anyone, and fill in the required values in the format `KEY=VALUE`. Otherwise, the code won't run.

### Database
Set up a MongoDB database and set `MONGO_URI` to the MongoDB database connection URI. Quotation marks are definetly recommended here!

### Proxy
- `PROXY_TYPE` (optional, defaults to `socks.PROXY_TYPE_HTTP`): the type of proxy - can be `http`, `https`, `socks4`, `socks5`, `4` or `5`, etc... 
- `PROXY_HOST`: the proxy host (host domain or IP address), without port!
- `PROXY_PORT` (optional)
- `PROXY_USER` (optional)
- `PROXY_PASS` (optional)

Want to use a proxy list? See the according section!
Keep in mind to set `USE_PROXY_LIST` to `True`! Otherwise, the proxy list won't be used.

### `ACTUAL_IPS` (optional)
This is a security measure to make sure a proxy, VPN, Tor or any other IP hiding service is used by the host when accessing "Closed"AI's API.
It is a space separated list of IP addresses that are allowed to access the API.
You can also just add the *beginning* of an API address, like `12.123.` (without an asterisk!) to allow all IPs starting with `12.123.`.
> To disable the warning if you don't have this feature enabled, set `ACTUAL_IPS` to `None`.

### Timeout
`TRANSFER_TIMEOUT` seconds to wait until the program throws an exception for if the request takes too long. We recommend rather long times like `120` for two minutes.

### Core Keys
`CORE_API_KEY` specifies the **very secret key** for  which need to access the entire user database etc.
`TEST_NOVA_KEY` is the API key the which is used in tests. It should be one with tons of credits.

### Webhooks
`DISCORD_WEBHOOK__USER_CREATED` is the Discord webhook URL for when a user is created.
`DISCORD_WEBHOOK__API_ISSUE` is the Discord webhook URL for when an API issue occurs.

### Other
`KEYGEN_INFIX` can be almost any string (avoid spaces or special characters) - this string will be put in the middle of every NovaAI API key which is generated. This is useful for identifying the source of the key using e.g. RegEx.

## Proxy Lists
To use proxy lists, navigate to `api/secret/proxies/` and create the following files:
- `http.txt`
- `socks4.txt`
- `socks5.txt`

Then, paste your proxies in the following format:

```
[username:password@]host:port
```

e.g.

```
1.2.3.4:8080
user:pass@127.0.0.1:1337
```

You can use comments just like in Python.

**Important:** to use the proxy lists, you need to change the `USE_PROXY_LIST` environment variable to `True`!

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