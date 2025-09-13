#!/usr/bin/env python3
"""
Screenshot Selection Tool
A Python script that implements a screenshot selection tool allowing users to 
drag to define a specific portion of the screen with dynamic resizing capabilities.
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import shutil
from PIL import Image, ImageTk
import os
import time
from datetime import datetime

class ScreenshotSelector:
    def __init__(self):
        self.root = None
        self.canvas = None
        self.screenshot = None
        self.photo = None
        self.start_x = None
        self.start_y = None
        self.current_x = None
        self.current_y = None
        self.rect_id = None
        self.selection_rect = None
        self.handles = []
        self.dragging = False
        self.resizing = False
        self.resize_handle = None
        
    def take_screenshot(self):
        """Take a full screenshot and return PIL Image"""
        try:
            # Hide any existing windows first
            if self.root:
                self.root.withdraw()
            
            # Wait a moment for window to hide
            time.sleep(0.1)
            
            # Use system command to take screenshot
            temp_file = "/tmp/temp_screenshot.png"
            
            # Try different screenshot tools available on Linux
            screenshot_tools = [
                ['scrot', temp_file],
                ['gnome-screenshot', '-f', temp_file],
                ['import', '-window', 'root', temp_file],  # ImageMagick
                ['xwd', '-root', '-out', '/tmp/temp_screenshot.xwd']  # X11 dump
            ]
            
            screenshot_taken = False
            for tool in screenshot_tools:
                if shutil.which(tool[0]):  # Check if tool exists
                    try:
                        if tool[0] == 'xwd':
                            # For xwd, we need to convert to png
                            result = subprocess.run(tool, capture_output=True, timeout=10)
                            if result.returncode == 0:
                                # Convert xwd to png using ImageMagick
                                convert_cmd = ['convert', '/tmp/temp_screenshot.xwd', temp_file]
                                if shutil.which('convert'):
                                    subprocess.run(convert_cmd, capture_output=True, timeout=10)
                                    if os.path.exists(temp_file):
                                        screenshot_taken = True
                                        break
                        else:
                            result = subprocess.run(tool, capture_output=True, timeout=10)
                            if result.returncode == 0 and os.path.exists(temp_file):
                                screenshot_taken = True
                                break
                    except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
                        continue
            
            if not screenshot_taken:
                # If no system tool works, create a dummy image for testing
                print("Warning: No screenshot tool found, creating test image")
                dummy_img = Image.new('RGB', (800, 600), color='lightblue')
                dummy_img.save(temp_file)
                screenshot_taken = True
            
            if screenshot_taken:
                screenshot = Image.open(temp_file)
                # Clean up temp file
                try:
                    os.remove(temp_file)
                except:
                    pass
                return screenshot
            else:
                raise Exception("No screenshot tool available")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to take screenshot: {str(e)}")
            return None
    
    def create_selection_window(self, screenshot):
        """Create a fullscreen transparent overlay for selection"""
        self.root = tk.Tk()
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', 0.3)
        self.root.configure(bg='black')
        self.root.overrideredirect(True)
        
        # Create canvas
        self.canvas = tk.Canvas(
            self.root, 
            highlightthickness=0,
            cursor='crosshair'
        )
        self.canvas.pack(fill='both', expand=True)
        
        # Convert screenshot for display
        self.photo = ImageTk.PhotoImage(screenshot)
        self.canvas.create_image(0, 0, anchor='nw', image=self.photo)
        
        # Bind mouse events
        self.canvas.bind('<Button-1>', self.start_selection)
        self.canvas.bind('<B1-Motion>', self.update_selection)
        self.canvas.bind('<ButtonRelease-1>', self.finish_selection)
        self.canvas.bind('<Double-Button-1>', self.confirm_selection)
        
        # Bind keyboard events
        self.root.bind('<Escape>', self.cancel_selection)
        self.root.bind('<Return>', self.confirm_selection)
        
        self.root.focus_force()
    
    def start_selection(self, event):
        """Start drawing selection rectangle"""
        # Check if clicking on a resize handle
        for i, handle in enumerate(self.handles):
            x1, y1, x2, y2 = self.canvas.coords(handle)
            if x1 <= event.x <= x2 and y1 <= event.y <= y2:
                self.resizing = True
                self.resize_handle = i
                return
        
        # Clear previous selection
        self.clear_selection()
        
        self.start_x = event.x
        self.start_y = event.y
        self.current_x = event.x
        self.current_y = event.y
        self.dragging = True
        
        # Create rectangle
        self.rect_id = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.current_x, self.current_y,
            outline='red', width=2, fill='', stipple='gray50'
        )
    
    def update_selection(self, event):
        """Update selection rectangle during drag"""
        if self.resizing and self.selection_rect:
            self.handle_resize(event)
        elif self.dragging:
            self.current_x = event.x
            self.current_y = event.y
            
            if self.rect_id:
                self.canvas.coords(
                    self.rect_id,
                    self.start_x, self.start_y,
                    self.current_x, self.current_y
                )
    
    def finish_selection(self, event):
        """Finish selection and show resize handles"""
        if self.resizing:
            self.resizing = False
            self.resize_handle = None
            return
            
        if not self.dragging:
            return
            
        self.dragging = False
        
        # Normalize coordinates
        x1 = min(self.start_x, self.current_x)
        y1 = min(self.start_y, self.current_y)
        x2 = max(self.start_x, self.current_x)
        y2 = max(self.start_y, self.current_y)
        
        # Update rectangle coordinates
        if self.rect_id:
            self.canvas.coords(self.rect_id, x1, y1, x2, y2)
            self.selection_rect = (x1, y1, x2, y2)
            self.create_resize_handles(x1, y1, x2, y2)
    
    def create_resize_handles(self, x1, y1, x2, y2):
        """Create resize handles around the selection"""
        self.clear_handles()
        
        handle_size = 8
        positions = [
            (x1 - handle_size//2, y1 - handle_size//2),  # top-left
            ((x1 + x2)//2 - handle_size//2, y1 - handle_size//2),  # top-center
            (x2 - handle_size//2, y1 - handle_size//2),  # top-right
            (x2 - handle_size//2, (y1 + y2)//2 - handle_size//2),  # right-center
            (x2 - handle_size//2, y2 - handle_size//2),  # bottom-right
            ((x1 + x2)//2 - handle_size//2, y2 - handle_size//2),  # bottom-center
            (x1 - handle_size//2, y2 - handle_size//2),  # bottom-left
            (x1 - handle_size//2, (y1 + y2)//2 - handle_size//2),  # left-center
        ]
        
        for x, y in positions:
            handle = self.canvas.create_rectangle(
                x, y, x + handle_size, y + handle_size,
                fill='red', outline='white', width=1
            )
            self.handles.append(handle)
    
    def handle_resize(self, event):
        """Handle resizing of the selection rectangle"""
        if not self.selection_rect or self.resize_handle is None:
            return
            
        x1, y1, x2, y2 = self.selection_rect
        
        # Update coordinates based on which handle is being dragged
        if self.resize_handle == 0:  # top-left
            x1, y1 = event.x, event.y
        elif self.resize_handle == 1:  # top-center
            y1 = event.y
        elif self.resize_handle == 2:  # top-right
            x2, y1 = event.x, event.y
        elif self.resize_handle == 3:  # right-center
            x2 = event.x
        elif self.resize_handle == 4:  # bottom-right
            x2, y2 = event.x, event.y
        elif self.resize_handle == 5:  # bottom-center
            y2 = event.y
        elif self.resize_handle == 6:  # bottom-left
            x1, y2 = event.x, event.y
        elif self.resize_handle == 7:  # left-center
            x1 = event.x
        
        # Ensure minimum size
        if abs(x2 - x1) < 10:
            return
        if abs(y2 - y1) < 10:
            return
        
        # Update selection rectangle
        self.selection_rect = (x1, y1, x2, y2)
        self.canvas.coords(self.rect_id, x1, y1, x2, y2)
        self.create_resize_handles(x1, y1, x2, y2)
    
    def clear_handles(self):
        """Clear all resize handles"""
        for handle in self.handles:
            self.canvas.delete(handle)
        self.handles.clear()
    
    def clear_selection(self):
        """Clear current selection"""
        if self.rect_id:
            self.canvas.delete(self.rect_id)
            self.rect_id = None
        self.clear_handles()
        self.selection_rect = None
    
    def cancel_selection(self, event=None):
        """Cancel selection and close window"""
        if self.root:
            self.root.destroy()
        return None
    
    def confirm_selection(self, event=None):
        """Confirm selection and return coordinates"""
        if not self.selection_rect:
            messagebox.showwarning("Warning", "No selection made. Please drag to select an area.")
            return None
        
        # Normalize coordinates
        x1, y1, x2, y2 = self.selection_rect
        x1, x2 = min(x1, x2), max(x1, x2)
        y1, y2 = min(y1, y2), max(y1, y2)
        
        result = (int(x1), int(y1), int(x2), int(y2))
        
        if self.root:
            self.root.destroy()
        
        return result
    
    def capture_area(self, coordinates):
        """Capture the selected area and return PIL Image"""
        if not coordinates or not self.screenshot:
            return None
        
        x1, y1, x2, y2 = coordinates
        
        try:
            # Crop the selected area from the original screenshot
            cropped = self.screenshot.crop((x1, y1, x2, y2))
            return cropped
        except Exception as e:
            messagebox.showerror("Error", f"Failed to capture area: {str(e)}")
            return None
    
    def save_image(self, image, filename=None):
        """Save the captured image"""
        if not image:
            return False
        
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"screenshot_{timestamp}.png"
            
            # Ask user where to save if no path provided
            if not os.path.dirname(filename):
                filename = filedialog.asksaveasfilename(
                    defaultextension=".png",
                    filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")],
                    initialname=filename
                )
                
                if not filename:  # User cancelled
                    return False
            
            image.save(filename)
            print(f"Screenshot saved as: {filename}")
            return True
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save image: {str(e)}")
            return False
    
    def run_selection_tool(self):
        """Main method to run the screenshot selection tool"""
        try:
            # Take initial screenshot
            screenshot = self.take_screenshot()
            if not screenshot:
                return None
            
            self.screenshot = screenshot
            
            # Create selection window
            self.create_selection_window(screenshot)
            
            print("Screenshot tool started. Instructions:")
            print("- Drag to select an area")
            print("- Use handles to resize the selection")
            print("- Double-click or press Enter to confirm")
            print("- Press Escape to cancel")
            
            # Start the main loop
            self.root.mainloop()
            
            return self.selection_rect
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            return None

def process_with_ai(image):
    """
    Placeholder function for AI processing of the captured image.
    This can be replaced with actual AI functionality as needed.
    """
    print("AI processing placeholder - implement your AI logic here")
    print(f"Image size: {image.size}")
    print(f"Image mode: {image.mode}")
    
    # Example: could integrate with OCR, image recognition, etc.
    # Return processed results
    return {"status": "processed", "description": "AI processing completed"}

def main():
    """Main function to run the screenshot tool"""
    print("Starting Screenshot Selection Tool...")
    
    # Create and run the selection tool
    selector = ScreenshotSelector()
    coordinates = selector.run_selection_tool()
    
    if coordinates:
        print(f"Selected area: {coordinates}")
        
        # Capture the selected area
        captured_image = selector.capture_area(coordinates)
        
        if captured_image:
            print(f"Captured image size: {captured_image.size}")
            
            # Ask user what to do with the image
            choice = input("\nWhat would you like to do with the captured image?\n1. Save to file\n2. Process with AI\n3. Both\nEnter choice (1/2/3): ").strip()
            
            if choice in ['1', '3']:
                # Save the image
                if selector.save_image(captured_image):
                    print("Image saved successfully!")
                else:
                    print("Failed to save image.")
            
            if choice in ['2', '3']:
                # Process with AI (placeholder)
                ai_result = process_with_ai(captured_image)
                print(f"AI processing result: {ai_result}")
            
            return captured_image
        else:
            print("Failed to capture the selected area.")
    else:
        print("No area selected or operation cancelled.")
    
    return None

if __name__ == "__main__":
    main()