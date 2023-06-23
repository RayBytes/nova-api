# ☄️ Nova API Server
Reverse proxy server for OpenAI's API.

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

### `ACTUAL_IPS` (optional)
This is a security measure to make sure a proxy, VPN, Tor or any other IP hiding service is used by the host when accessing OpenAI's API.
It is a space separated list of IP addresses that are allowed to access the API.
You can also just add the *beginning* of an API address, like `12.123.` to allow all IPs starting with `12.123.`.

> To disable the warning if you don't have this feature enabled, set `ACTUAL_IPS` to any value.

## Proxy
- `PROXY_TYPE` (optional, defaults to `socks.PROXY_TYPE_HTTP`): the type of proxy - can be `http`, `https`, `socks4`, `socks5`, `4` or `5`, etc... 
- `PROXY_HOST`: the proxy host (host domain or IP address), without port!
- `PROXY_PORT`
- `PROXY_USER` (optional)
- `PROXY_PASS` (optional)

## Run
`python cli`

You can remove the `--reload` flag if you don't want to reload the server on file changes.

## Test
`python tests`
