import asyncio
import cowsay
import shlex

class CowChatServer:
    def __init__(self, host='localhost', port=1337):
        self.host = host
        self.port = port
        self.available_cows = set(cowsay.list_cows())
        self.registered = {}
        self._lock = asyncio.Lock()

    async def handle_client(self, reader, writer):
        """Обработка подключения одного клиента."""
        peer = writer.get_extra_info('peername')

        client_info = {
            'registered': False,
            'cow_name': None,
            'writer': writer
        }

        try:
            while True:
                data = await reader.readline()
                if not data:
                    break

                line = data.decode().strip()
                if not line:
                    continue

                if ' ' in line:
                    req_id_str, cmd_line = line.split(' ', 1)
                    try:
                        req_id = int(req_id_str)
                    except ValueError:
                        req_id = 0
                        cmd_line = line
                else:
                    req_id = 0
                    cmd_line = line

                if cmd_line.lower() == 'quit':
                    break

                response = await self.process_command(cmd_line, client_info, req_id)
                if response:
                    writer.write(f"{req_id} {response}\n".encode())
                    await writer.drain()

        except asyncio.CancelledError:
            pass
        finally:
            if client_info['registered']:
                async with self._lock:
                    cow = client_info['cow_name']
                    if cow in self.registered:
                        del self.registered[cow]
                        self.available_cows.add(cow)
            writer.close()
            await writer.wait_closed()

    async def process_command(self, line, client_info, req_id):
        """Разбор и выполнение команды."""
        try:
            args = shlex.split(line)
        except ValueError as e:
            return f"Ошибка разбора команды: {e}"

        if not args:
            return None

        cmd = args[0].lower()
        rest = args[1:]

        if cmd == 'who':
            async with self._lock:
                if self.registered:
                    cows_list = ', '.join(sorted(self.registered.keys()))
                    return f"Зарегистрированные коровы: {cows_list}"
                else:
                    return "Нет зарегистрированных пользователей."

        elif cmd == 'cows':
            async with self._lock:
                if self.available_cows:
                    cows_list = ', '.join(sorted(self.available_cows))
                    return f"Доступные имена коров: {cows_list}"
                else:
                    return "Нет доступных имён."

        elif cmd == 'login':
            if client_info['registered']:
                return "Вы уже зарегистрированы."
            if len(rest) < 1:
                return "Использование: login <имя_коровы>"
            cow_name = rest[0]
            async with self._lock:
                if cow_name not in self.available_cows:
                    return f"Имя '{cow_name}' недоступно. Используйте 'cows' для просмотра свободных."
                self.available_cows.remove(cow_name)
                self.registered[cow_name] = client_info['writer']
                client_info['registered'] = True
                client_info['cow_name'] = cow_name
                return f"Вы вошли как {cow_name}."

        elif cmd == 'say':
            if not client_info['registered']:
                return "Сначала войдите в систему (login)."
            if len(rest) < 2:
                return "Использование: say <имя_коровы> <сообщение>"
            target_cow = rest[0]
            message = ' '.join(rest[1:])
            sender_cow = client_info['cow_name']

            async with self._lock:
                if target_cow not in self.registered:
                    return f"Корова '{target_cow}' не зарегистрирована."
                target_writer = self.registered[target_cow]

            cowsay_output = cowsay.cowsay(message, cow=sender_cow)
            try:
                target_writer.write(f"0 {cowsay_output}\n".encode())
                await target_writer.drain()
            except Exception as e:
                print(f"Ошибка отправки сообщения для {target_cow}: {e}")
            return None

        elif cmd == 'yield':
            if not client_info['registered']:
                return "Сначала войдите в систему (login)."
            if len(rest) < 1:
                return "Использование: yield <сообщение>"
            message = ' '.join(rest)
            sender_cow = client_info['cow_name']
            cowsay_output = cowsay.cowsay(message, cow=sender_cow)

            async with self._lock:
                recipients = list(self.registered.items())

            for name, w in recipients:
                try:
                    w.write(f"0 {cowsay_output}\n".encode())
                    await w.drain()
                except Exception as e:
                    print(f"Ошибка отправки сообщения для {name}: {e}")
            return None

        else:
            return f"Неизвестная команда: {cmd}"

    async def run(self):
        """Запуск сервера."""
        server = await asyncio.start_server(self.handle_client, self.host, self.port)
        print(f"Сервер запущен на {self.host}:{self.port}")
        async with server:
            await server.serve_forever()

if __name__ == '__main__':
    asyncio.run(CowChatServer().run())