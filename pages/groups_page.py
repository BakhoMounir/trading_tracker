import customtkinter as ctk
from telethon import TelegramClient
import asyncio
import logging
from datetime import datetime
import json
import os
import tkinter.messagebox as messagebox

logger = logging.getLogger(__name__)

class GroupsPage:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.frame = ctk.CTkFrame(parent)
        self.monitored_chats = set()
        self.keywords = {}
        
        # Default keywords from telegram_monitor.py
        self.default_keywords = {
            'actions': {
                'BUY': 'BUY',
                'SELL': 'SELL'
            },
            'asset_prefix': '(',
            'asset_suffix': ')',
            'entry': {
                'ENTRY': 'Entry'
            },
            'sl': {
                'SL': 'SL'
            },
            'tp': {
                'TP1': 'TP1',
                'TP2': 'TP2'
            }
        }

        # Create UI elements
        self.create_widgets()

    def create_widgets(self):
        # Title
        self.title_label = ctk.CTkLabel(
            self.frame,
            text="Select Groups to Monitor",
            font=("Helvetica", 20, "bold")
        )
        self.title_label.pack(pady=20)

        # Groups list frame
        self.groups_frame = ctk.CTkScrollableFrame(self.frame, width=600, height=300)
        self.groups_frame.pack(pady=10, padx=20, fill="both", expand=True)

        # Status label
        self.status_label = ctk.CTkLabel(
            self.frame,
            text="Loading groups...",
            font=("Helvetica", 12)
        )
        self.status_label.pack(pady=10)

        # Buttons frame
        self.buttons_frame = ctk.CTkFrame(self.frame)
        self.buttons_frame.pack(pady=20, fill="x")

        # Start monitoring button
        self.start_button = ctk.CTkButton(
            self.buttons_frame,
            text="Start Monitoring",
            command=self.start_monitoring,
            width=200,
            height=40,
            fg_color="#2CC985",
            hover_color="#28B67B"
        )
        self.start_button.pack(side="left", padx=10)
        self.start_button.configure(state="disabled")  # Initially disabled

    async def load_groups(self):
        """Load available groups and channels"""
        if not self.app.client:
            self.status_label.configure(text="Please login first")
            return

        # Clear existing groups
        for widget in self.groups_frame.winfo_children():
            widget.destroy()

        try:
            self.status_label.configure(text="Loading groups...")
            chats = []

            async for dialog in self.app.client.iter_dialogs():
                chat = dialog.entity
                chat_type = "Unknown"
                should_add = False

                if hasattr(chat, 'broadcast') and chat.broadcast:
                    chat_type = "Channel"
                    should_add = True
                elif hasattr(chat, 'megagroup') and chat.megagroup:
                    chat_type = "Supergroup"
                    should_add = True
                elif hasattr(chat, 'title'):
                    chat_type = "Group"
                    should_add = True

                if should_add:
                    chats.append({
                        'id': chat.id,
                        'title': chat.title if hasattr(chat, 'title') else "No Title",
                        'type': chat_type,
                        'last_message_date': dialog.date if dialog.date else datetime.min
                    })

            # Sort chats by last message date
            chats.sort(key=lambda x: x['last_message_date'], reverse=True)

            # Create checkboxes for each chat
            for chat in chats:
                var = ctk.BooleanVar(value=chat['id'] in self.monitored_chats)
                frame = ctk.CTkFrame(self.groups_frame)
                frame.pack(fill="x", padx=5, pady=2)

                ctk.CTkCheckBox(
                    frame,
                    text=f"[{chat['type']}] {chat['title']}",
                    variable=var,
                    command=lambda c=chat, v=var: self.toggle_chat(c, v)
                ).pack(side="left", padx=5)

            self.status_label.configure(text=f"Found {len(chats)} groups")
            self.start_button.configure(state="normal")

        except Exception as e:
            logger.error(f"Error loading groups: {e}")
            self.status_label.configure(text=f"Error loading groups: {str(e)}")

    def toggle_chat(self, chat, var):
        """Toggle chat selection and setup keywords"""
        if var.get():
            self.monitored_chats.add(chat['id'])
            # Setup keywords for the chat
            self.setup_keywords(chat['id'], chat['title'])
        else:
            self.monitored_chats.discard(chat['id'])
            # Remove keywords for the chat
            if str(chat['id']) in self.keywords:
                del self.keywords[str(chat['id'])]

    def setup_keywords(self, chat_id, chat_title):
        """Setup keywords for a specific chat"""
        # Create a new window for keyword setup
        setup_window = ctk.CTkToplevel(self.frame)
        setup_window.title(f"Setup Keywords for {chat_title}")
        setup_window.geometry("500x600")

        # Create scrollable frame for keyword inputs
        scroll_frame = ctk.CTkScrollableFrame(setup_window, width=450, height=500)
        scroll_frame.pack(pady=10, padx=20, fill="both", expand=True)

        # Initialize keyword entries
        keyword_entries = {}

        # Buy/Sell keywords
        ctk.CTkLabel(scroll_frame, text="Buy/Sell Keywords:", font=("Helvetica", 14, "bold")).pack(pady=5)
        buy_entry = ctk.CTkEntry(scroll_frame, placeholder_text="Buy keyword (default: BUY)")
        buy_entry.pack(pady=5, padx=10, fill="x")
        buy_entry.insert(0, "BUY")
        keyword_entries['buy'] = buy_entry

        sell_entry = ctk.CTkEntry(scroll_frame, placeholder_text="Sell keyword (default: SELL)")
        sell_entry.pack(pady=5, padx=10, fill="x")
        sell_entry.insert(0, "SELL")
        keyword_entries['sell'] = sell_entry

        # Entry point keyword
        ctk.CTkLabel(scroll_frame, text="Entry Point Keyword:", font=("Helvetica", 14, "bold")).pack(pady=5)
        entry_entry = ctk.CTkEntry(scroll_frame, placeholder_text="Entry point keyword (default: ENTRY)")
        entry_entry.pack(pady=5, padx=10, fill="x")
        entry_entry.insert(0, "ENTRY")
        keyword_entries['entry'] = entry_entry

        # Stop Loss keyword
        ctk.CTkLabel(scroll_frame, text="Stop Loss Keyword:", font=("Helvetica", 14, "bold")).pack(pady=5)
        sl_entry = ctk.CTkEntry(scroll_frame, placeholder_text="Stop loss keyword (default: SL)")
        sl_entry.pack(pady=5, padx=10, fill="x")
        sl_entry.insert(0, "SL")
        keyword_entries['sl'] = sl_entry

        # Take Profit keywords
        ctk.CTkLabel(scroll_frame, text="Take Profit Keywords:", font=("Helvetica", 14, "bold")).pack(pady=5)
        tp_entries = []
        for i in range(1, 6):  # Allow up to 5 take profit levels
            tp_entry = ctk.CTkEntry(scroll_frame, placeholder_text=f"TP{i} keyword (default: TP{i})")
            tp_entry.pack(pady=5, padx=10, fill="x")
            tp_entry.insert(0, f"TP{i}")
            tp_entries.append(tp_entry)
        keyword_entries['tp'] = tp_entries

        # Asset prefix/suffix
        ctk.CTkLabel(scroll_frame, text="Asset Format:", font=("Helvetica", 14, "bold")).pack(pady=5)
        prefix_entry = ctk.CTkEntry(scroll_frame, placeholder_text="Asset prefix (default: ()")
        prefix_entry.pack(pady=5, padx=10, fill="x")
        prefix_entry.insert(0, "(")
        keyword_entries['prefix'] = prefix_entry

        suffix_entry = ctk.CTkEntry(scroll_frame, placeholder_text="Asset suffix (default: ))")
        suffix_entry.pack(pady=5, padx=10, fill="x")
        suffix_entry.insert(0, ")")
        keyword_entries['suffix'] = suffix_entry

        def save_keywords():
            # Create keywords dictionary for this chat
            chat_keywords = {
                'actions': {
                    keyword_entries['buy'].get().strip().upper(): 'BUY',
                    keyword_entries['sell'].get().strip().upper(): 'SELL'
                },
                'asset_prefix': keyword_entries['prefix'].get().strip(),
                'asset_suffix': keyword_entries['suffix'].get().strip(),
                'entry': {
                    keyword_entries['entry'].get().strip().upper(): 'Entry'
                },
                'sl': {
                    keyword_entries['sl'].get().strip().upper(): 'SL'
                },
                'tp': {}
            }

            # Add take profit keywords
            for i, entry in enumerate(keyword_entries['tp'], 1):
                if entry.get().strip():
                    chat_keywords['tp'][entry.get().strip().upper()] = f'TP{i}'

            # Save keywords for this chat
            self.keywords[str(chat_id)] = chat_keywords

            # Save to file
            self.save_keywords_to_file()

            # Close window
            setup_window.destroy()

            # Update status
            self.status_label.configure(text=f"Keywords saved for {chat_title}")

        # Save button
        ctk.CTkButton(
            setup_window,
            text="Save Keywords",
            command=save_keywords,
            width=200,
            height=40
        ).pack(pady=20)

    def save_keywords_to_file(self):
        """Save keywords configuration to file"""
        try:
            with open('keywords_config.json', 'w') as f:
                json.dump(self.keywords, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving keywords: {e}")

    def load_keywords_from_file(self):
        """Load keywords configuration from file"""
        try:
            if os.path.exists('keywords_config.json'):
                with open('keywords_config.json', 'r') as f:
                    self.keywords = json.load(f)
        except Exception as e:
            logger.error(f"Error loading keywords: {e}")

    def start_monitoring(self):
        """Start monitoring selected groups"""
        if not self.monitored_chats:
            self.status_label.configure(text="Please select at least one group to monitor")
            return

        # Pass monitored chats and keywords to signals page
        self.app.signals_page.set_monitoring_config(self.monitored_chats, self.keywords)
        self.app.show_tab3()  # Switch to signals page

    def show(self):
        """Show the groups page"""
        self.frame.pack(fill="both", expand=True)
        # Load groups when page is shown
        if self.app.client and self.app.client.is_connected():
            asyncio.run_coroutine_threadsafe(self.load_groups(), self.app.loop)
            self.load_keywords_from_file()  # Load saved keywords

    def hide(self):
        """Hide the groups page"""
        self.frame.pack_forget()

    def cleanup(self):
        """Cleanup resources"""
        try:
            # Cancel any ongoing tasks
            if hasattr(self, 'current_task') and self.current_task and not self.current_task.done():
                self.current_task.cancel()
            
            # Clear any loaded groups
            self.monitored_chats.clear()
            
            # Clear the groups frame
            for widget in self.groups_frame.winfo_children():
                widget.destroy()
            
            # Reset status
            self.status_label.configure(text="Monitoring stopped")
            
            # Disable start button
            self.start_button.configure(state="disabled")
            
        except Exception as e:
            logger.error(f"Error cleaning up groups page: {e}")
