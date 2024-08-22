# import numpy as np
# from PIL import Image, ImageDraw, ImageFont

# import numpy as np
# from PIL import Image, ImageDraw, ImageFont

# def text_to_image(text, font_path=None, font_size=40, font_index=0):
#     if font_path:
#         font = ImageFont.truetype(font_path, font_size, index=font_index)
#     else:
#         font = ImageFont.load_default()  # Default PIL font
        
#     width, height = font.getbbox(text)[2:]
#     image = Image.new('L', (width, height), 255)
#     draw = ImageDraw.Draw(image)
#     draw.text((0, 0), text, font=font, fill=0)
#     return image, width, height

# def image_to_gcode(image, img_width, img_height, x_limits=(-130, 120), y_limits=(240, 380)):
#     # Calculate the scale to fit the text within the limits
#     x_scale = (x_limits[1] - x_limits[0]) / img_width
#     y_scale = (y_limits[1] - y_limits[0]) / img_height
#     scale = min(x_scale, y_scale)  # Choose the smaller scale to fit both axes

#     # Calculate the starting positions to center the image within the limits
#     x_start = (x_limits[0] + x_limits[1] - img_width * scale) / 2
#     y_start = (y_limits[0] + y_limits[1] - img_height * scale) / 2

#     width, height = image.size
#     image = np.array(image)
#     gcode = []
#     gcode.append("; Start G-code")
#     gcode.append("G21 ; Set units to millimeters")
#     gcode.append("G90 ; Absolute positioning")
#     gcode.append("G0 Z5 ; Lift to avoid collision")
    
#     for y in range(height):
#         line_started = False
#         for x in range(width):
#             x_pos = (x_start + x * scale)
#             y_pos = (y_start + y * scale)

#             if image[y, x] == 0:  # 0 means black pixel (i.e., part of the text)
#                 if not line_started:
#                     gcode.append(f"G0 X{x_pos:.2f} Y{y_pos:.2f} Z0")
#                     gcode.append(f"G1 Z0 ; Start drawing")
#                     line_started = True
#                 gcode.append(f"G1 X{x_pos:.2f} Y{y_pos:.2f}")
#             else:
#                 if line_started:
#                     gcode.append("G1 Z5 ; Stop drawing")
#                     line_started = False
        
#         if line_started:
#             gcode.append("G1 Z5 ; Stop drawing")
#             line_started = False
    
#     gcode.append("; End G-code")
#     return gcode

# def save_gcode(gcode, filename='output.gcode'):
#     with open(filename, 'w') as f:
#         f.write('\n'.join(gcode))

# text = "Hello"
# font_path = "/System/Library/Fonts/Supplemental/PTMono.ttc"
# image, img_width, img_height = text_to_image(text, font_path=font_path, font_size=40, font_index=0)
# gcode = image_to_gcode(image, img_width, img_height)
# save_gcode(gcode)




# # f = open("gcodeOriginal.txt", "t")
  
# # to erase all data  
# # f.write(json_output)
# # f.close()


from ttgLib.TextToGcode import ttg

gcode = ttg("Text to Gcode",1,0,"return",1).toGcode("M02 S500","M05 S0","G0","G1")
def save_gcode(gcode, filename='output.gcode'):
    with open(filename, 'w') as f:
        f.write('\n'.join(gcode))
print(gcode)

save_gcode(gcode)
