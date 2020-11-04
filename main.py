# Palette generator v2
# 2020 CppToast

from tkinter import *
from tkinter.messagebox import *
from tkinter.filedialog import *
import os

use_system_colorpicker = True # do not change until custom color picker is finished

if use_system_colorpicker:
    from tkinter.colorchooser import *
else:
    import colorpicker

palette_base_colors = [] #["#000000","#808080", "#ffffff"] #[ "#ff0000", "#00ff00", "#0000ff" ]
palette_size = 9
upscale_factor = 32
upscale_factor_x = 48
list_max_height = 20
dark_shade_color = "#ff00ff"
bright_shade_color = "#ffff00"

def colToHex(color):
    r, g, b = map(int,color)
    if r > 255: r = 255
    if g > 255: g = 255
    if b > 255: b = 255
    if r < 0: r = 0
    if g < 0: g = 0
    if b < 0: b = 0
    r = "{0:0{1}x}".format(r,2)
    g = "{0:0{1}x}".format(g,2)
    b = "{0:0{1}x}".format(b,2)
    return "#" + r + g + b

def hexToCol(hexcolor):
    hexcolor = hexcolor.strip("#")
    color = [hexcolor[0:2], hexcolor[2:4], hexcolor[4:6]]
    for i in range(3):
        color[i] = int(color[i], 16)
    return color

def text_color(color):
    r, g, b = map(int,color)
    brightness = 0.2126 * r + 0.7152 * g + 0.0722 * b
    if brightness > 128:
        return "#000000"
    else:
        return "#FFFFFF"
    
def lumToCol(lum, color, gamma = 1):
    lum -= 1
    if lum < 0: lum = 0
    if lum > 512: lum = 512
    lum /= 512
    lum = pow(lum, gamma)
    lum *= 512

    r, g, b = map(int,color)
    if lum < 255:
        r *= (lum / 255)
        g *= (lum / 255)
        b *= (lum / 255)
    if lum > 255:
        lum = lum - 255
        r += (255 - r) * (lum / 255)
        g += (255 - g) * (lum / 255)
        b += (255 - b) * (lum / 255)

    if r > 255: r = 255
    if g > 255: g = 255
    if b > 255: b = 255
    if r < 0: r = 0
    if g < 0: g = 0
    if b < 0: b = 0
    return [r, g, b]

def addColor():
    global palette_base_colors
    if use_system_colorpicker:
        color = askcolor()[1]
    else:
        color = colorpicker.askcolor()
    if color != None:
        palette_base_colors.append(color)
        refreshColorList()
        generate()

def removeColor():
    global palette_base_colors
    global colors_list
    selected = list(colors_list.curselection())
    for i in selected:
        palette_base_colors.pop(i)
    refreshColorList()
    generate()

def refreshColorList():
    global palette_base_colors
    global colors_list

    colors_list.delete(0, END)

    for i in range(len(palette_base_colors)):
        colors_list.insert(i, palette_base_colors[i])
        colors_list.itemconfig(i, bg = palette_base_colors[i], fg = text_color(hexToCol(palette_base_colors[i])))

def blendColors(color1, color2, ratio = 0.5):
    color = color1
    if ratio < 0: ratio = 0
    if ratio > 1: ratio = 1
    for i in range(len(color1)):
        color[i] *= (1-ratio)
        color[i] = color[i] + color2[i] * ratio
    return color

