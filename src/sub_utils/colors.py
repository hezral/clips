from .validators import validate_string_with_regex

def is_valid_color_code(str):
    '''
    Function validate is any of the HEX, RGB, RGBA, HSL, HSLA color code
    Function validate hexadecimal color code
    https://www.geeksforgeeks.org/how-to-validate-hexadecimal-color-code-using-regular-expression/
    '''
    HEX = ("hex", r"^#([\da-f]{3}|[\dA-F]{3}){1,2};?\s?$")
    RGB = ("rgb", r"^[Rr][Gg][Bb]\(\d{1,3}%?(,\s?\d{1,3}%?){2}\);?\s?$")
    RGBA = ("rgba", r"^[Rr][Gg][Bb][Aa]\((\d{1,3}%?,\s?){3}(1|0?\.\d+)\);?\s?$")
    HSL = ("hsl", r"^[Hh][Ss][Ll]\(\d{1,3}%?(,\s?\d{1,3}%?){2}\);?\s?$")
    HSLA = ("hsla", r"^[Hh][Ss][Ll][Aa]\((\d{1,3}%?,\s?){3}(1|0?\.\d+)\);?\s?$")
    color_regex = (HEX, RGB, RGBA, HSL, HSLA)

    for regex in color_regex:
        if validate_string_with_regex(str, regex[1]):
            return True, regex[0]
        else:
            pass

def hsl_to_rgb(hslcode):
    ''' Function to convert hsl string to RGB color code '''

    import colorsys
    h, s, l = hslcode
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    rgb = (int(r*255), int(g*255), int(b*255))
    return rgb

def hex_to_rgb(hexcode):
    '''
    Function to convert hexadecimal string to RGB color code
    https://stackoverflow.com/a/29643643/14741406
    '''
    h = hexcode.lstrip('#')
    rgb = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
    return rgb

def is_light_color(rgb=[0,0,0]):
    '''
    Function to determine light or dark color using RGB values
    https://stackoverflow.com/a/58270890/14741406
    '''
    import math
    [r,g,b] = rgb
    hsp = math.sqrt(0.299 * (r * r) + 0.587 * (g * g) + 0.114 * (b * b))
    if (hsp > 127.5):
        return 'light'
    else:
        return 'dark'

def get_css_background_color(str):
    '''
    function to extract background-color from html files
    https://stackoverflow.com/a/4894134/14741406
    '''
    HEX = ("hex", r"^#([\da-f]{3}|[\dA-F]{3}){1,2};?\s?$")
    RGB = ("rgb", r"^[Rr][Gg][Bb]\(\d{1,3}%?(,\s?\d{1,3}%?){2}\);?\s?$")
    RGBA = ("rgba", r"^[Rr][Gg][Bb][Aa]\((\d{1,3}%?,\s?){3}(1|0?\.\d+)\);?\s?$")
    HSL = ("hsl", r"^[Hh][Ss][Ll]\(\d{1,3}%?(,\s?\d{1,3}%?){2}\);?\s?$")
    HSLA = ("hsla", r"^[Hh][Ss][Ll][Aa]\((\d{1,3}%?,\s?){3}(1|0?\.\d+)\);?\s?$")
    color_regex = (HEX, RGB, RGBA, HSL, HSLA)
    
    import re
    regex = r"(?:background-color)\:(.*?)\;"
    result = re.search(regex, str)

    if result is not None:
        css_background_color = re.search(regex, str).group(1).strip()

        for regex in color_regex:
            if validate_string_with_regex(css_background_color, regex[1]):
                return css_background_color

def get_css_text_color(str):
    '''
    function to extract background-color from html files
    https://stackoverflow.com/a/4894134/14741406
    '''
    HEX = ("hex", r"^#([\da-f]{3}|[\dA-F]{3}){1,2};?\s?$")
    RGB = ("rgb", r"^[Rr][Gg][Bb]\(\d{1,3}%?(,\s?\d{1,3}%?){2}\);?\s?$")
    RGBA = ("rgba", r"^[Rr][Gg][Bb][Aa]\((\d{1,3}%?,\s?){3}(1|0?\.\d+)\);?\s?$")
    HSL = ("hsl", r"^[Hh][Ss][Ll]\(\d{1,3}%?(,\s?\d{1,3}%?){2}\);?\s?$")
    HSLA = ("hsla", r"^[Hh][Ss][Ll][Aa]\((\d{1,3}%?,\s?){3}(1|0?\.\d+)\);?\s?$")
    color_regex = (HEX, RGB, RGBA, HSL, HSLA)
    
    import re
    regex = r"(?:[^\-]color)\:(.*?)\;"
    result = re.search(regex, str)

    if result is not None:
        css_text_color = re.search(regex, str).group(1).strip()

        for regex in color_regex:
            if validate_string_with_regex(css_text_color, regex[1]):
                return css_text_color

def to_rgb(color_string):
    '''
    Function to convert color codes to string by stripping other caharcters and returning rgba codes in tuple format
    '''
    color_string = color_string.strip(" ").strip(";").strip(")") #strip "space ; )" chars    
    color_string = color_string.replace(" ","") #replace space chars
    color_string = color_string.split("(")
    
    if "#" in color_string[0]:
        a = 1
        rgb = hex_to_rgb(color_string[0])

    elif "rgb" in color_string[0] and not "rgba" in color_string[0]:
        r, g, b = color_string[1].split(",")[0:3]
        r = int(int(r.strip("%"))/100*255) if r.find("%") != -1 else int(r)
        g = int(int(g.strip("%"))/100*255) if g.find("%") != -1 else int(g)
        b = int(int(b.strip("%"))/100*255) if b.find("%") != -1 else int(b)
        a = 1
        rgb = (r, g, b)

    elif "rgba" in color_string[0]:
        r, g, b, a = color_string[1].split(",")
        
        r = int(int(r.strip("%"))/100*255) if r.find("%") != -1 else int(r)
        g = int(int(g.strip("%"))/100*255) if g.find("%") != -1 else int(g)
        b = int(int(b.strip("%"))/100*255) if b.find("%") != -1 else int(b)
        a = float(a.split(")")[0])
        rgb = (r, g, b)

    elif "hsl" in color_string[0] and not "hsla" in color_string[0]:
        h, s, l = color_string[1].split(",")[0:3]
        h = float(h) / 360
        s = float(s.replace("%","")) / 100
        l = float(l.replace("%","")) / 100
        a = 1
        rgb = hsl_to_rgb((h, s, l))

    elif "hsla" in color_string[0]:
        h, s, l, a = color_string[1].split(",") 
        h = int(h) / 360
        s = int(s.replace("%","")) / 100
        l = int(l.replace("%","")) / 100
        a = float(a.split(")")[0])
        rgb = hsl_to_rgb((h, s, l))
    
    else:
        rgb = None
        a = None
    
    if a == 1.0:
        a = 1
        return rgb, a
    else:
        return rgb, float(a)
