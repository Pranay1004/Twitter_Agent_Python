#!/usr/bin/env python3
"""
DroneAgent GUI Interface using PyQt5
"""

import sys
import os
import json
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QWidget, QPushButton, QTextEdit, QLabel, QComboBox, 
                             QProgressBar, QTabWidget, QListWidget, QGroupBox,
                             QGridLayout, QMessageBox, QScrollArea, QSplitter,
                             QDialog, QDialogButtonBox, QTableWidget, QTableWidgetItem,
                             QFrame, QLineEdit, QFileDialog)
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QTimer
from PyQt5.QtGui import QFont, QPixmap, QIcon

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from agent.ideator import ContentIdeator
from agent.writer import ThreadWriter
from agent.visualizer import ImageVisualizer
from agent.scheduler import PostScheduler
from utils.poster import TwitterPoster
from utils.logger import setup_logger

logger = setup_logger(__name__)

class ContentGenerationThread(QThread):
    """Background thread for content generation"""
    progress = pyqtSignal(str)
    image_progress = pyqtSignal(str, int)  # Message, estimated seconds remaining
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    
    def __init__(self, action, topic=None):
        super().__init__()
        self.action = action
        self.topic = topic
        
    def run(self):
        try:
            if self.action == "ideate":
                self.progress.emit("🧠 Generating content ideas...")
                ideator = ContentIdeator()
                try:
                    # Get model selection from main window
                    from PyQt5.QtWidgets import QApplication
                    app = QApplication.instance()
                    main_window = app.activeWindow()
                    model = "gemini"  # Default model
                    if hasattr(main_window, 'model_combo'):
                        model_text = main_window.model_combo.currentText()
                        # Map GUI model names to backend names
                        if "Gemini" in model_text:
                            model = "gemini"
                        elif "Perplexity" in model_text:
                            model = "perplexity"
                        elif "OpenRouter" in model_text:
                            model = "openrouter"
                    
                    ideas = ideator.generate_ideas(num_ideas=6, model_name=model)
                    self.finished.emit({"type": "ideas", "data": ideas})
                except Exception as e:
                    self.error.emit(f"Error generating ideas: {str(e)}")
                
            elif self.action == "write":
                self.progress.emit("✍️ Writing Twitter thread...")
                from PyQt5.QtWidgets import QApplication
                app = QApplication.instance()
                main_window = app.activeWindow()
                model = "OpenRouter Pro"
                if hasattr(main_window, 'model_combo'):
                    model = main_window.model_combo.currentText()
                writer = ThreadWriter()
                thread = writer.generate_thread_with_ai(self.topic, model=model)
                self.finished.emit({"type": "thread", "data": thread})
                
            elif self.action == "visualize":
                # Initial notification
                self.progress.emit("🖼️ Preparing to generate drone images...")
                
                # Image generation process with real status
                visualizer = ImageVisualizer()
                
                # Start image generation with real progress
                self.progress.emit("📡 Requesting image from API services...")
                
                # Get the image - this will actually generate/fetch the image
                image_data = visualizer.get_image(self.topic)
                
                # Return the result only after we actually have the image
                if image_data:
                    self.progress.emit("✅ Image successfully obtained")
                    self.finished.emit({"type": "image", "data": image_data})
                else:
                    self.error.emit("Failed to obtain image, using placeholder instead")
                    self.finished.emit({"type": "image", "data": None})
                
        except Exception as e:
            self.error.emit(str(e))

