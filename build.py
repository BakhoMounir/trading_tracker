import PyInstaller.__main__
import os

# Get the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Define the paths
icon_path = os.path.join(current_dir, 'utils', 'icon.ico')
main_script = os.path.join(current_dir, 'main.py')

# Create the application directory if it doesn't exist
app_dir = os.path.join(current_dir, 'application')
if not os.path.exists(app_dir):
    os.makedirs(app_dir)

# PyInstaller arguments
args = [
    main_script,
    '--name=Telegram_4_Trading',
    '--onefile',
    '--windowed',
    '--clean',
    f'--icon={icon_path}',
    '--add-data=utils;utils',
    '--add-data=pages;pages',
    '--hidden-import=telethon',
    '--hidden-import=customtkinter',
    '--hidden-import=PIL',
    '--hidden-import=asyncio',
    '--hidden-import=logging',
    '--hidden-import=json',
    '--hidden-import=tkinter',
    '--hidden-import=tkinter.messagebox',
    '--hidden-import=datetime',
    '--hidden-import=re',
    '--hidden-import=threading',
    f'--distpath={app_dir}',
    '--noconfirm'
]

# Run PyInstaller
PyInstaller.__main__.run(args) 