def generate(value = 0):
    global palette_base_colors, upscale_factor, palette_size
    global root, size_entry, scale_entry, outline_check_var, hex_check_var, font_size_entry, display, color_num_label
    global dark_shade_color, bright_shade_color
    global dark_shade_check_var, bright_shade_check_var
    global dark_shade_intensity_scale, bright_shade_intensity_scale
    global gamma_scale
    global palette
    
    try:
        palette_size = int(size_entry.get())
        upscale_factor = int(scale_entry.get())
        print_hex_font = font_size_entry.get()
        draw_outline = outline_check_var.get() == 1
        print_hex = hex_check_var.get() == 1
        dark_shade_intensity = dark_shade_intensity_scale.get() / 10
        bright_shade_intensity = bright_shade_intensity_scale.get() / 10
        dark_shade = dark_shade_check_var. get() == 1
        bright_shade = bright_shade_check_var. get() == 1
        gamma = 1 / gamma_scale.get()
    except:
        showerror("Invalid parameters","The parameters you inserted are invalid.")
        return

    palette = [ [ [ 0, 0, 0 ] for j in range(palette_size + 2) ] for i in range(len(palette_base_colors)) ]

    for i in range(len(palette_base_colors)):
        l_step = 512 / (palette_size + 1)
        #blend_ratio_step = 1 / (palette_size + 1)
        for shade in range(1, palette_size+1):
            current_color = hexToCol(palette_base_colors[i])
            current_lum = pow(l_step * shade / 512, gamma) * 512 - 256
            if current_lum < 0 and dark_shade:
                current_color = blendColors(current_color, hexToCol(dark_shade_color), -current_lum / 512 * dark_shade_intensity)
            if current_lum > 0 and bright_shade:
                current_color = blendColors(current_color, hexToCol(bright_shade_color), current_lum / 512 * bright_shade_intensity)
            palette[i][palette_size - shade] = lumToCol(l_step * shade, current_color, gamma)

    display.delete("all")
    display.configure(width = (len(palette_base_colors)) * upscale_factor_x, height = palette_size * upscale_factor)
    color_num_label.config(text = str(palette_size * len(palette_base_colors)))
    for y in range(palette_size):
        for x in range(len(palette_base_colors)):
            offset_x = x * upscale_factor_x
            offset_y = y * upscale_factor
            display.create_rectangle(offset_x, offset_y, offset_x + upscale_factor_x, offset_y + upscale_factor, fill = colToHex(palette[x][y]), outline = "black" if draw_outline else "")
            if print_hex: display.create_text(offset_x + 1, offset_y + 1, text = colToHex(palette[x][y]), fill = text_color(palette[x][y]), font = print_hex_font, anchor = NW)

def askForDarkShadeColor():
    global dark_shade_color
    global dark_shade_button
    if use_system_colorpicker:
        color = askcolor(dark_shade_color)[1]
    else:
        color = colorpicker.askcolor(dark_shade_color)
    
    if color != None:
        dark_shade_color = color
        dark_shade_button.config(text = color, fg = text_color(hexToCol(color)), bg = color)
        generate()

def askForBrightShadeColor():
    global bright_shade_color
    global bright_shade_button
    if use_system_colorpicker:
        color = askcolor(bright_shade_color)[1]
    else:
        color = colorpicker.askcolor(bright_shade_color)
    
    if color != None:
        bright_shade_color = color
        bright_shade_button.config(text = color, fg = text_color(hexToCol(color)), bg = color)
        generate()

def dumpHTML():
    global palette, palette_size
    save_path = asksaveasfilename(filetypes = [("Text file","*.txt"),("All files","*.*")]) # TODO: investigate why extension isn't appended
    if save_path != "":
        save_file = open(save_path, "w")
        for y in range(len(palette)):
            for x in range(palette_size):
                save_file.write(colToHex(palette[y][x])+"\t")
            save_file.write("\n")
        save_file.close()

def dumpGIMP():
    global palette, palette_size
    save_path = asksaveasfilename(filetypes = [("GIMP palette","*.gpl"),("Text file","*.txt"),("All files","*.*")]) # TODO: investigate why extension isn't appended
    if save_path != "":
        save_file = open(save_path, "w")
        save_file.write("GIMP Palette\nName: " + str(os.path.splitext(os.path.basename(save_path))[0]) + "\nColumns: " + str(palette_size) + "\n# Generated by CppToast's Palette Generator v2\n")
        for y in range(len(palette)):
            for x in range(palette_size):
                for channel in palette[y][x]:
                    save_file.write(str(int(channel))+"\t")
                save_file.write(colToHex(palette[y][x])+"\n")
        save_file.close()

root = Tk()
root.title("Palette Generator by CppToast")

# Setting the icon might not work on non-Windows systems, 
# and since icon is not really important, we can do without 
# an icon. I might think of an alternative solution later. 
try:
    root.iconbitmap(os.curdir + "/icon.ico")
except:
    pass

status = Label(text = "Total colors:")
status.grid(row = 1, column = 2, sticky = "e")
color_num_label = Label(text = str(palette_size * len(palette_base_colors)))
color_num_label.grid(row = 1, column = 3, sticky = "w")

display = Canvas(width = (len(palette_base_colors) + 2) * upscale_factor_x, height = palette_size * upscale_factor)
display.grid(row = 1, column = 1, rowspan = palette_size * 2 * upscale_factor)

size_label = Label(text = "Palette height:")
size_label.grid(row = 2, column = 2, sticky = "e")

size_entry = Entry()
size_entry.insert(0,str(palette_size))
size_entry.bind("<Return>",lambda x: generate())
size_entry.grid(row = 2, column = 3, sticky = "ew")

scale_label = Label(text = "Block height:")
scale_label.grid(row = 3, column = 2, sticky = "e")

