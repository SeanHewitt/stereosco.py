#!/usr/bin/env python3
#
#	Stereosco.py, stereoscopic 3D image creator
#	Copyright (C) 2016 Sean Hewitt <contact@SeanHewitt.com>
#
#	This library is free software: you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation, either version 3 of the License, or
#	(at your option) any later version.
#
#	This library is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with this library.  If not, see <http://www.gnu.org/licenses/>.
#

from PIL import Image

def to_pixels(value, reference):
	try:
		if value.endswith("%"):
			return round((int(value[:-1])/100)*reference)
	except:
		pass
	return int(value)

def fix_orientation(image):
	try:
		orientation = image._getexif()[274]
	except:
		return image
	
	if orientation == 3:
		return image.rotate(180, expand=True)
	elif orientation == 6:
		return image.rotate(270, expand=True)
	elif orientation == 8:
		return image.rotate(90, expand=True)
	else:
		return image

def crop(image, sides):
	return image.crop((
		to_pixels(sides[3], image.size[1]),
		to_pixels(sides[0], image.size[0]),
		image.size[0]-to_pixels(sides[1], image.size[1]),
		image.size[1]-to_pixels(sides[2], image.size[0])))

def resize(image, size, offset="50%"):
	width_ratio = size[0]/image.size[0]
	height_ratio = size[1]/image.size[1]
	
	offset_crop = None
	if width_ratio > height_ratio:
		re_size = (size[0], round(image.size[1] * width_ratio))
		if size[1]:
			offset = to_pixels(offset, re_size[1]-size[1])
			offset_crop = (0, offset, size[0], size[1]+offset)
	elif width_ratio < height_ratio:
		re_size = (round(image.size[0] * height_ratio), size[1])
		if size[0]:
			offset = to_pixels(offset, re_size[0]-size[0])
			offset_crop = (offset, 0, size[0]+offset, size[1])
	else:
		re_size = (size[0], size[1])
	
	image = image.resize(re_size, Image.ANTIALIAS)
	if offset_crop:
		image = image.crop(offset_crop)
	return image

def squash(image, horizontal=True):
	if horizontal:
		new_size = (round(image.size[0]/2), image.size[1])
	else:
		new_size = (image.size[0], round(image.size[1]/2))
	return image.resize(new_size, Image.ANTIALIAS)

def join(images, horizontal=True):
	if horizontal:
		size = (images[0].size[0]*2, images[0].size[1])
		pos = (images[0].size[0], 0)
	else:
		size = (images[0].size[0], images[0].size[1]*2)
		pos = (0, images[0].size[1])
	
	output = Image.new("RGB", size)
	output.paste(images[0], (0, 0))
	output.paste(images[1], pos)
	return output

COLOR_MATRICES = {
	"true": ((0.299, 0.587, 0.114, 0, 0, 0, 0, 0, 0), (0, 0, 0, 0, 0, 0, 0.299, 0.587, 0.114)),
	"gray": ((0.299, 0.587, 0.114, 0, 0, 0, 0, 0, 0), (0, 0, 0, 0.299, 0.587, 0.114, 0.299, 0.587, 0.114)),
	"color": ((1, 0, 0, 0, 0, 0, 0, 0, 0), (0, 0, 0, 0, 1, 0, 0, 0, 1)),
	"half-color": ((0.299, 0.587, 0.114, 0, 0, 0, 0, 0, 0), (0, 0, 0, 0, 1, 0, 0, 0, 1)),
	"optimized": ((0, 0.7, 0.3, 0, 0, 0, 0, 0, 0), (0, 0, 0, 0, 1, 0, 0, 0, 1)),
	"dubois-red-cyan": ((0.456, 0.500, 0.175, -0.040, -0.038, -0.016, -0.015, -0.021, -0.005), (-0.043, -0.088, -0.002, 0.378, 0.734, -0.018, -0.072, -0.113, 1.226)),
	"dubois-red-cyan2": ((0.437, 0.449, 0.164, -0.062, -0.062, -0.024, -0.048, -0.050, -0.017), (-0.011, -0.032, -0.007, 0.377, 0.761, 0.009, -0.026, -0.093, 1.234)),
	"dubois-green-magenta": ((-0.062, -0.158, -0.039, 0.284, 0.668, 0.143, -0.015, -0.027, 0.021), (0.529, 0.705, 0.024, -0.016, -0.015, -0.065, 0.009, 0.075, 0.937)),
	"dubois-amber-blue": ((1.062, -0.205, 0.299, -0.026, 0.908, 0.068, -0.038, -0.173, 0.022), (-0.016, -0.123, -0.017, 0.006, 0.062, -0.017, 0.094, 0.185, 0.911))
}

