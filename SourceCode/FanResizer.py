__version__ = "2.0.1"
from LanguagePack import *
from PIL import Image, ImageDraw, ImageChops
import base64
from io import BytesIO
import FanWheel_Resizer as fw

import threading, os, pickle, ctypes
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import askdirectory

"""
Fanseline Resizer - GUI
By Twitter @FanKetchup
https://github.com/FerryYoungFan/FanselineResizer
"""

# GUI Language
lang = lang_en
lang_code = "en"

img_format_dict = "*.jpg *.jpeg *.png *.gif *.bmp *.ico *.dib *.webp *.tiff *.tga *.txt *.b64 *.base64"
b64_format_dict = "*.txt *.b64 *.base64"


def loadImage(pathread):
    global image_open, image_preview
    if "*" + fw.getFileSuffix(pathread) in b64_format_dict.split(" "):
        print("base 64 file")
        data64 = open(pathread, "r")
        img_b64 = BytesIO(base64.b64decode(data64.read()))
        image_open = Image.open(img_b64).convert('RGBA')
    else:
        image_open = Image.open(pathread).convert('RGBA')
    if image_open is None:
        raise Exception("FileNotFoundError")
    else:
        if tk_output_path.get() is None or tk_output_path.get().replace(" ", "") == "":
            tk_output_path.set(fw.getFilePath(pathread) + lang["Resized"] + "/")
        tk_filename.set(fw.getFileName(pathread, False))
        image_preview = cropToCenter(image_open, list_crop_mode.current(), 300)
        insertList(olist, [min(image_preview.size)])
        refresh()
        viewer["bg"] = "#00FF00"


def selectImage():
    global image, image_open, viewer, image_prev, image_prev_tk, tk_output_path, tk_filename
    try:
        global tk_image_path
        pathread = askopenfilename(
            filetypes=[(lang["Image files"], img_format_dict), ("Base 64", b64_format_dict),
                       (lang["All files"], "*.*")])
        if not pathread or not os.path.exists(pathread):
            return
        else:
            tk_image_path.set(pathread)
            entry_img.xview("end")
            try:
                loadImage(pathread)
            except:
                tkinter.messagebox.showinfo(lang["Notice"], lang["Cannot Open Image."])
    except:
        return


def selectOutput():
    try:
        global tk_output_path
        pathexport = askdirectory()
        pathexport = pathexport + '/'
        if not pathexport or pathexport == "/":
            return
        else:
            tk_output_path.set(pathexport + lang["Resized"] + "/")
            entry_output.xview("end")
    except:
        return


def addSize(*args):
    global tk_width, olist
    try:
        add_width = tk_width.get()
        if add_width is not None:
            if add_width < 4:
                add_width = 4
            elif add_width > 8000:
                add_width = 8000
            add_width = int(add_width)
            insertList(olist, [add_width])
            tk_width.set("")
    except:
        pass


def clearSize():
    global olist
    olist.delete(0, "end")
    try:
        name = tk_preset.get()
    except:
        return
    if lang["Custom"] in name:
        c_num = int(name.replace(lang["Custom"], "").replace(" ", "").replace("-", "")) - 1
        custom[c_num] = parseList(olist)


def deleteSize():
    global olist
    try:
        olist.delete(olist.curselection())
    except:
        pass
    try:
        name = tk_preset.get()
    except:
        return
    if lang["Custom"] in name:
        c_num = int(name.replace(lang["Custom"], "").replace(" ", "").replace("-", "")) - 1
        custom[c_num] = parseList(olist)


def getRadius():
    global tk_radius
    try:
        radius = tk_radius.get()
        if radius < 0:
            radius = 0.0
        elif radius > 1:
            radius = 1.0
        return radius
    except:
        return 0


def saveConfig():
    global lang_code, custom, olist
    vdic = {
        "lang_code": lang_code,
        "size_list": parseList(olist),
        "custom": custom,
        "current_select": list_preset.current(),
        "radius": tk_radius.get(),
        "output_path": tk_output_path.get(),
        "filetype": tk_filetype.get(),
        "filename": tk_filename.get(),
        "crop_mode": list_crop_mode.current(),
        "image_path": tk_image_path.get(),
    }
    try:
        directory = os.path.dirname("./")
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open('./FanselineResizer.fconfig', 'wb') as handle:
            pickle.dump(vdic, handle, protocol=pickle.HIGHEST_PROTOCOL)
    except:
        pass


