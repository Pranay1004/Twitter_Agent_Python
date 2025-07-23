#!/usr/bin/env python3
"""
Image Preview Tool for DroneAgent
Displays all images that are going to be posted in a thread
"""

import sys
import json
import os
from pathlib import Path
from io import BytesIO
import requests

from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                            QWidget, QPushButton, QLabel, QScrollArea, 
                            QSplitter, QGridLayout, QGroupBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage, QFont

from agent.writer import ThreadWriter
from agent.visualizer import ImageVisualizer
from utils.logger import setup_logger

logger = setup_logger(__name__)

class ImagePreviewWindow(QMainWindow):
    def __init__(self, thread_data=None, topic=None):
        super().__init__()
        self.thread_data = thread_data
        self.topic = topic
        self.visualizer = ImageVisualizer()
        
        self.setWindowTitle("🖼️ DroneAgent - Thread Images Preview")
        self.setGeometry(100, 100, 1000, 800)
        
        # If no thread data provided but topic is, generate one
        if not self.thread_data and self.topic:
            writer = ThreadWriter()
            self.thread_data = writer.create_thread(self.topic)
        
        self.init_ui()
        
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Header
        header_label = QLabel("🖼️ Thread Images Preview")
        header_label.setFont(QFont("Arial", 16, QFont.Bold))
        header_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header_label)
        
        # Thread info
        if self.thread_data:
            info_label = QLabel(f"Topic: {self.thread_data.get('topic', 'Unknown')} | " +
                               f"Tweets: {len(self.thread_data.get('tweets', []))} | " +
                               f"Images: {len([t for t in self.thread_data.get('tweets', []) if t.get('needs_image', False)])}")
            main_layout.addWidget(info_label)
        
        # Scroll area for images
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        grid_layout = QGridLayout(scroll_widget)
        
        # Add images to grid
        if self.thread_data and self.thread_data.get('tweets'):
            tweets_with_images = [t for t in self.thread_data['tweets'] if t.get('needs_image', False)]
            
            # Button to generate all missing images
            if tweets_with_images:
                gen_all_btn = QPushButton("🔄 Generate All Missing Images")
                gen_all_btn.clicked.connect(self.generate_all_images)
                main_layout.addWidget(gen_all_btn)
            
            row = 0
            col = 0
            
            for i, tweet in enumerate(tweets_with_images):
                # Create image card
                image_card = self.create_image_card(tweet, i)
                
                # Add to grid
                grid_layout.addWidget(image_card, row, col)
                
                # Update grid position
                col += 1
                if col > 1:  # 2 images per row
                    col = 0
                    row += 1
        else:
            # No thread data
            no_data_label = QLabel("No thread data available. Please generate a thread first.")
            grid_layout.addWidget(no_data_label, 0, 0)
        
        scroll_area.setWidget(scroll_widget)
        main_layout.addWidget(scroll_area)
        
        # Bottom buttons
        button_layout = QHBoxLayout()
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        button_layout.addWidget(close_btn)
        
        main_layout.addLayout(button_layout)
    
    def create_image_card(self, tweet, index):
        """Create a card for displaying tweet and its image"""
        group = QGroupBox(f"Tweet #{index+1}")
        layout = QVBoxLayout(group)
        
        # Tweet text preview
        text_preview = tweet['text'][:150] + "..." if len(tweet['text']) > 150 else tweet['text']
        text_label = QLabel(text_preview)
        text_label.setWordWrap(True)
        text_label.setStyleSheet("background-color: #f5f5f5; padding: 8px; border-radius: 4px;")
        layout.addWidget(text_label)
        
        # Image
        image_box = QLabel("No image loaded")
        image_box.setAlignment(Qt.AlignCenter)
        image_box.setMinimumSize(400, 300)
        image_box.setStyleSheet("border: 1px solid #cccccc;")
        layout.addWidget(image_box)
        
        # Image info
        info_label = QLabel("Status: Not generated")
        layout.addWidget(info_label)
        
        # Generate button
        gen_btn = QPushButton("🔄 Generate Image")
        gen_btn.clicked.connect(lambda: self.generate_image(tweet, image_box, info_label))
        layout.addWidget(gen_btn)
        
        # If image already exists, display it
        if tweet.get('image') and tweet['image'].get('url'):
            self.display_image(tweet['image'], image_box, info_label)
        
        # Image
        image_path = tweet.get('image', {}).get('url')
        if image_path:
            image_path = os.path.normpath(image_path)
            if not os.path.exists(image_path):
                image_box.setText(f"Image not found: {image_path}")
                info_label.setText("Status: Image file missing")
                info_label.setStyleSheet("color: red;")
            else:
                pixmap = QPixmap(image_path)
                if not pixmap.isNull():
                    image_box.setPixmap(pixmap.scaled(400, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                    info_label.setText(f"Status: Image loaded\nSource: {tweet.get('image', {}).get('source', 'Unknown')}\nCredit: {tweet.get('image', {}).get('credit', 'None')}")
                    info_label.setStyleSheet("color: green;")
                else:
                    image_box.setText(f"Failed to load image: {image_path}")
                    info_label.setText("Status: Failed to load image")
                    info_label.setStyleSheet("color: red;")
        else:
            image_box.setText("No image available")
            info_label.setText("Status: Not generated")
            info_label.setStyleSheet("color: orange;")
        
        return group
    
    def generate_image(self, tweet, image_box, info_label):
        """Generate an image for a tweet"""
        try:
            info_label.setText("Status: Generating...")
            info_label.setStyleSheet("color: orange;")
            QApplication.processEvents()
            
            # Generate image
            image_data = self.visualizer.get_image(tweet['text'])
            
            if image_data:
                # Save image to tweet
                tweet['image'] = image_data
                
                # Display image
                self.display_image(image_data, image_box, info_label)
            else:
                info_label.setText("Status: Failed to generate image")
                info_label.setStyleSheet("color: red;")
        except Exception as e:
            info_label.setText(f"Status: Error - {str(e)[:50]}")
            info_label.setStyleSheet("color: red;")
    
    def generate_all_images(self):
        """Generate all missing images"""
        tweets_with_images = [t for t in self.thread_data['tweets'] if t.get('needs_image', False)]
        for i, tweet in enumerate(tweets_with_images):
            if not tweet.get('image'):
                # Find the corresponding card
                grid_layout = self.centralWidget().layout().itemAt(3).widget().widget().layout()
                row = i // 2
                col = i % 2
                
                image_card = grid_layout.itemAtPosition(row, col).widget()
                image_box = image_card.layout().itemAt(1).widget()
                info_label = image_card.layout().itemAt(2).widget()
                
                self.generate_image(tweet, image_box, info_label)
                QApplication.processEvents()
    
    def display_image(self, image_data, image_box, info_label):
        """Display an image on the image box"""
        try:
            if image_data.get('url'):
                # For placeholder images
                if 'placeholder' in image_data['url']:
                    image_box.setText("Placeholder Image")
                    info_label.setText(f"Status: Using placeholder image\nSource: Placeholder")
                    info_label.setStyleSheet("color: blue;")
                    return
                
                # Download and display the image
                response = requests.get(image_data['url'], stream=True, timeout=10)
                response.raise_for_status()
                
                # Save to file if we want to keep a local copy
                # filename = f"temp_image_{random.randint(1000, 9999)}.jpg"
                # with open(filename, 'wb') as f:
                #     f.write(response.content)
                
                # Convert to QPixmap
                from PIL import Image
                image = Image.open(BytesIO(response.content))
                
                # Convert PIL Image to QImage
                img = image.convert("RGBA")
                data = img.tobytes("raw", "RGBA")
                qimage = QImage(data, img.width, img.height, QImage.Format_RGBA8888)
                pixmap = QPixmap.fromImage(qimage)
                
                # Scale pixmap to fit label
                pixmap = pixmap.scaled(
                    image_box.width(), 
                    image_box.height(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                
                # Set pixmap to label
                image_box.setPixmap(pixmap)
                
                # Update info
                info_label.setText(f"Status: Image loaded\nSource: {image_data.get('source', 'Unknown')}\n" +
                                  f"Credit: {image_data.get('credit', 'None')}")
                info_label.setStyleSheet("color: green;")
        except Exception as e:
            info_label.setText(f"Status: Error displaying image - {str(e)[:50]}")
            info_label.setStyleSheet("color: red;")
        
        # Image
        image_path = tweet.get('image', {}).get('url')
        if image_path:
            image_path = os.path.normpath(image_path)
            if not os.path.exists(image_path):
                image_box.setText(f"Image not found: {image_path}")
                info_label.setText("Status: Image file missing")
                info_label.setStyleSheet("color: red;")
            else:
                pixmap = QPixmap(image_path)
                if not pixmap.isNull():
                    image_box.setPixmap(pixmap.scaled(400, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                    info_label.setText(f"Status: Image loaded\nSource: {tweet.get('image', {}).get('source', 'Unknown')}\nCredit: {tweet.get('image', {}).get('credit', 'None')}")
                    info_label.setStyleSheet("color: green;")
                else:
                    image_box.setText(f"Failed to load image: {image_path}")
                    info_label.setText("Status: Failed to load image")
                    info_label.setStyleSheet("color: red;")
        else:
            image_box.setText("No image available")
            info_label.setText("Status: Not generated")
            info_label.setStyleSheet("color: orange;")

def main():
    app = QApplication(sys.argv)
    
    # Check if a topic was provided
    topic = None
    if len(sys.argv) > 1:
        topic = sys.argv[1]
    
    # Try to load thread from file if it exists
    thread_data = None
    thread_file = Path("data/current_thread.json")
    
    if thread_file.exists():
        try:
            with open(thread_file, 'r') as f:
                thread_data = json.load(f)
        except:
            pass
    
    # Create and show window
    window = ImagePreviewWindow(thread_data, topic)
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
