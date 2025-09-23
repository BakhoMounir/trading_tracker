import sys
import customtkinter as ctk
from telethon import TelegramClient, events
from telethon.errors import (
    SessionPasswordNeededError,
    PhoneNumberInvalidError,
    PhoneCodeInvalidError,
    PhoneCodeExpiredError
)
import asyncio
import os
import tkinter.messagebox as messagebox
import logging
import json
import threading

from utils.config import API_ID, API_HASH
from pages.login_page import LoginPage
from pages.groups_page import GroupsPage
from pages.signals_page import SignalsPage

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TradingTracker:
    def __init__(self):
        self.window = ctk.CTk()
        self.window.title("Trading Tracker")
        self.window.geometry("800x600")
        
        # Initialize Telegram client and event loop
        self.client = None
        self.dialogs = []
        self.API_ID = API_ID
        self.API_HASH = API_HASH
        
        # Create and set event loop
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
        # Start event loop in a separate thread
        self.loop_thread = threading.Thread(target=self._run_event_loop, daemon=True)
        self.loop_thread.start()
        
        # Create navigation frame
        self.nav_frame = ctk.CTkFrame(self.window, height=50)
        self.nav_frame.pack(fill="x", padx=10, pady=5)
        
        # Create navigation buttons
        self.login_button = ctk.CTkButton(
            self.nav_frame,
            text="Login",
            command=self.show_tab1,
            width=120
        )
        self.login_button.pack(side="left", padx=5)
        
        self.groups_button = ctk.CTkButton(
            self.nav_frame,
            text="Groups",
            command=self.show_tab2,
            width=120
        )
        self.groups_button.pack(side="left", padx=5)
        
        self.signals_button = ctk.CTkButton(
            self.nav_frame,
            text="Signals",
            command=self.show_tab3,
            width=120
        )
        self.signals_button.pack(side="left", padx=5)
        
        # Create pages
        self.login_page = LoginPage(self.window, self)
        self.groups_page = GroupsPage(self.window, self)
        self.signals_page = SignalsPage(self.window, self)
        
        # Check for existing session
        self.check_session()
        
        # Set up window closing handler
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def _run_event_loop(self):
        """Run the event loop in a separate thread"""
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()
    
    def check_session(self):
        """Initialize the application without checking for existing sessions"""
        # Show login page
        self.show_tab1()
        
    def show_tab1(self):
        """Show login page"""
        self.hide_all_pages()
        self.login_page.show()
        self.login_button.configure(fg_color="#2CC985")
        self.groups_button.configure(fg_color=["#3B8ED0", "#1F6AA5"])
        self.signals_button.configure(fg_color=["#3B8ED0", "#1F6AA5"])
    
    def show_tab2(self):
        """Show groups page"""
        self.hide_all_pages()
        self.groups_page.show()
        self.login_button.configure(fg_color=["#3B8ED0", "#1F6AA5"])
        self.groups_button.configure(fg_color="#2CC985")
        self.signals_button.configure(fg_color=["#3B8ED0", "#1F6AA5"])
    
    def show_tab3(self):
        """Show signals page"""
        self.hide_all_pages()
        self.signals_page.show()
        self.login_button.configure(fg_color=["#3B8ED0", "#1F6AA5"])
        self.groups_button.configure(fg_color=["#3B8ED0", "#1F6AA5"])
        self.signals_button.configure(fg_color="#2CC985")
    
    def hide_all_pages(self):
        """Hide all pages"""
        self.login_page.hide()
        self.groups_page.hide()
        self.signals_page.hide()
    
    async def cleanup_and_logout(self):
        """Cleanup and logout from Telegram"""
        try:
            # Stop monitoring if active
            if self.signals_page.is_monitoring:
                try:
                    self.signals_page.is_monitoring = False
                    if self.client:
                        self.client.remove_event_handler(self.signals_page.handle_new_message)
                except Exception as e:
                    logger.error(f"Error stopping monitoring: {e}")
            
            # Logout from Telegram if connected
            if self.client:
                try:
                    if self.client.is_connected():
                        await self.client.log_out()
                        await self.client.disconnect()
                except Exception as e:
                    logger.error(f"Error during Telegram logout: {e}")
                finally:
                    self.client = None
                    self.dialogs = []
            
            # Clean up session files and JSON files
            files_to_delete = [
                'anon.session', 
                'anon.session-journal',
                'signals_output.json',
                'keywords_config.json'
            ]
            
            for file in files_to_delete:
                if os.path.exists(file):
                    try:
                        os.remove(file)
                        logger.info(f"Successfully removed file: {file}")
                    except Exception as e:
                        logger.error(f"Error removing file {file}: {e}")
            
            return True
        except Exception as e:
            logger.error(f"Error during cleanup and logout: {e}")
            return False

    def on_closing(self):
        """Handle window closing"""
        try:
            # Disable all buttons to prevent multiple clicks
            self.groups_button.configure(state='disabled')
            self.signals_button.configure(state='disabled')
            self.login_button.configure(state='disabled')
            
            # Stop all processes in both pages
            try:
                self.signals_page.stop_all_processes()
            except Exception as e:
                logger.error(f"Error stopping signals page: {e}")
                
            try:
                self.groups_page.stop_all_processes()
            except Exception as e:
                logger.error(f"Error stopping groups page: {e}")
            
            # Run cleanup and logout
            try:
                future = asyncio.run_coroutine_threadsafe(self.cleanup_and_logout(), self.loop)
                success = future.result(timeout=5.0)  # Wait for the cleanup to complete with timeout
            except Exception as e:
                logger.error(f"Error during cleanup: {e}")
                success = False
            
            if success:
                # Show goodbye message
                messagebox.showinfo(
                    "Goodbye",
                    "Thank you for using Trading Tracker!\nGoodbye!"
                )
            
            # Stop the event loop if it's running
            try:
                if self.loop.is_running():
                    self.loop.call_soon_threadsafe(self.loop.stop)
            except Exception as e:
                logger.error(f"Error stopping event loop: {e}")
            
            # Stop the mainloop
            try:
                self.window.quit()
            except Exception as e:
                logger.error(f"Error stopping mainloop: {e}")
            
            # Finally destroy the window
            try:
                self.window.destroy()
            except Exception as e:
                logger.error(f"Error destroying window: {e}")
            
        except Exception as e:
            logger.error(f"Error during window closing: {e}")
            # Force close if anything goes wrong
            try:
                self.window.destroy()
            except:
                pass

    async def cleanup_client(self):
        """Safely cleanup the Telegram client"""
        if self.client:
            try:
                # Stop monitoring if active
                if self.signals_page.is_monitoring:
                    self.signals_page.stop_monitoring()
                
                # Cancel all pending tasks
                for task in self.pending_tasks:
                    if not task.done():
                        task.cancel()
                        try:
                            await task
                        except asyncio.CancelledError:
                            pass
                self.pending_tasks.clear()
                
                if self.client.is_connected():
                    await self.client.disconnect()
                self.client = None
            except Exception as e:
                logger.error(f"Error during client cleanup: {e}")

    async def send_code(self, phone):
        """Send verification code to phone number"""
        try:
            if not self.client.is_connected():
                await self.client.connect()
            if not await self.client.is_user_authorized():
                try:
                    result = await self.client.send_code_request(phone)
                    self.phone_code_hash = result.phone_code_hash
                    return True
                except PhoneNumberInvalidError:
                    logger.error("Invalid phone number")
                    return False
                except Exception as e:
                    logger.error(f"Error sending code: {e}")
                    return False
            return True  # Already authorized
        except Exception as e:
            logger.error(f"Error in send_code: {e}")
            return False

    async def sign_in(self, phone, code):
        """Sign in with phone number and verification code"""
        try:
            if not await self.client.is_user_authorized():
                try:
                    await self.client.sign_in(phone, code, phone_code_hash=self.phone_code_hash)
                    return True
                except SessionPasswordNeededError:
                    # 2FA enabled, prompt for password
                    password = messagebox.askstring(
                        "Two-Factor Authentication",
                        "Please enter your Telegram password:",
                        show='*'
                    )
                    if not password:
                        logger.error("Password input cancelled or empty")
                        return False
                    try:
                        await self.client.sign_in(password=password)
                        return True
                    except Exception as e:
                        logger.error(f"Failed to sign in with password: {e}")
                        return False
                except PhoneCodeInvalidError:
                    logger.error("Invalid code")
                    return False
                except PhoneCodeExpiredError:
                    logger.error("Code has expired. Please request a new code.")
                    return False
                except Exception as e:
                    logger.error(f"Sign-in error: {e}")
                    return False
            return True  # Already authorized
        except Exception as e:
            logger.error(f"Error in sign_in: {e}")
            return False

def main():
    app = TradingTracker()
    app.window.mainloop()

if __name__ == "__main__":
    main() 