scale_entry = Entry()
scale_entry.insert(0,str(upscale_factor))
scale_entry.bind("<Return>",lambda x: generate())
scale_entry.grid(row = 3, column = 3, sticky = "ew")

outline_check_var = IntVar()
outline_check = Checkbutton(text = "Draw outlines", variable = outline_check_var, command = generate)
outline_check.grid(row = 5, column = 3, sticky = "w")

hex_check_var = IntVar()
hex_check = Checkbutton(text = "Print HTML color codes", variable = hex_check_var, command = generate)
hex_check.grid(row = 6, column = 3, sticky = "w")

#font_size_label = Label(text = "HTML color code font name and size:")
#font_size_label.grid(row = 7, column = 1, sticky = E)

font_size_entry = Entry()
font_size_entry.insert(0,"Consolas 7")
#font_size_entry.bind("<Return>",lambda x: generate())
#font_size_entry.grid(row = 7, column = 2)

bright_shade_check_var = IntVar()
bright_shade_check = Checkbutton(text = "Blend bright colors with ", variable = bright_shade_check_var, command = generate)
bright_shade_check.grid(row = 8, column = 2, sticky = "e")
bright_shade_button = Button(text = bright_shade_color, width = 8, fg = text_color(hexToCol(bright_shade_color)), bg = bright_shade_color, command = askForBrightShadeColor)
bright_shade_button.grid(row = 8, column = 3, sticky = "w")
bright_shade_intensity_label = Label(text = "Intensity:")
bright_shade_intensity_label.grid(row = 9, column = 2, sticky = "e")
bright_shade_intensity_scale = Scale(orient = HORIZONTAL, from_ = 0, to = 100, command = generate)
bright_shade_intensity_scale.set(10)
bright_shade_intensity_scale.grid(row = 9, column = 3, sticky = "ew")

dark_shade_check_var = IntVar()
dark_shade_check = Checkbutton(text = "Blend dark colors with ", variable = dark_shade_check_var, command = generate)
dark_shade_check.grid(row = 10, column = 2, sticky = "e")
dark_shade_button = Button(text = dark_shade_color, width = 8, fg = text_color(hexToCol(dark_shade_color)), bg = dark_shade_color, command = askForDarkShadeColor)
dark_shade_button.grid(row = 10, column = 3, sticky = "w")
dark_shade_intensity_label = Label(text = "Intensity:")
dark_shade_intensity_label.grid(row = 11, column = 2, sticky = "e")
dark_shade_intensity_scale = Scale(orient = HORIZONTAL, from_ = 0, to = 100, command = generate)
dark_shade_intensity_scale.set(15)
dark_shade_intensity_scale.grid(row = 11, column = 3, sticky = "ew")

gamma_label = Label(text = "Gamma:")
gamma_label.grid(row = 12, column = 2, sticky = "e")
gamma_scale = Scale(orient = HORIZONTAL, from_ = 0.1, to = 4, resolution = 0.01, command = generate)
gamma_scale.set(1)
gamma_scale.grid(row = 12, column = 3, sticky = "ew")

generate_button = Button(text = "Generate GIMP palette", command = dumpGIMP)
generate_button.grid(row = 15, column = 2, sticky = "e")
dump_hex_button = Button(text = "Dump HTML codes", command = dumpHTML)
dump_hex_button.grid(row = 15, column = 3, sticky = "w")

colors_label = Label(text = "Base colors:")
colors_label.grid(row = 1, column = 4)

list_scroll = Scrollbar()
colors_list = Listbox(width = 10, height = list_max_height, yscrollcommand = list_scroll.set)
list_scroll.config(command = colors_list.yview)
list_scroll.grid(row = 2, column = 5, rowspan = list_max_height, sticky = "nse")
colors_list.grid(row = 2, column = 4, rowspan = list_max_height)

# PADDING
# pad_label_n = Label(text = " ", width = 2, height = 1)
# pad_label_n.grid(column = 0, row = 0, columnspan = 20)
# pad_label_s = Label(text = " ", width = 2, height = 1)
# pad_label_s.grid(column = 0, row = 22, columnspan = 20)
pad_label_w = Label(text = " ", width = 2, height = 1)
pad_label_w.grid(column = 0, row = 0, rowspan = 20)
pad_label_e = Label(text = " ", width = 2, height = 1)
pad_label_e.grid(column = 22, row = 0, rowspan = 20)

refreshColorList()

color_add_button = Button(text = "+", width = 2, command = addColor)
color_add_button.grid(row = 2, column = 6)

color_remove_button = Button(text = "-", width = 2, command = removeColor)
color_remove_button.grid(row = 3, column = 6)

generate()

mainloop()