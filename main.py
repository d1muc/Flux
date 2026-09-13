import os
import sys
import time
import getpass
import socket
import subprocess
import shlex
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.application.current import get_app
from prompt_toolkit.filters import Condition
from rich.panel import Panel
from rich.table import Table

from config import state, console, get_msg, save_config, THEMES_INFO, LANGUAGES, prompt_style
import ai

if os.name == 'nt':
    import msvcrt
    def read_key():
        ch = msvcrt.getch()
        if ch in (b'\x00', b'\xe0'):
            ch2 = msvcrt.getch()
            if ch2 == b'H': return 'UP'
            elif ch2 == b'P': return 'DOWN'
        elif ch in (b'\r', b'\n'): return 'ENTER'
        elif ch == b'\x1b': return 'ESC'
        return None
else:
    import tty
    import termios
    def read_key():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
            if ch == '\x1b':
                ch2 = sys.stdin.read(1)
                if ch2 == '[':
                    ch3 = sys.stdin.read(1)
                    if ch3 == 'A': return 'UP'
                    elif ch3 == 'B': return 'DOWN'
                return 'ESC'
            elif ch in ('\r', '\n'): return 'ENTER'
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return None

class SmartPathCompleter(Completer):
    def __init__(self):
        self.path_commands = ['cd', 'ls', 'cat', 'nano', 'vim', 'rm', 'mkdir', 'touch']

    def get_completions(self, document, complete_event):
        text = document.text_before_cursor
        parts = text.split(' ')

        if len(parts) > 1 and parts[0] in self.path_commands:
            current_input = parts[-1]
            expanded_input = os.path.expanduser(current_input)
            
            if expanded_input.endswith('/'):
                search_dir = expanded_input
                basename = ''
            else:
                search_dir = os.path.dirname(expanded_input)
                basename = os.path.basename(expanded_input)
                if not search_dir: search_dir = '.'

            if os.path.isdir(search_dir):
                try:
                    for item in os.listdir(search_dir):
                        if not item.startswith('.') or basename.startswith('.'):
                            if item.startswith(basename):
                                item_path = os.path.join(search_dir, item)
                                is_dir = os.path.isdir(item_path)
                                insert_text = item + ('/' if is_dir else '')
                                yield Completion(
                                    insert_text,
                                    start_position=-len(basename),
                                    display=insert_text
                                )
                except PermissionError:
                    pass

def get_prompt():
    if state.get('ai_mode'):
        return FormattedText([('class:ai-prompt', 'AI: ')])

    theme = state['theme']
    last_status = state['last_status']
    
    cwd = os.getcwd()
    if cwd == os.path.expanduser("~"): folder = '~'
    else: 
        folder = os.path.basename(cwd)
        if not folder: folder = '/'

    status_color = 'class:arrow-green' if last_status == 0 else 'class:arrow-red'
    arrow_sym = '➜ '

    if theme == 'robbyrussell':
        return FormattedText([(status_color, arrow_sym), ('class:folder', f' {folder} '), ('class:git-branch', 'git:(main) ')])
    elif theme == 'zsh-arrow':
        return FormattedText([(status_color, arrow_sym), ('class:folder', f'{folder} ')])
    elif theme == 'zsh-classic':
        curr_time = time.strftime("%H:%M:%S")
        colon_color = '#00ffaa' if last_status == 0 else '#ff0000'
        return FormattedText([('class:time', f'[{curr_time}] '), ('class:userhost', f'{getpass.getuser()}@{socket.gethostname()}'), (f'fg:{colon_color} bold', ': ')])
    elif theme == 'agnoster':
        return FormattedText([('class:folder', f"{'~ ' if last_status == 0 else 'X '}{folder} "), (status_color, '❯ ')])
    elif theme == 'pure':
        return FormattedText([('class:folder', f'{folder} '), (f"fg:{'#00ffff' if last_status == 0 else '#ff0000'} bold", '❯ ')])
    elif theme == 'powerlevel':
        return FormattedText([('class:lambda', 'λ '), ('class:folder', f'{folder} '), (status_color, '❯ ')])
    elif theme == 'minimal':
        return FormattedText([('class:folder', f'{folder}'), (f"fg:{'#00ff00' if last_status == 0 else '#ff0000'} bold", ' $ ')])
        
    return FormattedText([('class:arrow-green', '> ')])

def interactive_menu(title, options_dict, current_selected=None):
    keys = [item[0] for item in options_dict]
    selected_idx = keys.index(current_selected) if current_selected in keys else 0

    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        content = ""
        for idx, (key, label) in enumerate(options_dict):
            if idx == selected_idx:
                content += f"[bold black on cyan] > {label} [/bold black on cyan]\n"
            else:
                content += f"   {label}\n"
                
        console.print(Panel(content, title=f"[bold]{title}[/bold]", border_style=state['border_style']))
        
        key_pressed = read_key()
        if key_pressed == 'UP': selected_idx = (selected_idx - 1) % len(options_dict)
        elif key_pressed == 'DOWN': selected_idx = (selected_idx + 1) % len(options_dict)
        elif key_pressed == 'ENTER':
            os.system('cls' if os.name == 'nt' else 'clear')
            return keys[selected_idx]