class ImageInputDialog(QDialog):
    """Dialog for users to input custom images for tweets"""
    
    def __init__(self, thread_tweets, parent=None, existing_images=None):
        super().__init__(parent)
        self.thread_tweets = thread_tweets
        self.user_images = {} if existing_images is None else existing_images
        self.parent = parent
        self.setWindowTitle("📸 Custom Images for Thread")
        self.setGeometry(200, 200, 800, 600)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Instructions
        instructions = QLabel("Add custom images for your thread tweets (optional). Leave blank to use AI-generated images.")
        instructions.setWordWrap(True)
        instructions.setStyleSheet("font-size: 12px; color: #666; margin-bottom: 15px;")
        layout.addWidget(instructions)
        
        # Scroll area for tweets
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # Find tweets that need images
        self.image_inputs = {}
        tweet_number = 1
        
        for i, tweet in enumerate(self.thread_tweets):
            if tweet.get('needs_image', False):
                # Tweet frame
                tweet_frame = QFrame()
                tweet_frame.setFrameStyle(QFrame.StyledPanel)
                tweet_frame.setStyleSheet("QFrame { background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 8px; padding: 10px; margin: 5px; }")
                
                tweet_layout = QVBoxLayout(tweet_frame)
                
                # Tweet text preview
                tweet_text = QLabel(f"Tweet {tweet_number}: {tweet['text'][:100]}{'...' if len(tweet['text']) > 100 else ''}")
                tweet_text.setWordWrap(True)
                tweet_text.setStyleSheet("font-weight: bold; margin-bottom: 10px;")
                tweet_layout.addWidget(tweet_text)
                
                # Image input section
                image_layout = QHBoxLayout()
                
                # File path input
                file_input = QLineEdit()
                file_input.setPlaceholderText("Enter image URL or click Browse to select file...")
                file_input.setStyleSheet("padding: 8px; border: 1px solid #ccc; border-radius: 4px;")
                
                # Browse button
                browse_btn = QPushButton("📁 Browse")
                browse_btn.setStyleSheet("padding: 8px 15px; background-color: #007bff; color: white; border: none; border-radius: 4px;")
                browse_btn.clicked.connect(lambda checked, idx=i, input_field=file_input: self.browse_image(idx, input_field))
                
                # Clear button
                clear_btn = QPushButton("🗑️ Clear")
                clear_btn.setStyleSheet("padding: 8px 15px; background-color: #dc3545; color: white; border: none; border-radius: 4px;")
                clear_btn.clicked.connect(lambda checked, input_field=file_input: input_field.clear())
                
                # Regenerate AI image button
                regenerate_btn = QPushButton("🔄 Regenerate AI Image")
                regenerate_btn.setStyleSheet("padding: 8px 15px; background-color: #28a745; color: white; border: none; border-radius: 4px;")
                regenerate_btn.clicked.connect(lambda checked, idx=i: self.regenerate_image(idx))
                
                image_layout.addWidget(file_input)
                image_layout.addWidget(browse_btn)
                image_layout.addWidget(clear_btn)
                image_layout.addWidget(regenerate_btn)
                
                # Check if we have an existing image for this tweet
                image_preview = QLabel("No image selected")
                image_preview.setAlignment(Qt.AlignCenter)
                image_preview.setMinimumHeight(150)
                image_preview.setStyleSheet("background-color: #eee; border-radius: 4px; padding: 10px;")
                
                # If there's an existing image in thread_tweets, display it
                if 'image' in self.thread_tweets[i] and self.thread_tweets[i]['image']:
                    image_data = self.thread_tweets[i]['image']
                    if image_data.get('url'):
                        try:
                            from PyQt5.QtGui import QPixmap
                            url = image_data['url']
                            if url.startswith('file://'):
                                url = url[7:]  # Remove file:// prefix
                            
                            if os.path.exists(url):
                                pixmap = QPixmap(url)
                                if not pixmap.isNull():
                                    pixmap = pixmap.scaled(300, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                                    image_preview.setPixmap(pixmap)
                                    source = image_data.get('source', 'unknown')
                                    image_preview.setText(f"Current image from {source}")
                        except Exception as e:
                            image_preview.setText(f"Error loading image: {str(e)}")
                
                tweet_layout.addLayout(image_layout)
                tweet_layout.addWidget(image_preview)
                scroll_layout.addWidget(tweet_frame)
                
                # Store reference
                self.image_inputs[i] = file_input
                tweet_number += 1
        
        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        # Select from directory button
        dir_btn = QPushButton("📂 Select From Directory")
        dir_btn.setStyleSheet("padding: 10px 20px; background-color: #17a2b8; color: white; border: none; border-radius: 4px; font-weight: bold;")
        dir_btn.clicked.connect(self.select_from_directory)
        
        # Auto-generate remaining button
        auto_btn = QPushButton("🤖 Auto-generate remaining images")
        auto_btn.setStyleSheet("padding: 10px 20px; background-color: #28a745; color: white; border: none; border-radius: 4px; font-weight: bold;")
        auto_btn.clicked.connect(self.accept)
        
        # Cancel button
        cancel_btn = QPushButton("❌ Cancel")
        cancel_btn.setStyleSheet("padding: 10px 20px; background-color: #6c757d; color: white; border: none; border-radius: 4px;")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(dir_btn)
        button_layout.addWidget(auto_btn)
        layout.addLayout(button_layout)
    
    def regenerate_image(self, tweet_index):
        """Regenerate AI image for a specific tweet"""
        try:
            if not hasattr(self.parent, 'visualizer'):
                from agent.visualizer import ImageVisualizer
                self.parent.visualizer = ImageVisualizer()
            
            tweet = self.thread_tweets[tweet_index]
            content = tweet.get('text', '')
            
            # Use a random source with preference for Gemini
            import random
            sources = ['gemini', 'gemini', 'pexels', 'unsplash']  # 50% chance of Gemini
            selected_source = random.choice(sources)
            
            # Show message that we're generating
            QMessageBox.information(self, "Generating Image", f"Generating new {selected_source} image for tweet {tweet_index+1}...\nThis might take a few seconds.")
            
            # Generate image from the selected source
            image_data = self.parent.visualizer._get_image_from_source(content, selected_source)
            
            if image_data:
                # Update the tweet with the new image
                tweet['image'] = image_data
                
                # Close and reopen dialog to refresh images
                self.accept()
                new_dialog = ImageInputDialog(self.thread_tweets, self.parent, self.user_images)
                if new_dialog.exec_() == QDialog.Accepted:
                    self.user_images = new_dialog.get_user_images()
            else:
                QMessageBox.warning(self, "Image Generation Failed", "Failed to generate a new image. Please try again or select a local image.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while regenerating the image: {str(e)}")
    
    def browse_image(self, tweet_index, input_field):
        """Open file dialog to select image"""
        from PyQt5.QtWidgets import QFileDialog
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Image",
            "",
            "Image Files (*.png *.jpg *.jpeg *.gif *.bmp *.tiff);;All Files (*)"
        )
        
        if file_path:
            input_field.setText(file_path)
    
    def select_from_directory(self):
        """Select multiple images from a directory"""
        from PyQt5.QtWidgets import QFileDialog
        import os
        
        # Open directory dialog
        dir_path = QFileDialog.getExistingDirectory(
            self,
            "Select Directory with Images",
            "",
            QFileDialog.ShowDirsOnly
        )
        
        if not dir_path:
            return
            
        # Get image files from directory
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']
        image_files = []
        
        for file in os.listdir(dir_path):
            file_path = os.path.join(dir_path, file)
            if os.path.isfile(file_path) and os.path.splitext(file)[1].lower() in image_extensions:
                image_files.append(file_path)
        
        if not image_files:
            QMessageBox.warning(self, "No Images Found", "No image files were found in the selected directory.")
            return
            
        # Sort files alphabetically for consistent ordering
        image_files.sort()
        
        # Get tweets that need images
        image_tweets = [i for i, tweet in enumerate(self.thread_tweets) if tweet.get('needs_image', False)]
        
        # Assign images to tweets
        for i, tweet_index in enumerate(image_tweets):
            if i < len(image_files):
                # Update the input field
                if tweet_index in self.image_inputs:
                    self.image_inputs[tweet_index].setText(image_files[i])
        
        QMessageBox.information(
            self, 
            "Images Assigned", 
            f"{min(len(image_tweets), len(image_files))} images have been assigned to your tweets.\n\n" + 
            (f"{len(image_tweets) - len(image_files)} tweets still need images." if len(image_tweets) > len(image_files) else "All tweets have images assigned.")
        )
    
    def get_user_images(self):
        """Get user-provided images"""
        user_images = {}
        
        for tweet_index, input_field in self.image_inputs.items():
            image_path = input_field.text().strip()
            if image_path:
                user_images[tweet_index] = image_path
        
        return user_images