def create_anaglyph(images, color_matrix):
	output = images[0].copy()
	left = output.load()
	right = images[1].load()
	
	m = color_matrix
	for y in range(0, output.size[1]):
		for x in range(0, output.size[0]):
			lr, lg, lb = left[x, y]
			rr, rg, rb = right[x, y]
			left[x, y] = (
				round(lr*m[0][0] + lg*m[0][1] + lb*m[0][2] + rr*m[1][0] + rg*m[1][1] + rb*m[1][2]),
				round(lr*m[0][3] + lg*m[0][4] + lb*m[0][5] + rr*m[1][3] + rg*m[1][4] + rb*m[1][5]),
				round(lr*m[0][6] + lg*m[0][7] + lb*m[0][8] + rr*m[1][6] + rg*m[1][7] + rb*m[1][8]))
	return output

def main():
	import argparse
	parser = argparse.ArgumentParser(description="Convert 2 images into a stereoscopic 3D image")

	parser.add_argument("image_left",
		metavar="LEFT", type=str, help="left image")
	parser.add_argument("image_right",
		metavar="RIGHT", type=str, help="right image")
	parser.add_argument("image_output",
		metavar="OUT", type=str, help="output image")
	parser.add_argument("image_output2",
		metavar="OUT2", nargs='?', type=str,
		help="optional second output image for split left and right")
	
	parser.add_argument("-x", "--cross-eye",
		dest='is_cross_eye', action='store_true',
		help="cross-eye output: Right/Left")
	parser.add_argument("-p", "--parallel",
		dest='is_parallel',  action='store_true',
		help="Parallel output: Left/Right")
	parser.add_argument("-o", "--over-under",
		dest='is_over_under', action='store_true',
		help="Over/under output: Left is over and right is under")
	parser.add_argument("-u", "--under-over",
		dest='is_under_over', action='store_true',
		help="Under/Over output: Left is under and right is over")
	
	parser.add_argument("-s", "--squash",
		dest='is_squash', action='store_true',
		help="Squash the two sides to make an image of size equal to that of the sides")
		
	parser.add_argument("-a", "--anaglyph",
		dest='anaglyph', nargs="?", type=str, metavar="method", const="dubois-red-cyan", 
		help="Anaglyph output with a choice of following methods: " +
			", ".join(sorted(COLOR_MATRICES.keys())) + " (default method: %(const)s)")

	parser.add_argument("-c", "--crop",
		dest='crop', type=str,
		nargs=4, metavar=("TOP", "RIGHT", "BOTTOM", "LEFT"), default=(0, 0, 0, 0),
		help="Crop both images in either pixels or percentage")

	parser.add_argument("-r", "--resize",
		dest='resize', type=int,
		nargs=2, metavar=("WIDTH", "HEIGHT"), default=(0, 0),
		help="Resize both images to WIDTHxHEIGHT: A side with 0 is calculated automatically to preserve aspect ratio")
	parser.add_argument("-f", "--offset",
		dest='offset', type=str, default="50%",
		help="Offset after resize from top or left in either pixels or percentage (default: %(default)s)")
	
	args = parser.parse_args()

	images = [Image.open(args.image_left), Image.open(args.image_right)]

	for i, _ in enumerate(images):
		images[i] = fix_orientation(images[i])
		
		if any(args.crop):
			images[i] = crop(images[i], args.crop)
		
		if any(args.resize):
			images[i] = resize(images[i], args.resize, args.offset)
	
	if args.anaglyph:
		output = to_anaglyph(images, COLOR_MATRICES[args.anaglyph])
		output.save(args.image_output)
	else:
		if not (args.is_cross_eye or args.is_parallel or
			args.is_over_under or args.is_under_over):
			args.is_cross_eye = True
			
		is_horizontal = args.is_cross_eye or args.is_parallel
		
		if args.is_squash:
			for i, _ in enumerate(images):
				images[0] = squash(images[0], is_horizontal)

		if args.is_cross_eye or args.is_under_over:
			images.reverse()

		if args.image_output2 is None:
			output = join(images, is_horizontal)
			output.save(args.image_output)
		else:
			images[0].save(args.image_output)
			images[1].save(args.image_output2)

if __name__ == '__main__':
	main()
