# to do:
# print loaded filename to panel (DONE)
# create button to generate line pixel sum text doc.  Button will generate a dialog for user to select path and filename. (DONE)
# create a confirmation dialog for saving text file. (DONE)
# analyze side bars *idea, try rotating image 90 degrees after loading (DONE) *idea worked
# batch load (DONE)
# analyse images input and compare aspect ratio against either a user input value or the value of one frame (first frame)
#   print out which frame deviates from the batch to a doc file. (DONE)
# extend to UHD both 16x9 and 4x3 (DONE)
# load a pro res / video file (DONE)
# Sample video source to expedite analysis (DONE)
# Add extract all frames function. (DONE)
# Exclude frames with hard visible mattes undefined. e.g. The star wars 'in a galaxy...' opening (DONE)
# Define black frames and exclude from analysis. *Note: all black frames will return a Divide-by-zero error (DONE)
# Open report text document automatically after running function (DONE)
# Add line numbers to print_line_sum (DONE, but could be improved)

# load dpx *NOTE: dpx requires a hack that won't work with the algorithm since the getdata() method isn't available.
# Add function to be able to input either the frame or timecode and the amount of frames or the end timecode to extract
# Add style to text to highlight filenames and paths in both output text doc and message boxes

# Add exception to analyzer module in case something other than HD or UHD images are loaded (need to apply to compare functions)
# report the found base aspect ratio in a message box before analyzing
# apply undefined mattes check to menu_load & menu_load_pbox functions
# apply black frame handling to compare functions
# Add a check to ths Save Line Sum function to allow user to load a file if one hasn't been loaded yet,
# Add what the resolution of the 'not supported frame' is to the error message

# exceptions:
# 1. Not HD or UHD full raster frame
# 2. Frame is all black
# 3. Frame has undefined mattes


import wx, os, wx.media, cv2, subprocess, stat
from aspectRatioANALyzer import *
from aspectRatioANALyzer_pBox import *
# import dpx


wildcard = 'image file (*.png)|*.png|, ' \
           '(*.jpg)|*.jpg|' \
            '(*.tif)|*.tif|' \
            '(*.jp2)|*.jp2|' \
            '(*.dpx)|*.dpx|' #\
           # 'all files (*.*)|*.*|'

wildcard_video = 'video file (*.mov)|*.mov|, ' \
           '(*.avi)|*.avi|' \
            '(*.mp4)|*.mp4|' \
            '(*.mxf)|*.mxf|' \
            '(*.mpeg)|*.mpeg|' #\
           # 'all files (*.*)|*.*|'


