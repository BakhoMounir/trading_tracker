import customtkinter as ctk
from telethon import events
import asyncio
import logging
from datetime import datetime
import re
import tkinter.messagebox as messagebox
import json
import os

logger = logging.getLogger(__name__)

class SignalsPage:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.frame = ctk.CTkFrame(parent)
        self.is_monitoring = False
        self.monitored_chats = set()
        self.group_keywords = {}  # Store keywords for each group
        
        # Create UI elements
        self.create_widgets()
        
    def create_widgets(self):
        # Title
        self.title_label = ctk.CTkLabel(
            self.frame,
            text="Signal Monitor",
            font=("Helvetica", 20, "bold")
        )
        self.title_label.pack(pady=20)
        
        # Messages frame
        self.messages_frame = ctk.CTkScrollableFrame(self.frame, width=700, height=400)
        self.messages_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        # Control buttons frame
        self.control_frame = ctk.CTkFrame(self.frame)
        self.control_frame.pack(pady=10, padx=20, fill="x")
        
        # Buttons frame
        self.buttons_frame = ctk.CTkFrame(self.control_frame)
        self.buttons_frame.pack(pady=10, fill="x")
        
        # Clear messages button
        self.clear_button = ctk.CTkButton(
            self.buttons_frame,
            text="Clear Messages",
            command=self.clear_messages,
            width=200,
            height=40
        )
        self.clear_button.pack(side="left", padx=10)
        
        # Stop monitoring button
        self.stop_button = ctk.CTkButton(
            self.buttons_frame,
            text="Stop Reading Signals",
            command=self.stop_all_processes,
            width=200,
            height=40,
            fg_color="#FF5555",
            hover_color="#FF3333",
            state="disabled"
        )
        self.stop_button.pack(side="left", padx=10)
        
        # Status label
        self.status_label = ctk.CTkLabel(
            self.frame,
            text="Monitoring is not active",
            font=("Helvetica", 12)
        )
        self.status_label.pack(pady=10)
    
    def set_monitoring_config(self, monitored_chats, keywords):
        self.monitored_chats = monitored_chats
        self.group_keywords = keywords
        self.start_monitoring()
        self.stop_button.configure(state="normal")  # Enable stop button
    
    def get_keywords_for_chat(self, chat_id):
        """Get keywords for a specific chat"""
        return self.group_keywords.get(str(chat_id), self.group_keywords.get("Default", {}))
    
    def start_monitoring(self):
        if not self.app.client or not self.monitored_chats:
            self.status_label.configure(text="Cannot start monitoring: No groups selected or not logged in")
            return
            
        if self.is_monitoring:
            return
            
        self.is_monitoring = True
        self.status_label.configure(text="Monitoring active")
        
        # Register message handler
        @self.app.client.on(events.NewMessage)
        async def handle_new_message(event):
            try:
                chat = await event.get_chat()
                if chat.id not in self.monitored_chats:
                    return
                    
                message = event.message.text
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                text_upper = message.upper()
                chat_keywords = self.get_keywords_for_chat(chat.id)

                # Initialize signal data with all possible fields
                signal_data = {
                    "timestamp": timestamp,
                    "chat_title": chat.title,
                    "raw_message": message,
                    "asset": None,
                    "action": None,
                    "sl": None,
                    "entry": None
                }

                # Extract action (BUY/SELL)
                for keyword, alias in chat_keywords.get('actions', {}).items():
                    pattern = r'\b' + re.escape(keyword) + r'\b'
                    if re.search(pattern, text_upper):
                        signal_data["action"] = alias
                        break

                # Extract asset name
                prefix = re.escape(chat_keywords.get('asset_prefix', '('))
                suffix = re.escape(chat_keywords.get('asset_suffix', ')'))
                asset_pattern = rf'{prefix}\s*([A-Z0-9/._\s-]+?)\s*{suffix}'
                asset_match = re.search(asset_pattern, text_upper)
                if asset_match:
                    signal_data["asset"] = asset_match.group(1).strip()

                # Extract entry price
                entry_keywords = chat_keywords.get('entry', {})
                for keyword, alias in entry_keywords.items():
                    pattern = r'\b' + re.escape(keyword) + r'\s*[:=]?\s*(-?\d+(?:\.\d+)?)'
                    match = re.search(pattern, text_upper)
                    if match:
                        signal_data["entry"] = match.group(1)
                        break

                # Extract stop loss
                sl_keywords = chat_keywords.get('sl', {})
                for keyword, alias in sl_keywords.items():
                    pattern = r'\b' + re.escape(keyword) + r'\s*[:=]?\s*(-?\d+(?:\.\d+)?)'
                    match = re.search(pattern, text_upper)
                    if match:
                        signal_data["sl"] = match.group(1)
                        break

                # Extract take profit levels
                tp_keywords = chat_keywords.get('tp', {})
                for keyword, alias in tp_keywords.items():
                    pattern = r'\b' + re.escape(keyword) + r'\s*[:=]?\s*(-?\d+(?:\.\d+)?)'
                    match = re.search(pattern, text_upper)
                    if match:
                        tp_number = alias.replace('TP', '')
                        signal_data[f"tp{tp_number}"] = match.group(1)

                # Save to JSON if we have a valid signal
                if signal_data["asset"] and signal_data["action"]:
                    SIGNAL_FILE = "signals_output.json"
                    signals = []
                    if os.path.exists(SIGNAL_FILE):
                        try:
                            with open(SIGNAL_FILE, "r") as f:
                                signals = json.load(f)
                        except json.JSONDecodeError:
                            signals = []

                    signals.append(signal_data)
                    with open(SIGNAL_FILE, "w") as f:
                        json.dump(signals, f, indent=2)

                # Create message frame
                msg_frame = ctk.CTkFrame(self.messages_frame)
                msg_frame.pack(fill="x", padx=5, pady=5)
                
                # Add message content
                ctk.CTkLabel(
                    msg_frame,
                    text=f"Time: {timestamp}",
                    font=("Helvetica", 10)
                ).pack(anchor="w", padx=5)
                
                ctk.CTkLabel(
                    msg_frame,
                    text=f"Chat: {chat.title}",
                    font=("Helvetica", 10, "bold")
                ).pack(anchor="w", padx=5)
                
                # Add message text
                ctk.CTkLabel(
                    msg_frame,
                    text=message,
                    font=("Helvetica", 11),
                    wraplength=650
                ).pack(anchor="w", padx=5, pady=5)
                
                # Display extracted signal data
                if signal_data["asset"] and signal_data["action"]:
                    signal_frame = ctk.CTkFrame(msg_frame)
                    signal_frame.pack(fill="x", padx=5, pady=5)
                    
                    ctk.CTkLabel(
                        signal_frame,
                        text="Extracted Signal:",
                        font=("Helvetica", 10, "bold")
                    ).pack(anchor="w", padx=5)
                    
                    # Display only non-None values
                    for key, value in signal_data.items():
                        if value is not None and key not in ["timestamp", "chat_title", "raw_message"]:
                            ctk.CTkLabel(
                                signal_frame,
                                text=f"{key}: {value}",
                                font=("Helvetica", 10)
                            ).pack(anchor="w", padx=5)
                
                # Add separator at the end
                ctk.CTkFrame(msg_frame, height=1, fg_color="gray").pack(fill="x", padx=5, pady=2)
                
            except Exception as e:
                logger.error(f"Error handling message: {e}")
                
    def clear_messages(self):
        for widget in self.messages_frame.winfo_children():
            widget.destroy()
            
    def show(self):
        self.frame.pack(fill="both", expand=True)
        
    def hide(self):
        self.frame.pack_forget()

    def stop_all_processes(self):
        """Stop all processes and cleanup resources"""
        try:
            # Stop monitoring
            self.is_monitoring = False
            
            # Clear all messages
            self.clear_messages()
            
            # Reset status
            self.status_label.configure(text="Monitoring stopped")
            
            # Clear any pending tasks
            if hasattr(self, 'current_task') and self.current_task and not self.current_task.done():
                self.current_task.cancel()
            
            # Disable stop button
            self.stop_button.configure(state="disabled")
            
            # Show confirmation message
            messagebox.showinfo(
                "Signals Monitoring Stopped",
                "Successfully stopped reading Telegram signals."
            )
            
        except Exception as e:
            logger.error(f"Error stopping signals page processes: {e}")
            messagebox.showerror(
                "Error",
                f"Error stopping signals monitoring: {str(e)}"
            )
