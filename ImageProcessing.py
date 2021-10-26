from asyncio.windows_events import NULL
import tkinter as tk
from tkinter import *
from tkinter import filedialog
from PIL import ImageTk, Image
import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

plt.rcParams.update({'font.size': 5.5})

class Main:
  def __init__(self, root):
    self.root = root
    self.baseImg = None
    self.img = np.zeros([])

    # Image mode = 0, Histogram mode = 1
    self.viewMode = 0
    self.currentMode = NULL
    self.is_firstImg = TRUE

    # Prepare Window Settings
    self.screenWidth= self.root.winfo_screenwidth()
    self.screenHeight= self.root.winfo_screenheight()
    self.root.title('Image Processing App')
    self.root.geometry("%dx%d" %(self.screenWidth, self.screenHeight))
    self.root.option_add('*tearOff', FALSE)

    # Set up panels to show the image
    self.imgPanelSize = [self.screenWidth/1.2, self.screenHeight/1.2]
    self.imgPanelSizeHist = [self.screenWidth/2, self.screenHeight/2]

    self.panelLeft = tk.Label(self.root)
    self.panelLeft.pack(side="left", padx=85, pady=10)

    self.panelRight = tk.Label(self.root)
    self.panelRight.pack(side="right", padx=85, pady=10)

    # Initialize View Mode Information
    self.currentMode = Label(self.root, text = "Standard Image Mode")
    self.currentMode.config(font =("Courier", 14))
    self.currentMode.pack()

    # Initialize Histogram Figures
    self.redFigure = plt.Figure(figsize=(3,3), dpi=100)
    self.redCanvas = FigureCanvasTkAgg(self.redFigure, self.root)
    self.greenFigure = plt.Figure(figsize=(3,3), dpi=100)
    self.greenCanvas = FigureCanvasTkAgg(self.greenFigure, self.root)
    self.blueFigure = plt.Figure(figsize=(3,3), dpi=100)
    self.blueCanvas = FigureCanvasTkAgg(self.blueFigure, self.root)

    # Set up needed action menus
    self.menubar = Menu(self.root)
    self.menu1 = Menu(self.menubar)
    self.menubar.add_cascade(label="File", menu=self.menu1)
    self.menu1.add_command(label="Select Image", command=self.selectImage)
    self.menu1.add_command(label="Clear Result", command=self.clearRightPanel)
    self.menu1.add_separator()
    self.menu1.add_command(label="Exit", command=self.root.quit)

    self.menu2 = Menu(self.menubar)
    self.menubar.add_cascade(label="Edit", menu=self.menu2)
    self.menu2.add_command(label="Scaling 2x", command=lambda: self.scaleImage(200))
    self.menu2.add_command(label="Scaling 1/2x", command=lambda: self.scaleImage(50))
    self.menu2.add_command(label="Gray Scaling", command=self.grayImage)
    self.menu2.add_command(label="Down Sampling", command=self.downSampling)
    self.menu2.add_command(label="Quantization", command=self.quantization)
    self.menu2.add_command(label="Negative Color", command=self.createKlise)
    self.menu2.add_command(label="Increase Intensity", command=self.modifyIntensity)

    self.menu3 = Menu(self.menubar)
    self.menubar.add_cascade(label="View Mode", menu=self.menu3)
    self.menu3.add_command(label="Standard Image", command=self.toImgMode)
    self.menu3.add_command(label="Image Histogram", command=self.toHistMode)

    self.root.config(menu=self.menubar)
    self.root.mainloop()

  # Handle image selection
  def selectImage(self):
    self.clearLeftPanel()
    self.clearRightPanel()
    self.unpackHistogramCanvas()
    
    filename =  filedialog.askopenfilename(filetypes=[("Image files", ".jpg .jpeg .jp2 .png .tiff .svg .gif .bmp")])
    self.img = cv.cvtColor(cv.imread(filename), cv.COLOR_BGR2RGB)
    self.baseImg = Image.open(filename)
    image = Image.fromarray(self.img)
    if(self.viewMode==0):
      image.thumbnail(self.imgPanelSize, Image.ANTIALIAS)
    elif(self.viewMode==1):
      image.thumbnail(self.imgPanelSizeHist, Image.ANTIALIAS)
    
    image_tk = ImageTk.PhotoImage(image)

    if(self.viewMode==0):
      self.showLeftPanel(image_tk)
    elif(self.viewMode==1):
      self.clearLeftPanel()
      self.showLeftPanel(image_tk)
      self.showHistogramCanvas()
    
    self.is_firstImg = FALSE
  
  # Show or Clear panel handlers
  def showLeftPanel(self, img):
    self.panelLeft.configure(image=img)
    self.panelLeft.image = img

  def showRightPanel(self, img):
    self.panelRight.configure(image=img)
    self.panelRight.image = img

  def clearLeftPanel(self):
    self.panelLeft.configure(image='')

  def clearRightPanel(self):
    self.panelRight.configure(image='')
  
  def unpackHistogramCanvas(self):
    self.redCanvas.get_tk_widget().pack_forget()
    self.greenCanvas.get_tk_widget().pack_forget()
    self.blueCanvas.get_tk_widget().pack_forget()

  # Handle view mode changes
  def toImgMode(self):
    self.viewMode = 0
    self.showCurrentModeText()
    self.unpackHistogramCanvas()

  def toHistMode(self):
    self.viewMode = 1
    self.showCurrentModeText()

  def showCurrentModeText(self):
    if(self.currentMode != NULL):
      self.currentMode.destroy()

    if (self.viewMode == 0):
      self.currentMode = Label(self.root, text = "Standard Image Mode")
      self.currentMode.config(font =("Courier", 14))
    elif (self.viewMode == 1):
      self.currentMode = Label(self.root, text = "Image Histogram Mode")
      self.currentMode.config(font =("Courier", 14))

    self.currentMode.pack()

  ################# Image Processing Operations #################
  def scaleImage(self, scalePercent):
    self.clearRightPanel()

    imgScale = scalePercent
    imgHeight = int(self.baseImg.size[0] * (imgScale / 100))
    imgWidth = int(self.baseImg.size[1] * (imgScale / 100))
    dimension = (imgWidth, imgHeight)

    resizedImg = cv.resize(self.img, dimension, interpolation = cv.INTER_LINEAR)
    resizedImg = Image.fromarray(resizedImg, 'RGB')
    self.baseImg = resizedImg
    self.img = np.array(resizedImg)
    resizedImg = ImageTk.PhotoImage(resizedImg)

    if(self.viewMode==0):
      self.showRightPanel(resizedImg)
    elif(self.viewMode==1):
      self.clearLeftPanel()
      self.showLeftPanel(resizedImg)
      self.showHistogramCanvas()

  def grayImage(self):
    self.clearRightPanel()

    grayedImg = cv.cvtColor(self.img, cv.COLOR_BGR2GRAY)
    
    grayedImg = Image.fromarray(grayedImg)
    img = np.array(grayedImg)
    if(self.viewMode==0):
      grayedImg.thumbnail(self.imgPanelSize, Image.ANTIALIAS)
    elif(self.viewMode==1):
      grayedImg.thumbnail(self.imgPanelSizeHist, Image.ANTIALIAS)
    image_tk = ImageTk.PhotoImage(grayedImg)

    if(self.viewMode==0):
      self.showRightPanel(image_tk)
    elif(self.viewMode==1):
      self.clearLeftPanel()
      self.showLeftPanel(image_tk)
      self.showHistogramCanvas()

  def downSampling(self):
    self.clearRightPanel()
    downSampledImg = cv.pyrDown(self.img)
    
    downSampledImg = Image.fromarray(downSampledImg)
    self.img = np.array(downSampledImg)
    if(self.viewMode==0):
      downSampledImg.thumbnail(self.imgPanelSize, Image.ANTIALIAS)
    elif(self.viewMode==1):
      downSampledImg.thumbnail(self.imgPanelSizeHist, Image.ANTIALIAS)
    image_tk = ImageTk.PhotoImage(downSampledImg)

    if(self.viewMode==0):
      self.showRightPanel(image_tk)
    elif(self.viewMode==1):
      self.clearLeftPanel()
      self.showLeftPanel(image_tk)
      self.showHistogramCanvas()

  def quantization(self):
    self.clearRightPanel()
    imgHeight = self.img.shape[0]
    imgWidth = self.img.shape[1]

    quantizationImg = np.zeros((imgHeight, imgWidth, 3), np.uint8)

    for i in range(imgHeight):
      for j in range(imgWidth):
          for k in range(3):  
              if self.img[i, j][k] < 128:
                  gray = 0
              else:
                  gray = 129
              quantizationImg[i, j][k] = np.uint8(gray)

    quantizationImg = Image.fromarray(quantizationImg)
    self.img = np.array(quantizationImg)
    if(self.viewMode==0):
      quantizationImg.thumbnail(self.imgPanelSize, Image.ANTIALIAS)
    elif(self.viewMode==1):
      quantizationImg.thumbnail(self.imgPanelSizeHist, Image.ANTIALIAS)
    image_tk = ImageTk.PhotoImage(quantizationImg)

    if(self.viewMode==0):
      self.showRightPanel(image_tk)
    elif(self.viewMode==1):
      self.clearLeftPanel()
      self.showLeftPanel(image_tk)
      self.showHistogramCanvas()

  def createKlise(self):
    self.clearRightPanel()

    self.img[:,:,0] = 255 - self.img[:,:,0]
    self.img[:,:,1] = 255 - self.img[:,:,1]
    self.img[:,:,2] = 255 - self.img[:,:,2]

    negativeImg = Image.fromarray(self.img)
    self.img = np.array(negativeImg)
    if(self.viewMode==0):
      negativeImg.thumbnail(self.imgPanelSize, Image.ANTIALIAS)
    elif(self.viewMode==1):
      negativeImg.thumbnail(self.imgPanelSizeHist, Image.ANTIALIAS)
    image_tk = ImageTk.PhotoImage(negativeImg)

    if(self.viewMode==0):
      self.showRightPanel(image_tk)
    elif(self.viewMode==1):
      self.clearLeftPanel()
      self.showLeftPanel(image_tk)
      self.showHistogramCanvas()

  def modifyIntensity(self, value=100):
    hsv = cv.cvtColor(self.img, cv.COLOR_RGB2HSV)
    h, s, v = cv.split(hsv)

    lim = 255 - value
    v[v > lim] = 255
    v[v <= lim] += value

    final_hsv = cv.merge((h, s, v))
    self.img = cv.cvtColor(final_hsv, cv.COLOR_HSV2RGB)

    intensityImg = Image.fromarray(self.img)
    self.img = np.array(intensityImg)
    if(self.viewMode==0):
      intensityImg.thumbnail(self.imgPanelSize, Image.ANTIALIAS)
    elif(self.viewMode==1):
      intensityImg.thumbnail(self.imgPanelSizeHist, Image.ANTIALIAS)
    image_tk = ImageTk.PhotoImage(intensityImg)

    if(self.viewMode==0):
      self.showRightPanel(image_tk)
    elif(self.viewMode==1):
      self.clearLeftPanel()
      self.showLeftPanel(image_tk)
      self.showHistogramCanvas()

  ################# Image Histogram #################
  def showHistogramCanvas(self):
    self.clearRightPanel()
    self.unpackHistogramCanvas()

    self.redFigure = plt.Figure(figsize=(3,3), dpi=100)
    self.greenFigure = plt.Figure(figsize=(3,3), dpi=100)
    self.blueFigure = plt.Figure(figsize=(3,3), dpi=100)
    
    # Red Channel Histogram
    self.redFigure.add_subplot(111).plot(cv.calcHist([self.img],[0],None,[256],[0,256]), color = "red")
    self.redFigure.suptitle("Red Channel")
    self.redCanvas = FigureCanvasTkAgg(self.redFigure, self.root)
    self.redCanvas.get_tk_widget().pack(side="top")  

    # Green Channel Histogram
    self.greenFigure.add_subplot(111).plot(cv.calcHist([self.img],[1],None,[256],[0,256]), color = "green")
    self.greenFigure.suptitle("Green Channel")
    self.greenCanvas = FigureCanvasTkAgg(self.greenFigure, self.root)
    self.greenCanvas.get_tk_widget().pack(side="right")  

    # Blue Channel Histogram
    self.blueFigure.add_subplot(111).plot(cv.calcHist([self.img],[2],None,[256],[0,256]), color = "blue")
    self.blueFigure.suptitle("Blue Channel")
    self.blueCanvas = FigureCanvasTkAgg(self.blueFigure, self.root)
    self.blueCanvas.get_tk_widget().pack(side="right")

    self.toHistMode()

  def donothing():
    pass

Main(Tk())