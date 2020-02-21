import tkinter as tk
import os
import glob
from PIL import Image, ImageTk
from tkinter import messagebox
from tkinter import filedialog
from tkinter.simpledialog import askstring

font = ('Arial', 12)
DEST_SIZE = 800, 520
COLORS = ['red', 'blue', 'cyan', 'green', 'purple', 'violet', 'black']

class labelImg():
    def __init__(self, master):
        self.parent = master
        self.parent.title('Image Labeling Tool')
        self.frame = tk.Frame(self.parent)
        self.frame.pack(fill=tk.BOTH, expand=1)
        self.parent.resizable(tk.TRUE, tk.TRUE)

        self.imageDir = ''
        self.imageList = []
        self.outputDir = ''
        self.cur = 0
        self.total = 0
        self.imageName = ''
        self.labelFileName = ''
        self.tkimg = None

        # set up mouse state
        self.STATE = {}
        self.STATE['click'] = 0
        self.STATE['X'], self.STATE['y'] = 0, 0
        self.STATE['draw'] = 0

        # set up label
        self.labelIdList = []
        self.labelId = None
        self.labelList = []
        self.hl = None
        self.vl = None

        # set up GUI
        self.label = tk.Label(self.frame, text='Image directory:')
        self.label.grid(row=0, column=0, sticky=tk.E + tk.W)
        self.filepath = tk.StringVar()
        self.entry = tk.Entry(self.frame, textvariable=self.filepath, state='readonly')
        self.entry.grid(row=0, column=1, sticky=tk.E + tk.W)
        self.ldBtn = tk.Button(self.frame, text='Open directory', command=self.loadDir)
        self.ldBtn.grid(row=0, column=2, sticky=tk.W + tk.E)

        # control panel
        self.ctrPanel = tk.Frame(self.frame)
        self.ctrPanel.grid(row=1, column=0, sticky=tk.N)

        # file panel
        self.filePanel = tk.Frame(self.ctrPanel)
        self.filePanel.pack(anchor=tk.N)
        self.fileListLb = tk.Label(self.filePanel, text='fileList', width=25)
        self.fileListLb.pack()
        # set scroll bar
        self.scrollbar1 = tk.Scrollbar(self.filePanel)
        self.scrollbar1.pack(side=tk.RIGHT, fill=tk.Y)
        self.scrollbar2 = tk.Scrollbar(self.filePanel, orient=tk.HORIZONTAL)
        self.scrollbar2.pack(side=tk.BOTTOM, fill=tk.X, anchor=tk.S)
        self.fileList = tk.Listbox(self.filePanel, width=25, height=20,
                                   yscrollcommand=self.scrollbar1.set, xscrollcommand=self.scrollbar2.set)
        self.fileList.pack()
        self.fileList.bind('<Double-Button-1>', self.changeImage)
        self.scrollbar1.config(command=self.fileList.yview)
        self.scrollbar2.config(command=self.fileList.xview)

        self.prevBtn = tk.Button(self.ctrPanel, text='prev Image', width=25, command=self.prevImage)
        self.prevBtn.pack()
        self.nextBtn = tk.Button(self.ctrPanel, text='next Image', width=25, command=self.nextImage)
        self.nextBtn.pack()
        self.circleBtn = tk.Button(self.ctrPanel, text='draw circle', width=25, command=self.drawCircle)
        self.circleBtn.pack()
        self.rectBtn = tk.Button(self.ctrPanel, text='draw rectangle', width=25, command=self.drawRect)
        self.rectBtn.pack()

        # main panel for image labeling
        self.imgPanel = tk.Canvas(self.frame, width=DEST_SIZE[0], height=DEST_SIZE[1], bg='white', cursor='tcross')
        self.imgPanel.bind('<Button-1>', self.mouseClick)
        self.imgPanel.bind('<Motion>', self.mouseMove)
        self.parent.bind('<Escape>', self.cancelBox)  # press <Escape> to cancel
        self.parent.bind('s', self.cancelBox)
        self.parent.bind('a', self.prevImage)
        self.parent.bind('d', self.nextImage)
        self.imgPanel.grid(row=1, column=1, sticky=tk.N)

        # label panel
        self.labelPanel = tk.Frame(self.frame)
        self.labelPanel.grid(row=1, column=2, sticky=tk.N)

        # label list panel
        self.labelListPanel = tk.Frame(self.labelPanel)
        self.labelIdListLb = tk.Label(self.labelListPanel, text='LabelIdList')
        self.labelIdListLb.pack(anchor=tk.N)
        self.scrollbar3 = tk.Scrollbar(self.labelListPanel)
        self.scrollbar3.pack(side=tk.RIGHT, fill=tk.Y)
        self.scrollbar4 = tk.Scrollbar(self.labelListPanel, orient=tk.HORIZONTAL)
        self.scrollbar4.pack(side=tk.BOTTOM, fill=tk.X, anchor=tk.S)
        self.labelIdListBox = tk.Listbox(self.labelListPanel, width=25, height=20,
                                         yscrollcommand=self.scrollbar3.set, xscrollcommand=self.scrollbar4.set)
        self.labelIdListBox.pack()
        self.scrollbar3.config(command=self.labelIdListBox.yview)
        self.scrollbar4.config(command=self.labelIdListBox.xview)
        self.labelListPanel.pack(anchor=tk.N)
        self.delBtn = tk.Button(self.labelPanel, text='Delete', width=25, command=self.deleteLabel)
        self.delBtn.pack()
        self.clearBtn = tk.Button(self.labelPanel, text='clear All', width=25, command=self.clearLabels)
        self.clearBtn.pack()
        self.saveBtn = tk.Button(self.labelPanel, text='save', width=25, command=self.saveImage)
        self.saveBtn.pack()
        self.disp = tk.Label(self.labelPanel, text='x: 0.00, y: 0.00')
        self.disp.pack()

    def loadDir(self):
        self.imageDir = filedialog.askdirectory()
        self.parent.focus()
        # print('imageDir', self.imageDir)
        if not os.path.isdir(self.imageDir):
            messagebox.showerror("Error!", message="directory doesn't exist!")
            return

        self.filepath.set(self.imageDir)
        self.imageList = glob.glob(os.path.join(self.imageDir, '*.jpg'))
        if len(self.imageList) == 0:
            print('No .jpg image found in the directory!')
            messagebox.showerror('Error!', 'No .jpg image file found in the directory!')
            return

        if self.fileList.size() > 0:
            self.fileList.delete(0, tk.END)

        for imagepath in self.imageList:
            imagename = os.path.split(imagepath)[-1]
            self.fileList.insert(tk.END, imagename)

        self.cur = 0
        self.total = len(self.imageList)
        print(self.total)
        # print(self.imageDir)
        self.outputDir = os.path.join(self.imageDir, r'labels')
        # print(self.outputDir)
        if not os.path.exists(self.outputDir):
            os.mkdir(self.outputDir)
        # print(self.imageDir)
        # print(self.outputDir)
        # filelist = glob.glob(os.path.join(self.imageDir, '*.jpg'))
        self.loadImage()

    def loadImage(self):
        print(self.cur)
        imagepath = self.imageList[self.cur]
        img = Image.open(imagepath)
        self.fileList.activate(self.cur)
        # print(imagepath)
        w, h = img.size
        # print(w, h)
        factor = 1
        if w > h:
            if w > DEST_SIZE[0]:
                factor = DEST_SIZE[0] / w
        else:
            if h > DEST_SIZE[1]:
                factor = DEST_SIZE[1] / h
        w1 = int(w * factor)
        h1 = int(h * factor)
        # print(w1, h1)
        img = img.resize((w1, h1), Image.ANTIALIAS)
        self.tkimg = ImageTk.PhotoImage(img)
        self.imgPanel.create_image(DEST_SIZE[0] / 2, DEST_SIZE[1] / 2,
                                   image=self.tkimg, anchor=tk.CENTER)
        #load labels
        self.clearLabels()
        self.imageName = os.path.split(imagepath)[-1].split('.')[0]
        labelname = self.imageName + '.txt'
        self.labelFileName = os.path.join(self.outputDir, labelname)
        if os.path.exists(self.labelFileName):
            with open(self.labelFileName) as f:
                for (i, line) in enumerate(f):
                    if i == 0:
                        continue
                    # print(line)
                    info = [(t.strip()) for t in line.split()]
                    # print('**************')
                    # print(DEST_SIZE)
                    # print('tmp[0, 1, 2, 3, 4] === %.2f, %.2f, %.2f %.2f %d %s' %
                      #    (float(info[0]), float(info[1]), float(info[2]), float(info[3]), int(info[4]), info[5]))
                    # print('***************')
                    self.labelList.append(tuple(info))
                    info[0] = float(info[0])
                    info[1] = float(info[1])
                    info[2] = float(info[2])
                    info[3] = float(info[3])
                    info[4] = int(info[4])
                    tx0 = int(info[0] * DEST_SIZE[0])
                    ty0 = int(info[1] * DEST_SIZE[1])
                    tx1 = int(info[2] * DEST_SIZE[0])
                    ty1 = int(info[3] * DEST_SIZE[1])
                    # print('tx0, ty0, tx1, ty1')
                    # print(tx0, ty0, tx1, ty1)
                    if info[4] == 0:
                        tmpId = self.imgPanel.create_rectangle(
                            tx0, ty0, tx1, ty1, width=2, outline=COLORS[(len(self.labelList) - 1) % len(COLORS)]
                        )
                    else:
                        tmpId = self.imgPanel.create_oval(
                            tx0, ty0, tx1, ty1, width=2, outline=COLORS[(len(self.labelList) - 1) % len(COLORS)]
                        )
                    self.labelIdList.append(tmpId)
                    self.labelIdListBox.insert(tk.END, info[5])
                    self.labelIdListBox.itemconfig(len(self.labelIdList) - 1,
                                            fg=COLORS[(len(self.labelIdList) - 1) % len(COLORS)])

    def saveImage(self):
        if len(self.labelList) > 0:
            with open(self.labelFileName, 'w') as f:
                f.write('%d\n' % len(self.labelList))
                for label in self.labelList:
                    f.write(' '.join(map(str, label)) + '\n')
            # print('Image saved')

    def mouseClick(self, event):
        if self.STATE['click'] == 0:
            self.STATE['x'], self.STATE['y'] = event.x, event.y
        else:
            if self.STATE['draw'] == 0:
                x1, x2 = min(self.STATE['x'], event.x), max(self.STATE['x'], event.x)
                y1, y2 = min(self.STATE['y'], event.y), max(self.STATE['y'], event.y)
                x1, x2 = x1 / DEST_SIZE[0], x2 / DEST_SIZE[0]
                y1, y2 = y1 / DEST_SIZE[1], y2 / DEST_SIZE[1]
                # print(self.labelId)
                # print(self.labelIdList)
            else:
                r = ((event.x - self.STATE['x'])**2 + (event.y - self.STATE['y'])**2)**0.5
                x1, x2 = self.STATE['x'] - r, self.STATE['x'] + r
                y1, y2 = self.STATE['y'] - r, self.STATE['y'] + r
                x1, x2 = x1 / DEST_SIZE[0], x2 / DEST_SIZE[0]
                y1, y2 = y1 / DEST_SIZE[1], y2 / DEST_SIZE[1]

            labelname = askstring('label name', 'input label name')
            # print(labelname)
            if labelname is not None and labelname != '':
                self.labelList.append((x1, y1, x2, y2, self.STATE['draw'], labelname))
                self.labelIdList.append(self.labelId)
                self.labelId = None
                # self.labelIdListBox.insert(tk.END, '(%.2f, %.2f)-(%.2f, %.2f)' % (x1, y1, x2, y2))
                self.labelIdListBox.insert(tk.END, labelname)
                self.labelIdListBox.itemconfig(len(self.labelIdList) - 1, fg=COLORS[(len(self.labelIdList) - 1) % len(COLORS)])
            else:
                self.imgPanel.delete(self.labelId)
                self.labelId = None
        self.STATE['click'] = 1 - self.STATE['click']

    def mouseMove(self, event):
        self.disp.config(text='x: %.2f, y: %.2f' % (event.x / DEST_SIZE[0], event.y / DEST_SIZE[1]))
        if self.tkimg:
            if self.hl:
                self.imgPanel.delete(self.hl)
            self.hl = self.imgPanel.create_line(0, event.y, DEST_SIZE[0], event.y, width=2)
            if self.vl:
                self.imgPanel.delete(self.vl)
            self.vl = self.imgPanel.create_line(event.x, 0, event.x, DEST_SIZE[1], width=2)

        if 1 == self.STATE['click']:
            if 0 == self.STATE['draw']:
                if self.labelId:
                    self.imgPanel.delete(self.labelId)
                self.labelId = self.imgPanel.create_rectangle(
                    self.STATE['x'], self.STATE['y'], event.x, event.y, width=2,
                    outline=COLORS[len(self.labelList) % len(COLORS)])
            else:
                if self.labelId:
                    self.imgPanel.delete(self.labelId)
                r = ((event.x - self.STATE['x'])**2 + (event.y - self.STATE['y'])**2)**0.5
                self.labelId = self.imgPanel.create_oval(
                    self.STATE['x'] - r, self.STATE['y'] - r, self.STATE['x'] + r, self.STATE['y'] + r,
                    width=2, outline=COLORS[len(self.labelList) % len(COLORS)])

    def cancelBox(self, event):
        if 1 == self.STATE['click']:
            if self.labelId:
                self.imgPanel.delete(self.labelId)
                self.labelId = None
                self.STATE['click'] = 0

    def deleteLabel(self):
        selected = self.labelIdListBox.curselection()
        if len(selected) != 1:
            return
        idx = int(selected[0])
        self.imgPanel.delete(self.labelIdList[idx])
        self.labelIdList.pop(idx)
        self.labelList.pop(idx)
        self.labelIdListBox.delete(idx)

    def clearLabels(self):
        for idx in range(len(self.labelIdList)):
            self.imgPanel.delete(self.labelIdList[idx])
        self.labelIdListBox.delete(0, len(self.labelList))
        self.labelIdList = []
        self.labelList = []

    def prevImage(self, event=None):
        if self.total == 0:
            return
        self.saveImage()
        if self.cur > 0:
            self.cur -= 1
        else:
            self.cur = self.total - 1
        self.loadImage()

    def nextImage(self, event=None):
        if self.total == 0:
            return
        self.saveImage()
        if self.cur < self.total - 1:
            self.cur += 1
        else:
            self.cur = 0
        self.loadImage()

    def changeImage(self, event=None):
        if self.total == 0:
            return
        self.saveImage()
        print(self.cur)
        self.cur = int(self.fileList.curselection()[0])
        self.loadImage()
        # print(self.fileList.curselection())

    def drawCircle(self):
        self.STATE['draw'] = 1

    def drawRect(self):
        self.STATE['draw'] = 0


if __name__ == '__main__':
    root = tk.Tk()
    # root.geometry('1280x720')
    labelImg = labelImg(root)
    root.mainloop()
