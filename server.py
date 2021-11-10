import asyncio
import json
counter = 0

async def serve_client(reader, writer):
    global counter
    cid = counter
    counter += 1  # Потоко-безопасно, так все выполняется в одном потоке
    print(f'Client #{cid} connected')

    request = await read_request(reader)
    if request is None:
        print(f'Client #{cid} unexpectedly disconnected')
    else:
        # await self.write_response(writer, request, cid)
        print(request)

async def read_request(reader):
    request = bytearray()
    while True:
        chunk = await reader.read(2 ** 10)
        if not chunk:
            # Клиент преждевременно отключился.
            break
        request += chunk
        try:
            data = json.loads(request.decode("utf-8").replace("'", "\""))
            return data
        except:
            pass
        # if delimiter in request:
        #     return request[:-2]
    return None

async def write_response(writer, response, cid):
    # await self.broadcaster(response.decode())
    writer.write(response)
    await writer.drain()
    writer.close()
    print(f'Client #{cid} has been served')

async def run_server(host, port):
    server = await asyncio.start_server(serve_client, host, port)
    await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(run_server("localhost",2345))