import customtkinter as ctk
import asyncio
import logging
from telethon import TelegramClient
from telethon.errors import (
    SessionPasswordNeededError,
    PhoneNumberInvalidError,
    PhoneCodeInvalidError,
    PhoneCodeExpiredError
)

logger = logging.getLogger(__name__)

class LoginPage:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.frame = ctk.CTkFrame(parent)
        self.current_task = None
        
        # Create UI elements
        self.create_widgets()
        
    def create_widgets(self):
        # Title
        self.title_label = ctk.CTkLabel(
            self.frame,
            text="Telegram Login",
            font=("Helvetica", 24, "bold")
        )
        self.title_label.pack(pady=20)
        
        # Phone number entry
        self.phone_frame = ctk.CTkFrame(self.frame)
        self.phone_frame.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkLabel(
            self.phone_frame,
            text="Phone Number (with country code):",
            font=("Helvetica", 12)
        ).pack(anchor="w", padx=5)
        
        self.phone_entry = ctk.CTkEntry(
            self.phone_frame,
            placeholder_text="e.g., +1234567890",
            width=300
        )
        self.phone_entry.pack(pady=5, padx=5)
        
        # Code entry (initially hidden)
        self.code_frame = ctk.CTkFrame(self.frame)
        self.code_frame.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkLabel(
            self.code_frame,
            text="Verification Code:",
            font=("Helvetica", 12)
        ).pack(anchor="w", padx=5)
        
        self.code_entry = ctk.CTkEntry(
            self.code_frame,
            placeholder_text="Enter the code you received",
            width=300
        )
        self.code_entry.pack(pady=5, padx=5)
        
        # Buttons
        self.button_frame = ctk.CTkFrame(self.frame)
        self.button_frame.pack(pady=20, padx=20, fill="x")
        
        self.send_code_button = ctk.CTkButton(
            self.button_frame,
            text="Send Code",
            command=self.send_code,
            width=200,
            height=40
        )
        self.send_code_button.pack(side="left", padx=10)
        
        self.verify_button = ctk.CTkButton(
            self.button_frame,
            text="Verify Code",
            command=self.verify_code,
            width=200,
            height=40,
            state="disabled"
        )
        self.verify_button.pack(side="left", padx=10)
        
        # Status label
        self.status_label = ctk.CTkLabel(
            self.frame,
            text="Enter your phone number to begin",
            font=("Helvetica", 12)
        )
        self.status_label.pack(pady=10)
        
        # Initially hide code entry
        self.code_frame.pack_forget()
        
    def send_code(self):
        phone = self.phone_entry.get().strip()
        if not phone:
            self.status_label.configure(text="Please enter a phone number")
            return
            
        self.status_label.configure(text="Sending verification code...")
        self.send_code_button.configure(state="disabled")
        
        # Cancel any existing task
        if self.current_task and not self.current_task.done():
            self.current_task.cancel()
            
        # Create and run new task
        self.current_task = asyncio.run_coroutine_threadsafe(self._send_code(phone), self.app.loop)
        
    async def _send_code(self, phone):
        try:
            if not self.app.client:
                self.app.client = TelegramClient('anon', self.app.API_ID, self.app.API_HASH)
                
            if not self.app.client.is_connected():
                await self.app.client.connect()
                
            if not await self.app.client.is_user_authorized():
                try:
                    result = await self.app.client.send_code_request(phone)
                    self.app.phone_code_hash = result.phone_code_hash
                    
                    # Show code entry
                    self.code_frame.pack(pady=10, padx=20, fill="x")
                    self.verify_button.configure(state="normal")
                    self.status_label.configure(text="Code sent! Enter the verification code")
                    
                except PhoneNumberInvalidError:
                    self.status_label.configure(text="Invalid phone number")
                    self.send_code_button.configure(state="normal")
                except Exception as e:
                    logger.error(f"Error sending code: {e}")
                    self.status_label.configure(text=f"Error: {str(e)}")
                    self.send_code_button.configure(state="normal")
            else:
                self.status_label.configure(text="Already logged in")
                self.send_code_button.configure(state="normal")
                
        except Exception as e:
            logger.error(f"Error during code sending: {e}")
            self.status_label.configure(text=f"Error: {str(e)}")
            self.send_code_button.configure(state="normal")
            
    def verify_code(self):
        phone = self.phone_entry.get().strip()
        code = self.code_entry.get().strip()
        
        if not code:
            self.status_label.configure(text="Please enter the verification code")
            return
            
        self.status_label.configure(text="Verifying code...")
        self.verify_button.configure(state="disabled")
        
        # Cancel any existing task
        if self.current_task and not self.current_task.done():
            self.current_task.cancel()
            
        # Create and run new task
        self.current_task = asyncio.run_coroutine_threadsafe(self._verify_code(phone, code), self.app.loop)
        
    async def _verify_code(self, phone, code):
        try:
            if not await self.app.client.is_user_authorized():
                try:
                    await self.app.client.sign_in(phone, code, phone_code_hash=self.app.phone_code_hash)
                    self.on_successful_login()
                    
                except SessionPasswordNeededError:
                    # 2FA enabled, prompt for password
                    password = ctk.CTkInputDialog(
                        text="Please enter your Telegram password:",
                        title="Two-Factor Authentication"
                    ).get_input()
                    
                    if not password:
                        self.status_label.configure(text="Password input cancelled")
                        self.verify_button.configure(state="normal")
                        return
                        
                    try:
                        await self.app.client.sign_in(password=password)
                        self.on_successful_login()
                    except Exception as e:
                        logger.error(f"Failed to sign in with password: {e}")
                        self.status_label.configure(text=f"Error: {str(e)}")
                        self.verify_button.configure(state="normal")
                        
                except PhoneCodeInvalidError:
                    self.status_label.configure(text="Invalid code")
                    self.verify_button.configure(state="normal")
                except PhoneCodeExpiredError:
                    self.status_label.configure(text="Code has expired. Please request a new code.")
                    self.verify_button.configure(state="normal")
                except Exception as e:
                    logger.error(f"Error during verification: {e}")
                    self.status_label.configure(text=f"Error: {str(e)}")
                    self.verify_button.configure(state="normal")
            else:
                self.status_label.configure(text="Already logged in")
                self.verify_button.configure(state="normal")
                
        except Exception as e:
            logger.error(f"Error during verification: {e}")
            self.status_label.configure(text=f"Error: {str(e)}")
            self.verify_button.configure(state="normal")
            
    def on_successful_login(self):
        self.status_label.configure(text="Login successful!")
        
        # Enable navigation buttons
        self.app.groups_button.configure(state="normal")
        self.app.signals_button.configure(state="normal")
        
        # Switch to groups page
        self.app.show_tab2()
        
    def reset_ui(self):
        # Cancel any existing task
        if self.current_task and not self.current_task.done():
            self.current_task.cancel()
            
        self.phone_entry.delete(0, "end")
        self.code_entry.delete(0, "end")
        self.code_frame.pack_forget()
        self.send_code_button.configure(state="normal")
        self.verify_button.configure(state="disabled")
        self.status_label.configure(text="Enter your phone number to begin")
        
    def show(self):
        self.frame.pack(fill="both", expand=True)
        
    def hide(self):
        self.frame.pack_forget()
        # Cancel any existing task when hiding the page
        if self.current_task and not self.current_task.done():
            self.current_task.cancel() 