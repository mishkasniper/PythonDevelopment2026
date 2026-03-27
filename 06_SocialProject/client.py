import cmd
import socket
import threading
import sys
import shlex
import readline
import time
import re

class CowChatClient(cmd.Cmd):
    intro = "Добро пожаловать в коровий чат. Введите help для списка команд."
    prompt = "cowchat> "

    def __init__(self, host='localhost', port=1337):
        super().__init__()
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        self.running = True
        self.next_req_id = 1
        self.pending_responses = {}
        self.pending_lock = threading.Lock()
        self.output_lock = threading.Lock()

        self.available_cows = []
        self.registered_cows = []

        self.reader_thread = threading.Thread(target=self._reader_loop, daemon=True)
        self.reader_thread.start()

        self._update_caches()

    def _safe_print(self, text):
        """Безопасный вывод текста с восстановлением строки ввода."""
        with self.output_lock:
            sys.stdout.write('\n' + text + '\n' + self.prompt + readline.get_line_buffer())
            sys.stdout.flush()

    def _send_command(self, command):
        """Отправить команду и дождаться ответа."""
        req_id = self.next_req_id
        self.next_req_id += 1
        self.sock.sendall(f"{req_id} {command}\n".encode())
        while True:
            with self.pending_lock:
                if req_id in self.pending_responses:
                    response = self.pending_responses.pop(req_id)
                    break
            time.sleep(0.05)
        self._update_caches_from_response(response)
        return response

    def _update_caches_from_response(self, response):
        """Обновляет кэши, если ответ является списком коров."""
        if response.startswith("Доступные имена коров:"):
            cows_str = response.split(':', 1)[1].strip()
            if cows_str:
                self.available_cows = [c.strip() for c in cows_str.split(',')]
            else:
                self.available_cows = []

        elif response.startswith("Зарегистрированные коровы:"):
            cows_str = response.split(':', 1)[1].strip()
            if cows_str:
                self.registered_cows = [c.strip() for c in cows_str.split(',')]
            else:
                self.registered_cows = []

    def _update_caches(self):
        """Запрашивает текущие списки коров и обновляет кэши."""
        cows_resp = self._send_command("cows")
        who_resp = self._send_command("who")

    def _reader_loop(self):
        """Фоновый поток чтения из сокета."""
        f = self.sock.makefile('r', encoding='utf-8')
        while self.running:
            try:
                line = f.readline()
                if not line:
                    break
                line = line.strip()
                if not line:
                    continue
                if ' ' in line:
                    req_id_str, text = line.split(' ', 1)
                    try:
                        req_id = int(req_id_str)
                    except ValueError:
                        req_id = 0
                        text = line
                else:
                    req_id = 0
                    text = line

                if req_id == 0:
                    self._safe_print(text)
                else:
                    with self.pending_lock:
                        self.pending_responses[req_id] = text
            except Exception as e:
                if self.running:
                    self._safe_print(f"Ошибка чтения: {e}")
                break
        f.close()

    def do_who(self, arg):
        """Показать список зарегистрированных коров."""
        resp = self._send_command("who")
        self._safe_print(resp)

    def do_cows(self, arg):
        """Показать список доступных имён коров."""
        resp = self._send_command("cows")
        self._safe_print(resp)

    def do_login(self, arg):
        """Войти в чат как корова. Использование: login <имя_коровы>"""
        if not arg:
            self._safe_print("Использование: login <имя_коровы>")
            return
        if arg not in self.available_cows:
            self._safe_print(f"Имя '{arg}' недоступно. Используйте 'cows' для просмотра свободных.")
            return
        resp = self._send_command(f"login {arg}")
        self._safe_print(resp)
        self._update_caches()

    def do_say(self, arg):
        """Отправить сообщение конкретной корове. Использование: say <имя_коровы> <сообщение>"""
        if not arg:
            self._safe_print("Использование: say <имя_коровы> <сообщение>")
            return
        try:
            parts = shlex.split(arg)
        except ValueError as e:
            self._safe_print(f"Ошибка разбора: {e}")
            return
        if len(parts) < 2:
            self._safe_print("Использование: say <имя_коровы> <сообщение>")
            return
        target = parts[0]
        message = ' '.join(parts[1:])
        command = f"say {target} {shlex.quote(message)}"
        resp = self._send_command(command)
        if resp:
            self._safe_print(resp)

    def do_yield(self, arg):
        """Отправить сообщение всем. Использование: yield <сообщение>"""
        if not arg:
            self._safe_print("Использование: yield <сообщение>")
            return
        command = f"yield {shlex.quote(arg)}"
        resp = self._send_command(command)
        if resp:
            self._safe_print(resp)

    def do_quit(self, arg):
        """Выйти из чата."""
        self._safe_print("Выход...")
        self.running = False
        self.sock.close()
        return True

    def complete_login(self, text, line, begidx, endidx):
        """Автодополнение для login: имена доступных коров."""
        if not text:
            return self.available_cows
        return [cow for cow in self.available_cows if cow.startswith(text)]

    def complete_say(self, text, line, begidx, endidx):
        """Автодополнение для say: имена зарегистрированных коров."""
        if not text:
            return self.registered_cows
        return [cow for cow in self.registered_cows if cow.startswith(text)]

if __name__ == '__main__':
    host = sys.argv[1] if len(sys.argv) > 1 else 'localhost'
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 1337
    client = CowChatClient(host, port)
    try:
        client.cmdloop()
    except KeyboardInterrupt:
        client.do_quit("")