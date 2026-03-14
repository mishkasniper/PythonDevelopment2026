import asyncio
import cowsay

class CowChatServer:
    def __init__(self, host='localhost', port=1337):
        self.host = host
        self.port = port
        self.available_cows = set(cowsay.list_cows())
        self.registered = {}
        self._lock = asyncio.Lock()

    async def handle_client(self, reader, writer):
        """Обработка подключения одного клиента."""


    async def process_command(self, line, client_info):
        """Разбор и выполнение команды."""
        

    async def run(self):
        """Запуск сервера."""
        server = await asyncio.start_server(self.handle_client, self.host, self.port)
        print(f"Сервер запущен на {self.host}:{self.port}")
        async with server:
            await server.serve_forever()

if __name__ == '__main__':
    asyncio.run(CowChatServer().run())