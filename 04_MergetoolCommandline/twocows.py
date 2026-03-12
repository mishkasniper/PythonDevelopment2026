import cmd
import shlex
from typing import List, Dict, Tuple

import cowsay

class CowsayCmd(cmd.Cmd):
    """Interactive command processor for cowsay utilities."""
    
    intro = """
    Welcome to Cowsay Interactive Shell!
    Type 'help' for available commands or 'quit' to exit.
    """
    prompt = 'twocows> '
    
    def __init__(self):
        super().__init__()
        self.cow_list = cowsay.list_cows()
        self.first_message = ""
        self.second_message = ""
        self.first_cow = "default"
        self.second_cow = "default"
        self.first_eyes = "oo"
        self.second_eyes = "oo"
        self.first_tongue = "  "
        self.second_tongue = "  "
        self.width = 40
        self.wrap_text = True
    
    def _parse_part(self, args: List[str], default_cow: str,
                    default_eyes: str, default_tongue: str) -> Tuple[str, str, Dict[str, str]]:
        """
        Parse one part of a command (before or after 'reply').

        Args:
            args: list of tokens for this part (message, optional cow, key=value pairs)
            default_cow: cow name to use if not specified
            default_eyes: default eyes string
            default_tongue: default tongue string

        Returns:
            (message, cow_name, kwargs) where kwargs contains 'eyes' and/or 'tongue'
        """
        if not args:
            raise ValueError("Missing message")

        message = args[0]
        cow = default_cow
        kwargs = {}

        idx = 1
        if idx < len(args) and '=' not in args[idx]:
            cow = args[idx]
            idx += 1

        for token in args[idx:]:
            if '=' not in token:
                raise ValueError(f"Unexpected token without '=': {token}")
            key, value = token.split('=', 1)
            if key in ('eyes', 'tongue'):
                kwargs[key] = value
            else:
                print(f"Ignoring unknown parameter: {key}")

        if 'eyes' not in kwargs:
            kwargs['eyes'] = default_eyes
        if 'tongue' not in kwargs:
            kwargs['tongue'] = default_tongue

        return message, cow, kwargs

    def _do_cow_command(self, args: List[str], command_func):
        """
        Common implementation for cowsay and cowthink.

        Args:
            args: full token list from command line
            command_func: either cowsay.cowsay or cowsay.cowthink
        """
        if not args:
            print("Error: Missing arguments")
            return

        if 'reply' in args:
            reply_idx = args.index('reply')
            left_args = args[:reply_idx]
            right_args = args[reply_idx + 1:]

            if not left_args or not right_args:
                print("Error: Both parts need at least a message")
                return

            try:
                left_msg, left_cow, left_kw = self._parse_part(
                    left_args, self.first_cow, self.first_eyes, self.first_tongue)
                right_msg, right_cow, right_kw = self._parse_part(
                    right_args, self.second_cow, self.second_eyes, self.second_tongue)
            except ValueError as e:
                print(f"Error: {e}")
                return

            left_output = command_func(
                message=left_msg,
                cow=left_cow,
                eyes=left_kw['eyes'],
                tongue=left_kw['tongue'],
                width=self.width,
                wrap_text=self.wrap_text
            )
            right_output = command_func(
                message=right_msg,
                cow=right_cow,
                eyes=right_kw['eyes'],
                tongue=right_kw['tongue'],
                width=self.width,
                wrap_text=self.wrap_text
            )

            self._display_two_cows(left_output, right_output)
        else:
            try:
                msg, cow, kw = self._parse_part(
                    args, self.first_cow, self.first_eyes, self.first_tongue)
            except ValueError as e:
                print(f"Error: {e}")
                return

            output = command_func(
                message=msg,
                cow=cow,
                eyes=kw['eyes'],
                tongue=kw['tongue'],
                width=self.width,
                wrap_text=self.wrap_text
            )
            print(output)
    
    def _display_two_cows(self, first_cow_text: str, second_cow_text: str):
        """Display two cows side by side."""
        first_lines = first_cow_text.split('\n')
        second_lines = second_cow_text.split('\n')
        
        width = max(len(line) for line in first_lines) if first_lines else 0
        
        if len(first_lines) > len(second_lines):
            second_lines = [''] * (len(first_lines) - len(second_lines)) + second_lines
        else:
            first_lines = [''] * (len(second_lines) - len(first_lines)) + first_lines
        
        result = []
        for i in range(len(first_lines)):
            result.append(first_lines[i].ljust(width) + second_lines[i])
        
        for line in result:
            print(line)
    
    def do_list_cows(self, arg: str):
        """
        List all available cows in COWPATH.
        Usage: list_cows
        """
        cows = cowsay.list_cows()
        print("\nAvailable cows:")
        print(", ".join(sorted(cows)))
    
    def complete_list_cows(self, text: str, line: str, begidx: int, endidx: int) -> List[str]:
        """Autocomplete for list_cows command."""
        return []
    
    def do_make_bubble(self, arg: str):
        """
        Create a speech bubble for given text.
        Usage: make_bubble text [width=40] [wrap_text=True]
        """
        if not arg:
            print("Error: Missing text argument")
            return
        
        args = shlex.split(arg)
        kwargs = self._parse_keyword_args(args)
        
        if not args:
            print("Error: Missing text argument")
            return
        
        text = args[0]
        width = int(kwargs.get('width', self.width))
        wrap_text = kwargs.get('wrap_text', 'True').lower() == 'true'
        
        bubble = cowsay.make_bubble(text, width=width, wrap_text=wrap_text)
        print(bubble)
    
    def complete_make_bubble(self, text: str, line: str, begidx: int, endidx: int) -> List[str]:
        """Autocomplete for make_bubble command."""
        return []
    
    def do_cowsay(self, arg: str):
        """
        Make a cow say something.
        Usage: cowsay message [cow_name [eyes=oo [tongue="  "]]] reply response [cow_name [eyes=oo]]
        """
        if not arg:
            print("Error: Missing arguments")
            return
        args = shlex.split(arg)
        self._do_cow_command(args, cowsay.cowsay)
    
    def complete_cowsay(self, text: str, line: str, begidx: int, endidx: int) -> List[str]:
        """Autocomplete cow names for cowsay."""
        if not text:
            return self.cow_list
        return [cow for cow in self.cow_list if cow.startswith(text)]
    
    def do_cowthink(self, arg: str):
        """
        Make a cow think something.
        Usage: cowthink message [cow_name] [eyes=..] [tongue=..] [reply message [cow_name] [eyes=..] [tongue=..]]
        """
        if not arg:
            print("Error: Missing arguments")
            return
        args = shlex.split(arg)
        self._do_cow_command(args, cowsay.cowthink)
    
    def complete_cowthink(self, text: str, line: str, begidx: int, endidx: int) -> List[str]:
        """Autocomplete for cowthink command."""
        return self.complete_cowsay(text, line, begidx, endidx)
    
    def do_set(self, arg: str):
        """
        Set default parameters.
        Usage: set parameter=value
        Parameters: first_cow, second_cow, first_eyes, second_eyes, tongue, width, wrap_text
        """
        if not arg:
            print("Current settings:")
            print(f"  first_cow: {self.first_cow}")
            print(f"  second_cow: {self.second_cow}")
            print(f"  first_eyes: {self.first_eyes}")
            print(f"  second_eyes: {self.second_eyes}")
            print(f"  first_tongue: {self.first_tongue}")
            print(f"  second_tongue: {self.second_tongue}")
            print(f"  width: {self.width}")
            print(f"  wrap_text: {self.wrap_text}")
            return
        
        args = shlex.split(arg)
        for arg in args:
            if '=' not in arg:
                print(f"Error: Invalid format '{arg}'. Use parameter=value")
                continue
            
            key, value = arg.split('=', 1)
            key = key.strip()
            value = value.strip()
            
            if key == 'first_cow':
                if value in self.cow_list or value == 'default':
                    self.first_cow = value
                else:
                    print(f"Error: '{value}' is not a valid cow")
            elif key == 'second_cow':
                if value in self.cow_list or value == 'default':
                    self.second_cow = value
                else:
                    print(f"Error: '{value}' is not a valid cow")
            elif key == 'first_eyes':
                self.first_eyes = value
            elif key == 'second_eyes':
                self.second_eyes = value
            elif key == 'first_tongue':
                self.first_tongue = value
            elif key == 'second_tongue':
                self.second_tongue = value
            elif key == 'width':
                try:
                    self.width = int(value)
                except ValueError:
                    print("Error: width must be an integer")
            elif key == 'wrap_text':
                self.wrap_text = value.lower() == 'true'
            else:
                print(f"Error: Unknown parameter '{key}'")
    
    def complete_set(self, text: str, line: str, begidx: int, endidx: int) -> List[str]:
        """Autocomplete for set command."""
        params = ['first_cow=', 'second_cow=', 'first_eyes=', 'second_eyes=', 
                 'tongue=', 'width=', 'wrap_text=']
        
        if not text:
            return params
        
        return [p for p in params if p.startswith(text)]
    
    def do_quit(self, arg: str):
        """Exit the interactive shell."""
        print("Goodbye!")
        return True
    
    def do_exit(self, arg: str):
        """Exit the interactive shell."""
        return self.do_quit(arg)
    
    def do_EOF(self, arg: str):
        """Handle Ctrl-D to exit."""
        print()
        return self.do_quit(arg)


def main():
    """Main entry point."""
    try:
        CowsayCmd().cmdloop()
    except KeyboardInterrupt:
        print("\nGoodbye!")


if __name__ == '__main__':
    main()