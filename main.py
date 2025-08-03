import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,QStatusBar,
    QPushButton, QFileDialog, QLabel, QScrollArea, QGridLayout
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
from PIL import Image, ImageQt

PURPLE_STYLESHEET = """
QWidget {
    font-family: Segoe UI;
    color: #333;
}
QMainWindow {
    background-color: #f2f0f5;
}
QLabel#titleLabel {
    color: #5b2c6f;
    font-size: 20px;
    font-weight: bold;
    padding: 10px;
}
/* Default Button Style */
QPushButton {
    background-color: #8e44ad;
    color: white;
    font-size: 15px;
    font-weight: bold;
    border: none;
    padding: 12px;
    border-radius: 8px;
}
QPushButton:hover {
    background-color: #7d3c98;
}
QPushButton:pressed {
    background-color: #6c3483;
}
QScrollArea {
    border: 1px solid #d5cde5;
    border-radius: 8px;
    background-color: #e8e4ef;
}
QLabel#imagePreview {
    border: 2px solid #8e44ad;
    border-radius: 5px;
    background-color: white;
}
/* Edit Buttons Style */
QPushButton[class="editButton"] {
    background-color: white;
    color: #8e44ad;
    border: 1.5px solid #8e44ad;
    font-size: 16px;
    font-weight: bold;
    padding: 5px 8px;
    border-radius: 5px;
}
QPushButton[class="editButton"]:hover {
    background-color: #f5f0f8;
}
/* Danger Button Style */
QPushButton[class="dangerButton"] {
    background-color: #e74c3c;
    color: white;
}
QPushButton[class="dangerButton"]:hover {
    background-color: #c0392b;
}
"""

class ImageToPDFApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image to PDF Converter")
        self.setGeometry(100, 100, 850, 700)
        self.images_data = []
        self.init_ui()
        self.setStyleSheet(PURPLE_STYLESHEET)

    def init_ui(self):
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Ready | Created by: Dorsa")

        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        title_label = QLabel("Select images to edit and convert to PDF")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignCenter)

        upload_button = QPushButton("📂  Upload Images")
        upload_button.clicked.connect(self.upload_images)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.image_grid_layout = QGridLayout(self.scroll_content)
        self.image_grid_layout.setSpacing(20)
        self.scroll_area.setWidget(self.scroll_content)

        self.create_pdf_button = QPushButton("📄  Create PDF File")
        self.create_pdf_button.clicked.connect(self.create_pdf)
        self.create_pdf_button.setEnabled(False)

        self.reset_button = QPushButton("🔄 Reset Application")
        self.reset_button.setProperty("class", "dangerButton")
        self.reset_button.clicked.connect(self.reset_app)
        self.reset_button.setEnabled(False)

        bottom_buttons_layout = QHBoxLayout()
        bottom_buttons_layout.addWidget(self.reset_button)
        bottom_buttons_layout.addWidget(self.create_pdf_button)

        main_layout.addWidget(title_label)
        main_layout.addWidget(upload_button)
        main_layout.addWidget(self.scroll_area, 1)
        main_layout.addLayout(bottom_buttons_layout)
        self.setCentralWidget(main_widget)

    def pil_to_pixmap(self, pil_image):
        return QPixmap.fromImage(ImageQt.ImageQt(pil_image))

    def upload_images(self):
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, "Select Images", "", "Image Files (*.png *.jpg *.jpeg *.bmp)"
        )
        if file_paths:
            for path in file_paths:
                try:
                    image = Image.open(path)
                    self.images_data.append({'path': path, 'image': image})
                except Exception as e:
                    print(f"Error opening {path}: {e}")
            self.display_images()
            self.create_pdf_button.setEnabled(True)
            self.reset_button.setEnabled(True)

    def display_images(self):
        for i in reversed(range(self.image_grid_layout.count())):
            item = self.image_grid_layout.takeAt(i)
            if item.widget():
                item.widget().deleteLater()

        row, col = 0, 0
        for idx, data in enumerate(self.images_data):
            container = QWidget()
            container_layout = QVBoxLayout(container)
            
            image_label = QLabel()
            image_label.setObjectName("imagePreview")
            pixmap = self.pil_to_pixmap(data['image'])
            image_label.setPixmap(pixmap.scaled(180, 180, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            image_label.setFixedSize(180, 180)
            image_label.setAlignment(Qt.AlignCenter)

            buttons_layout = QHBoxLayout()
            rotate_button = QPushButton("🔄")
            rotate_button.setProperty("class", "editButton")
            rotate_button.clicked.connect(lambda checked, i=idx: self.rotate_image(i))
            
            delete_button = QPushButton("❌")
            delete_button.setProperty("class", "editButton")
            delete_button.clicked.connect(lambda checked, i=idx: self.delete_image(i))

            buttons_layout.addWidget(rotate_button)
            buttons_layout.addWidget(delete_button)
            
            container_layout.addWidget(image_label)
            container_layout.addLayout(buttons_layout)

            self.image_grid_layout.addWidget(container, row, col)
            col += 1
            if col % 4 == 0:
                row += 1
                col = 0
    
    def rotate_image(self, index):
        self.images_data[index]['image'] = self.images_data[index]['image'].rotate(-90, expand=True)
        self.display_images()

    def delete_image(self, index):
        if 0 <= index < len(self.images_data):
            del self.images_data[index]
            self.display_images()
            if not self.images_data:
                self.create_pdf_button.setEnabled(False)
                self.reset_button.setEnabled(False)

    def reset_app(self):
        self.images_data.clear()
        self.display_images()
        self.create_pdf_button.setEnabled(False)
        self.reset_button.setEnabled(False)

    def create_pdf(self):
        if not self.images_data:
            return

        save_path, _ = QFileDialog.getSaveFileName(
            self, "Save PDF File", "", "PDF Files (*.pdf)"
        )
        if save_path:
            if not save_path.lower().endswith('.pdf'):
                save_path += '.pdf'

            try:
                A4_WIDTH_PX = 2480
                A4_HEIGHT_PX = 3508
                
                final_pages = []
                
                for data in self.images_data:
                    user_img = data['image']
                    if user_img.mode in ('RGBA', 'P'):
                        user_img = user_img.convert('RGB')

                    a4_page = Image.new('RGB', (A4_WIDTH_PX, A4_HEIGHT_PX), 'white')

                    original_width, original_height = user_img.size
                    aspect_ratio = original_height / original_width
                    
                    new_width = A4_WIDTH_PX
                    new_height = int(new_width * aspect_ratio)

                    if new_height > A4_HEIGHT_PX:
                        new_height = A4_HEIGHT_PX
                        new_width = int(new_height / aspect_ratio)

                    resized_img = user_img.resize((new_width, new_height), Image.LANCZOS)
                    
                    paste_x = (A4_WIDTH_PX - new_width) // 2
                    paste_y = (A4_HEIGHT_PX - new_height) // 2
                    
                    a4_page.paste(resized_img, (paste_x, paste_y))
                    
                    final_pages.append(a4_page)

                if final_pages:
                    final_pages[0].save(
                        save_path, save_all=True, append_images=final_pages[1:]
                    )
                    print(f"PDF file successfully saved to {save_path}")

            except Exception as e:
                print(f"Error creating PDF file: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageToPDFApp()
    window.show()
    sys.exit(app.exec())
