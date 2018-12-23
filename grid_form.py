from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit,\
    QTextEdit, QGridLayout, QApplication,\
    QHBoxLayout, QVBoxLayout,\
    QPushButton, QComboBox, QFileDialog
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
import sys
import pyperclip 
import product_and_jump


class MyWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.A_str = ''
        #self.pixmap = QPixmap('kapture.png')
        self.pixmap = QPixmap('images/from-bishop.png')
        #self.pixmap = QPixmap('/home/wucf20/project-self-motivated/matrix_pdf_to_plain_text/images/from-bishop.png')
        self.pixmap = self.pixmap.scaledToHeight(200)
        #smaller_pixmap = pixmap.scaled(32, 32, Qt.KeepAspectRatio, Qt.FastTransformation)
        self.pixmap_as_label = QLabel(self)
        self.pixmap_as_label.setPixmap(self.pixmap)
        snip_btn = QPushButton('Snip')
        load_btn = QPushButton('Load from ...')
        load_btn.clicked.connect(self.loadImg)

        self.tex = 'To be implemented...'
        self.output = QTextEdit(self.tex)
        #self.output.setDisabled(True)
        self.output.setReadOnly(True)
        #inn = QTextEdit()
        self.of_combo = QComboBox()
        self.of_combo.addItem('tex')
        self.of_combo.addItem('np')
        self.of_combo.addItem('csv')
        #self.of = 'tex'
        # of: output format
        # np: numpy
        self.of_combo.activated[str].connect(self.choose_of)
        cp_btn = QPushButton('Copy')
        cp_btn.clicked.connect(self.cp_output)

        #grid = QGridLayout()
        self.grid = QGridLayout()
        #grid.setSpacing(20)
        self.grid.setSpacing(20)
        # 10px?


        #grid.addWidget(self.pixmap_as_label, 0, 0, 3, 0)
        #grid.addWidget(self.pixmap_as_label, 0, 0, 2, 0)
        #grid.addWidget(self.pixmap_as_label, 0, 0)
        #grid.addWidget(inn, 0, 0, 1, 0)
        #grid.addWidget(inn, 0, 0, 2, 1)
        #grid.addWidget(self.pixmap_as_label, 0, 0, 2, 1)
        #grid.addWidget(snip_btn, 0, 1)
        #grid.addWidget(load_btn, 1, 1)
        self.grid.addWidget(self.pixmap_as_label, 0, 0, 2, 1)
        self.grid.addWidget(snip_btn, 0, 1)
        self.grid.addWidget(load_btn, 1, 1)

        #grid.addWidget(self.output, 4, 0, 7, 0)
        #grid.addWidget(self.output, 3, 0, 4, 0)
        #grid.addWidget(self.output, 2, 0)
        #grid.addWidget(self.output, 2, 0, 2, 1)
        #grid.addWidget(of_combo, 2, 1)
        #grid.addWidget(cp_btn, 3, 1)
        self.grid.addWidget(self.output, 2, 0, 2, 1)
        self.grid.addWidget(self.of_combo, 2, 1)
        self.grid.addWidget(cp_btn, 3, 1)

        #self.setLayout(grid)
        self.setLayout(self.grid)
        
        self.setGeometry(300,300,550,500)
        #print(self.Geometry())
        self.setWindowTitle('Matrix Reader')
        self.show()

    # Reimplement the keyPressEvent()
    def keyPressEvent(self, e):
        '''
        input: e stands for "event object"
        '''
        #if e.key() in (Qt.Key_Escape, Qt.Key_Q):
        if e.key() == Qt.Key_Escape:
            #print(Qt.Key_Q)
            self.close()

    def loadImg(self):
        """
        1/ construct A_str and remember it
        2/ display on TextEditor, (so we need to know comboBox value)
        """
        #filter_ = 'Images (*.png *.xpm *.jpg)'
        filter_ = 'Images (*.png *.xpm *.jpg);;XML files (*.xml)'
        #file_info = QFileDialog.getOpenFileName(self, 'Open file', './')
        file_info = QFileDialog.getOpenFileName(self, 'Open file', './', filter_)
        print(file_info)
        # A typical file_info would look like the following:
        # Il s'agit d'un tuple de len=2
        # ('/home/wucf20/project-self-motivated/matrix_pdf_to_plain_text/grid_form.py', 'All Files (*)')
        # Or when you click on Cancel button:
        # ('', '')
        #if file_info[0] != '':
        # equiv. to
        #if file_info[0]:
        #    with open(file_info[0], 'r') as f:
        #        pass
        if file_info[0]:
            try:
                self.pixmap = QPixmap(file_info[0])
                self.pixmap = self.pixmap.scaledToHeight(100)
                self.pixmap_as_label.setPixmap(self.pixmap)
                self.grid.addWidget(self.pixmap_as_label, 0, 0, 2, 1)
                # (?1) any way to grid.update()?
                self.update()

                self.A_str = product_and_jump.img2A_str(file_info[0])
                self.output.setText(product_and_jump.A_str2tex(self.A_str, output_format=self.of_combo.currentText()))
            except Exception as e:
                print(e)
        #try:
        #    self.A_str = product_and_jump.img2A_str(file_info[0])
        #    self.output.setText(product_and_jump.A_str2tex(self.A_str, output_format=self.of_combo.currentText()))
        #except Exception as e:
        #    print(e)

    def choose_of(self, text):
        #self.of_combo = text
        #print(self.of)
        #print(self.of_combo.currentData())
        print(self.of_combo.currentText())
        self.output.setText(product_and_jump.A_str2tex(self.A_str, output_format=self.of_combo.currentText()))
    
    def cp_output(self):
        #self.output.copy()
        #self.output.toPlainText()
        #print(self.output.toPlainText())
        pyperclip.copy(self.output.toPlainText())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win= MyWindow()
    sys.exit(app.exec_())
