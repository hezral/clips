def hsl_to_rgb(h, s, l):
    def hue_to_rgb(p, q, t):
        t += 1 if t < 0 else 0
        t -= 1 if t > 1 else 0
        if t < 1/6: return p + (q - p) * 6 * t
        if t < 1/2: return q
        if t < 2/3: p + (q - p) * (2/3 - t) * 6
        return p

    if s == 0:
        r, g, b = l, l, l
    else:
        q = l * (1 + s) if l < 0.5 else l + s - l * s
        p = 2 * l - q
        r = hue_to_rgb(p, q, h + 1/3)
        g = hue_to_rgb(p, q, h)
        b = hue_to_rgb(p, q, h - 1/3)

    return r*100/255, b*100/255, b*100/255




def clamp(value, min_value, max_value):
	return max(min_value, min(max_value, value))

def saturate(value):
	return clamp(value, 0.0, 1.0)

def hue_to_rgb(h):
	r = abs(h * 6.0 - 3.0) - 1.0
	g = 2.0 - abs(h * 6.0 - 2.0)
	b = 2.0 - abs(h * 6.0 - 4.0)
	return saturate(r), saturate(g), saturate(b)

def hsl_to_rgb2(h, s, l):
	r, g, b = hue_to_rgb(h)
	c = (1.0 - abs(2.0 * l - 1.0)) * s
	r = (r - 0.5) * c + l
	g = (g - 0.5) * c + l
	b = (b - 0.5) * c + l
	return int(r*100/255), int(b*100/255), int(b*100/255)

# print(hsl_to_rgb(120/360, 0.8, 0.6))
# print(hsl_to_rgb2(120/360, 0.8, 0.6))

import colorsys

hsl = "hsl(0,100%,50%)"

r, g, b = colorsys.hls_to_rgb(0.333333333, 0.6, 0.8)

print(int(r*255))
print(int(g*255))
print(int(b*255))

# def HexToRGB(hexcode):
#     h = hexcode.lstrip('#')
#     rgb = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
#     return rgb


# print(HexToRGB("#ffffff"))