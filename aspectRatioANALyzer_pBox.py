from PIL import Image

# Initialize variables
width = 1080
height = 1920
width_UHD = 2160
height_UHD = 3840
UHD = False
SAR = True # Supported Aspect Ratio
black_frame = False
pixel_sum_lines = []


def ANALyzer_pBox(path_name):
    global height
    global height_UHD
    global UHD
    global black_frame
    global pixel_sum_lines
    global SAR
    black_frame = False
    black = 10000
    height = 1920
    height_UHD = 3840
    UHD = False
    SAR = True
    pixel_sum_list = []
    line_sum_list = []
    pixel_sum_lines = []  # Needs to be on to reset the function, otherwise the results will be be cumulative
    im = Image.open(path_name)  # load the image
    rotated=im.rotate(angle=90, expand=True)
    # rotated.show()
    seq_obj = list(rotated.getdata(band=None)) # analyzes image and reports pixel values as tuples in one long list (flattens?)
    if len(seq_obj) == 2073600:
        lines = [seq_obj[x:x+1080] for x in range(0, len(seq_obj), 1080)] # splits list into objects containing 1080 tuples
        for i in range(len(lines)): # increment through the lines of 1080 pixel tuples
            for j in range(1080): # increment through the pixels in the line
                pixel_sum = lines[i][j][0] + lines[i][j][1] + lines[i][j][2] # add the R,G,B values of each pixel. Note: i = the line number, j = to the pixel number, and the 3rd element is equal to the channel value
                pixel_sum_list.append(pixel_sum) # Create new list of all pixel RGB value sums
        pixel_sum_lines = [pixel_sum_list[x:x + 1080] for x in range(0, len(pixel_sum_list), 1080)] # splits list into objects containing 1080 tuples
        for k in range(len(pixel_sum_lines)):
            line_sums = sum(pixel_sum_lines[k]) # adds summed pixel RGB values for each line
            line_sum_list.append(line_sums)
        for l in line_sum_list:
            if l < black:
                height -= 1
        if height == 0:
            black_frame = True
    elif len(seq_obj) == 8294400:
        UHD = True
        lines = [seq_obj[x:x+2160] for x in range(0, len(seq_obj), 2160)] # splits list into objects containing 2160 tuples
        for i in range(len(lines)): # increment through the lines of 2160 pixel tuples
            for j in range(2160): # increment through the pixels in the line
                pixel_sum = lines[i][j][0] + lines[i][j][1] + lines[i][j][2] # add the R,G,B values of each pixel. Note: i = the line number, j = to the pixel number, and the 3rd element is equal to the channel value
                pixel_sum_list.append(pixel_sum) # Create new list of all pixel RGB value sums
        pixel_sum_lines = [pixel_sum_list[x:x + 2160] for x in range(0, len(pixel_sum_list), 2160)] # splits list into objects containing 2160 tuples
        for k in range(len(pixel_sum_lines)):
            line_sums = sum(pixel_sum_lines[k]) # adds summed pixel RGB values for each line
            line_sum_list.append(line_sums)
        for l in line_sum_list:
            if l < black:
                height_UHD -= 1
        if height == 0:
            black_frame = True
    else:
        SAR = False


def print_line_sum_pBox(path):
    with open(f'{path}', 'w') as f:  # create a text file and store in variable 'f'
        print('Line #   Pixel Sum', file=f)
        for k in range(len(pixel_sum_lines)):
            print(f'Line {k+1}.   {sum(pixel_sum_lines[k])}', file=f)
        f.close()

def is_black_frame_pBox():
    return black_frame

def is_SAR_pBox():
    return SAR

def get_resolution_pBox():
    if not UHD:
        resolution = str(height) + ' x ' + str(width)
        return resolution
    elif UHD:
        resolution = str(height_UHD) + ' x ' + str(width_UHD)
        return resolution


def get_aspect_ratio_pBox():
    if not UHD:
        aspect_ratio = str(height / width)
        return aspect_ratio
    elif UHD:
        aspect_ratio = str(height_UHD / width_UHD)
        return aspect_ratio