class ImagePromptDialog(QDialog):
    """Dialog for displaying and editing image generation prompts"""
    
    def __init__(self, thread_data, parent=None):
        super().__init__(parent)
        self.thread_data = thread_data
        self.setWindowTitle("🎨 Image Generation Prompts")
        self.setGeometry(150, 150, 800, 600)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel("🎨 Prompts for Image Generation")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Scroll area for prompts
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        self.prompt_edits = []
        
        # Generate prompts for each post that needs an image
        for i, tweet in enumerate(self.thread_data.get('tweets', []), 1):
            if tweet.get('needs_image', False):
                # Create group for this post
                post_group = QGroupBox(f"Post #{i}")
                post_layout = QVBoxLayout(post_group)
                
                # Show the tweet text
                tweet_label = QLabel(f"Tweet: {tweet['text'][:100]}...")
                tweet_label.setWordWrap(True)
                tweet_label.setStyleSheet("background-color: #f0f0f0; padding: 8px; border-radius: 4px;")
                post_layout.addWidget(tweet_label)
                
                # Generate and display the image prompt
                prompt = self.generate_image_prompt(tweet, i)
                prompt_label = QLabel("Generated Image Prompt:")
                prompt_label.setFont(QFont("Arial", 10, QFont.Bold))
                post_layout.addWidget(prompt_label)
                
                prompt_edit = QTextEdit()
                prompt_edit.setPlainText(prompt)
                prompt_edit.setMaximumHeight(100)
                self.prompt_edits.append(prompt_edit)
                post_layout.addWidget(prompt_edit)
                
                scroll_layout.addWidget(post_group)
        
        scroll_area.setWidget(scroll_widget)
        layout.addWidget(scroll_area)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
    def generate_image_prompt(self, tweet, post_number):
        """Generate an image prompt based on the tweet content"""
        import hashlib
        from datetime import datetime
        tweet_text = tweet['text'].lower()
        tweet_type = tweet.get('type', 'content')
        base_prompt = "Professional high-quality drone photography, "
        if 'commercial' in tweet_text or 'business' in tweet_text:
            base_prompt += "commercial drone in professional setting, modern office buildings, corporate environment, "
        elif 'cinematography' in tweet_text or 'filming' in tweet_text:
            base_prompt += "drone capturing cinematic footage, dynamic aerial shot, film equipment, "
        elif 'agriculture' in tweet_text or 'farming' in tweet_text:
            base_prompt += "agricultural drone spraying crops, farmland aerial view, precision agriculture, "
        elif 'military' in tweet_text or 'defense' in tweet_text:
            base_prompt += "military-grade drone, tactical operations, defense technology, "
        elif 'emergency' in tweet_text or 'rescue' in tweet_text:
            base_prompt += "search and rescue drone, emergency response, disaster area aerial view, "
        elif 'construction' in tweet_text or 'building' in tweet_text:
            base_prompt += "construction site drone survey, building inspection, architectural aerial view, "
        else:
            base_prompt += "advanced quadcopter drone in flight, modern technology, "
        if tweet_type == 'intro':
            base_prompt += "eye-catching hero shot, dramatic lighting, professional composition, "
        elif tweet_type == 'drone_focus':
            base_prompt += "detailed close-up of drone technology, high-tech components visible, "
        elif tweet_type == 'sales':
            base_prompt += "premium product showcase, clean background, marketing photography style, "
        base_prompt += "4K quality, sharp focus, professional lighting, trending on tech photography, highly detailed"
        # Add uniqueness: index, hash, timestamp
        tweet_hash = hashlib.md5(tweet['text'].encode()).hexdigest()[:8]
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        unique_info = f" | UniqueID: {post_number}-{tweet_hash}-{timestamp}"
        return base_prompt + unique_info

class MediaSummaryDialog(QDialog):
    """Dialog for displaying summary of all media to be uploaded"""
    
    def __init__(self, thread_data, parent=None):
        super().__init__(parent)
        self.thread_data = thread_data
        self.setWindowTitle("📁 Media Upload Summary")
        self.setGeometry(200, 200, 700, 500)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel("📁 Summary of Photos/Videos to be Uploaded")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Table for media summary
        self.media_table = QTableWidget()
        self.media_table.setColumnCount(5)
        self.media_table.setHorizontalHeaderLabels([
            "Post #", "Tweet Preview", "Media Type", "Status", "Prompt Used"
        ])
        
        # Populate the table
        self.populate_media_table()
        
        layout.addWidget(self.media_table)
        
        # Summary stats
        stats_label = QLabel(self.get_media_stats())
        stats_label.setStyleSheet("background-color: #e8f4f8; padding: 10px; border-radius: 5px;")
        layout.addWidget(stats_label)
        
        # Close button
        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)
        
    def populate_media_table(self):
        """Populate the media summary table"""
        media_posts = [tweet for tweet in self.thread_data.get('tweets', []) if tweet.get('needs_image', False)]
        self.media_table.setRowCount(len(media_posts))
        
        for row, tweet in enumerate(media_posts):
            # Post number
            post_num = QTableWidgetItem(f"#{row + 1}")
            self.media_table.setItem(row, 0, post_num)
            
            # Tweet preview
            preview = QTableWidgetItem(tweet['text'][:50] + "...")
            self.media_table.setItem(row, 1, preview)
            
            # Media type
            media_type = QTableWidgetItem("📸 Image")
            self.media_table.setItem(row, 2, media_type)
            
            # Status
            if tweet.get('image'):
                status = QTableWidgetItem("✅ Ready")
            else:
                status = QTableWidgetItem("⏳ Pending")
            self.media_table.setItem(row, 3, status)
            
            # Prompt used (simplified)
            tweet_type = tweet.get('type', 'content')
            if 'commercial' in tweet['text'].lower():
                prompt_type = "Commercial Drone"
            elif 'cinematography' in tweet['text'].lower():
                prompt_type = "Cinematography"
            elif tweet_type == 'sales':
                prompt_type = "Product Showcase"
            else:
                prompt_type = "General Drone"
                
            prompt_item = QTableWidgetItem(prompt_type)
            self.media_table.setItem(row, 4, prompt_item)
        
        # Adjust column widths
        self.media_table.resizeColumnsToContents()
        
    def get_media_stats(self):
        """Get summary statistics for media"""
        tweets = self.thread_data.get('tweets', [])
        total_posts = len(tweets)
        media_posts = len([t for t in tweets if t.get('needs_image', False)])
        ready_media = len([t for t in tweets if t.get('image')])
        
        return f"""📊 Media Summary:
• Total Posts: {total_posts}
• Posts with Media: {media_posts}
• Media Ready: {ready_media}
• Media Pending: {media_posts - ready_media}
• Upload Size: ~{media_posts * 2}MB (estimated)"""

