import os
import json
from rich.console import Console
from prompt_toolkit.styles import Style

console = Console()
CONFIG_FILE = os.path.expanduser("~/.flux_config.json")

DEFAULT_STATE = {
    'theme': 'robbyrussell',
    'lang': 'en',  
    'last_status': 0,
    'border_style': 'cyan',
    'ai_mode': False,
    'ai_model': None,
    'history': []
}

LANGUAGES = {'en': 'English', 'uk': 'Ukrainian', 'ru': 'Russian'}

MESSAGES = {
    'en': {
        'welcome': "[bold cyan]Welcome to Flux Shell v3.1[/bold cyan]\nType [bold green]help[/bold green] for manual. [dim]Press TAB on an empty line to switch AI Mode.[/dim]",
        'settings_title': "Flux Configuration Center",
        'opt_theme': "Change Prompt Theme", 'opt_lang': "Change Interface Language",
        'opt_border': "Change UI Border Color", 'opt_ai': "Select AI Model (Ollama)",
        'opt_view': "View Active Configuration", 'opt_back': "Return to Flux",
        'theme_title': "Select Prompt Theme", 'lang_title': "Select Language",
        'border_title': "Select Border Color", 'ai_title': "Select Local AI Model",
        'ai_fetching': "Asking AI...", 'ai_empty': "No models found (Is Ollama running?)"
    },
    'uk': {
        'welcome': "[bold cyan]Ласкаво просимо до Flux Shell v3.1[/bold cyan]\nВведіть [bold green]help[/bold green] для довідки. [dim]Натисніть TAB у порожньому рядку, щоб увімкнути/вимкнути AI Mode.[/dim]",
        'settings_title': "Центр налаштувань Flux",
        'opt_theme': "Змінити тему підказки", 'opt_lang': "Змінити мову інтерфейсу",
        'opt_border': "Змінити колір рамки UI", 'opt_ai': "Обрати модель AI (Ollama)",
        'opt_view': "Переглянути поточну конфігурацію", 'opt_back': "Повернутися до Flux",
        'theme_title': "Оберіть тему підказки", 'lang_title': "Оберіть мову",
        'border_title': "Оберіть колір рамки", 'ai_title': "Оберіть локальну модель AI",
        'ai_fetching': "Запит до AI...", 'ai_empty': "Моделі не знайдені (чи запущено Ollama?)"
    },
    'ru': {
        'welcome': "[bold cyan]Добро пожаловать в Flux Shell v3.1[/bold cyan]\nВведите [bold green]help[/bold green] для справки. [dim]Нажмите TAB в пустой строке, чтобы переключить AI Mode.[/dim]",
        'settings_title': "Центр настроек Flux",
        'opt_theme': "Изменить тему приглашения", 'opt_lang': "Изменить язык интерфейса",
        'opt_border': "Изменить цвет рамки UI", 'opt_ai': "Выбрать модель AI (Ollama)",
        'opt_view': "Просмотреть текущую конфигурацию", 'opt_back': "Вернуться в Flux",
        'theme_title': "Выберите тему приглашения", 'lang_title': "Выберите язык",
        'border_title': "Выберите цвет рамки", 'ai_title': "Выберите локальную модель AI",
        'ai_fetching': "Запрос к AI...", 'ai_empty': "Модели не найдены (запущен ли Ollama?)"
    }
}

THEMES_INFO = {
    'robbyrussell': {'name': 'RobbyRussell', 'desc': '➜ ~ git:(main)'},
    'zsh-arrow': {'name': 'Flux Arrow', 'desc': '➜ ~'},
    'zsh-classic': {'name': 'Flux Classic', 'desc': '[16:17:43] user@host:'},
    'agnoster': {'name': 'Agnoster', 'desc': '~ ❯'},
    'pure': {'name': 'Pure', 'desc': '~ ❯'},
    'powerlevel': {'name': 'Powerlevel', 'desc': 'λ ~ ❯'},
    'minimal': {'name': 'Minimalist', 'desc': '~ $'}
}

prompt_style = Style.from_dict({
    'arrow-green': '#00ff00 bold',
    'arrow-red': '#ff0000 bold',
    'folder': '#00ffff bold',
    'time': '#808080',
    'userhost': '#00ffaa bold',
    'git-branch': '#ff00ff',
    'lambda': '#ffb000 bold',
    'ai-prompt': '#bd93f9 bold'  
})

def load_config():
    state = DEFAULT_STATE.copy()
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                state.update(json.load(f))
        except Exception:
            pass
    return state

def save_config(state):
    to_save = {
        'theme': state['theme'],
        'lang': state['lang'],
        'border_style': state['border_style'],
        'ai_model': state['ai_model']
    }
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(to_save, f, indent=4)
    except Exception as e:
        console.print(f"[red]Failed to save config: {e}[/red]")

state = load_config()

def get_msg(key):
    lang = state['lang']
    return MESSAGES.get(lang, MESSAGES['en']).get(key, MESSAGES['en'].get(key, key))