class Annie(wx.Frame):

    def __init__(self, parent, id):
        wx.Frame.__init__(self, parent, id, 'Annie', size=(1000, 500))
        self.CenterOnScreen()
        self.CreateStatusBar()

        self.panel=wx.Panel(self)
        self.panel.SetBackgroundColour('orange')

        self.answer_font = wx.Font(25, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        self.pBox = False

        ### Empty static text to destroy for purposes of resetting
        self.text_filename = wx.StaticText(self.panel, -1, '', (30, 50))
        self.text_res = wx.StaticText(self.panel, -1, '', (30, 150))
        self.text_ar = wx.StaticText(self.panel, -1, '', (30, 250))
        self.file_names = ''
        self.path_names = ''
        self.video_path_names = ''
        self.video_file_names = ''

        ### Create buttons
        self.exit_button=wx.Button(self.panel, label='Quit', pos=(900,400), size=(60,60))
        self.PLS_button=wx.Button(self.panel, label='Pixel Line Sum', pos=(800,30), size=(150,20))

        # Event Handler Binding for buttons
        self.Bind(wx.EVT_BUTTON, self.close_button, self.exit_button)
        self.Bind(wx.EVT_CLOSE, self.close_window)
        self.Bind(wx.EVT_BUTTON, self.write_line_sum, self.PLS_button)

        # Creating a bitmap button
        hitmonlee = wx.Bitmap('/Users/delue003/PycharmProjects/hitmonlee_button.jpg')
        self.hitmonlee_button = wx.BitmapButton(self.panel, -1, hitmonlee, pos=(800,80))
        self.Bind(wx.EVT_BUTTON, self.frame_capture_sample, self.hitmonlee_button)
        self.hitmonlee_button.SetDefault()

        squirtle = wx.Bitmap('/Users/delue003/PycharmProjects/squirtle_button.jpg')
        self.squirtle_button = wx.BitmapButton(self.panel, -1, squirtle, pos=(800,220))
        self.Bind(wx.EVT_BUTTON, self.frame_capture, self.squirtle_button)
        self.squirtle_button.SetDefault()

        # Header text
        wx.StaticText(self.panel, -1, 'Filename:', (30, 25))
        wx.StaticText(self.panel, -1, 'The resolution of the image is:', (30, 125))
        wx.StaticText(self.panel, -1, 'Which is equivalent to:', (30, 225))
        # fancy_text = wx.StaticText(panel, -1, 'This is an example of stylyzed static text', (10, 100), (500,-1), wx.ALIGN_CENTER)
        # fancy_text.SetForegroundColour('green')
        # fancy_text.SetBackgroundColour('black')

        ### Let the Menu's begin! ###
        menu_bar=wx.MenuBar()
        menu1=wx.Menu()
        # menu2=wx.Menu()
        item = wx.MenuItem(menu1, 500, '&Load Image\tCtrl+O', 'Load an image file')
        item.SetBitmap(wx.Bitmap('/Users/delue003/PyCharmProjects/kirby_button.jpg'))
        item2 = wx.MenuItem(menu1, 501, '&Save Line Sum\tCtrl+S', 'Create a text file with LinePixelSum Values')
        item2.SetBitmap(wx.Bitmap('/Users/delue003/PyCharmProjects/charmander_button.jpg'))
        item3 = wx.MenuItem(menu1, 502, '&Load Pillar-Box Image\tCtrl+P', 'Load a pillar-boxed image')
        item3.SetBitmap(wx.Bitmap('/Users/delue003/PyCharmProjects/bulbasaur_button.jpg'))
        item4 = wx.MenuItem(menu1, 503, '&Compare\tCtrl+C', 'Compares aspect ratios of loaded images')
        item4.SetBitmap(wx.Bitmap('/Users/delue003/PyCharmProjects/jigglypuff_button.jpg'))
        item5 = wx.MenuItem(menu1, 504, '&Compare_pBox\tCtrl+L', 'Compares aspect ratios of loaded pillar-boxed images')
        item5.SetBitmap(wx.Bitmap('/Users/delue003/PyCharmProjects/megaMan_button.jpg'))
        menu1.Append(item)
        menu1.Append(item2)
        menu1.Append(item3)
        menu1.Append(item4)
        menu1.Append(item5)
        menu_bar.Append(menu1, '&File')
        # menu_bar.Append(menu1, '&Save')

        self.SetMenuBar(menu_bar)

        # Event Handler Bindings for menu items
        self.Bind(wx.EVT_MENU, self.load, id=500)
        self.Bind(wx.EVT_MENU, self.write_line_sum, id=501)
        self.Bind(wx.EVT_MENU, self.load_pBox, id=502)
        self.Bind(wx.EVT_MENU, self.compare, id=503)
        self.Bind(wx.EVT_MENU, self.compare_pBox, id=504)

        ### Basic input text box
        # text_box = wx.TextEntryDialog(None, 'Hello, what is your name?', 'TITLE GOES HERE', 'enter name ')
        # if text_box.ShowModal() == wx.ID_OK:
        #     name = text_box.GetValue()

        ### Basic binary text box
        # box=wx.MessageDialog(None, 'Are you winning today?', 'How Are You?', wx.YES_NO)
        # winning=box.ShowModal()
        # box.Destroy()
        # if winning == 5103:
        #     print(f'Greetings {name}, whose favorite color is {favorite_color}.  I see that you are Winning today!')
        # else:
        #     print(f'Greetings {name}, whose favorite color is {favorite_color}.  I\'m sorry you aren\'t Winning today.')

        ### List box (choose one)
        # list_box = wx.SingleChoiceDialog(None, 'What is your favorite color?', 'TITLE GOES HERE', ['Black', 'Blue', 'Pink', 'Yellow', 'Green'])
        # if list_box.ShowModal() == wx.ID_OK:
        #     favorite_color = list_box.GetStringSelection()

        ### List box (choose multiple)
        # consoles = ['Switch', 'Playstation 4', '2DS', 'Wii-U', 'Playstation 3']
        # container = wx.ListBox(panel, -1, (80, 200), (150, 60), consoles, wx.LB_SINGLE)
        # container.SetSelection(0)

        ### Slider
        # slider = wx.Slider(panel, -1, 50, 0, 100, size=(500, -1), style=wx.SL_AUTOTICKS | wx.SL_LABELS)
        # slider.SetTickFreq(5)
        # sizer = wx.BoxSizer(wx.VERTICAL)
        # sizer.Add((1,300))
        # sizer.Add(slider, 0, wx.LEFT, 20)
        # self.SetSizer(sizer)

        ### Spinner
        # spinner = wx.SpinCtrl(panel, -1, '', (500,30), (90,-1))
        # spinner.SetRange(0,100)
        # spinner.SetValue(10)

        ### Checkbox
        # wx.CheckBox(panel, -1, 'Not Satisfied', (60,120), (250,-1))
        # wx.CheckBox(panel, -1, 'Satisfied',(60, 140), (250, -1))
        # wx.CheckBox(panel, -1, 'Very Satisfied',(60, 160), (250, -1))


    def load(self, event):
        with wx.FileDialog(self, message='Choose an Image File', defaultDir=os.getcwd(), defaultFile='', wildcard=wildcard,
                            style=wx.FD_OPEN | wx.FD_MULTIPLE | wx.FD_CHANGE_DIR | wx.FD_FILE_MUST_EXIST | wx.FD_PREVIEW) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return
        self.path_names = fileDialog.GetPaths()
        self.file_names = fileDialog.GetFilenames()
        # print_out(path_name, file_name)
        if len(self.path_names) == 1:
            self.text_filename.Destroy()
            self.text_res.Destroy()
            self.text_ar.Destroy()
            ANALyzer(self.path_names[0])
            if is_black_frame():
                self.text_filename = wx.StaticText(self.panel, 500, self.file_names[0], (30, 50))
                self.text_res = wx.StaticText(self.panel, 500, 'BLACK FRAME', (30, 150))
                self.text_ar = wx.StaticText(self.panel, 500, 'BLACK FRAME', (30, 250))
                self.text_filename.SetFont(self.answer_font)
                self.text_res.SetFont(self.answer_font)
                self.text_ar.SetFont(self.answer_font)
                wx.MessageBox('You have Loaded a black image', 'ERROR')
            elif not is_SAR(): # Supported Aspect Ratio
                self.text_filename = wx.StaticText(self.panel, 500, self.file_names[0], (30, 50))
                self.text_res = wx.StaticText(self.panel, 500, 'NOT SUPPORTED FRAME', (30, 150))
                self.text_ar = wx.StaticText(self.panel, 500, 'NOT SUPPORTED FRAME', (30, 250))
                self.text_filename.SetFont(self.answer_font)
                self.text_res.SetFont(self.answer_font)
                self.text_ar.SetFont(self.answer_font)
                wx.MessageBox('You have Loaded an image that does not have a HD (1920x1080) or UHD (3840x2160) frame', 'ERROR')
            else:
                resolution = get_resolution()
                aspect_ratio = get_aspect_ratio()
                self.text_filename = wx.StaticText(self.panel, 500, self.file_names[0], (30, 50))
                self.text_res = wx.StaticText(self.panel, 500, resolution, (30, 150))
                self.text_ar = wx.StaticText(self.panel, 500, aspect_ratio, (30, 250))
                self.text_filename.SetFont(self.answer_font)
                self.text_res.SetFont(self.answer_font)
                self.text_ar.SetFont(self.answer_font)
        else:
            with wx.FileDialog(self, message='Save file as...', defaultDir=os.getcwd(), defaultFile='_frameData',
                               wildcard='text file (*.txt)|*.txt|, ',
                               style=wx.FD_SAVE | wx.FD_CHANGE_DIR | wx.FD_OVERWRITE_PROMPT) as dlg:
                if dlg.ShowModal() == wx.ID_OK:
                    save_path_name = dlg.GetPath()
                    f = open(f'{save_path_name}', 'w')
                    i = 0
                    while i < len(self.path_names):
                        ANALyzer(self.path_names[i])
                        if is_black_frame():
                            print(f'{i+1}. {self.file_names[i]}:  BLACK FRAME', file=f)
                        elif not is_SAR():
                            print(f'{i+1}. {self.file_names[i]}:  NOT SUPPORTED FRAME', file=f)
                        else:
                            resolution = get_resolution()
                            aspect_ratio = get_aspect_ratio()
                            print(f'{i+1}. {self.file_names[i]}:  resolution = {resolution}, aspect-ratio = {aspect_ratio}', file=f)
                        i += 1
                    f.close()
            wx.MessageBox(save_path_name, 'WHOMP! There It Is!')
            os.chmod(save_path_name, mode=stat.S_IRWXO | stat.S_IRWXU | stat.S_IRWXG)
            subprocess.run(['open', save_path_name], check=True)


    def load_pBox(self, event):
        with wx.FileDialog(self, message='Choose a Pillar-Box Image File(s)', defaultDir=os.getcwd(), defaultFile='', wildcard=wildcard,
                            style=wx.FD_OPEN | wx.FD_MULTIPLE | wx.FD_CHANGE_DIR | wx.FD_FILE_MUST_EXIST | wx.FD_PREVIEW) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return
        self.path_names = fileDialog.GetPaths()
        self.file_names = fileDialog.GetFilenames()
        # print_out(path_name, file_name)
        if len(self.path_names) == 1:
            self.pBox = True
            self.text_filename.Destroy()
            self.text_res.Destroy()
            self.text_ar.Destroy()
            ANALyzer_pBox(self.path_names[0])
            if is_black_frame_pBox():
                self.text_filename = wx.StaticText(self.panel, 500, self.file_names[0], (30, 50))
                self.text_res = wx.StaticText(self.panel, 500, 'BLACK FRAME', (30, 150))
                self.text_ar = wx.StaticText(self.panel, 500, 'BLACK FRAME', (30, 250))
                self.text_filename.SetFont(self.answer_font)
                self.text_res.SetFont(self.answer_font)
                self.text_ar.SetFont(self.answer_font)
                wx.MessageBox('You have Loaded a black image', 'ERROR')
            elif not is_SAR_pBox(): # Supported Aspect Ratio
                self.text_filename = wx.StaticText(self.panel, 500, self.file_names[0], (30, 50))
                self.text_res = wx.StaticText(self.panel, 500, 'NOT SUPPORTED FRAME', (30, 150))
                self.text_ar = wx.StaticText(self.panel, 500, 'NOT SUPPORTED FRAME', (30, 250))
                self.text_filename.SetFont(self.answer_font)
                self.text_res.SetFont(self.answer_font)
                self.text_ar.SetFont(self.answer_font)
                wx.MessageBox('You have Loaded an image that does not have a HD (1920x1080) or UHD (3840x2160) frame', 'ERROR')
            else:
                resolution = get_resolution_pBox()
                aspect_ratio = get_aspect_ratio_pBox()
                answer_font = wx.Font(25, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
                self.text_filename = wx.StaticText(self.panel, 500, self.file_names[0], (30, 50))
                self.text_res = wx.StaticText(self.panel, 500, resolution, (30, 150))
                self.text_ar = wx.StaticText(self.panel, 500, aspect_ratio, (30, 250))
                self.text_filename.SetFont(answer_font)
                self.text_res.SetFont(answer_font)
                self.text_ar.SetFont(answer_font)
        else:
            with wx.FileDialog(self, message='Save file as...', defaultDir=os.getcwd(), defaultFile='_frameData',
                               wildcard='text file (*.txt)|*.txt|, ',
                               style=wx.FD_SAVE | wx.FD_CHANGE_DIR | wx.FD_OVERWRITE_PROMPT) as dlg:
                if dlg.ShowModal() == wx.ID_OK:
                    save_path_name = dlg.GetPath()
                    f = open(f'{save_path_name}', 'w')
                    i = 0
                    while i < len(self.path_names):
                        ANALyzer_pBox(self.path_names[i])
                        if is_black_frame_pBox():
                            print(f'{i+1}. {self.file_names[i]}:  BLACK FRAME', file=f)
                        elif not is_SAR_pBox():
                            print(f'{i+1}. {self.file_names[i]}:  NOT SUPPORTED FRAME', file=f)
                        else:
                            resolution = get_resolution_pBox()
                            aspect_ratio = get_aspect_ratio_pBox()
                            print(f'{i+1}. {self.file_names[i]}:  resolution = {resolution}, aspect-ratio = {aspect_ratio}', file=f)
                        i += 1
                    f.close()
            wx.MessageBox(save_path_name, 'WHOMP! There It Is!')
            os.chmod(save_path_name, mode=stat.S_IRWXO | stat.S_IRWXU | stat.S_IRWXG)
            subprocess.run(['open', save_path_name], check=True)


    def compare(self, event):
        global base_AR
        with wx.FileDialog(self, message='Choose Image Files to compare ', defaultDir=os.getcwd(), defaultFile='', wildcard=wildcard,
                            style=wx.FD_OPEN | wx.FD_MULTIPLE | wx.FD_CHANGE_DIR | wx.FD_FILE_MUST_EXIST | wx.FD_PREVIEW) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return
        self.path_names = fileDialog.GetPaths()
        self.file_names = fileDialog.GetFilenames()
        a = str(self.path_names[0])
        path = a.replace(f'{self.file_names[0]}', '')
        if len(self.path_names) == 1:
            wx.MessageBox('At Least 2 files must be selected','ERROR')
        else:
            i = 0 # incrementer
            j = 0 # counter for frames that differ
            f = open(os.getcwd() + f'/{self.file_names[i]}_compare.txt', 'w')
            log = os.getcwd() + f'/{self.file_names[i]}_compare.txt'
            autoAR_dlg = wx.MessageDialog(None, '', 'Do you want to enter an aspect ratio to check?', style=wx.YES_NO)
            val = autoAR_dlg.ShowModal()
            if val == wx.ID_YES: # 5103 means 'yes'
                valid_base_input = False
                while not valid_base_input:
                    try:
                        dlg = Base_AR_Dialog(self, -1, "RESOLUTION CHECK", size=(350, 200), style=wx.DEFAULT_DIALOG_STYLE)
                        dlg.CenterOnScreen()
                        val = dlg.ShowModal()
                        if val == wx.ID_OK:
                            base_AR = int(dlg.base_width.GetValue()) / int(dlg.base_height.GetValue())
                            while base_AR > 2.55 or base_AR < 1.33: # Checking for valid aspect ratio standard
                                wx.MessageBox(f'You have entered a non-standard aspect ratio of {base_AR}\n\nPlease re-enter.', 'ERROR!')
                                dlg = Base_AR_Dialog(self, -1, "RESOLUTION CHECK", size=(350, 200), style=wx.DEFAULT_DIALOG_STYLE)
                                dlg.CenterOnScreen()
                                val = dlg.ShowModal()
                                if val == wx.ID_OK:
                                    base_AR = int(dlg.base_width.GetValue()) / int(dlg.base_height.GetValue())
                        valid_base_input = True
                    except ValueError:
                        wx.MessageBox(f'Please only enter integer values.', 'ERROR!')
                    except ZeroDivisionError:
                        wx.MessageBox(f'There\'s no such thing as a 0 pixel height.\n\nPlease re-enter.', 'ERROR!')
                    else:
                        print('USER / MANUAL ASPECT RATIO ENTERED:\n'
                              f'Path = {path}\n'
                              f'Base Resolution = {dlg.base_width.GetValue()} x {dlg.base_height.GetValue()}\n'
                              f'Base Aspect Ratio = {base_AR}\n\n'
                              'The files below do not match the base aspect ratio:\n', file=f)
                        while i < len(self.path_names):
                            ANALyzer(self.path_names[i])
                            if is_black_frame():
                                print(f'{j+1}. {self.file_names[i]}:  BLACK FRAME', file=f)
                                j += 1
                            elif not is_SAR():
                                print(f'{j+1}. {self.file_names[i]}:  NOT SUPPORTED FRAME', file=f)
                                j += 1
                            else:
                                resolution = get_resolution()
                                aspect_ratio = get_aspect_ratio()
                                if float(aspect_ratio) > 2.55 or float(aspect_ratio) < 1.33:
                                    print(f'{j+1}. {self.file_names[i]} - {resolution} ({aspect_ratio}) UNDEFINED MATTES', file=f)
                                    j += 1
                                elif float(aspect_ratio) != base_AR:
                                    print(f'{j+1}. {self.file_names[i]} - {resolution} ({aspect_ratio})', file=f)
                                    j += 1
                            i += 1
                        if j != 0:
                            if j == 1:
                                wx.MessageBox(f'{j} frame does not match the user input aspect ratio of '
                                              f'{dlg.base_width.GetValue()} x {dlg.base_height.GetValue()} ({base_AR})\n\n'
                                              f'Details saved as: {log}', 'Mismatch!')
                            elif j+1 == len(self.path_names): # All of the input is bad
                                wx.MessageBox(f'No frames match the user input aspect ratio of\n'
                                              f'{dlg.base_width.GetValue()} x {dlg.base_height.GetValue()} ({base_AR})\n\n'
                                              f'Details saved as: {log}', 'Mismatch!')
                            else:
                                wx.MessageBox(f'{j} frames do not match the user input aspect ratio of '
                                              f'{dlg.base_width.GetValue()} x {dlg.base_height.GetValue()} ({base_AR})\n\n'
                                              f'Details saved as: {log}', 'Mismatch!')
                        else:
                            print('Woo-hoo! All frames are a match!', file=f)
                            wx.MessageBox(f'All images match. Details saved as: {log}', 'No Issues')
                        f.close()
                        os.chmod(f'{self.file_names[0]}_compare.txt', mode=stat.S_IRWXO | stat.S_IRWXU | stat.S_IRWXG)
                        subprocess.run(['open', f'{self.file_names[0]}_compare.txt'], check=True)
            else:
                wx.MessageBox('Annie will take the aspect ratio from the first frame as the base to compare the rest '
                              'of the frames', 'A You Guuuuuys!')
                mismatch = []
                valid_base = False
                while not valid_base:
                    try: # find a base file
                        ANALyzer(self.path_names[i])
                        if not is_SAR(): # SAR is HD or UHD frame
                            if i+1 == len(self.file_names):
                                wx.MessageBox(f'{self.file_names[i]} has an Unsupported Frame\n\n'
                                              'No more frames to check', 'ERROR!')
                                mismatch.append(f'{j+1}. {self.file_names[i]}:  UNSUPPORTED FRAME')
                            else:
                                wx.MessageBox(f'{self.file_names[i]} has an Unsupported Frame\n\nMoving to the next frame:\n'
                                              f'{self.file_names[i+1]}', 'ERROR!')
                                mismatch.append(f'{j+1}. {self.file_names[i]}:  UNSUPPORTED FRAME')
                            i += 1
                            j += 1
                            continue
                        base_AR = get_aspect_ratio() # Black frame check, will return ZeroDivisionError
                        base_res = get_resolution()
                        if float(base_AR) > 2.55 or float(base_AR) < 1.33: # Undefined mattes check
                            if i+1 == len(self.file_names):
                                wx.MessageBox(f'{self.file_names[i]} has undefined mattes with an aspect ratio of ({base_AR})\n\n'
                                              'No more frames to check', 'ERROR!')
                                mismatch.append(f'{j+1}. {self.file_names[i]} - {base_res} ({base_AR}): UNDEFINED MATTES')
                            else:
                                wx.MessageBox(f'{self.file_names[i]} has undefined mattes with an aspect ratio of ({base_AR})\n\n'
                                              f'Moving to the next frame:\n{self.file_names[i+1]}', 'ERROR!')
                                mismatch.append(f'{j+1}. {self.file_names[i]} - {base_res} ({base_AR}): UNDEFINED MATTES')
                            i += 1
                            j += 1
                            continue
                    except ZeroDivisionError: # Black Frame
                        if i+1 == len(self.file_names):  # check if all input is analyzed
                            wx.MessageBox(f'{self.file_names[i]} is a Black Frame\n\nNo more frames to check\n',
                                          'ERROR!')
                            mismatch.append(f'{j+1}. {self.file_names[i]}:  BLACK FRAME')
                        else:
                            wx.MessageBox(f'{self.file_names[i]} is a Black Frame\n\nMoving to the next frame:\n'
                                          f'{self.file_names[i+1]}', 'ERROR!')
                            mismatch.append(f'{j+1}. {self.file_names[i]}:  BLACK FRAME')
                        i += 1
                        j += 1
                    except IndexError:
                        wx.MessageBox('', 'No files can be analyzed')
                        print('No files below can be analyzed:\n', file=f)
                        for bad_frames in mismatch:
                            print(bad_frames, file=f)
                        f.close()
                        os.chmod(f'{self.file_names[0]}_compare.txt', mode=stat.S_IRWXO | stat.S_IRWXU | stat.S_IRWXG)
                        subprocess.run(['open', f'{self.file_names[0]}_compare.txt'], check=True)
                        return
                    else:
                        valid_base = True # break out of the loop
                        print('AUTO ASPECT RATIO:\n'
                              f'Path = {path}\n'
                              f'Base File = {self.file_names[i]}\n'
                              f'Base Resolution = {base_res}\n'
                              f'Base Aspect Ratio = {base_AR}\n\n'
                              'The files below do not match the base aspect ratio:\n', file=f)
                        i += 1
                while i < len(self.path_names):
                    try:
                        ANALyzer(self.path_names[i])
                        resolution = get_resolution()
                        aspect_ratio = get_aspect_ratio()
                        if float(aspect_ratio) > 2.55 or float(aspect_ratio) < 1.33:
                            mismatch.append(f'{j+1}. {self.file_names[i]} - {resolution} ({aspect_ratio}) UNDEFINED MATTES')
                            i += 1
                            j += 1
                        elif not is_SAR(): # SAR is HD or UHD frame
                            mismatch.append(f'{j+1}. {self.file_names[i]}:  UNSUPPORTED FRAME')
                            i += 1
                            j += 1
                        elif float(base_AR) != float(aspect_ratio):
                            mismatch.append(f'{j+1}. {self.file_names[i]} - {resolution} ({aspect_ratio})')
                            i += 1
                            j += 1
                        else:
                            i +=1
                    except ZeroDivisionError: # Black Frame
                        mismatch.append(f'{j+1}. {self.file_names[i]}:  BLACK FRAME')
                        i += 1
                        j += 1
                if j != 0:
                    if j == 1:
                        wx.MessageBox(f'{j} frame does not match the aspect ratio of the base frame ({base_AR})\n\n'
                                      f'Details saved as: {log}', 'Nope!')
                        for bad_frames in mismatch:
                            print(bad_frames, file=f)
                    elif j+1 == len(self.path_names):
                        wx.MessageBox(f'No frames match the aspect ratio of the base frame ({base_AR})\n\n'
                                      f'Details saved as: {log}', 'Issue!')
                        for bad_frames in mismatch:
                            print(bad_frames, file=f)
                    else:
                        wx.MessageBox(f'{j} frames do not match the aspect ratio of the base frame ({base_AR})\n\n'
                                      f'Details saved as: {log}', 'Nope!')
                        for bad_frames in mismatch:
                            print(bad_frames, file=f)
                else:
                    print('Woo-hoo! All frames are a match!', file=f)
                    wx.MessageBox(f'All images match. Details saved as: {log}', 'Woo-hoo!')
                f.close()
                os.chmod(f'{self.file_names[0]}_compare.txt', mode=stat.S_IRWXO | stat.S_IRWXU | stat.S_IRWXG)
                subprocess.run(['open', f'{self.file_names[0]}_compare.txt'], check=True)

# Need a 1.33 undefined mattes test (crop lucasfilm logo images)
# Have to redefine black frames as 0 aspect ratio rather than a ZeroDivideError
    def compare_pBox(self, event):
        global base_AR
        with wx.FileDialog(self, message='Choose Image Files to compare ', defaultDir=os.getcwd(), defaultFile='',
                           wildcard=wildcard, style=wx.FD_OPEN | wx.FD_MULTIPLE | wx.FD_CHANGE_DIR |
                           wx.FD_FILE_MUST_EXIST | wx.FD_PREVIEW) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return
        self.path_names = fileDialog.GetPaths()
        self.file_names = fileDialog.GetFilenames()
        a = str(self.path_names[0])
        path = a.replace(f'{self.file_names[0]}', '')
        if len(self.path_names) == 1:
            wx.MessageBox('At Least 2 files must be selected','ERROR')
        else:
            i = 0 # incrementer
            j = 0 # counter for frames that differ
            f = open(os.getcwd() + f'/{self.file_names[0]}_compare.txt', 'w')
            log = os.getcwd() + f'/{self.file_names[0]}_compare.txt'
            autoAR_dlg = wx.MessageDialog(None, '', 'Do you want to enter an aspect ratio to check?', wx.YES_NO)
            val = autoAR_dlg.ShowModal()
            if val == wx.ID_YES:
                valid_base_input = False
                while not valid_base_input:
                    try:
                        dlg = Base_AR_Dialog(self, -1, "RESOLUTION CHECK", size=(350, 200), style=wx.DEFAULT_DIALOG_STYLE)
                        dlg.CenterOnScreen()
                        val = dlg.ShowModal()
                        if val == wx.ID_OK:
                            base_AR = int(dlg.base_width.GetValue()) / int(dlg.base_height.GetValue())
                            while base_AR > 2.55 or base_AR < 1.33: # Checking for valid aspect ratio standard
                                wx.MessageBox(f'You have entered a non-standard aspect ratio of {base_AR}\n\n'
                                              f'Please re-enter.', 'ERROR!')
                                dlg = Base_AR_Dialog(self, -1, "RESOLUTION CHECK", size=(350, 200), style=wx.DEFAULT_DIALOG_STYLE)
                                dlg.CenterOnScreen()
                                val = dlg.ShowModal()
                                if val == wx.ID_OK:
                                    base_AR = int(dlg.base_width.GetValue()) / int(dlg.base_height.GetValue())
                        valid_base_input = True
                    except ValueError:
                        wx.MessageBox(f'Please only enter integer values.', 'ERROR!')
                    except ZeroDivisionError:
                        wx.MessageBox(f'There\'s no such thing as a 0 pixel height.\n\nPlease re-enter.', 'ERROR!')
                    else:
                        print('USER / MANUAL ASPECT RATIO ENTERED:\n'
                              f'Path = {path}\n'
                              f'Base Resolution = {dlg.base_width.GetValue()} x {dlg.base_height.GetValue()}\n'
                              f'Base Aspect Ratio = {base_AR}\n\n'
                              'The files below do not match the base aspect ratio:\n', file=f)
                        while i < len(self.path_names):
                            ANALyzer_pBox(self.path_names[i])
                            if is_black_frame_pBox():
                                print(f'{j+1}. {self.file_names[i]}:  BLACK FRAME', file=f)
                                j += 1
                            elif not is_SAR_pBox():
                                print(f'{j+1}. {self.file_names[i]}:  NOT SUPPORTED FRAME', file=f)
                                j += 1
                            else:
                                resolution = get_resolution_pBox()
                                aspect_ratio = get_aspect_ratio_pBox()
                                if float(aspect_ratio) > 2.55 or float(aspect_ratio) < 1.33:
                                    print(f'{j+1}. {self.file_names[i]} - {resolution} ({aspect_ratio}) UNDEFINED MATTES', file=f)
                                    j += 1
                                elif base_AR != float(aspect_ratio):
                                    print(f'{j+1}. {self.file_names[i]} - {resolution} ({aspect_ratio})', file=f)
                                    j += 1
                            i += 1
                        if j != 0:
                            if j == 1:
                                wx.MessageBox(f'{j} frame does not match the user input aspect ratio of '
                                              f'{dlg.base_width.GetValue()} x {dlg.base_height.GetValue()} ({base_AR})\n\n'
                                              f'Details saved as: {log}', 'Mismatch!')
                            elif j+1 == len(self.path_names): # All of the input is bad
                                wx.MessageBox(f'No frames match the user input aspect ratio of\n'
                                              f'{dlg.base_width.GetValue()} x {dlg.base_height.GetValue()} ({base_AR})\n\n'
                                              f'Details saved as: {log}', 'Mismatch!')
                            else:
                                wx.MessageBox(f'{j} frames do not match the user input aspect ratio of '
                                              f'{dlg.base_width.GetValue()} x {dlg.base_height.GetValue()} ({base_AR})\n\n'
                                              f'Details saved as: {log}', 'Mismatch!')
                        else:
                            print('Woo-hoo! All frames are a match!', file=f)
                            wx.MessageBox(f'All images match. Details saved as: {log}', 'No Issues')
                        f.close()
                        os.chmod(f'{self.file_names[0]}_compare.txt', mode=stat.S_IRWXO | stat.S_IRWXU | stat.S_IRWXG)
                        subprocess.run(['open', f'{self.file_names[0]}_compare.txt'], check=True)
            else:
                wx.MessageBox('Annie will take the aspect ratio from the first frame as the base to compare the rest '
                              'of the frames', 'A You Guuuuuys!')
                mismatch = []
                valid_base = False
                while not valid_base:
                    try: # find a base file
                        ANALyzer_pBox(self.path_names[i])
                        if not is_SAR_pBox(): # SAR is HD or UHD frame
                            if i+1 == len(self.file_names):
                                wx.MessageBox(f'{self.file_names[i]} has an Unsupported Frame\n\n'
                                              'No more frames to check', 'ERROR!')
                                mismatch.append(f'{j+1}. {self.file_names[i]}:  UNSUPPORTED FRAME')
                            else:
                                wx.MessageBox(f'{self.file_names[i]} has an Unsupported Frame\n\nMoving to the next frame:\n'
                                              f'{self.file_names[i+1]}', 'ERROR!')
                                mismatch.append(f'{j+1}. {self.file_names[i]}:  UNSUPPORTED FRAME')
                            i += 1
                            j += 1
                            continue
                        base_AR = get_aspect_ratio_pBox() # Black frame check, will return ZeroDivisionError
                        base_res = get_resolution_pBox()
                        if float(base_AR) >= 1.78 or (1.33 > float(base_AR) > 0): # Undefined mattes check
                            if i+1 == len(self.file_names):
                                wx.MessageBox(f'{self.file_names[i]} has undefined mattes with an aspect ratio of ({base_AR})\n\n'
                                              'No more frames to check', 'ERROR!')
                                mismatch.append(f'{j+1}. {self.file_names[i]} - {base_res} ({base_AR}): UNDEFINED MATTES')
                            else:
                                wx.MessageBox(f'{self.file_names[i]} has undefined mattes with an aspect ratio of ({base_AR})\n\n'
                                              f'Moving to the next frame:\n{self.file_names[i+1]}', 'ERROR!')
                                mismatch.append(f'{j+1}. {self.file_names[i]} - {base_res} ({base_AR}): UNDEFINED MATTES')
                            i += 1
                            j += 1
                            continue
                        if float(base_AR) == 0: # Black frame
                            if i+1 == len(self.file_names):  # check if all input is analyzed
                                wx.MessageBox(f'{self.file_names[i]} is a Black Frame\n\nNo more frames to check\n',
                                              'ERROR!')
                                mismatch.append(f'{j+1}. {self.file_names[i]}:  BLACK FRAME')
                            else:
                                wx.MessageBox(f'{self.file_names[i]} is a Black Frame\n\nMoving to the next frame:\n'
                                              f'{self.file_names[i+1]}', 'ERROR!')
                                mismatch.append(f'{j+1}. {self.file_names[i]}:  BLACK FRAME')
                            i += 1
                            j += 1
                            continue
                    # except ZeroDivisionError: # Black Frame
                    #     if i+1 == len(self.file_names):  # check if all input is analyzed
                    #         wx.MessageBox(f'{self.file_names[i]} is a Black Frame\n\nNo more frames to check\n',
                    #                       'ERROR!')
                    #         mismatch.append(f'{j+1}. {self.file_names[i]}:  BLACK FRAME')
                    #     else:
                    #         wx.MessageBox(f'{self.file_names[i]} is a Black Frame\n\nMoving to the next frame:\n'
                    #                       f'{self.file_names[i+1]}', 'ERROR!')
                    #         mismatch.append(f'{j+1}. {self.file_names[i]}:  BLACK FRAME')
                    #     i += 1
                    #     j += 1
                    except IndexError:
                        wx.MessageBox('', 'No files can be analyzed')
                        print('No files below can be analyzed:\n', file=f)
                        for bad_frames in mismatch:
                            print(bad_frames, file=f)
                        f.close()
                        os.chmod(f'{self.file_names[0]}_compare.txt', mode=stat.S_IRWXO | stat.S_IRWXU | stat.S_IRWXG)
                        subprocess.run(['open', f'{self.file_names[0]}_compare.txt'], check=True)
                        return
                    else:
                        valid_base = True # Break out of the loop
                        print('AUTO ASPECT RATIO:\n'
                              f'Path = {path}\n'
                              f'Base File = {self.file_names[i]}\n'
                              f'Base Resolution = {base_res}\n'
                              f'Base Aspect Ratio = {base_AR}\n\n'
                              'The files below do not match the base aspect ratio:\n', file=f)
                        i += 1
                while i < len(self.path_names):
                    try:
                        ANALyzer_pBox(self.path_names[i])
                        resolution = get_resolution_pBox()
                        aspect_ratio = get_aspect_ratio_pBox()
                        if float(aspect_ratio) > 2.55 or float(aspect_ratio) < 1.33:
                            mismatch.append(f'{j+1}. {self.file_names[i]} - {resolution} ({aspect_ratio}) UNDEFINED MATTES')
                            i += 1
                            j += 1
                        elif not is_SAR_pBox(): # SAR is HD or UHD frame
                            mismatch.append(f'{j+1}. {self.file_names[i]}:  UNSUPPORTED FRAME')
                            i += 1
                            j += 1
                        elif float(base_AR) != float(aspect_ratio):
                            mismatch.append(f'{j+1}. {self.file_names[i]} - {resolution} ({aspect_ratio})')
                            i += 1
                            j += 1
                        else:
                            i +=1
                    except ZeroDivisionError: # Black Frame
                        mismatch.append(f'{j+1}. {self.file_names[i]}:  BLACK FRAME')
                        i += 1
                        j += 1
                if j != 0:
                    if j == 1:
                        wx.MessageBox(f'{j} frame does not match the aspect ratio of the base frame ({base_AR})\n\n'
                                      f'Details saved as: {log}', 'Nope!')
                        for bad_frames in mismatch:
                            print(bad_frames, file=f)
                    elif j+1 == len(self.path_names):
                        wx.MessageBox(f'No frames match the aspect ratio of the base frame ({base_AR})\n\n'
                                      f'Details saved as: {log}', 'Issue!')
                        for bad_frames in mismatch:
                            print(bad_frames, file=f)
                    else:
                        wx.MessageBox(f'{j} frames do not match the aspect ratio of the base frame ({base_AR})\n\n'
                                      f'Details saved as: {log}', 'Nope!')
                        for bad_frames in mismatch:
                            print(bad_frames, file=f)
                else:
                    print('Woo-hoo! All frames are a match!', file=f)
                    wx.MessageBox(f'All images match. Details saved as: {log}', 'Woo-hoo!')
                f.close()
                os.chmod(f'{self.file_names[0]}_compare.txt', mode=stat.S_IRWXO | stat.S_IRWXU | stat.S_IRWXG)
                subprocess.run(['open', f'{self.file_names[0]}_compare.txt'], check=True)


    def write_line_sum(self, event):
        with wx.FileDialog(self, message='Save file as...', defaultDir=os.getcwd(), defaultFile=self.file_names[0] + '_lineSumValue',
                           wildcard='text file (*.txt)|*.txt|, ',
                           style=wx.FD_SAVE | wx.FD_CHANGE_DIR | wx.FD_OVERWRITE_PROMPT) as dlg:
            # dlg.SetFilterIndex(2)
            if dlg.ShowModal() == wx.ID_OK:
                path_name = dlg.GetPath()
                if self.pBox:
                    print_line_sum_pBox(path_name)
                    wx.MessageBox(path_name, 'WHOMP! There It Is!\nPixel-Sum values reflect the image rotated 90 degrees')
                else:
                    print_line_sum(path_name)
                    wx.MessageBox(path_name, 'WHOMP! There It Is!')
                os.chmod(path_name, mode=stat.S_IRWXO | stat.S_IRWXU | stat.S_IRWXG) # these chained modes are = chmod777
                subprocess.run(['open', path_name], check=True)
            else:
                return


    def frame_capture_sample(self, event):
        with wx.FileDialog(self, message='Choose a VIDEO File', defaultDir=os.getcwd(), defaultFile='', wildcard=wildcard_video,
                            style=wx.FD_OPEN | wx.FD_MULTIPLE | wx.FD_CHANGE_DIR | wx.FD_FILE_MUST_EXIST | wx.FD_PREVIEW) as dlg:
            if dlg.ShowModal() == wx.ID_CANCEL:
                return
        self.video_path_names = dlg.GetPaths()
        self.video_file_names = dlg.GetFilenames()
        a = str(self.video_path_names[0])
        path = a.replace(f'{self.video_file_names[0]}', '')
        vid = cv2.VideoCapture(self.video_path_names[0])
        total_frames = int(vid.get(propId=7)) # propId=7 is cv2.CAP_PROP_FRAME_COUNT
        print(f'total frames={total_frames}')
        print('total seconds at 24fps=' + str(round(total_frames / 24, 3)))
        print(f'frame increment not rounded={total_frames/10}')
        print('frame increment rounded='+ str(round(total_frames/10)))
        for i in range(0, total_frames, round(total_frames / 10)):
            vid.set(1, i) # propID=1 is cv2.CAP_PROP_POS_FRAMES for setting the start frame
            ret, still = vid.read()
            cv2.imwrite(f'{self.video_path_names[0]}_frame{i+1}.jpg', still)
        wx.MessageBox(path, f'HitMonLEEEE! Frame Samples Output To:')


        ### NOTE: To convert milliseconds to frames first divide 1000 by the frame-rate.  That will give you ~ how many
        # ms in each frame.  Then simply divide the ms by that value.  The remainder will have to be rounded.


    def frame_capture(self, event):
        with wx.FileDialog(self, message='Choose a VIDEO File', defaultDir=os.getcwd(), defaultFile='', wildcard=wildcard_video,
                            style=wx.FD_OPEN | wx.FD_MULTIPLE | wx.FD_CHANGE_DIR | wx.FD_FILE_MUST_EXIST | wx.FD_PREVIEW) as dlg:
            if dlg.ShowModal() == wx.ID_CANCEL:
                return
        self.video_path_names = dlg.GetPaths()
        self.video_file_names = dlg.GetFilenames()
        a = str(self.video_path_names[0])
        path = a.replace(f'{self.video_file_names[0]}', '')
        vid = cv2.VideoCapture(self.video_path_names[0])
        total_frames = int(vid.get(propId=7)) # propId=7 is cv2.CAP_PROP_FRAME_COUNT
        print(f'total frames={total_frames}')
        print('total seconds at 24fps=' + str(round(total_frames / 24, 3)))
        print(f'frame increment not rounded={total_frames/10}')
        print('frame increment rounded='+ str(round(total_frames/10)))
        for i in range(total_frames):
            vid.set(1, i) # propID=1 is cv2.CAP_PROP_POS_FRAMES for setting the start frame
            ret, still = vid.read()
            cv2.imwrite(f'{self.video_path_names[0]}_frame{i+1}.jpg', still)
        wx.MessageBox(path, f'Squirtle Squirt! All Frames From {self.video_file_names[0]} Output To:')


        ### NOTE: To convert milliseconds to frames first divide 1000 by the frame-rate.  That will give you ~ how many
        # ms in each frame.  Then simply divide the ms by that value.  The remainder will have to be rounded.


    def close_button(self, event):
        self.Close(True)

    def close_window(self, event):
        self.Destroy()


class Base_AR_Dialog(wx.Dialog):
    def __init__(
            self, parent, id, title, size=wx.DefaultSize, pos=wx.DefaultPosition,
            style=wx.DEFAULT_DIALOG_STYLE, name='base_aspect_ratio_dialog'
            ):

        # Instead of calling wx.Dialog.__init__ we pre-create the dialog
        # so we can set an extra style that must be set before
        # creation, and then we create the GUI object using the Create
        # method.
        wx.Dialog.__init__(self)
        self.SetExtraStyle(wx.DIALOG_EX_CONTEXTHELP)
        self.Create(parent, id, title, pos, size, style, name)

        # Now continue with the normal construction of the dialog
        # contents
        sizer = wx.BoxSizer(wx.VERTICAL)

        label = wx.StaticText(self, -1, "Enter An Aspect Ratio To Check")
        label.SetHelpText("The values below will be used as the base to compare all the selected frames")
        sizer.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)

        box = wx.BoxSizer(wx.HORIZONTAL)

        label = wx.StaticText(self, -1, "WIDTH:")
        # label.SetHelpText("This is the help text for the label")
        box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)

        self.base_width = wx.TextCtrl(self, -1, '', size=(80,-1))
        # base_width.SetHelpText("Here's some help text for field #1")
        box.Add(self.base_width, 1, wx.ALIGN_CENTRE|wx.ALL, 5)

        sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

        box = wx.BoxSizer(wx.HORIZONTAL)

        label = wx.StaticText(self, -1, 'HEIGHT:')
        # label.SetHelpText("This is the help text for the label")
        box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)

        self.base_height = wx.TextCtrl(self, -1, '', size=(80,-1))
        # self.base_height.SetHelpText("Here's some help text for field #2")
        box.Add(self.base_height, 1, wx.ALIGN_CENTRE|wx.ALL, 5)

        sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

        line = wx.StaticLine(self, -1, size=(20,-1), style=wx.LI_HORIZONTAL)
        sizer.Add(line, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.TOP, 5)

        btnsizer = wx.StdDialogButtonSizer()

        if wx.Platform != "__WXMSW__":
            btn = wx.ContextHelpButton(self)
            btnsizer.AddButton(btn)

        btn = wx.Button(self, wx.ID_OK)
        # btn.SetHelpText("The OK button completes the dialog")
        btn.SetDefault()
        btnsizer.AddButton(btn)

        btn = wx.Button(self, wx.ID_CANCEL)
        # btn.SetHelpText("The Cancel button cancels the dialog. (Cool, huh?)")
        btnsizer.AddButton(btn)
        btnsizer.Realize()

        sizer.Add(btnsizer, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

        self.SetSizer(sizer)
        sizer.Fit(self)

if __name__=='__main__':
    app=wx.App()
    frame=Annie(parent=None, id=-1)
    frame.Show()
    app.MainLoop()