import sys
import matplotlib.pyplot as plt
import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLineEdit, QLabel,QPushButton
from PyQt5.QtGui import QPixmap
from PyQt5 import QtCore
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from PIL import Image
import numpy as np

class InteractivePlot(QMainWindow):
    def __init__(self, df):
        super().__init__()

        self.initUI()
        self.df = df
        # df: columns is x-axis and values are y-axis
        self.chart_plotting()

    def initUI(self):
        # Ana pencere boyutu ve başlık
        self.setGeometry(100, 100, 1200, 800)
        self.setWindowTitle('Interactive Plot')
        self.setStyleSheet("background-color: white;") 

        self.colors_base = ["#C0C0C0"
        ,"#A0A0A0"
        ,"#808080"
        ,"#606060"
        ,"#404040"
        ,"#202020"]

        self.line_list = []
        self.cid = None

        # Merkezi bir widget oluştur
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # QVBoxLayout oluştur
        vbox = QVBoxLayout(central_widget)

        # QHBoxLayout oluştur
        hbox = QHBoxLayout()

        self.figure = Figure(figsize=(5, 3))
        self.canvas = FigureCanvas(self.figure)
        vbox.addWidget(self.canvas)

        #vbox.addStretch(1)

        #adding indicator

        basewidth = 400
        """img = Image.open('indicator_assignment3.png')
        wpercent = (basewidth / float(img.size[0]))
        hsize = int((float(img.size[1]) * float(wpercent)))
        img = img.resize((basewidth, hsize), Image.ANTIALIAS)
        img.save('indicator_assignment3_changed.png')"""

        pixmap = QPixmap("color scale indicator.png")
        #pixmap.setScale(1/10*pixmap.scale())
        self.label = QLabel()
        self.label.setPixmap(pixmap)
        #self.label.setFixedSize(150, 80)
        self.label.resize(200, 20)
        hbox.addWidget(self.label)
        self.label.setGeometry(QtCore.QRect(30, 40, 30, 30))

        hbox.addStretch(1)

        vbox.addLayout(hbox)

        self.textbox = QLineEdit(self)
        self.textbox.setMinimumSize(250, 40)
        self.textbox.setPlaceholderText('Please give the value for control: ')
        self.textbox.returnPressed.connect(self.on_textbox_entered)
        hbox.addWidget(self.textbox)

        self.button = QPushButton("RESET")
        self.button.clicked.connect(self.on_button_click)
        hbox.addWidget(self.button)

        self.click_count = 0
        self.reset_pressed = False
        self.y_values = []
        self.canvas.mpl_connect('button_press_event', self.on_click)


  

  
    def chart_parameters(self):

        self.df.index = [str(index) for index in self.df.index]
        categories0 = self.df.T.columns
        categories = ["0_dummy"] + list(categories0) + ["last_dummy"]

        bottomL = [np.quantile(self.df.T[col], 0.25) for col in self.df.T.columns]
        bottom = max(bottomL)

        means = self.df.T.mean()
        std = self.df.T.std()
        count = self.df.T.count()
        std_err0 = std/(count**0.5)
        std_err = [0] + list(std_err0) + [0]

        height0 = means - bottom
        height = [bottom] + list(height0) + [bottom]
        yrange = bottom
        yrangeL = []
        while yrange < 55000:
            yrangeL.append(yrange)
            yrange = yrange + 3*np.mean(std_err)

        return categories0, categories, height, bottom, std_err, yrangeL
    
    def color_bars(self, value1, value2):
        colors = []
        value = np.mean([value1,value2])
        print("value1: ",value1," --------------------------- value2: ",value2)
        categories0, categories, height, bottom, std_err, yrangeL = self.chart_parameters()

        colors = {0: "#330000", 0.09:"#990000", 0.18:"#FF0000",0.27:"#FF6666",0.36:"#FF99CC",0.45:"#FFCCE5"
                  ,0.55:"#9999FF",0.64:"#66B2FF",0.73:"#0080FF",0.82:"#004C99",0.91:"#001933",1:"#001933"}
        bars = self.ax.bar(categories, height-bottom, bottom = bottom, width = 1)
        i = 0

        print("Sample: ", value1, " - ", value2)
        print("--------------------------------------------------------------------------")
        for bar in bars:
            max = height[i] + std_err[i]
            min = height[i] - std_err[i]

            rate_value = 1-((max-value)/(2*std_err[i]))
            print(categories[i], ":",height[i]," - ",std_err[i])
            print("max:", max," - min:",min)
            print("height:", bar.get_height())
            for x in list(colors.keys()):
                min_rate = x
                max_rate = x+0.09
                if value >= max:
                    bar.set_facecolor(colors[1])
                elif value <= min:
                    bar.set_facecolor(colors[0])
                elif rate_value >= min_rate and rate_value < max_rate:
                    bar.set_facecolor(colors[x])
            i = i + 1

    def chart_plotting(self):

        categories0, categories, height, bottom, std_err, yrangeL = self.chart_parameters()

        self.ax = self.figure.add_subplot(111)
        self.ax.set_xlim(-1, len(categories)-2)
        self.ax.set_ylim(0, 50000)

        self.ax.bar(x = categories, height = height-bottom, bottom = bottom, yerr = std_err
        ,width = 1, capsize = 15, color = self.colors_base)

        # Hareketli çizgiyi oluştur
        self.line = Line2D([-1, len(categories)-1], [0, 0], color='red', linestyle='-', linewidth=2)
        self.ax.add_line(self.line)

        #self.ax.set_xlabel('Categories')
        #self.ax.set_ylabel('Values')
        #self.ax.set_title('')

        self.ax.spines['left'].set_position(('data', 0))
        self.ax.spines['bottom'].set_position(('data', bottom))
        self.ax.set_xticks(range(1, len(categories0)+1),categories0, fontsize = 12)
        self.ax.set_yticks(yrangeL, fontsize = 12)
        self.ax.set_xlim(-1, 5)
        self.ax.set_ylim(0, yrangeL[-1])

        #self.ax.set_facecolor('#E5E5E5') 

    def event_push(self):
        
        self.canvas.mpl_connect('button_press_event', self.onpress)
        self.canvas.mpl_connect('button_release_event', self.onrelease)
        self.canvas.mpl_connect('motion_notify_event', self.onmove)
        
    def on_textbox_entered(self):
        categories0, categories, height, bottom, std_err, yrangeL = self.chart_parameters()
        try:
            new_height = float(self.textbox.text())
            for line in self.line_list:
                line.remove()  # Tüm çizgileri kaldır
            self.line_list.clear()  # Liste içeriğini temizle
            self.canvas.draw() # Önceki çizgiyi kaldır
            self.line = Line2D([-1, len(categories)-1], [new_height, new_height], color='red', linestyle='-', linewidth=2)
            self.ax.add_line(self.line)
            self.line_list.append(self.line)

            self.color_bars(new_height, new_height)
            self.canvas.draw()
        except ValueError:
            print('Lütfen geçerli bir sayı girin.')
    def on_button_click(self):
        categories0, categories, height, bottom, std_err, yrangeL = self.chart_parameters()
        bars = self.ax.bar(categories, height-bottom, bottom = bottom, width = 1)

        self.click_count = 0
        self.y_values = []
        self.reset_pressed = True

        for line in self.line_list:
            line.remove()  # Tüm çizgileri kaldır
        self.line_list.clear()  # Liste içeriğini temizle
        self.canvas.draw()

        self.line = Line2D([-1, len(categories)-1], [0, 0], color='red', linestyle='-', linewidth=2)
        self.ax.add_line(self.line)
        self.line_list.append(self.line)

        i = 0
        for bar in bars:
            bar.set_facecolor(self.colors_base[i])
            i = i + 1
        self.canvas.draw()
        self.textbox.clear()
        #self.textbox.setText("Please give the value for control:")
        self.textbox.returnPressed.connect(self.on_textbox_entered)
        self.canvas.mpl_connect('button_press_event', self.on_click)
        if self.cid is None:  # Eğer olay dinleyici zaten aktif değilse
            self.cid = self.canvas.mpl_connect('button_press_event', self.on_click)

    def on_click(self, event):
        # Tıklama olayını işle
        categories0, categories, height, bottom, std_err, yrangeL = self.chart_parameters()

        if self.reset_pressed:
            for line in self.line_list:
                line.remove()  # Tüm çizgileri kaldır
            self.line_list.clear()  # Liste içeriğini temizle
            self.canvas.draw()
            self.reset_pressed = False  # İşlem tamamlandı, tekrar sıfırlanabilir
        
        if self.click_count == 0:
            try:
                if self.line:
                    self.line.remove()
                self.canvas.draw()
            except:
                k = 0
            
        print("click_count:",self.click_count)
            
        if event.button == 1 and self.click_count < 2:  # Sadece sol fare düğmesi tıklamalarını ele al ve 2 çizgi çizildiyse devre dışı bırak
            print("click_count:",self.click_count)
            x_value = int(event.xdata)
            y_value = event.ydata
            new_height = y_value
            self.line = Line2D([-1, len(categories)-1], [new_height, new_height], color='red', linestyle='-', linewidth=2)
            self.line_list.append(self.line)
            self.ax.add_line(self.line)
            self.y_values.append(y_value)
            print(self.y_values)
            self.color_bars(self.y_values[0], self.y_values[-1])
            self.canvas.draw()
            self.cid = self.canvas.mpl_connect('button_press_event', self.on_click)
            self.click_count += 1


        print("click_count:",self.click_count, type(self.click_count))
        self.button.clicked.connect(self.on_button_click)
        
        if self.click_count == 2:
            print(self.canvas.callbacks.callbacks)
            #self.canvas.mpl_disconnect(self.canvas.callbacks.callbacks['button_press_event'][0]) 
            if self.cid is not None:
                self.canvas.mpl_disconnect(self.cid)
                self.cid = None
            self.button.setEnabled(True)
            self.click_count = 0
