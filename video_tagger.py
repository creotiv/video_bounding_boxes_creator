# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets
import skvideo.io
import json
import sys

class GraphView(QtWidgets.QGraphicsView):

    def __init__(self, *args, **kwargs):
        super(GraphView,self).__init__(*args, **kwargs)
        self.rubberBand = None
        self.select_callback = None

    def mousePressEvent(self, event):
        self.origin = event.pos()
        if not self.rubberBand:
            self.rubberBand = QtWidgets.QRubberBand(QtWidgets.QRubberBand.Rectangle, self)
        self.rubberBand.setGeometry(QtCore.QRect(self.origin, QtCore.QSize()))
        self.rubberBand.show()

    def mouseMoveEvent(self, event):
        self.rubberBand.setGeometry(QtCore.QRect(self.origin, event.pos()).normalized())
        
    def mouseReleaseEvent(self, event):
        self.rubberBand.hide()
        if self.select_callback:
            self.select_callback((self.origin.x(), self.origin.y()), (event.pos().x(), event.pos().y()))
    
    def set_selection_callback(self, callback):
        self.select_callback = callback
    

class Ui_MainWindow(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()
        self.cap = None
        self.video_path = None
        self.selections = []
        self.frame_selections = []
        self.frame_number = 0
        self.setupUi()

    def setupUi(self):
        MainWindow = self
    
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.setMinimumSize(QtCore.QSize(600, 500))
        self.setObjectName("centralWidget")
        
        self.gridLayout = QtWidgets.QGridLayout(self)
        self.gridLayout.setContentsMargins(11, 11, 11, 11)
        self.gridLayout.setSpacing(6)
        self.gridLayout.setObjectName("gridLayout")
        
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)
        self.horizontalLayout.setContentsMargins(11, 11, 11, 11)
        self.horizontalLayout.setSpacing(6)
        self.horizontalLayout.setObjectName("horizontalLayout")
        
        self.next_button = QtWidgets.QPushButton(self)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.next_button.sizePolicy().hasHeightForWidth())
        self.next_button.setSizePolicy(sizePolicy)
        self.next_button.setMinimumSize(QtCore.QSize(150, 0))
        self.next_button.setObjectName("next_button")

        self.open_button = QtWidgets.QPushButton(self)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.open_button.sizePolicy().hasHeightForWidth())
        self.open_button.setSizePolicy(sizePolicy)
        self.open_button.setMinimumSize(QtCore.QSize(150, 0))
        self.open_button.setObjectName("open_button")
        
        self.label = QtWidgets.QLabel(self)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setObjectName("label")
        
        self.frames = QtWidgets.QLineEdit(self)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frames.sizePolicy().hasHeightForWidth())
        self.frames.setSizePolicy(sizePolicy)
        self.frames.setMinimumSize(QtCore.QSize(50, 0))
        self.frames.setMaximumSize(QtCore.QSize(50, 50))
        self.frames.setObjectName("frames")
        self.frames.setText("24")
        
        self.horizontalLayout.addWidget(self.open_button, 0, QtCore.Qt.AlignLeft)
        self.horizontalLayout.addWidget(self.next_button, 0, QtCore.Qt.AlignLeft)
        self.horizontalLayout.addWidget(self.label, 0, QtCore.Qt.AlignLeft)
        self.horizontalLayout.addWidget(self.frames, 0, QtCore.Qt.AlignLeft)
        
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        
        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 1)
        
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)
        self.verticalLayout.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout.setSpacing(6)
        self.verticalLayout.setObjectName("verticalLayout")
        
        self.scene = QtWidgets.QGraphicsScene()
        
        self.graphicsView = GraphView(self.scene)
        self.graphicsView.setAlignment(QtCore.Qt.AlignTop|QtCore.Qt.AlignLeft)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.graphicsView.sizePolicy().hasHeightForWidth())
        self.graphicsView.setSizePolicy(sizePolicy)
        self.graphicsView.setObjectName("graphicsView")
        self.verticalLayout.addWidget(self.graphicsView)
        self.graphicsView.set_selection_callback(self.selected)
        
        self.gridLayout.addLayout(self.verticalLayout, 1, 0, 1, 1)

        self.retranslateUi(MainWindow)
        self.open_button.clicked.connect(self.open_video)
        self.next_button.clicked.connect(self.next_frame)
        
        self.back_selections = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+Z"), self)
        self.back_selections.activated.connect(self.remove_last_selection)

    def skip_frames(self, num=24):
        if not self.video_path or not self.cap:
            return

        for i in range(num):
            next(self.cap)
            self.frame_number += 1
    
    def show_image(self):
        if not self.video_path or not self.cap:
            return
            
        image = next(self.cap)
        image = QtGui.QImage(image, image.shape[1], image.shape[0], image.shape[1] * 3, QtGui.QImage.Format_RGB888)
        self.pix = QtGui.QPixmap(image)
        self.scene.clear()
        self.scene.addPixmap(self.pix)
        self.frame_number += 1
    
    def open_video(self):
        self.video_path = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', '/home/creotiv/ENVS/KaggleProjects/TrafficCounter/inputs/')[0]
        self.cap = skvideo.io.vreader(self.video_path)
        self.show_image()        
        
    def draw_boxes(self, boxes):
        self.scene.clear()
        self.scene.addPixmap(self.pix)
        red = QtGui.QBrush(QtGui.QColor(0xFF, 0, 0, 0x80))
        for (start, end) in boxes:
            self.scene.addRect(start[0], start[1], end[0]-start[0], end[1]-start[1], brush=red)
        
    def selected(self, start, end):
        self.frame_selections.append((start,end))
        self.draw_boxes(self.frame_selections)
        
    def remove_last_selection(self):
        if self.frame_selections:
            self.frame_selections.pop(len(self.frame_selections)-1)
            self.draw_boxes(self.frame_selections)
        
    def next_frame(self):
        if not self.video_path:
            return
        self.selections.append((self.frame_number,self.frame_selections))
        self.skip_frames(int(self.frames.text()))
        self.show_image()
        self.frame_selections = []
        
    def retranslateUi(self, MainWindow):
        #_translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle("Video Tagger")
        self.next_button.setText("Next frame")
        self.open_button.setText("Open video")
        self.label.setText("Frames to skip:")
        
    def close(self):
        self.selections.append((self.frame_number,self.frame_selections))
        name = '_'.join(self.video_path.split('/')[-1].split('.')[:-1])
        json.dump(self.selections, open('./%s_bounding_boxes.json' % (name),'w'))
        
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Ui_MainWindow()
    window.show()
    import atexit
    atexit.register(window.close)    
    sys.exit(app.exec_())
    