def parse_command(cmd_string):
    try: 
        parts = shlex.split(cmd_string, posix=(os.name != 'nt'))
    except ValueError: 
        parts = cmd_string.split()
    if not parts: 
        return "", []
    return parts[0].lower(), parts[1:]

def display_help():
    table = Table(title="Flux Shell Internal Commands", border_style=state['border_style'])
    table.add_column("Command", style="cyan bold", no_wrap=True)
    table.add_column("Description", style="white")

    table.add_row("help", "Show this help screen")
    table.add_row("settings", "Open interactive configuration panel")
    table.add_row("clear", "Clear terminal screen")
    table.add_row("cd [dir]", "Change working directory")
    table.add_row("exit / quit", "Exit Flux Shell")
    table.add_row("<TAB>", "Press TAB on empty line to toggle AI Mode")

    console.print(table)

def handle_settings(args):
    while True:
        menu_options = [
            ('theme', f"{get_msg('opt_theme')} [{state['theme']}]"),
            ('lang', f"{get_msg('opt_lang')} [{LANGUAGES[state['lang']]}]"),
            ('border', f"{get_msg('opt_border')} [{state['border_style']}]"),
            ('ai', f"{get_msg('opt_ai')} [{state['ai_model'] or 'None'}]"),
            ('back', get_msg('opt_back'))
        ]
        
        choice = interactive_menu(get_msg('settings_title'), menu_options)
        
        if choice == 'theme':
            theme_opts = [(k, f"{v['name']} - {v['desc']}") for k, v in THEMES_INFO.items()]
            state['theme'] = interactive_menu(get_msg('theme_title'), theme_opts, state['theme'])
        elif choice == 'lang':
            state['lang'] = interactive_menu(get_msg('lang_title'), [(k, v) for k, v in LANGUAGES.items()], state['lang'])
        elif choice == 'border':
            colors = ["cyan", "magenta", "green", "yellow", "red", "blue", "white"]
            state['border_style'] = interactive_menu(get_msg('border_title'), [(c, c.capitalize()) for c in colors], state['border_style'])
        elif choice == 'ai':
            models = ai.get_ollama_models()
            if not models:
                console.print(f"[red]{get_msg('ai_empty')}[/red]")
                time.sleep(2)
                continue
            state['ai_model'] = interactive_menu(get_msg('ai_title'), [(m, m) for m in models], state['ai_model'])
        elif choice == 'back':
            break

    save_config(state)

def main():
    available_models = ai.get_ollama_models()
    if available_models and not state.get('ai_model'):
        state['ai_model'] = available_models[0]
        save_config(state)

    kb = KeyBindings()

    @Condition
    def is_buffer_empty():
        return not get_app().current_buffer.text.strip()

    @kb.add('tab', filter=is_buffer_empty)
    def _(event):
        state['ai_mode'] = not state['ai_mode']
        event.app.invalidate()

    @kb.add('enter')
    def _(event):
        b = event.current_buffer
        if b.complete_state:
            if b.complete_state.current_completion:
                b.complete_state = None
                return
            else:
                b.complete_state = None
                b.validate_and_handle()
        else:
            b.validate_and_handle()

    session = PromptSession(completer=SmartPathCompleter(), complete_while_typing=False, key_bindings=kb)
    console.print(Panel(get_msg('welcome'), border_style=state['border_style']))

    while True:
        try:
            prefilled_cmd = state.pop('next_default', '')
            cmd_line = session.prompt(get_prompt, style=prompt_style, default=prefilled_cmd).strip()
            if not cmd_line: continue

            if state.get('ai_mode'):
                if not state['ai_model']:
                    console.print("[red]AI Model not selected/found! Check 'settings'.[/red]")
                    state['ai_mode'] = False
                    continue
                    
                with console.status(f"[bold purple] {get_msg('ai_fetching')}[/bold purple]"):
                    generated_cmd = ai.generate_ai_command(cmd_line, state['ai_model'], state['history'])
                
                state['next_default'] = generated_cmd
                state['ai_mode'] = False
                continue

            base_cmd, args = parse_command(cmd_line)
            
            if base_cmd not in ['exit', 'quit', 'settings', 'clear', 'help']:
                state['history'].append(cmd_line)
                if len(state['history']) > 15:
                    state['history'].pop(0)

            if base_cmd in ['exit', 'quit']:
                break
            elif base_cmd == 'help':
                display_help()
                state['last_status'] = 0
            elif base_cmd == 'clear':
                os.system('cls' if os.name == 'nt' else 'clear')
                state['last_status'] = 0
            elif base_cmd == 'cd':
                if args:
                    try:
                        os.chdir(os.path.expanduser(args[0]))
                        state['last_status'] = 0
                    except Exception as e:
                        console.print(f"[red]cd: {e}[/red]")
                        state['last_status'] = 1
                else:
                    os.chdir(os.path.expanduser("~"))
                    state['last_status'] = 0
            elif base_cmd == 'settings':
                handle_settings(args)
                state['last_status'] = 0
            else:
                result = subprocess.run(cmd_line, shell=True)
                state['last_status'] = result.returncode
                
        except KeyboardInterrupt:
            state['ai_mode'] = False
            print("^C")
            state['last_status'] = 130
            continue
        except EOFError:
            break
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            state['last_status'] = 1

if __name__ == "__main__":
    main()