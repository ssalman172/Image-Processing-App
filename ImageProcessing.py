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
    self.is_grayscale = FALSE

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
    self.histFigure = plt.Figure(figsize=(6,6), dpi=100)
    self.histCanvas = FigureCanvasTkAgg(self.histFigure, self.root)

    # Set up needed action menus
    self.menubar = Menu(self.root)

    ############################# FILE MENUS #############################
    self.fileMenu = Menu(self.menubar)
    self.menubar.add_cascade(label="File", menu=self.fileMenu)
    self.fileMenu.add_command(label="Select Image", command=self.selectImage)
    self.fileMenu.add_command(label="Clear Result", command=self.clearRightPanel)
    self.fileMenu.add_separator()
    self.fileMenu.add_command(label="Exit", command=self.root.quit)

    ############################# EDIT MENUS #############################
    self.editMenu = Menu(self.menubar)
    self.menubar.add_cascade(label="Edit", menu=self.editMenu)

    # Basic arithmetic operation to color value
    self.colorMenu = Menu(self.editMenu)
    self.editMenu.add_cascade(label="Color Value", menu=self.colorMenu)
    self.incColorMenu = Menu(self.colorMenu)
    self.colorMenu.add_cascade(label="Increase Color Value", menu=self.incColorMenu)
    self.incColorMenu.add_command(label="Red Channel", command=lambda: self.increaseColorValue(0))
    self.incColorMenu.add_command(label="Green Channel", command=lambda: self.increaseColorValue(1))
    self.incColorMenu.add_command(label="Blue Channel", command=lambda: self.increaseColorValue(2))
    self.decColorMenu = Menu(self.colorMenu)
    self.colorMenu.add_cascade(label="Decrease Color Value", menu=self.decColorMenu)
    self.decColorMenu.add_command(label="Red Channel", command=lambda: self.decreaseColorValue(0))
    self.decColorMenu.add_command(label="Green Channel", command=lambda: self.decreaseColorValue(1))
    self.decColorMenu.add_command(label="Blue Channel", command=lambda: self.decreaseColorValue(2))

    # Size scaling
    self.scaleMenu = Menu(self.editMenu)
    self.editMenu.add_cascade(label="Image Scale", menu=self.scaleMenu)
    self.scaleMenu.add_command(label="Scaling 2x", command=lambda: self.scaleImage(200))
    self.scaleMenu.add_command(label="Scaling 1/2x", command=lambda: self.scaleImage(50))

    self.editMenu.add_command(label="Gray Scaling", command=self.grayImage)
    self.editMenu.add_command(label="Down Sampling", command=self.downSampling)
    self.editMenu.add_command(label="Quantization", command=self.quantization)
    self.editMenu.add_command(label="Negative Color", command=self.createKlise)

    # Modify Intensity
    self.intensityMenu = Menu(self.editMenu)
    self.editMenu.add_cascade(label="Image Intensity", menu=self.intensityMenu)
    self.intensityMenu.add_command(label="Increase", command=lambda: self.modifyIntensity(70))
    self.intensityMenu.add_command(label="Decrease", command=lambda: self.modifyIntensity(-70))

    ############################# HISTOGRAM MENUS #############################
    self.histMenu = Menu(self.menubar)
    self.menubar.add_cascade(label="Histogram & Filter", menu=self.histMenu)
    self.histMenu.add_command(label="Histogram Equalization", command=self.histEqualization)
    self.histMenu.add_command(label="Low Pass Filter", command=self.lowPassFilter)
    self.histMenu.add_command(label="High Pass Filter", command=self.highPassFilter)
    self.histMenu.add_command(label="Band Pass Filter", command=self.bandPassFilter)

    ############################# VIEW MODE MENUS #############################
    self.viewMenu = Menu(self.menubar)
    self.menubar.add_cascade(label="View Mode", menu=self.viewMenu)
    self.viewMenu.add_command(label="Standard Image", command=self.toImgMode)
    self.viewMenu.add_command(label="Image Histogram", command=self.toHistMode)    

    # self.showBottomPanel()
    self.root.config(menu=self.menubar)
    self.root.mainloop()

  # Handle image selection
  def selectImage(self):
    self.clearLeftPanel()
    self.clearRightPanel()
    self.unpackHistogramCanvas()
    
    filename =  filedialog.askopenfilename(filetypes=[("Image files", ".jpg .jpeg .jp2 .png .tiff .svg .gif .bmp")])
    self.img = cv.cvtColor(cv.imread(filename), cv.COLOR_BGR2RGB)
    image = Image.fromarray(self.img)
    self.baseImg = Image.open(filename)
    self.setSize(image)
    image_tk = ImageTk.PhotoImage(image)

    if(self.viewMode==0):
      self.showLeftPanel(image_tk)
    elif(self.viewMode==1):
      self.clearLeftPanel()
      self.showLeftPanel(image_tk)
      self.showHistogramCanvas()
    self.is_firstImg = FALSE

  # Handle Display Image
  def showImage(self, img):
    if(self.viewMode==0):
      self.showRightPanel(img)
    elif(self.viewMode==1):
      self.clearLeftPanel()
      self.showLeftPanel(img)
      self.showHistogramCanvas()
  
  # Handle thumbnail size
  def setSize(self, img):
    if(self.viewMode==0):
      img.thumbnail(self.imgPanelSize, Image.ANTIALIAS)
    elif(self.viewMode==1):
      img.thumbnail(self.imgPanelSizeHist, Image.ANTIALIAS)

  def handleGray(self, img):
    if(self.is_grayscale == TRUE):
      self.img = cv.cvtColor(img, cv.COLOR_GRAY2RGB)
      self.is_grayscale = FALSE
  
  # Show or Clear panel handlers
  def showLeftPanel(self, img):
    self.panelLeft.configure(image=img)
    self.panelLeft.image = img

  def showRightPanel(self, img):
    self.panelRight.configure(image=img)
    self.panelRight.image = img

  def showBottomPanel(self):
    # RED CHANNEL
    scaleBar = Scale(self.root, from_=0, to=255, length=700, orient=HORIZONTAL)
    scaleBar.pack(side="bottom", pady=(0,10))
    barTitle = Label(self.root, text = "Red Channel")
    barTitle.config(font =("Courier", 11))
    barTitle.pack(side="bottom", pady=(0,0))

    # GREEN CHANNEL
    scaleBar = Scale(self.root, from_=0, to=255, length=700, orient=HORIZONTAL)
    scaleBar.pack(side="bottom", pady=(0,10))
    barTitle = Label(self.root, text = "Green Channel")
    barTitle.config(font =("Courier", 11))
    barTitle.pack(side="bottom", pady=(0,0))

    # BLUE CHANNEL
    scaleBar = Scale(self.root, from_=0, to=255, length=700, orient=HORIZONTAL)
    scaleBar.pack(side="bottom", pady=(0,10))
    barTitle = Label(self.root, text = "Blue Channel")
    barTitle.config(font =("Courier", 11))
    barTitle.pack(side="bottom", pady=(0,0))

  def clearLeftPanel(self):
    self.panelLeft.configure(image='')

  def clearRightPanel(self):
    self.panelRight.configure(image='')
  
  def unpackHistogramCanvas(self):
    self.histCanvas.get_tk_widget().pack_forget()

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
  def increaseColorValue(self, color, value=50):
    self.clearRightPanel()
    self.handleGray(self.img)
    lim = 255

    self.img[:,:,color] = np.clip(self.img[:,:,color]+value, 0, lim)
    increasedImg = Image.fromarray(self.img)
    self.setSize(increasedImg)    
    image_tk = ImageTk.PhotoImage(increasedImg)

    self.showImage(image_tk)

  def decreaseColorValue(self, color, value=50):
    self.clearRightPanel()
    self.handleGray(self.img)
    lim = 0
    
    self.img[:,:,color] = np.clip(self.img[:,:,color]-value, lim, 255)
    decreasedImg = Image.fromarray(self.img)
    self.setSize(decreasedImg)
    image_tk = ImageTk.PhotoImage(decreasedImg)

    self.showImage(image_tk)    

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

    self.showImage(resizedImg)

  def grayImage(self):
    self.clearRightPanel()

    grayedImg = cv.cvtColor(self.img, cv.COLOR_BGR2GRAY)
    
    grayedImg = Image.fromarray(grayedImg)
    self.img = np.array(grayedImg)
    self.setSize(grayedImg)
    image_tk = ImageTk.PhotoImage(grayedImg)

    self.is_grayscale = TRUE
    self.showImage(image_tk)

  def downSampling(self):
    self.clearRightPanel()
    downSampledImg = cv.pyrDown(self.img)
    
    downSampledImg = Image.fromarray(downSampledImg)
    self.img = np.array(downSampledImg)
    self.setSize(downSampledImg)
    image_tk = ImageTk.PhotoImage(downSampledImg)

    self.showImage(image_tk)

  def quantization(self):
    self.clearRightPanel()
    self.handleGray(self.img)
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
    self.setSize(quantizationImg)
    image_tk = ImageTk.PhotoImage(quantizationImg)

    self.showImage(image_tk)    

  def createKlise(self):
    self.clearRightPanel()
    self.handleGray(self.img)

    # 0 = Red, 1 = Green, 2 = Blue
    self.img[:,:,0] = 255 - self.img[:,:,0]
    self.img[:,:,1] = 255 - self.img[:,:,1]
    self.img[:,:,2] = 255 - self.img[:,:,2]

    negativeImg = Image.fromarray(self.img)
    self.img = np.array(negativeImg)
    self.setSize(negativeImg)
    image_tk = ImageTk.PhotoImage(negativeImg)

    self.showImage(image_tk)

  def modifyIntensity(self, value):
    self.clearRightPanel()
    self.handleGray(self.img)

    hsv = cv.cvtColor(self.img, cv.COLOR_RGB2HSV)
    h, s, v = cv.split(hsv)

    if value >= 0:
      lim = 255 - value
      v[v > lim] = 255
      v[v <= lim] += value
    else:
      value = abs(value)
      lim = 0 + value
      v[v < lim] = 0
      v[v >= lim] -= value

    final_hsv = cv.merge((h, s, v))
    self.img = cv.cvtColor(final_hsv, cv.COLOR_HSV2RGB)

    intensityImg = Image.fromarray(self.img)
    self.img = np.array(intensityImg)
    self.setSize(intensityImg)
    image_tk = ImageTk.PhotoImage(intensityImg)

    self.showImage(image_tk)
    
  def histEqualization(self):
    self.clearRightPanel()

    colorChannel = cv.split(self.img)
    equalizedChannel = []
    for ch, color in zip(colorChannel, ['R', 'G', 'B']):
        equalizedChannel.append(cv.equalizeHist(ch))

    equalizedImg = cv.merge(equalizedChannel)

    equalizedImg = Image.fromarray(equalizedImg)
    self.img = np.array(equalizedImg)
    self.setSize(equalizedImg)
    image_tk = ImageTk.PhotoImage(equalizedImg)

    self.showImage(image_tk)
    
  def lowPassFilter (self):
    self.clearRightPanel()

    kernel = np.array([
      [1/9,1/9,1/9],
      [1/9,1/9,1/9],
      [1/9,1/9,1/9]])
    
    lowpassImg = cv.filter2D(self.img, -1, kernel)

    lowpassImg = Image.fromarray(lowpassImg)
    self.img = np.array(lowpassImg)
    self.setSize(lowpassImg)
    image_tk = ImageTk.PhotoImage(lowpassImg)

    self.showImage(image_tk)

  def highPassFilter (self):
    self.clearRightPanel()

    kernel = np.array([
      [0, -1, 0], 
      [-1, 4, -1],
      [0, -1, 0]])

    if (np.sum(kernel)!=0):
      kernel = kernel/(np.sum(kernel))
    else: 1
    highpassImg = cv.filter2D(self.img, -1, kernel)

    highpassImg = Image.fromarray(highpassImg)
    self.img = np.array(highpassImg)
    self.setSize(highpassImg)
    image_tk = ImageTk.PhotoImage(highpassImg)

    self.showImage(image_tk)

  def bandPassFilter (self):
    self.clearRightPanel()

    kernel = np.array([
      [0, -1, 0], 
      [-1, 5, -1],
      [0, -1, 0]])

    if (np.sum(kernel)!=0):
      kernel = kernel/(np.sum(kernel))
    else: 1
    bandpassImg = cv.filter2D(self.img, -1, kernel)

    bandpassImg = Image.fromarray(bandpassImg)
    self.img = np.array(bandpassImg)
    self.setSize(bandpassImg)
    image_tk = ImageTk.PhotoImage(bandpassImg)

    self.showImage(image_tk)

  ################# Image Histogram #################
  def showHistogramCanvas(self):
    self.clearRightPanel()
    self.unpackHistogramCanvas()

    self.histFigure = plt.Figure(figsize=(6,6), dpi=100)
    
    # Red Channel Histogram
    redChannel = self.histFigure.add_subplot(221)
    redChannel.plot(cv.calcHist([self.img],[0],None,[256],[0,256]), color = "red")
    redChannel.title.set_text("Red Channel")

    # Green Channel Histogram
    greenChannel = self.histFigure.add_subplot(222)
    greenChannel.plot(cv.calcHist([self.img],[1],None,[256],[0,256]), color = "green")
    greenChannel.title.set_text("Green Channel")

    # Blue Channel Histogram
    blueChannel = self.histFigure.add_subplot(223)
    blueChannel.plot(cv.calcHist([self.img],[2],None,[256],[0,256]), color = "blue")
    blueChannel.title.set_text("Blue Channel")

    # Assign figure to canvas to show in main window
    self.histFigure.suptitle("Image Histogram")
    self.histCanvas = FigureCanvasTkAgg(self.histFigure, self.root)
    self.histCanvas.get_tk_widget().pack(side="right")  

    self.toHistMode()

  def donothing():
    pass

Main(Tk())