def loadConfig():
    global lang, lang_code, custom, olist, list_preset, image_open
    try:
        with open('./FanselineResizer.fconfig', 'rb') as handle:
            vdic = pickle.load(handle)
            lang_code = vdic["lang_code"]
            if lang_code == "cn_s":
                lang = lang_cn_s
            else:
                lang = lang_en
            custom = vdic["custom"]
            replaceList(olist, vdic["size_list"])
            if vdic["current_select"] > 0:
                list_preset.current(vdic["current_select"])
            tk_radius.set(vdic["radius"])
            tk_output_path.set(vdic["output_path"])
            tk_filetype.set(vdic["filetype"])
            pathread = vdic["image_path"]
            list_crop_mode.current(vdic["crop_mode"])
            try:
                loadImage(pathread)
            except:
                return
            tk_image_path.set(pathread)
    except:
        return


def resetGUI(*args):
    global lang_code, exit_flag, root, list_lang
    if list_lang.get() == "简体中文":
        lang_code = "cn_s"
    else:
        lang_code = "en"
    saveConfig()
    exit_flag = False
    root.destroy()


def resizing():
    global image_open
    btn_blend["state"] = "disabled"
    ctr = 1
    size_list = parseList(olist)
    combine_name = fw.getFilePath(tk_output_path.get()) + tk_filename.get()
    log_path = fw.getFilePath(tk_output_path.get()) + lang["Resize_Log"] + "_" + tk_filename.get() + ".txt"
    log_content = lang["Export path:"] + "\n"
    log_content = log_content + fw.getFilePath(tk_output_path.get()) + "\n\n"
    log_content = log_content + lang["The following {0} image(s) were exported:"].format(len(size_list)) + "\n\n"
    progress["value"] = 0
    image_crop = cropToCenter(image_open, list_crop_mode.current())
    img_copy = resizeMax(image_crop, max(size_list))
    img_copy = cropRadius(img_copy, getRadius())
    for size in size_list:
        temp_image = resizeMax(img_copy, size)
        if "jpg" in tk_filetype.get():
            temp_image = temp_image.convert("RGB")
        if (not "base64" in tk_filetype.get()) and (not "b64" in tk_filetype.get()):
            path = combine_name + "_" + str(temp_image.width) + "x" + str(temp_image.height) + tk_filetype.get()
            path = fw.protectPath(path)
            try:
                temp_image.save(path, quality=100)
            except:
                pass
        else:
            path = combine_name + "_" + str(temp_image.width) + "x" +\
                   str(temp_image.height) + "_" + tk_filetype.get().replace("-", "_") + ".txt"
            formatb = tk_filetype.get().split("-")[-1].upper()
            if formatb == "JPG":
                formatb = "JPEG"
            path = fw.protectPath(path)
            try:
                output_buffer = BytesIO()
                temp_image.save(output_buffer, quality=100, format=formatb)
                base64_str = base64.b64encode(output_buffer.getvalue())
                base64_str = str(base64_str)[2:-1]
                b64_file = open(path, "w")
                b64_file.write(base64_str)
                b64_file.close()
            except:
                pass

        log_content = log_content + fw.getFileName(path) + "\n"
        ctr += 1
        progress["value"] = (100 * ctr / len(size_list))
    log_path = fw.protectPath(log_path)
    log_file = open(log_path, "w")
    log_file.write(log_content)
    log_file.close()
    btn_blend["state"] = "normal"
    tkinter.messagebox.showinfo(lang["Notice"], lang["Resizing done!"])


def runResize(*args):
    global olist, image_open, tk_output_path, tk_filename
    if image_open is None:
        tkinter.messagebox.showinfo(lang["Notice"], lang["Please open an image first!"])
        return
    size_list = parseList(olist)
    if len(size_list) == 0:
        tkinter.messagebox.showinfo(lang["Notice"], lang["Please add image size first!"])
        return
    fname = tk_filename.get()
    if not fw.legalFileName(fname):
        tkinter.messagebox.showinfo(lang["Notice"], lang["Please input the corrent file name!"])
        return
    try:
        output_path = fw.getFilePath(tk_output_path.get())
        fw.ensureDir(output_path)
        if not os.path.exists(output_path):
            raise Exception("DirectoryError")
    except:
        tkinter.messagebox.showinfo(lang["Notice"], lang["Please select the correct output path!"])
        return
    saveConfig()
    th_blend = threading.Thread(target=resizing)
    th_blend.setDaemon(True)
    th_blend.start()


