#!/usr/bin/env python3
"""
Basic tests for the screenshot tool functionality
"""

import unittest
import sys
import os
import tempfile
from unittest.mock import patch, MagicMock

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from screenshot_tool import ScreenshotSelector, process_with_ai
from PIL import Image

class TestScreenshotTool(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.selector = ScreenshotSelector()
    
    def test_screenshot_selector_init(self):
        """Test ScreenshotSelector initialization"""
        self.assertIsNone(self.selector.root)
        self.assertIsNone(self.selector.canvas)
        self.assertIsNone(self.selector.screenshot)
        self.assertIsNone(self.selector.photo)
        self.assertEqual(self.selector.handles, [])
        self.assertFalse(self.selector.dragging)
        self.assertFalse(self.selector.resizing)
    
    def test_take_screenshot(self):
        """Test screenshot capture functionality"""
        screenshot = self.selector.take_screenshot()
        self.assertIsNotNone(screenshot)
        self.assertIsInstance(screenshot, Image.Image)
        self.assertEqual(screenshot.size, (800, 600))  # Test image size
        self.assertEqual(screenshot.mode, 'RGB')
    
    def test_capture_area(self):
        """Test area capture functionality"""
        # First take a screenshot
        self.selector.screenshot = self.selector.take_screenshot()
        
        # Test capturing a specific area
        coordinates = (100, 100, 300, 200)  # x1, y1, x2, y2
        captured = self.selector.capture_area(coordinates)
        
        self.assertIsNotNone(captured)
        self.assertIsInstance(captured, Image.Image)
        self.assertEqual(captured.size, (200, 100))  # width=300-100, height=200-100
    
    def test_save_image(self):
        """Test image saving functionality"""
        # Create a test image
        test_image = Image.new('RGB', (100, 100), color='red')
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            success = self.selector.save_image(test_image, tmp_file.name)
            self.assertTrue(success)
            self.assertTrue(os.path.exists(tmp_file.name))
            
            # Verify the saved image
            saved_image = Image.open(tmp_file.name)
            self.assertEqual(saved_image.size, (100, 100))
            
            # Clean up
            os.unlink(tmp_file.name)
    
    def test_process_with_ai(self):
        """Test AI processing placeholder"""
        test_image = Image.new('RGB', (100, 100), color='blue')
        result = process_with_ai(test_image)
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result['status'], 'processed')
        self.assertEqual(result['description'], 'AI processing completed')
    
    def test_invalid_coordinates(self):
        """Test capture with invalid coordinates"""
        self.selector.screenshot = self.selector.take_screenshot()
        
        # Test with None coordinates
        result = self.selector.capture_area(None)
        self.assertIsNone(result)
        
        # Test with empty coordinates
        result = self.selector.capture_area([])
        self.assertIsNone(result)

class TestFlaskIntegration(unittest.TestCase):
    
    def test_flask_app_import(self):
        """Test that Flask app can be imported with screenshot functionality"""
        try:
            import app
            self.assertTrue(hasattr(app, 'SCREENSHOT_AVAILABLE'))
            self.assertTrue(app.SCREENSHOT_AVAILABLE)
        except ImportError as e:
            self.fail(f"Failed to import Flask app: {e}")

if __name__ == '__main__':
    # Run tests
    print("Running Screenshot Tool Tests...")
    unittest.main(verbosity=2)