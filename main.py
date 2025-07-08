import flet as ft
import json
import time
import requests
import hashlib
from datetime import datetime
import os
import asyncio

class TikTokReporterApp:
    def __init__(self, page):
        self.page = page
        self.page.title = "TikTok User Reporter"
        self.page.window_width = 1024
        self.page.window_height = 768
        self.page.window_resizable = True
        self.page.window_center()
        
        # Report reasons
        self.report_reasons = {
            "Harassment": "1001",
            "Hate Speech": "1002",
            "Violent Extremism": "1003",
            "Suicide or Self-harm": "1004",
            "Nudity or Sexual Content": "2001",
            "Minor Safety": "2002",
            "Dangerous Acts": "2003",
            "Illegal Activities": "3001",
            "Animal Cruelty": "3002",
            "Fraud or Scam": "4001",
            "Misinformation": "4002",
            "Spam": "90061",
            "Other": "90062"
        }
        
        self.report_counter = 0
        self.setup_ui()
    
    def setup_ui(self):
        # Input fields
        self.target_username = ft.TextField(
            label="Target Username:",
            width=300
        )
        
        self.reason_combo = ft.Dropdown(
            label="Reason:",
            options=[ft.dropdown.Option(key) for key in self.report_reasons.keys()],
            value=list(self.report_reasons.keys())[0],
            width=300
        )
        
        self.report_count = ft.TextField(
            label="Number of Reports:",
            value="1",
            width=300
        )
        
        self.delay_seconds = ft.TextField(
            label="Delay (seconds):",
            value="5",
            width=300
        )
        
        # Buttons
        self.load_headers_btn = ft.ElevatedButton(
            text="Load Headers",
            on_click=lambda _: self.load_json_file(self.headers_text, "Select Headers JSON File"),
            width=150
        )
        
        self.load_cookies_btn = ft.ElevatedButton(
            text="Load Cookies",
            on_click=lambda _: self.load_json_file(self.cookies_text, "Select Cookies JSON File"),
            width=150
        )
        
        self.save_log_btn = ft.ElevatedButton(
            text="Save Log",
            on_click=self.save_log,
            width=150
        )
        
        # JSON text fields
        self.headers_text = ft.TextField(
            label="Headers (JSON):",
            value='{\n    "User-Agent": "Mozilla/5.0",\n    "Accept": "application/json"\n}',
            multiline=True,
            min_lines=5,
            max_lines=5
        )
        
        self.cookies_text = ft.TextField(
            label="Cookies (JSON):",
            value='{\n    "sessionid": "YOUR_SESSION_ID"\n}',
            multiline=True,
            min_lines=5,
            max_lines=5
        )
        
        # Run button
        self.run_button = ft.ElevatedButton(
            text="Run Reports",
            on_click=self.run_reports,
            color=ft.colors.WHITE,
            bgcolor=ft.colors.BLUE,
            width=200,
            height=50
        )
        
        # Log area
        self.log_area = ft.ListView(expand=True)
        
        # Counter label
        self.counter_label = ft.Text(
            value="Reports Done: 0",
            color=ft.colors.GREEN,
            size=14
        )
        
        # Layout
        self.page.add(
            ft.Column(
                [
                    ft.Row(
                        [
                            ft.Column(
                                [
                                    self.target_username,
                                    self.reason_combo,
                                    self.report_count,
                                    self.delay_seconds,
                                    ft.Row(
                                        [
                                            self.load_headers_btn,
                                            self.load_cookies_btn,
                                            self.save_log_btn
                                        ],
                                        spacing=10
                                    )
                                ],
                                spacing=10
                            )
                        ],
                        alignment=ft.MainAxisAlignment.CENTER
                    ),
                    self.headers_text,
                    self.cookies_text,
                    ft.Row([self.run_button], alignment=ft.MainAxisAlignment.CENTER),
                    ft.Text("Log:", size=16),
                    ft.Container(
                        self.log_area,
                        border=ft.border.all(1, ft.colors.GREY_800),
                        border_radius=5,
                        padding=10,
                        expand=True
                    ),
                    ft.Row([self.counter_label], alignment=ft.MainAxisAlignment.END)
                ],
                spacing=20,
                expand=True
            )
        )
    
    async def load_json_file(self, text_field, title):
        file_picker = ft.FilePicker()
        self.page.overlay.append(file_picker)
        self.page.update()
        
        def on_dialog_result(e: ft.FilePickerResultEvent):
            if e.files:
                file_path = e.files[0].path
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                        text_field.value = json.dumps(data, indent=4)
                        self.page.update()
                except Exception as e:
                    self.show_snackbar(f"Failed to load file: {str(e)}")
        
        file_picker.on_result = on_dialog_result
        file_picker.pick_files(dialog_title=title, allowed_extensions=["json"])
    
    async def save_log(self, e):
        file_picker = ft.FilePicker()
        self.page.overlay.append(file_picker)
        self.page.update()
        
        def on_dialog_result(e: ft.FilePickerResultEvent):
            if e.path:
                try:
                    with open(e.path, 'w') as f:
                        for log_entry in self.log_area.controls:
                            f.write(log_entry.value + "\n")
                    self.show_snackbar("Log saved successfully!")
                except Exception as e:
                    self.show_snackbar(f"Failed to save log: {str(e)}")
        
        file_picker.on_result = on_dialog_result
        file_picker.save_file(dialog_title="Save Log File", allowed_extensions=["txt"])
    
    def show_snackbar(self, message):
        self.page.snack_bar = ft.SnackBar(ft.Text(message))
        self.page.snack_bar.open = True
        self.page.update()
    
    async def run_reports(self, e):
        try:
            headers = json.loads(self.headers_text.value.strip())
            cookies = json.loads(self.cookies_text.value.strip())
            reason_text = self.reason_combo.value
            reason_code = self.report_reasons.get(reason_text, "90062")
            
            self.report_counter = 0
            self.update_counter()
            
            self.log("\n=== Starting Reports ===")
            self.log(f"Target: @{self.target_username.value}")
            self.log(f"Reason: {reason_text} (Code: {reason_code})")
            self.log(f"Count: {self.report_count.value} reports")
            self.log(f"Delay: {self.delay_seconds.value} seconds\n")
            
            await self.report_tiktok_user(
                target_username=self.target_username.value,
                reason_code=reason_code,
                cookies=cookies,
                headers=headers,
                report_count=int(self.report_count.value),
                delay_seconds=int(self.delay_seconds.value)
            )
            
            self.show_snackbar("All reports completed!")
        except json.JSONDecodeError:
            self.show_snackbar("Invalid JSON format in headers/cookies!")
        except Exception as e:
            self.show_snackbar(str(e))
    
    def increment_counter(self):
        self.report_counter += 1
        self.update_counter()
    
    def update_counter(self):
        self.counter_label.value = f"Reports Done: {self.report_counter}"
        self.page.update()
    
    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_area.controls.append(ft.Text(f"[{timestamp}] {message}"))
        self.page.update()
    
    async def report_tiktok_user(self, target_username, reason_code, cookies, headers, report_count=1, delay_seconds=5):
        for i in range(1, report_count + 1):
            try:
                self.log(f"Attempting report #{i} of {report_count}...")
                
                base_params = {
                    'aid': '1988',
                    'app_language': 'en',
                    'app_name': 'tiktok_web',
                    'nickname': target_username,
                    'reason': reason_code,
                    'report_type': 'user',
                    'device_platform': 'web_pc',
                    'region': 'US',
                    'priority_region': 'US',
                    'tz_name': 'America/New_York',
                    'user_is_login': 'true'
                }
                
                response = requests.get(
                    'https://www.tiktok.com/aweme/v2/aweme/feedback/',
                    params=base_params,
                    cookies=cookies,
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    self.log("Success! Response received.")
                    self.increment_counter()
                else:
                    self.log(f"Failed with status code: {response.status_code}")
                
                if i < report_count:
                    await asyncio.sleep(delay_seconds)
                    
            except Exception as e:
                self.log(f"Error: {str(e)}")
                await asyncio.sleep(delay_seconds)

async def main(page: ft.Page):
    app = TikTokReporterApp(page)

if __name__ == "__main__":
    ft.app(target=main)
