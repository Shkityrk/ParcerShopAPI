import asyncio

import uvicorn

from src.app_object import app
from src.config import HTTP_HOST, HTTP_PORT, configurate_logger


async def main() -> None:
    configurate_logger()

    server_config = uvicorn.Config(app, host=HTTP_HOST, port=HTTP_PORT)
    server = uvicorn.Server(server_config)

    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())
