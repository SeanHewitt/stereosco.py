# Stereosco.py
This is a Python script/library to converting two images into a stereoscopic 3D image. The output formats are currently anagraph, side-by-side (cross-eye and parallel) and over/under.

##Requirements
* Python3
* PIP

##Command-Line Examples
###Cross-eyed (Right/Left)
20% cropped from the top, resized to 1920x1080 and offset to the right by 100%.
```
./stereosco.py DSC_0611.JPG DSC_0610.JPG --crop 20% 0 0 0 --resize 1920 1080 --offset 100% --cross-eye
./stereosco.py DSC_0611.JPG DSC_0610.JPG -c 20% 0 0 0 -r 1920 1080 -f 100% -x
```

###Squashed Parallel (Left/Right)
```
./stereosco.py DSC_0611.JPG DSC_0610.JPG -c 20% 0 0 0 -r 1920 1080 -f 100% -ps
```

###Anagraph
```
./stereosco.py DSC_0596.JPG DSC_0597.JPG out.jpg -c 20% 40% 15% 40% -r 1920 1080 -a color
```

###Over/under (Left/Right)
20% cropped from left and right and resized to be 1400 wide, preserving the aspect ratio.
```
./stereosco.py DSC_5616.JPG DSC_5615.JPG out.jpg -r 1400 0 -c 0 20% 0 20% -o
```

###Help
```
python3 stereosco.py --help
```