def insertList(listbox, list_values):
    current_list = parseList(listbox)
    current_list.sort()
    for index in list_values:
        if index in current_list:
            continue
        list_name = "{0}x{1}".format(index, index)+lang[" (Max)"]
        listbox.insert(0, list_name)

    try:
        name = tk_preset.get()
    except:
        return
    if lang["Custom"] in name:
        c_num = int(name.replace(lang["Custom"], "").replace(" ", "").replace("-", "")) - 1
        custom[c_num] = parseList(listbox)


def replaceList(listbox, list_values):
    listbox.delete(0, "end")
    insertList(listbox, list_values)


def parseInt(str_value):
    try:
        return int(str_value.split("x")[0])
    except:
        return 0


def parseList(_olist):
    str_list = _olist.get(0, tk.END)
    opt_list = []
    for index in str_list:
        opt_list.append(parseInt(index))
    return opt_list


def _resizeImage(event):
    global image_prev, image, viewer, image_prev_tk
    win_w = event.width
    win_h = event.height
    if image is not None:
        try:
            img_w, img_h = image.size
            ratio = min(win_w / img_w, win_h / img_h)
            ratio = ratio
            width = int(round(img_w * ratio))
            height = int(round(img_h * ratio))
            image_prev = image.resize((width, height), Image.ANTIALIAS)
            image_prev_tk = fw.pil2tk(image_prev)
            viewer.configure(image=image_prev_tk)
        except:
            pass


def refresh(*args):
    global image, image_open, image_prev, image_prev_tk, viewer, image_preview
    if image_preview is not None:
        image = cropRadius(image_preview, getRadius())
        img_w, img_h = image.size
        win_w, win_h = viewer.winfo_width(), viewer.winfo_height()
        ratio = min(win_w / img_w, win_h / img_h)
        ratio = ratio
        width = int(round(img_w * ratio))
        height = int(round(img_h * ratio))
        image_prev = image.resize((width, height), Image.ANTIALIAS)
        image_prev_tk = fw.pil2tk(image_prev)
        viewer.configure(image=image_prev_tk)


def refreshCrop(*args):
    global image, image_open, image_prev, image_prev_tk, viewer, image_preview
    mode = list_crop_mode.current()
    if image_open is not None:
        image_preview = cropToCenter(image_open, list_crop_mode.current(), 300)
        refresh()


def resizeMax(img, maxsize=None):
    if maxsize is not None:
        ratio = max(img.size) / maxsize
        newsize = int(round(img.size[0] / ratio)), int(round(img.size[1] / ratio))
        img = img.resize(newsize, Image.ANTIALIAS)
        return img
    else:
        return img


def cropToCenter(img, mode=0, maxsize=None):
    img = resizeMax(img, maxsize)

    if mode == 0:
        width, height = img.size
        square = min(width, height)
        left = (width - square) / 2
        top = (height - square) / 2
        right = (width + square) / 2
        bottom = (height + square) / 2
        return img.crop((left, top, right, bottom))
    elif mode == 1:
        psize = max(img.size)
        _canvas = Image.new("RGBA", (psize, psize), (0, 0, 0, 0))
        _x = (psize - img.width) // 2
        _y = (psize - img.height) // 2
        _canvas.paste(img, (_x, _y), img)
        return _canvas
    elif mode == 2:
        width, height = img.size
        square = min(width, height)
        return img.resize((square, square), Image.ANTIALIAS)
    elif mode == 3:
        return img


