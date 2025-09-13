#!/usr/bin/env python3
"""
Screenshot Tool Demo
Demonstrates the screenshot selection functionality
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from screenshot_tool import ScreenshotSelector, process_with_ai

def demo_screenshot_tool():
    """Demonstrate the screenshot tool functionality"""
    print("=== Screenshot Selection Tool Demo ===")
    print()
    
    print("Features implemented:")
    print("✓ Full screen screenshot capture")
    print("✓ Drag-to-select area functionality")
    print("✓ Dynamic resizing with handle grips")
    print("✓ Save captured screenshots")
    print("✓ AI processing integration (placeholder)")
    print("✓ Flask API endpoints for web integration")
    print()
    
    # Test screenshot capture
    print("Testing screenshot capture...")
    selector = ScreenshotSelector()
    screenshot = selector.take_screenshot()
    
    if screenshot:
        print(f"✓ Screenshot captured successfully: {screenshot.size}")
        
        # Save test screenshot
        timestamp = selector.save_image(screenshot, f"/tmp/demo_screenshot_{os.getpid()}.png")
        if timestamp:
            print("✓ Screenshot saved successfully")
        
        # Test AI processing placeholder
        ai_result = process_with_ai(screenshot)
        print(f"✓ AI processing result: {ai_result}")
        
    else:
        print("✗ Screenshot capture failed")
    
    print()
    print("Interactive mode usage (in graphical environment):")
    print("1. Run: python3 screenshot_tool.py")
    print("2. Drag to select area on screen")
    print("3. Use handles to resize selection")
    print("4. Double-click or press Enter to confirm")
    print("5. Press Escape to cancel")
    print()
    
    print("Flask API endpoints:")
    print("- GET  /api/screenshot/status    - Check if screenshot tool is available")
    print("- POST /api/screenshot/capture   - Capture screenshot with selection")
    print("- POST /api/screenshot/save      - Save screenshot image")
    print()
    
    return True

if __name__ == "__main__":
    demo_screenshot_tool()