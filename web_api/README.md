
# SimpleAPI class <!--omit in toc-->

Creation of the SimpleApi class, wich implements a simple infraestructure for the deploying of simple apis, as the name states.
It is based on paralelism, upon creation of a SimpleApi object, `n` threads shall be started to accept and process the requisitions.

## Instantitation of a SimpeApi object

```python
server = SimpleApi(host_addr = '0.0.0.0', port = 8000, load_size = 2048, max_connections = 5)
```

| | | |
|---------|--------|----------|
| - `host_addr`: | ``str`` | Address in which the socket will be binded to |
| - `port` | ``int`` | Port in which the socket will be binded to |
| - `load_size` | ``int`` | Buffer size of the incoming message in bytes |
| - `max_connections` | ``int`` | maximum value of the concurrent sessions open at the same time</br>Also the number of threads created to process the requisitions |

A socket object is used in the backgroungd to bind to the ``address`` and ``port`` provided. The `max_connections` represents the maximum simultaneous connections that the socket will allow to connect and the thread count for the workers to process the incoming connections and requisitions.

## Endpoints configuration

```python
server.configure_endpoints(method:str, endpoint:str, function:function):
```

| | | |
|---|---|---|
| - `method` | `str` | The API endpoint's method. |
| - `endpoint` | `str` | The endpoint's string, including the `/` at the begining. |
| - `function` | `function` | The reference to the function. </br>It must be created beforehand. |

IMPORTANT: The function created has to receive and threat or ignore the `payload:str` argument.

Method supported so far:

- GET
- POST

TODO: The http handler needs to pass ip and port of the connection.