def cropRadius(img, radius=0.0):
    img = img.copy()
    if radius > 1:
        radius = 1
    elif radius < 0:
        radius = 0
    width, height = img.size
    if radius != 0:
        scale = 8  # Antialiasing Drawing
        size_anti = width * scale, height * scale
        r = int(round(radius * min(width, height) * scale / 2))
        old_mask = img.split()[-1].resize(size_anti)
        mask = Image.new('L', size_anti, 255)
        draw = ImageDraw.Draw(mask)
        draw.rectangle((0, r, size_anti[0], size_anti[1] - r), fill=0)
        draw.rectangle((r, 0, size_anti[0] - r, size_anti[1]), fill=0)
        draw.ellipse((0, 0, 2 * r, 2 * r), fill=0)
        draw.ellipse((0 + size_anti[0] - 2 * r, 0, 2 * r + size_anti[0] - 2 * r, 2 * r), fill=0)
        draw.ellipse((0, 0 + size_anti[1] - 2 * r, 2 * r, 2 * r + size_anti[1] - 2 * r), fill=0)
        draw.ellipse((0 + size_anti[0] - 2 * r, 0 + size_anti[1] - 2 * r, 2 * r + size_anti[0] - 2 * r,
                      2 * r + size_anti[1] - 2 * r), fill=0)
        try:
            mask = ImageChops.subtract(old_mask, mask)
        except Exception as e:
            print(e)
        mask = mask.resize((width, height), Image.ANTIALIAS)
        img.putalpha(mask)
        return img
    else:
        return img


def presetImage(*args):
    global tk_preset, preset_dic, olist, custom
    try:
        preset_name = tk_preset.get()
    except:
        return

    if lang["Custom"] in preset_name:
        code = preset_name.replace(lang["Custom"], "").replace(" ", "").replace("-", "")
        c_num = int(code) - 1
        replaceList(olist, custom[c_num])
        return

    for name, value in preset_dic.items():
        if preset_name == name:
            replaceList(olist, value)
            break