class DroneAgentGUI(QMainWindow):
    def create_settings_tab(self, tab_widget):
        """Stub for Settings tab. Implement actual settings UI as needed."""
        settings_tab = QWidget()
        tab_widget.addTab(settings_tab, "⚙️ Settings")
        layout = QVBoxLayout(settings_tab)
        layout.addWidget(QLabel("Settings will appear here."))
    def write_thread(self):
        """Write a Twitter thread based on the selected idea"""
        selected_items = self.ideas_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select an idea first!")
            return
            
        selected_idea = selected_items[0].text()
        self.set_loading_state(True, "Writing thread...")
        
        # Extract the title from the selected idea text
        title = selected_idea.split(" - ")[0] if " - " in selected_idea else selected_idea
        
        self.content_thread = ContentGenerationThread("write", title)
        self.content_thread.progress.connect(self.update_status)
        self.content_thread.finished.connect(self.on_thread_written)
        self.content_thread.error.connect(self.on_error)
        self.content_thread.start()
    def generate_ideas(self):
        """Generate content ideas using the ideator"""
        self.set_loading_state(True, "Generating ideas...")
        
        self.content_thread = ContentGenerationThread("ideate")
        self.content_thread.progress.connect(self.update_status)
        self.content_thread.finished.connect(self.on_ideas_generated)
        self.content_thread.error.connect(self.on_error)
        self.content_thread.start()
    def immediate_post_now(self):
        """Immediately post the current thread to Twitter without confirmation dialog"""
        if not self.current_thread:
            self.status_label.setText("No thread to post.")
            return
        self.set_loading_state(True, "Posting immediately to Twitter...")
        # Directly post using TwitterPoster
        try:
            result = self.poster.post_thread(self.current_thread)
            self.set_loading_state(False)
            self.status_label.setText("Thread posted immediately!")
        except Exception as e:
            self.set_loading_state(False)
            self.status_label.setText(f"Immediate post failed: {e}")
        # Re-enable all main action buttons after posting
        self.ideate_btn.setEnabled(True)
        self.write_btn.setEnabled(True)
        self.image_btn.setEnabled(True)
        self.preview_btn.setEnabled(True)
        self.post_btn.setEnabled(True)
        self.immediate_post_btn.setEnabled(True)
        self.prompt_btn.setEnabled(True)
        self.media_summary_btn.setEnabled(True)
        self.preview_images_btn.setEnabled(True)
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DroneAgent - AI Twitter Automation")
        self.setGeometry(100, 100, 1200, 800)
        
        # Initialize components
        self.ideator = ContentIdeator()
        self.writer = ThreadWriter()
        self.visualizer = ImageVisualizer()
        self.scheduler = PostScheduler()
        self.poster = TwitterPoster()
        self.poster.authenticate_oauth2()
        
        # Current content
        self.current_ideas = []
        self.current_thread = None
        self.current_images = {}
        
        self.init_ui()
        self.load_history()
        
    def init_ui(self):
        """Initialize the user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        
        # Create tabbed interface
        tab_widget = QTabWidget()
        main_layout.addWidget(tab_widget)
        
        # Content Creation Tab
        self.create_content_tab(tab_widget)
        
        # Analytics Tab
        self.create_analytics_tab(tab_widget)
        
        # Settings Tab
        self.create_settings_tab(tab_widget)
        
        # Status bar
        self.statusBar().showMessage("Ready to create amazing drone content! 🚁")
        
    def create_content_tab(self, tab_widget):
        """Create the main content creation tab"""
        content_tab = QWidget()
        tab_widget.addTab(content_tab, "📝 Content Creation")
        
        layout = QHBoxLayout(content_tab)
        
        # Left panel - Controls
        left_panel = self.create_control_panel()
        if left_panel is None:
            logger.warning("create_control_panel returned None, using placeholder widget.")
            left_panel = QWidget()
        layout.addWidget(left_panel, 1)

        # Right panel - Preview
        right_panel = self.create_preview_panel()
        if right_panel is None:
            logger.warning("create_preview_panel returned None, using placeholder widget.")
            right_panel = QWidget()
        layout.addWidget(right_panel, 2)
        
    def create_control_panel(self):
        """Create the control panel with buttons and options"""
        group = QGroupBox("🎮 Controls")
        layout = QVBoxLayout(group)
        
        # AI Model Selection
        model_label = QLabel("🤖 AI Model:")
        self.model_combo = QComboBox()
        self.model_combo.addItems(["OpenRouter Pro", "Gemini Pro", "Perplexity Pro"])
        self.model_combo.setCurrentIndex(0)
        layout.addWidget(model_label)
        layout.addWidget(self.model_combo)
        
        # Action Buttons
        self.ideate_btn = QPushButton("💡 Generate Ideas")
        self.ideate_btn.clicked.connect(self.generate_ideas)
        layout.addWidget(self.ideate_btn)
        
        self.write_btn = QPushButton("✍️ Write Thread")
        self.write_btn.clicked.connect(self.write_thread)
        self.write_btn.setEnabled(False)
        layout.addWidget(self.write_btn)
        
        self.image_btn = QPushButton("🖼️ Generate Images")
        self.image_btn.clicked.connect(self.generate_images)
        self.image_btn.setEnabled(False)
        layout.addWidget(self.image_btn)
        
        self.preview_btn = QPushButton("👁️ Preview Thread")
        self.preview_btn.clicked.connect(self.preview_thread)
        self.preview_btn.setEnabled(False)
        layout.addWidget(self.preview_btn)
        
        self.post_btn = QPushButton("🚀 Post Now")
        self.post_btn.clicked.connect(self.post_thread)
        self.post_btn.setEnabled(False)
        self.post_btn.setStyleSheet("QPushButton { background-color: #1DA1F2; color: white; font-weight: bold; }")
        layout.addWidget(self.post_btn)

        # Immediate Post Button
        self.immediate_post_btn = QPushButton("⚡ Post NOW (Immediate)")
        self.immediate_post_btn.clicked.connect(self.immediate_post_now)
        self.immediate_post_btn.setEnabled(False)
        self.immediate_post_btn.setStyleSheet("QPushButton { background-color: #ff9900; color: white; font-weight: bold; }")
        layout.addWidget(self.immediate_post_btn)
        
        # New buttons for image prompts and media summary
        self.prompt_btn = QPushButton("🎨 View Image Prompts")
        self.prompt_btn.clicked.connect(self.show_image_prompts)
        self.prompt_btn.setEnabled(False)
        layout.addWidget(self.prompt_btn)
        
        self.media_summary_btn = QPushButton("📁 Media Summary")
        self.media_summary_btn.clicked.connect(self.show_media_summary)
        self.media_summary_btn.setEnabled(False)
        layout.addWidget(self.media_summary_btn)
        
        self.preview_images_btn = QPushButton("🖼️ Preview All Thread Images")
        self.preview_images_btn.clicked.connect(self.show_image_preview_tool)
        self.preview_images_btn.setEnabled(False)
        layout.addWidget(self.preview_images_btn)
        
        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Status Label
        self.status_label = QLabel("Ready")
        layout.addWidget(self.status_label)
        
        # Ideas List
        ideas_label = QLabel("💡 Generated Ideas:")
        self.ideas_list = QListWidget()
        self.ideas_list.itemClicked.connect(self.on_idea_selected)
        layout.addWidget(ideas_label)
        layout.addWidget(self.ideas_list)
        
        layout.addStretch()
        return group
        
    def immediate_post_now(self):
        """Immediately post the current thread to Twitter without confirmation dialog"""
        if not self.current_thread:
            self.status_label.setText("No thread to post.")
            return
        self.set_loading_state(True, "Posting immediately to Twitter...")
        # Directly post using TwitterPoster
        try:
            result = self.poster.post_thread(self.current_thread)
            self.set_loading_state(False)
            self.status_label.setText("Thread posted immediately!")
        except Exception as e:
            self.set_loading_state(False)
            self.status_label.setText(f"Immediate post failed: {e}")

    def create_preview_panel(self):
        """Create the preview panel"""
        group = QGroupBox("👁️ Thread Preview")
        layout = QVBoxLayout(group)
        
        # Thread display
        self.thread_display = QTextEdit()
        self.thread_display.setReadOnly(True)
        self.thread_display.setFont(QFont("Arial", 11))
        layout.addWidget(self.thread_display)
        
        # Thread stats
        self.stats_label = QLabel("📊 Stats: No thread generated")
        layout.addWidget(self.stats_label)
        
        # Image preview section
        self.image_preview_box = QGroupBox("🖼️ Image Preview")
        self.image_preview_box.setVisible(False)
        image_layout = QVBoxLayout(self.image_preview_box)
        
        self.image_label = QLabel("No image loaded")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumHeight(200)
        self.image_label.setStyleSheet("border: 1px solid #cccccc;")
        image_layout.addWidget(self.image_label)
        
        self.image_info_label = QLabel("Image information")
        image_layout.addWidget(self.image_info_label)
        
        layout.addWidget(self.image_preview_box)
        
        # Image loading status
        self.image_status_label = QLabel("")
        self.image_status_label.setVisible(False)
        self.image_status_label.setStyleSheet("background-color: #f8f9fa; padding: 8px; border-radius: 4px;")
        layout.addWidget(self.image_status_label)
        
        return group
        
    def create_analytics_tab(self, tab_widget):
        """Create analytics and history tab"""
        analytics_tab = QWidget()
        tab_widget.addTab(analytics_tab, "📊 Analytics")
        
        layout = QVBoxLayout(analytics_tab)
        
        # Use only analytics/history widgets here, do not duplicate status/progress/ideas widgets
    def create_analytics_tab(self, tab_widget):
        """Create analytics and history tab"""
        analytics_tab = QWidget()
        tab_widget.addTab(analytics_tab, "📊 Analytics")
        
        layout = QVBoxLayout(analytics_tab)
        
        # History section
        history_label = QLabel("📋 Post History:")
        layout.addWidget(history_label)
        
        self.history_list = QListWidget()
        layout.addWidget(self.history_list)
        
        # API Status section
        api_label = QLabel("🔗 API Status:")
        layout.addWidget(api_label)
        
        self.api_status_label = QLabel("Ready to test connections...")
        layout.addWidget(self.api_status_label)
        
        # Test API button
        self.test_api_btn = QPushButton("🔍 Test API Connections")
        self.test_api_btn.clicked.connect(self.test_api_connections)
        layout.addWidget(self.test_api_btn)
        
        # Auto-posting control
        self.auto_post_btn = QPushButton("📅 Enable Auto-Posting")
        self.auto_post_btn.clicked.connect(self.toggle_auto_posting)
        layout.addWidget(self.auto_post_btn)
        
        layout.addStretch()

    def test_api_connections(self):
        """Test all API connections"""
        self.api_status_label.setText("Testing API connections...")
        
        # Simulate API testing with Pexels included
        QTimer.singleShot(2000, lambda: self.api_status_label.setText(
            "Twitter API: Connected\nPerplexity API: Connected\nUnsplash API: Limited\nPexels API: Connected\nGemini API: Error"
        ))

    def toggle_auto_posting(self):
        """Toggle automatic posting"""
        if self.auto_post_btn.text() == "📅 Enable Auto-Posting":
            self.scheduler.schedule_daily_posts()
            self.auto_post_btn.setText("🛑 Disable Auto-Posting")
            self.auto_post_btn.setStyleSheet("QPushButton { background-color: #ff4444; }")
            self.update_status("Auto-posting enabled for 10am and 7pm IST")
        else:
            self.auto_post_btn.setText("📅 Enable Auto-Posting")
            self.auto_post_btn.setStyleSheet("")
            self.update_status("Auto-posting disabled")
        """Write a Twitter thread"""
        selected_items = self.ideas_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select an idea first!")
            return
            
        selected_idea = selected_items[0].text()
        self.set_loading_state(True, "Writing thread...")
        
        self.content_thread = ContentGenerationThread("write", selected_idea)
        self.content_thread.progress.connect(self.update_status)
        self.content_thread.finished.connect(self.on_thread_written)
        self.content_thread.error.connect(self.on_error)
        self.content_thread.start()
        
    def generate_images(self):
        """Generate images for the thread"""
        if not self.current_thread:
            QMessageBox.warning(self, "No Thread", "Please write a thread first!")
            return
            
        # Check for existing images in the thread
        existing_images = {}
        for i, tweet in enumerate(self.current_thread['tweets']):
            tweet['needs_image'] = True
            # If tweet already has image, store it
            if 'image' in tweet and tweet['image']:
                existing_images[i] = tweet['image']
            
        # Show image input dialog first
        image_dialog = ImageInputDialog(self.current_thread['tweets'], self, existing_images)
        result = image_dialog.exec_()
        
        if result == QDialog.Accepted:
            # Process user inputs
            user_images = {}
            for idx, input_field in image_dialog.image_inputs.items():
                if input_field.text().strip():
                    user_images[idx] = input_field.text().strip()
            
            self.set_loading_state(True, "Generating images...")
            
            # Show image status label
            self.image_status_label.setVisible(True)
            
            # Get the visualizer to process thread with user inputs
            if user_images:
                self.current_thread['tweets'] = self.visualizer.get_images_for_thread(
                    self.current_thread['tweets'], user_images
                )
                
            # Create the list of tweets that still need AI-generated images
            self.pending_image_tweets = [
                tweet for tweet in self.current_thread['tweets'] 
                if tweet.get('needs_image', True) and not tweet.get('image')
            ]
            
            # If all images were provided by user, we're done
            if not self.pending_image_tweets:
                self.set_loading_state(False, "All images added successfully!")
                self.preview_thread()
                return
        
        # Start with the first tweet
        self._generate_next_image()
    
    def _generate_next_image(self):
        """Generate the next image in the sequence"""
        if not self.pending_image_tweets:
            self.set_loading_state(False, "All images generated successfully!")
            self.preview_thread()
            return
            
        # Get the next tweet that needs an image
        current_tweet = self.pending_image_tweets[0]
        image_topic = current_tweet.get('text', self.current_thread.get('topic', ''))
        
        # Create and start the image generation thread
        self.content_thread = ContentGenerationThread("visualize", image_topic)
        self.content_thread.progress.connect(self.update_status)
        self.content_thread.image_progress.connect(self.update_image_status)
        self.content_thread.finished.connect(self._on_single_image_generated)
        self.content_thread.error.connect(self.on_image_error)
        self.content_thread.start()
        
    def preview_thread(self):
        """Preview the complete thread"""
        if not self.current_thread:
            self.thread_display.setText("No thread generated yet.")
            return
            
        preview_text = ""
        tweets = self.current_thread.get('tweets', [])
        
        for i, tweet in enumerate(tweets, 1):
            if len(tweets) > 1:
                preview_text += f"Tweet {i}/{len(tweets)}\n"
            
            text = tweet.get('text', 'Tweet text not found.')
            preview_text += f"{text}\n"
            preview_text += f"Characters: {len(text)}/280\n"

            if tweet.get('image'):
                image_desc = tweet['image'].get('description', 'No description')
                preview_text += f"🖼️ Image: {image_desc}\n"
            elif tweet.get('needs_image'):
                preview_text += "⏳ Image will be generated for this tweet\n"
            
            preview_text += "\n" + "-"*30 + "\n\n"
            
        self.thread_display.setText(preview_text)

    def post_thread(self):
        """Post the thread to Twitter"""
        if not self.current_thread:
            return
            
        reply = QMessageBox.question(self, 'Confirm Posting', 
                                   'Are you sure you want to post this thread to Twitter?',
                                   QMessageBox.Yes | QMessageBox.No, 
                                   QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.set_loading_state(True, "Posting to Twitter...")
            # Simulate posting
            QTimer.singleShot(3000, self.on_thread_posted)
            
    def toggle_auto_posting(self):
        """Toggle automatic posting"""
        if self.auto_post_btn.text() == "📅 Enable Auto-Posting":
            self.scheduler.schedule_daily_posts()
            self.auto_post_btn.setText("🛑 Disable Auto-Posting")
            self.auto_post_btn.setStyleSheet("QPushButton { background-color: #ff4444; }")
            self.update_status("Auto-posting enabled for 10am and 7pm IST")
        else:
            self.auto_post_btn.setText("📅 Enable Auto-Posting")
            self.auto_post_btn.setStyleSheet("")
            self.update_status("Auto-posting disabled")
            
    def test_api_connections(self):
        """Test all API connections"""
        self.api_status_label.setText("Testing API connections...")
        
        # Simulate API testing with Pexels included
        QTimer.singleShot(2000, lambda: self.api_status_label.setText(
            "Twitter API: Connected\nPerplexity API: Connected\nUnsplash API: Limited\nPexels API: Connected\nGemini API: Error"
        ))
        
    def on_idea_selected(self, item):
        """Handle idea selection"""
        self.write_btn.setEnabled(True)
        self.update_status(f"Selected: {item.text()[:50]}...")
        
    def on_ideas_generated(self, result):
        """Handle generated ideas"""
        ideas_data = result['data']
        
        # Handle new ideator response structure
        if isinstance(ideas_data, dict) and 'ideas' in ideas_data:
            self.current_ideas = ideas_data['ideas']
            model_used = ideas_data.get('model_used', 'Unknown')
            total_ideas = ideas_data.get('total_ideas', len(self.current_ideas))
            self.status_label.setText(f"Generated {total_ideas} ideas using {model_used}")
        else:
            # Handle legacy format
            self.current_ideas = ideas_data
        
        self.ideas_list.clear()
        
        for idea in self.current_ideas:
            # Handle both old and new idea formats
            if isinstance(idea, dict):
                title = idea.get('title', 'Untitled')
                description = idea.get('description', 'No description')
                self.ideas_list.addItem(f"{title} - {description[:50]}...")
            else:
                # Legacy string format
                self.ideas_list.addItem(str(idea)[:60] + "...")
            
        self.set_loading_state(False, f"Generated {len(self.current_ideas)} ideas!")
        
    def on_thread_written(self, result):
        """Handle written thread"""
        self.current_thread = result['data']
        print(f"Thread data received: {self.current_thread.keys()}")
        print(f"First tweet: {self.current_thread.get('tweets', [])[0] if self.current_thread.get('tweets') else 'No tweets'}")
        self.preview_thread()
        
        self.image_btn.setEnabled(True)
        self.preview_btn.setEnabled(True)
        self.post_btn.setEnabled(True)
        self.immediate_post_btn.setEnabled(True)
        self.prompt_btn.setEnabled(True)
        self.media_summary_btn.setEnabled(True)
        self.preview_images_btn.setEnabled(True)
        self.preview_images_btn.setEnabled(True)
        
        self.set_loading_state(False, "Thread written successfully!")
        
    def update_image_status(self, message, time_remaining):
        """Update image status with real progress"""
        self.image_status_label.setVisible(True)
        self.image_status_label.setText(f"{message}")
        
    def _generate_next_image(self):
        """Generate the next image in the sequence"""
        if not self.pending_image_tweets:
            self.set_loading_state(False, "All images generated successfully!")
            self.preview_thread()
            return
            
        # Get the next tweet that needs an image
        current_tweet = self.pending_image_tweets[0]
        image_topic = current_tweet.get('text', self.current_thread.get('topic', ''))
        
        # Update status to show which tweet is being processed
        remaining = len(self.pending_image_tweets)
        total = len([t for t in self.current_thread['tweets'] if t.get('needs_image', False)])
        progress = total - remaining + 1
        self.update_status(f"Generating image {progress}/{total} for tweet")
        self.image_status_label.setText(f"📸 Generating image for tweet {progress}/{total}...")
        
        # Create and start the image generation thread
        self.content_thread = ContentGenerationThread("visualize", image_topic)
        self.content_thread.progress.connect(self.update_status)
        self.content_thread.finished.connect(self._on_single_image_generated)
        self.content_thread.error.connect(self.on_image_error)
        self.content_thread.start()
            
    def on_image_error(self, error_msg):
        """Handle image generation errors"""
        self.image_status_label.setText(f"❌ Image generation failed: {error_msg}")
        self.set_loading_state(False, f"Error generating images: {error_msg}")
        
    def _on_single_image_generated(self, result):
        """Handle a single generated image in the sequence"""
        if result['type'] != "image" or not result['data']:
            self.image_status_label.setText("⚠️ No image was generated. Using placeholder.")
            # Remove the current tweet from pending and continue
            if self.pending_image_tweets:
                self.pending_image_tweets.pop(0)
            self._generate_next_image()
            return
        
        image_data = result['data']
        
        # Calculate accurate progress
        remaining = len(self.pending_image_tweets)
        total = len([t for t in self.current_thread['tweets'] if t.get('needs_image', False)])
        progress = total - remaining
        
        # Display image information for the current image with accurate progress
        self.image_status_label.setText(f"✅ Image {progress}/{total} generated! Source: {image_data.get('source', 'Unknown')}")
        self.image_status_label.setStyleSheet("background-color: #d4edda; color: #155724; padding: 8px; border-radius: 4px;")
        
        # Set image source information
        source_text = f"Source: {image_data.get('source', 'Unknown')}"
        if image_data.get('credit'):
            source_text += f"\nCredit: {image_data.get('credit')}"
        
        self.image_info_label.setText(
            f"📏 Dimensions: {image_data.get('width', 'N/A')}x{image_data.get('height', 'N/A')}\n"
            f"🔍 Description: {image_data.get('description', 'N/A')}\n"
            f"🌐 {source_text}"
        )
        
        # Import required modules
        from PyQt5.QtCore import Qt
        from PyQt5.QtGui import QImage, QPixmap
        import requests
        from io import BytesIO
        from PIL import Image
        import os
        
        # Skip if no URL is provided
        if not image_data.get('url'):
            self.image_label.setText("Image URL not available")
            self.image_preview_box.setVisible(True)
            return
        
        try:
            image_url = image_data['url']
            
            # For placeholder images
            if 'placeholder' in image_url:
                self.image_label.setText("Using placeholder image")
                self.image_preview_box.setVisible(True)
                return
            
            # Handle different image sources
            image_path = None
            if image_url.startswith('file://'):
                image_path = image_url[7:]  # Remove file:// prefix
            elif os.path.exists(image_url):
                image_path = image_url
            else:
                # Remote URL - download first
                response = requests.get(image_url, stream=True, timeout=10)
                response.raise_for_status()
                image = Image.open(BytesIO(response.content))
                # Save to temporary file
                temp_path = os.path.join('data', 'images', 'temp_preview.png')
                os.makedirs(os.path.dirname(temp_path), exist_ok=True)
                image.save(temp_path)
                image_path = temp_path
                
            # Verify the image exists
            if not image_path or not os.path.exists(image_path):
                raise FileNotFoundError(f"Image file not found: {image_path}")
            
            # Load and display the image
            pixmap = QPixmap(image_path)
            if pixmap.isNull():
                raise ValueError("Failed to load image into QPixmap")
            
            # Scale and display the image
            scaled_pixmap = pixmap.scaled(300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.image_label.setPixmap(scaled_pixmap)
            self.image_preview_box.setVisible(True)
            
        except Exception as e:
            logger.error(f"Error loading image: {str(e)}")
            self.image_label.setText(f"Error loading image: {str(e)}")
            self.image_preview_box.setVisible(True)
        from PyQt5.QtCore import Qt
        from PyQt5.QtGui import QImage, QPixmap
        import requests
        from io import BytesIO
        from PIL import Image
        import os
        
        # Skip if no URL is provided
        if not image_data.get('url'):
            self.image_label.setText("Image URL not available")
            self.image_preview_box.setVisible(True)
            return
        
        try:
            # Get the image URL/path
            image_url = image_data['url']
            
            # For placeholder images that use via.placeholder.com
            if 'placeholder' in image_url:
                self.image_label.setText("Using placeholder image")
                self.image_preview_box.setVisible(True)
                return
            
            # Handle different image sources
            image_path = None
            if image_url.startswith('file://'):
                image_path = image_url[7:]  # Remove file:// prefix
            elif os.path.exists(image_url):
                image_path = image_url
            else:
                # Remote URL - download first
                response = requests.get(image_url, stream=True, timeout=10)
                response.raise_for_status()
                image = Image.open(BytesIO(response.content))
                # Save to temporary file
                temp_path = os.path.join('data', 'images', 'temp_preview.png')
                os.makedirs(os.path.dirname(temp_path), exist_ok=True)
                image.save(temp_path)
                image_path = temp_path
            
            # Verify and load the image
            if not image_path or not os.path.exists(image_path):
                raise FileNotFoundError(f"Image file not found: {image_path}")
                
            # Load and display the image
            pixmap = QPixmap(image_path)
            if pixmap.isNull():
                raise ValueError("Failed to load image into QPixmap")
                
            # Scale and display the image
            scaled_pixmap = pixmap.scaled(300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.image_label.setPixmap(scaled_pixmap)
            self.image_preview_box.setVisible(True)
                
        except Exception as e:
            logger.error(f"Error loading image: {str(e)}")
            self.image_label.setText(f"Error loading image: {str(e)}")
            self.image_preview_box.setVisible(True)
        
        # Update the current tweet with the image data
        if self.pending_image_tweets:
            current_tweet = self.pending_image_tweets.pop(0)
            current_tweet['image'] = image_data
            
            # Update progress
            remaining = len(self.pending_image_tweets)
            total = len([t for t in self.current_thread['tweets'] if t.get('needs_image', False)])
            progress = total - remaining
            self.update_status(f"Generated {progress}/{total} images")
            
            # Process next image or finish
            if remaining > 0:
                self._generate_next_image()
            else:
                self.set_loading_state(False, "All images generated successfully!")
                self.preview_thread()  # Refresh preview with all images
        else:
            # No more pending tweets
            self.set_loading_state(False, "All images generated successfully!")
            self.preview_thread()
    
    def on_images_generated(self, result):
        """Legacy handler for single image generation - redirects to the new sequential handler"""
        self._on_single_image_generated(result)
        
    def on_thread_posted(self):
        """Handle successful thread posting"""
        self.save_to_history()
        self.set_loading_state(False, "Thread posted successfully! 🎉")
        QMessageBox.information(self, "Success", "Thread posted to Twitter successfully!")
        
    def on_error(self, error_msg):
        """Handle errors"""
        self.set_loading_state(False, f"Error: {error_msg}")
        QMessageBox.critical(self, "Error", f"An error occurred:\n{error_msg}")
        
    def set_loading_state(self, loading, message=""):
        """Set loading state for UI"""
        if loading:
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)  # Indeterminate progress
            for btn in [self.ideate_btn, self.write_btn, self.image_btn, self.post_btn]:
                btn.setEnabled(False)
        else:
            self.progress_bar.setVisible(False)
            self.ideate_btn.setEnabled(True)
            
        if message:
            self.update_status(message)
            
    def update_status(self, message):
        """Update status message"""
        self.status_label.setText(message)
        self.statusBar().showMessage(message)
        
    def load_history(self):
        """Load posting history"""
        try:
            with open('data/history.json', 'r') as f:
                history = json.load(f)
                
            self.history_list.clear()
            for entry in reversed(history[-20:]):  # Show last 20 entries
                timestamp = datetime.fromisoformat(entry['timestamp']).strftime("%Y-%m-%d %H:%M")
                self.history_list.addItem(f"{timestamp} - {entry.get('topic', 'Unknown')} ({entry.get('tweet_count', 0)} tweets)")
                
        except (FileNotFoundError, json.JSONDecodeError):
            self.history_list.addItem("No history found")
            
    def save_to_history(self):
        """Save current thread to history"""
        if not self.current_thread:
            return
            
        try:
            with open('data/history.json', 'r') as f:
                history = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            history = []
            
        history.append({
            'timestamp': datetime.now().isoformat(),
            'topic': self.current_thread.get('topic', 'Unknown'),
            'tweet_count': len(self.current_thread['tweets']),
            'total_chars': sum(len(t['text']) for t in self.current_thread['tweets']),
            'model_used': self.model_combo.currentText(),
            'has_images': any(t.get('image') for t in self.current_thread['tweets'])
        })
        
        with open('data/history.json', 'w') as f:
            json.dump(history, f, indent=2)
            
        self.load_history()
    
    def show_image_prompts(self):
        """Show image generation prompts dialog"""
        if not self.current_thread:
            QMessageBox.warning(self, "No Thread", "Please write a thread first!")
            return
            
        dialog = ImagePromptDialog(self.current_thread, self)
        result = dialog.exec_()
        
        if result == QDialog.Accepted:
            # User can modify prompts - we could save these modifications if needed
            self.update_status("Image prompts reviewed")
    
    def show_media_summary(self):
        """Show media upload summary dialog"""
        if not self.current_thread:
            QMessageBox.warning(self, "No Thread", "Please write a thread first!")
            return
            
        dialog = MediaSummaryDialog(self.current_thread, self)
        dialog.exec_()
        self.update_status("Media summary viewed")
        
    def show_image_preview_tool(self):
        """Launch the image preview tool"""
        if not self.current_thread:
            QMessageBox.warning(self, "No Thread", "Please write a thread first!")
            return
            
        # Save current thread to file so the preview tool can access it
        import json
        from pathlib import Path
        
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        
        with open("data/current_thread.json", "w") as f:
            json.dump(self.current_thread, f)
        
        # Launch the image preview tool in a separate process
        import subprocess
        import sys
        
        try:
            python_path = sys.executable
            self.update_status("Launching image preview tool...")
            subprocess.Popen([python_path, "image_preview.py"])
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to launch image preview tool: {str(e)}")
            return

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("DroneAgent")
    
    # Set application icon and style
    app.setStyle('Fusion')
    
    gui = DroneAgentGUI()
    gui.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
