# nova-api
☄️ Nova API
<<<<<<< HEAD

## `.env` configuration

### `ACTUAL_IPS` (optional)
This is a security measure to make sure a proxy, VPN, Tor or any other IP hiding service is used by the host when accessing OpenAI's API.
It is a space separated list of IP addresses that are allowed to access the API.
You can also just add the *beginning* of an API address, like `12.123.` to allow all IPs starting with `12.123.`.

> To disable the warning if you don't have this feature enabled, set `ACTUAL_IPS` to any value.

## Proxy
- `PROXY_TYPE` (optional, defaults to `socks.PROXY_TYPE_HTTP`): the type of proxy - can be `http`, `https`, `socks4`, `socks5`, `4` or `5`, etc... 
- `PROXY_HOST`: the host used by the proxy
- `PROXY_PORT`: the port used by the proxy
- `PROXY_USER` (optional)
- `PROXY_PASS` (optional)

## Run
`cd api && uvicorn main:app --reload && cd ..`

You can remove the `--reload` flag if you don't want to reload the server on file changes.

## Test
`python3 tests`
=======
>>>>>>> 5dad208be237c43fa339b4cb98eb68ed398e30be