if __name__ == '__main__':
    exit_flag = False
    GUI_WIDTH = 600
    GUI_HEIGHT = 430

    while not exit_flag:
        exit_flag = True
        isRunning = False

        root = tk.Tk()

        image_open = None
        image_preview = None
        image = None
        image_prev = None
        image_prev_tk = None

        custom = []
        loadConfig()

        old_vdic = None
        tk_image_path = tk.StringVar()
        tk_output_path = tk.StringVar()
        tk_filename = tk.StringVar()
        tk_lang = tk.StringVar()
        tk_preset = tk.StringVar()
        tk_filetype = tk.StringVar()
        tk_crop_mode = tk.StringVar()
        reset_crop = False

        tk_width = tk.IntVar(value=256)
        tk_radius = tk.DoubleVar(value=0.0)
        tk_radius.trace("w", lambda name, index, mode=tk_radius: refresh())

        root.title(lang["Fanseline Image Resizer"] + " - V." + __version__)
        canvas = tk.Canvas(root, width=GUI_WIDTH, height=GUI_HEIGHT)
        canvas.pack()
        frame1 = tk.Frame(master=root)
        frame1.place(relx=0, rely=0, relwidth=1, relheight=1, anchor='nw')

        rely, devy = 0.01, 0.09
        relh = 0.075

        label_lang = tk.Label(master=frame1, text="Language/语言:", anchor="e")
        label_lang.place(relwidth=0.18, relheight=relh, relx=0.05, rely=rely, anchor='nw')
        list_lang = ttk.Combobox(master=frame1, textvariable=tk_lang, state="readonly")
        list_lang["values"] = ("English", "简体中文")
        if lang_code == "cn_s":
            list_lang.current(1)
        else:
            list_lang.current(0)
        list_lang.place(relwidth=0.17, relheight=relh, relx=0.23, rely=rely, anchor='nw')
        list_lang.bind("<<ComboboxSelected>>", resetGUI)

        label_preset = tk.Label(master=frame1, text=lang["Preset:"], anchor="e")
        label_preset.place(relwidth=0.1, relheight=relh, relx=0.5, rely=rely, anchor='nw')
        list_preset = ttk.Combobox(master=frame1, textvariable=tk_preset, state="readonly")
        preset_dic = {
            lang["Desktop"]: [16, 24, 32, 48, 72, 96, 144, 192, 256],
            "Android": [16, 32, 48, 128, 256],
            "iOS": [29, 58, 57, 60, 75, 80, 87, 120, 144, 152, 180, 512, 1024],
            "iPad": [40, 48, 72, 76, 50, 100, 144, 167],
        }
        custom_num = 5
        for i in range(custom_num):
            preset_dic[lang["Custom"] + " " + str(i + 1)] = []
            custom.append([])
        list_preset["values"] = list(preset_dic.keys())
        list_preset.bind("<<ComboboxSelected>>", presetImage)
        list_preset.set(lang["-Please Select-"])
        list_preset.place(relwidth=0.19, relheight=relh, relx=0.6, rely=rely, anchor='nw')

        list_crop_mode = ttk.Combobox(master=frame1, textvariable=tk_crop_mode, state="readonly")
        list_crop_mode["values"] = (lang["Zoom In"], lang["Zoom Out"], lang["Stretch"], lang["Origin"])
        list_crop_mode.place(relwidth=0.15, relheight=relh, relx=0.8, rely=rely, anchor='nw')
        list_crop_mode.current(0)
        list_crop_mode.bind("<<ComboboxSelected>>", refreshCrop)

        rely += devy
        entry_img = tk.Entry(master=frame1, textvariable=tk_image_path)
        entry_img.place(relwidth=0.74, relheight=relh, relx=0.05, rely=rely, anchor='nw')
        btn_img = tk.Button(master=frame1, text=lang["Open"], command=selectImage)
        btn_img.place(relwidth=0.15, relheight=relh, relx=0.8, rely=rely, anchor='nw')

        rely += devy

        olist = tk.Listbox(master=frame1)
        olist.place(relwidth=0.29, relheight=relh * 5.8, relx=0.5, rely=rely, anchor='nw')

        btn_delete = tk.Button(master=frame1, text=lang["Delete"], command=deleteSize)
        btn_delete.place(relwidth=0.15, relheight=relh, relx=0.8, rely=rely, anchor='nw')

        ### Image Viewer ###
        viewer = tk.Label(frame1, bg="#666666")
        viewer.place(relwidth=0.44, relheight=relh * 8.15, relx=0.05, rely=rely, anchor='nw')
        viewer.bind('<Configure>', _resizeImage)

        rely += devy
        btn_clear = tk.Button(master=frame1, text=lang["Clear"], command=clearSize)
        btn_clear.place(relwidth=0.15, relheight=relh, relx=0.8, rely=rely, anchor='nw')

        rely += relh * 4.8

        label_width = tk.Label(master=frame1, textvariable=tk.StringVar(value=lang["Image Size:"]), anchor="e")
        label_width.place(relwidth=0.15, relheight=relh, relx=0.5, rely=rely, anchor='nw')
        entry_width = tk.Entry(master=frame1, textvariable=tk_width)
        entry_width.place(relwidth=0.14, relheight=relh, relx=0.65, rely=rely, anchor='nw')
        entry_width.bind('<Return>', addSize)
        btn_add = tk.Button(master=frame1, text=lang["Add"], command=addSize)
        btn_add.place(relwidth=0.15, relheight=relh, relx=0.8, rely=rely, anchor='nw')

        rely += devy

        label_radius = tk.Label(master=frame1, textvariable=tk.StringVar(value=lang["Border-R:"]), anchor="e")
        label_radius.place(relwidth=0.15, relheight=relh, relx=0.5, rely=rely, anchor='nw')
        list_radius = ttk.Combobox(master=frame1, textvariable=tk_radius)
        list_radius.place(relwidth=0.14, relheight=relh, relx=0.65, rely=rely, anchor='nw')
        list_radius["values"] = [round((1 - i / 20) * 100) / 100 for i in list(range(21))]
        list_radius.current(20)
        btn_refresh = tk.Button(master=frame1, text=lang["Refresh"], command=refresh)
        btn_refresh.place(relwidth=0.15, relheight=relh, relx=0.8, rely=rely, anchor='nw')

        rely += devy

        entry_output = tk.Entry(master=frame1, textvariable=tk_output_path)
        entry_output.place(relwidth=0.44, relheight=relh, relx=0.05, rely=rely, anchor='nw')
        entry_fname = tk.Entry(master=frame1, textvariable=tk_filename)
        entry_fname.place(relwidth=0.29, relheight=relh, relx=0.5, rely=rely, anchor='nw')
        btn_output = tk.Button(master=frame1, text=lang["Output to"], command=selectOutput)
        btn_output.place(relwidth=0.15, relheight=relh, relx=0.8, rely=rely, anchor='nw')

        rely += devy

        progress = ttk.Progressbar(master=frame1, orient=tk.HORIZONTAL, mode='determinate', value=0)
        progress.place(relwidth=0.44, relheight=relh, relx=0.05, rely=rely, anchor='nw')

        list_type = ttk.Combobox(master=frame1, textvariable=tk_filetype, state="readonly")
        list_type["values"] = [".png", ".ico", ".gif", ".jpg", ".bmp", ".webp", ".tiff", ".tga",
                               "base64-png", "base64-ico", "base64-gif", "base64-jpg", "base64-bmp", "base64-webp",
                               "base64-tiff", "base64-tga"]
        list_type.current(0)
        list_type.place(relwidth=0.29, relheight=relh, relx=0.5, rely=rely, anchor='nw')

        btn_blend = tk.Button(master=frame1, text=lang["Export"], command=runResize)
        btn_blend.place(relwidth=0.15, relheight=relh, relx=0.8, rely=rely, anchor='nw')

        loadConfig()
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
            ScaleFactor = ctypes.windll.shcore.GetScaleFactorForDevice(0)
            root.tk.call('tk', 'scaling', ScaleFactor / 75)  # DPI settings
            fr_logo = b'iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAD/ElEQVR4nJ2VS2xUVRjHf985d+7M9DXtFISCtpVKyyvyUAlGNBofG3bGYISV0ZWuwZhgIiQmENSdLIgbFxAfMYHYGBPtRhdNpBqQFiS1jW3RUqZQOh3mde89n4tppzYlZMq3OLnJSf7P7+TKvmP9GyVhT6vIHo3COCA84AgggmJiRefcL6HlbeN8PreJhuc1DB4IXASsEYwRIlVyxUiKpWIiXtf4ihdGpzxBnw3ysw4RUyuoEUEEnCrl0FEKHCJCuj7Gno1p5vIBlyZmXNzKi15FQ+3KnSrFwBFEjrhnWJ9O8nh7E09uaGbrI420Nvgc+eqqRJGKeCLeSuOIe5butUme2NDMrkdTdLc14HuL5qdmS1wamyXpW5wqNRMoYBCOvtbD9o7UUldOiZziWcMf41myhZBUvU8UKSvIHUphxKkf/yaTLQMQRlq5M4K1lV4GRmaW5F0zgSokfcvwZI7DZ4eYnivjWcG5eRIRCuWIwYk54jGDcysgWFCULYR4RhjL5Dl8ZohMtoQxQhBV0P78N8eN2eJ8J1obgQCRU5xTdne1sL0zRdK3jN7Mc+jMFTLZEjFrcKr8NnqHIFREZB6ee5esVDJXrXwrcOTVbvb2tALw02CGT3tHmLiV59CZIU4e3MbqJp+B0Tv4XoVswfcyByJgRSiHDs8a8qWInZ0p9va0Vp28tG01PesasEYYny7wwddX+fWvGf6ZqcSjuoi3hMCp4nuGY/s30bGqjlwxqBSpi+SVA1Qrq9mY9Bi9eZej315DVReulxMYEcqBo2NVHTs7Uxzbv4mH00mcKpcnsvQNZjAiGIHvL05x5focSd8SRlp9aP9XvjDVDkQgiJSnNjSjCm3NCU4c2Mp7Z4cYny7wSe8Ivb9PoQpD17PE7GIU9wJe5sCpkogZdj/WglPl56u3WNsc5/iBLbSvSlIKHUPXs1yemCUeM8uiuC+BCJQDx7p0kq419QzfuMv7X17h/MAN2poTHH9jC+vTCSKnNCS8+yq+J4ERoRQ6tnc0gVQKbKmPcfK7Yc4PTNLWkuDkwa10PVRPsexqVl8l0HmS3V0tCLB5fSMfvb6Z1kafj3tHOHdhkjWpOG++0I5nZUUOZN/xfo1UScYsX7y7iyB0jE8X2NGZon/4Nh9+cw1rhHXpBDdnSzin1IQvAqpFzxghVwh5pruVxoTHuQuTnO4b4+nuFkan8tWXOZbJE7O1l7vo4ER/VAodO9qbxLNGBieyBJFSChyeleqOi9x/HZeOKmJVNSp66rSvsSn98sWx20QKyZjF8wy+Z3EKC4Eo1P5jVcSva5JSbuYHLwy9t6SQ+yyZSDyHC2KRc0adEK0siapwjDixsXKQz/aFnr7zH20BzvqarZSNAAAAAElFTkSuQmCC'
            root.iconphoto(False, tk.PhotoImage(data=fr_logo))
        except:
            pass


        def disable_event():
            saveConfig()
            root.destroy()


        root.protocol("WM_DELETE_WINDOW", disable_event)
        frame1.tkraise()
        root.mainloop()
