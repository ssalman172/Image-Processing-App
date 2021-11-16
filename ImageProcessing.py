from asyncio.windows_events import NULL
import tkinter as tk
from tkinter import *
from tkinter import filedialog
from PIL import ImageTk, Image
import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt
from skimage import exposure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

plt.rcParams.update({'font.size': 5.5})

class Main:
  def __init__(self, root):
    self.root = root
    self.baseImg = None
    self.img = np.zeros([])
    self.oriImg = np.zeros([])
    self.saveImg = np.zeros([])

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
    self.imgPanelSize = [self.screenWidth//1.2, self.screenHeight//1.2]
    self.imgPanelSizeHist = [self.screenWidth//2, self.screenHeight//2]

    self.panelLeft = tk.Label(self.root, width=int(self.screenWidth//2.15), height=int(self.screenHeight//1.6), relief="ridge")
    self.panelLeft.grid(row=1, column=0, ipadx=20, ipady=20)

    self.panelRight = tk.Label(self.root, width=int(self.screenWidth//2.15), height=int(self.screenHeight//1.6), relief="ridge")
    self.panelRight.grid(row=1, column=1, ipadx=20, ipady=20)

    # Scalebar Variables
    self.redScale = DoubleVar()
    self.redScale.set(120)
    self.greenScale = DoubleVar()
    self.greenScale.set(120)
    self.blueScale = DoubleVar()
    self.blueScale.set(120)

    # Initialize View Mode Information
    self.currentMode = tk.Label(self.root, text = "Standard Image Mode")
    self.currentMode.config(font =("Courier", 14))
    self.currentMode.grid(row=0, column=0, columnspan=2)

    # Initialize Histogram Figures
    self.histFigure = plt.Figure(figsize=(5.2,5.2), dpi=100)
    self.histCanvas = FigureCanvasTkAgg(self.histFigure, self.root)

    # Set up needed action menus
    self.menubar = Menu(self.root)

    ############################# FILE MENUS #############################
    self.fileMenu = Menu(self.menubar)
    self.menubar.add_cascade(label="File", menu=self.fileMenu)
    self.fileMenu.add_command(label="Select Image", command=self.selectImage)
    self.fileMenu.add_command(label="Save Image", command=self.saveImage)
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

    # Modify Intensity
    self.intensityMenu = Menu(self.editMenu)
    self.editMenu.add_cascade(label="Image Intensity", menu=self.intensityMenu)
    self.intensityMenu.add_command(label="Increase", command=lambda: self.modifyIntensity(70))
    self.intensityMenu.add_command(label="Decrease", command=lambda: self.modifyIntensity(-70))

    ############################# VIEW MODE MENUS #############################
    self.viewMenu = Menu(self.menubar)
    self.menubar.add_cascade(label="View Mode", menu=self.viewMenu)
    self.viewMenu.add_command(label="Standard Image", command=self.toImgMode)
    self.viewMenu.add_command(label="Image Histogram", command=self.toHistMode)    

    self.showBottomPanel()
    self.root.config(menu=self.menubar)
    self.root.mainloop()

  # Handle image selection
  def selectImage(self):       
    filename = filedialog.askopenfilename(filetypes=[("Image files", ".jpg .jpeg .jp2 .png .tiff .svg .gif .bmp")])
    if not filename:
        return
    else:
      self.clearLeftPanel()
      self.clearRightPanel()
      self.clearHistogramCanvas()
      self.img = cv.cvtColor(cv.imread(filename), cv.COLOR_BGR2RGB)
      self.oriImg = cv.cvtColor(cv.imread(filename), cv.COLOR_BGR2RGB)
      image = Image.fromarray(self.img)
      self.baseImg = Image.open(filename)

      self.setSize(image)
      image_tk = ImageTk.PhotoImage(image)

      if(self.viewMode==0):
        self.showLeftPanel(image_tk)
        self.showRightPanel(image_tk)
      elif(self.viewMode==1):
        self.clearLeftPanel()
        self.showLeftPanel(image_tk)
        self.showHistogramCanvas()
      self.is_firstImg = FALSE
      self.redScale.set(120)
      self.greenScale.set(120)
      self.blueScale.set(120)

  def saveImage(self):
    filename = filedialog.asksaveasfile(mode='w', defaultextension=".jpg", filetypes=[("Image files", ".jpg .jpeg .jp2 .png .tiff .svg .gif .bmp")])
    if not filename:
        return
    self.saveImg.save(filename)
  
  def setImgArray(self, img):
    self.saveImg = img
    self.img = np.array(img)

  # Reset effect
  def clearEffect(self):
    self.handleGray(self.img)
    self.img = self.oriImg
    img = Image.fromarray(self.img)
    self.setSize(img)
    img = ImageTk.PhotoImage(img)
    self.clearLeftPanel()
    self.clearRightPanel()
    self.showLeftPanel(img)
    self.clearHistogramCanvas()
    if(self.viewMode==0):
      self.showRightPanel(img)
    else:
      self.showHistogramCanvas()
    self.redScale.set(120)
    self.greenScale.set(120)
    self.blueScale.set(120)

  # Handle Display Image
  def showImage(self, img):
    if(self.viewMode==0):
      oriImg = Image.fromarray(self.oriImg)
      self.setSize(oriImg)
      oriImg = ImageTk.PhotoImage(oriImg)
      self.showLeftPanel(oriImg)
      self.showRightPanel(img)
    elif(self.viewMode==1):
      self.clearLeftPanel()
      self.showLeftPanel(img)
      self.showHistogramCanvas()
  
  # Handle thumbnail size
  def setSize(self, img):
    img.thumbnail(self.imgPanelSize, Image.ANTIALIAS)

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
    self.showButtonPanel()
    self.showColorPanel()

  def showButtonPanel(self):
    buttonFrame = tk.Frame(self.root)
    buttonFrame.grid(row=2, column=0)

    clearEffBtn = tk.Button(buttonFrame, text="Clear Effect", command=self.clearEffect)
    clearEffBtn.grid(row=0, column=0, sticky="ewns", rowspan=3, padx=(0,15))

    grayBtn = tk.Button(buttonFrame, text="Gray Scaling", command=self.grayImage)
    grayBtn.grid(row=0, column=1, sticky="ew")

    samplingBtn = tk.Button(buttonFrame, text="Down Sampling", command=self.downSampling)
    samplingBtn.grid(row=0, column=2, sticky="ew")

    quantizeBtn = tk.Button(buttonFrame, text="Image Quantization", command=self.quantization)
    quantizeBtn.grid(row=2, column=1, sticky="ew")

    kliseBtn = tk.Button(buttonFrame, text="Negative Image", command=self.createKlise)
    kliseBtn.grid(row=2, column=2, sticky="ew")

    lowpassBtn = tk.Button(buttonFrame, text="Lowpass Filter", command=self.lowPassFilter)
    lowpassBtn.grid(row=0, column=3, sticky="ew", padx=(15,0))

    highpassBtn = tk.Button(buttonFrame, text="Highpass Filter", command=self.highPassFilter)
    highpassBtn.grid(row=1, column=3, sticky="ew", padx=(15,0))

    bandpassBtn = tk.Button(buttonFrame, text="Bandpass Filter", command=self.bandPassFilter)
    bandpassBtn.grid(row=2, column=3, sticky="ew", padx=(15,0))

    histSqualizationBtn = tk.Button(buttonFrame, text="Histogram Equalization", command=self.histEqualization)
    histSqualizationBtn.grid(row=0, column=4, sticky="ewns", rowspan=3)

    histSpecificationBtn = tk.Button(buttonFrame, text="Histogram Specification", command=self.histSpecification)
    histSpecificationBtn.grid(row=0, column=5, sticky="ewns", rowspan=3)

  def showColorPanel(self):
    colorFrame = tk.Frame(self.root)
    colorFrame.grid(row=2, column=1)
    # RED CHANNEL
    redFrame = tk.Frame(colorFrame)
    redFrame.grid(row=0, column=0)
    barTitle = Label(redFrame, text = "RED")
    barTitle.config(font =("Courier", 11))
    barTitle.grid(row=0, column=0)
    scaleBar = Scale(redFrame, from_=0, to=255, length=500, orient=HORIZONTAL, command=self.modifyRedChannel, variable=self.redScale)
    scaleBar.grid(row=0, column=1)

    # GREEN CHANNEL
    greenFrame = tk.Frame(colorFrame)
    greenFrame.grid(row=1, column=0)
    barTitle = Label(greenFrame, text = "GREEN")
    barTitle.config(font =("Courier", 11))
    barTitle.grid(row=0, column=0)
    scaleBar = Scale(greenFrame, from_=0, to=255, length=500, orient=HORIZONTAL, command=self.modifyGreenChannel, variable=self.greenScale)
    scaleBar.grid(row=0, column=1)

    # BLUE CHANNEL
    blueFrame = tk.Frame(colorFrame)
    blueFrame.grid(row=2, column=0)
    barTitle = Label(blueFrame, text = "BLUE")
    barTitle.config(font =("Courier", 11))
    barTitle.grid(row=0, column=0)
    scaleBar = Scale(blueFrame, from_=0, to=255, length=500, orient=HORIZONTAL, command=self.modifyBlueChannel, variable=self.blueScale)
    scaleBar.grid(row=0, column=1)

    # INTENSITY
    intensityFrame = tk.Frame(colorFrame)
    intensityFrame.grid(row=3, column=0)
    barTitle = Label(intensityFrame, text = "INTENSITY")
    barTitle.config(font =("Courier", 11))
    barTitle.grid(row=0, column=0)
    scaleBar = Scale(intensityFrame, from_=-30, to=30, length=500, orient=HORIZONTAL, command=self.modifyIntensity)
    scaleBar.grid(row=0, column=1)    

  def clearLeftPanel(self):
    self.panelLeft.configure(image='')

  def clearRightPanel(self):
    self.panelRight.configure(image='')
  
  def clearHistogramCanvas(self):
    self.histCanvas.get_tk_widget().grid_remove()

  # Handle view mode changes
  def refreshImg(self):
    img = Image.fromarray(self.img)
    self.setSize(img)
    img = ImageTk.PhotoImage(img)
    self.showImage(img)

  def toImgMode(self):
    self.viewMode = 0
    self.showCurrentModeText()
    self.clearHistogramCanvas()
    self.panelRight.grid(row=1, column=1, ipadx=20, ipady=20)

    self.refreshImg()

  def toHistMode(self):
    self.viewMode = 1
    self.showCurrentModeText()
    self.clearRightPanel()
    self.showHistogramCanvas()

    self.refreshImg()

  def showCurrentModeText(self):
    if(self.currentMode != NULL):
      self.currentMode.destroy()

    if (self.viewMode == 0):
      self.currentMode = tk.Label(self.root, text = "Standard Image Mode")
      self.currentMode.config(font =("Courier", 14))
      self.currentMode.grid(row=0, column=0, columnspan=2)
    elif (self.viewMode == 1):
      self.currentMode = tk.Label(self.root, text = "Image Histogram Mode")
      self.currentMode.config(font =("Courier", 14))
      self.currentMode.grid(row=0, column=0, columnspan=2)


  ################# Image Processing Operations #################
  def modifyRedChannel(self, val):
    self.clearRightPanel()
    self.handleGray(self.img)
    value = int(val)

    self.img[:,:,0] = value

    modifiedRed = Image.fromarray(self.img)
    self.setImgArray(modifiedRed)
    self.setSize(modifiedRed)    
    image_tk = ImageTk.PhotoImage(modifiedRed)

    self.showImage(image_tk)

  def modifyGreenChannel(self, val):
    self.clearRightPanel()
    self.handleGray(self.img)
    value = int(val)

    self.img[:,:,1] = value

    modifiedGreen = Image.fromarray(self.img)
    self.setImgArray(modifiedGreen)
    self.setSize(modifiedGreen)    
    image_tk = ImageTk.PhotoImage(modifiedGreen)

    self.showImage(image_tk)

  def modifyBlueChannel(self, val):
    self.clearRightPanel()
    self.handleGray(self.img)
    value = int(val)

    self.img[:,:,2] = value
    
    modifiedBlue = Image.fromarray(self.img)
    self.setImgArray(modifiedBlue)
    self.setSize(modifiedBlue)    
    image_tk = ImageTk.PhotoImage(modifiedBlue)

    self.showImage(image_tk)

  def increaseColorValue(self, color, value=50):
    self.clearRightPanel()
    self.handleGray(self.img)
    lim = 255

    self.img[:,:,color] = self.img[:,:,color] = np.clip(self.img[:,:,color]+value, 0, lim)
    increasedImg = Image.fromarray(self.img)
    self.setImgArray(increasedImg)
    self.setSize(increasedImg)    
    image_tk = ImageTk.PhotoImage(increasedImg)

    self.showImage(image_tk)

  def decreaseColorValue(self, color, value=50):
    self.clearRightPanel()
    self.handleGray(self.img)
    lim = 0
    
    self.img[:,:,color] = np.clip(self.img[:,:,color]-value, lim, 255)
    decreasedImg = Image.fromarray(self.img)
    self.setImgArray(decreasedImg)
    self.setSize(decreasedImg)
    image_tk = ImageTk.PhotoImage(decreasedImg)

    self.showImage(image_tk)    

  def scaleImage(self, scalePercent):
    self.clearRightPanel()

    imgScale = scalePercent
    imgHeight = int(self.screenWidth//1.2 * (imgScale / 100))
    imgWidth = int(self.screenHeight//1.2 * (imgScale / 100))
    dimension = (imgWidth, imgHeight)

    resizedImg = cv.resize(self.img, dimension, interpolation = cv.INTER_LINEAR)
    resizedImg = Image.fromarray(resizedImg, 'RGB')
    self.baseImg = resizedImg
    self.img = np.array(resizedImg)
    resizedImg = ImageTk.PhotoImage(resizedImg)

    self.showImage(resizedImg)

  def grayImage(self):
    self.clearRightPanel()
    self.handleGray(self.img)
    grayedImg = cv.cvtColor(self.img, cv.COLOR_BGR2GRAY)
    
    grayedImg = Image.fromarray(grayedImg)
    self.setImgArray(grayedImg)
    self.setSize(grayedImg)
    image_tk = ImageTk.PhotoImage(grayedImg)

    self.is_grayscale = TRUE
    self.showImage(image_tk)

  def downSampling(self):
    self.clearRightPanel()
    self.handleGray(self.img)
    imgHeight = self.img.shape[0]
    imgWidth = self.img.shape[1]
    downsample = 64

    numHeight, numWidth = imgHeight / downsample, imgWidth / downsample

    for i in range(downsample):
    #  Get Y coordinates
      y = int(i * numHeight)
      for j in range(downsample):
          #  Get  X  coordinates 
          x = int(j * numWidth)
          #  Get fill color , Pixel dot in upper left corner 
          r = self.img[y, x][0]
          g = self.img[y, x][1]
          b = self.img[y, x][2]

          #  Loop setting small area sampling 
          for n in range(int(numHeight)):
              for m in range(int(numWidth)):
                  self.img[y+n, x+m][0] = np.uint8(r)
                  self.img[y+n, x+m][1] = np.uint8(g)
                  self.img[y+n, x+m][2] = np.uint8(b)

    downSampledImg = Image.fromarray(self.img)
    self.setImgArray(downSampledImg)
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
    self.setImgArray(quantizationImg)
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
    self.setImgArray(negativeImg)
    self.setSize(negativeImg)
    image_tk = ImageTk.PhotoImage(negativeImg)

    self.showImage(image_tk)

  def modifyIntensity(self, val):
    self.clearRightPanel()
    self.handleGray(self.img)
    value = int(val)

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
    self.setImgArray(intensityImg)
    self.setSize(intensityImg)
    image_tk = ImageTk.PhotoImage(intensityImg)

    self.showImage(image_tk)
    
  def histEqualization(self):
    self.clearRightPanel()
    self.handleGray(self.img)

    colorChannel = cv.split(self.img)
    equalizedChannel = []
    for ch, color in zip(colorChannel, ['R', 'G', 'B']):
        equalizedChannel.append(cv.equalizeHist(ch))

    equalizedImg = cv.merge(equalizedChannel)

    equalizedImg = Image.fromarray(equalizedImg)
    self.setImgArray(equalizedImg)
    self.setSize(equalizedImg)
    image_tk = ImageTk.PhotoImage(equalizedImg)

    self.showImage(image_tk)
  
  def histSpecification(self):
    self.handleGray(self.img)
    # load image reference
    filename = filedialog.askopenfilename(filetypes=[("Image files", ".jpg .jpeg .jp2 .png .tiff .svg .gif .bmp")])
    if not filename:
        return
    imgRef = cv.cvtColor(cv.imread(filename), cv.COLOR_BGR2RGB)

    # determine if we are performing multichannel histogram matching
    # and then perform histogram matching itself
    if(self.img.shape[-1] > 1):
      multi = True
    else:
      multi = False

    matchedImg = exposure.match_histograms(self.img, imgRef, multichannel=multi)

    matchedImg = Image.fromarray(matchedImg)
    self.setImgArray(matchedImg)
    self.setSize(matchedImg)
    image_tk = ImageTk.PhotoImage(matchedImg)

    self.showImage(image_tk)
    
  def lowPassFilter (self):
    self.clearRightPanel()

    kernel = np.array([
      [1/9,1/9,1/9],
      [1/9,1/9,1/9],
      [1/9,1/9,1/9]])
    
    lowpassImg = cv.filter2D(self.img, -1, kernel)

    lowpassImg = Image.fromarray(lowpassImg)
    self.setImgArray(lowpassImg)
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
    self.setImgArray(highpassImg)
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
    self.setImgArray(bandpassImg)
    self.setSize(bandpassImg)
    image_tk = ImageTk.PhotoImage(bandpassImg)

    self.showImage(image_tk)

  ################# Image Histogram #################
  def showHistogramCanvas(self):
    self.panelRight.grid_remove()
    self.clearHistogramCanvas()

    self.histFigure = plt.Figure(figsize=(5.2,5.2), dpi=100)
    
    if(self.is_grayscale == FALSE):
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
      self.histCanvas.get_tk_widget().grid(row=1, column=1)
    else:
      grayHist = self.histFigure.add_subplot(111)
      grayHist.plot(cv.calcHist([self.img], [0], None, [256], [0, 256]), color = "gray")
      self.histFigure.suptitle("Gray Image Histogram")
      self.histCanvas = FigureCanvasTkAgg(self.histFigure, self.root)
      self.histCanvas.get_tk_widget().grid(row=1, column=1)

  def donothing():
    pass

Main(Tk())