from PIL import Image
# from matplotlib import pyplot

# Initialize variables
width = 1920
height = 1080
width_UHD = 3840
height_UHD = 2160
UHD = False
SAR = True # Supported Aspect Ratio
black_frame = False
pixel_sum_lines = []

# file = '/Users/delue003/PycharmProjects/images/megaMan.jpg'
# file = '/Users/delue003/PycharmProjects/images/swars4.mov_frame1.jpg'

def ANALyzer(path_name):
    global height
    global height_UHD
    global UHD
    global pixel_sum_lines
    global black_frame
    global SAR
    black = 10000
    height = 1080
    height_UHD = 2160
    UHD = False
    black_frame = False
    SAR = True
    pixel_sum_list = []
    line_sum_list = []
    pixel_sum_lines = [] # Needs to be on to reset the function, otherwise the result will be be cumulative
    im = Image.open(path_name)  # load the image
    seq_obj = list(im.getdata(band=None)) # analyzes image and reports pixel values as tuples in one long list (flattens?)
    if len(seq_obj) == 2073600: # HD pixel count
        lines = [seq_obj[x:x+1920] for x in range(0, len(seq_obj), 1920)] # splits list into objects containing 1920 tuples
        for i in range(len(lines)): # increment through the lines of 1920 pixel tuples
            for j in range(1920): # increment through the pixels in the line
                pixel_sum = lines[i][j][0] + lines[i][j][1] + lines[i][j][2] # add the R,G,B values of each pixel. Note: i = the line number, j = to the pixel number, and the 3rd element is equal to the channel value
                pixel_sum_list.append(pixel_sum) # Create new list of all pixel RGB value sums
        pixel_sum_lines = [pixel_sum_list[x:x + 1920] for x in range(0, len(pixel_sum_list), 1920)] # splits list into objects containing 1920 tuples
        for k in range(len(pixel_sum_lines)):
            line_sums = sum(pixel_sum_lines[k]) # adds summed pixel RGB values for each line
            line_sum_list.append(line_sums)
        for l in line_sum_list:
            if l < black:
                height -= 1
        if height == 0:
            black_frame = True
    elif len(seq_obj) == 8294400: # UHD pixel count
        UHD = True
        lines = [seq_obj[x:x+3840] for x in range(0, len(seq_obj), 3840)] # splits list into objects containing 3840 tuples
        for i in range(len(lines)): # increment through the lines of 3840 pixel tuples
            for j in range(3840): # increment through the pixels in the line
                pixel_sum = lines[i][j][0] + lines[i][j][1] + lines[i][j][2] # add the R,G,B values of each pixel. Note: i = the line number, j = to the pixel number, and the 3rd element is equal to the channel value
                pixel_sum_list.append(pixel_sum) # Create new list of all pixel RGB value sums
        pixel_sum_lines = [pixel_sum_list[x:x + 3840] for x in range(0, len(pixel_sum_list), 3840)] # splits list into objects containing 3840 tuples
        for k in range(len(pixel_sum_lines)):
            line_sums = sum(pixel_sum_lines[k]) # adds summed pixel RGB values for each line
            line_sum_list.append(line_sums)
        for l in line_sum_list:
            if l < black:
                height_UHD -= 1
        if height_UHD == 0:
            black_frame = True
    else:
        SAR = False


def print_line_sum(path):
    with open(f'{path}', 'w') as f:  # create a text file and store in variable 'f'
        print('Line #   Pixel Sum', file=f)
        for k in range(len(pixel_sum_lines)):
            print(f'Line {k+1}.   {sum(pixel_sum_lines[k])}', file=f)
        f.close()

def is_black_frame():
    return black_frame

def is_SAR():
    return SAR

def get_resolution():
    if not UHD:
        resolution = str(width) + ' x ' + str(height)
        return resolution
    elif UHD:
        resolution = str(width_UHD) + ' x ' + str(height_UHD)
        return resolution

def get_aspect_ratio():
    if not UHD:
        aspect_ratio = str(width / height)
        return aspect_ratio
    elif UHD:
        aspect_ratio = str(width_UHD / height_UHD)
        return aspect_ratio



### Use to check individual pixels
# pel = lines[137][0]
# if pel[0] + pel[1] + pel[2] < 4:
#     print('This is a black pixel.')
# else:
#     print('This is an active pixel.')


