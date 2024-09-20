
# Description
This software is meant to automatically generate chapters of a given video, achieved using a scene change detection tools.

# How it works 
The script first uses "ffmpeg" to detect scene changes and output the data to a file
Then the script collects all timestamps out of the file and generates an xml file that contains this data in a standard format that can be imported.
Finally, the script calls "mkvtoolnix" via command line to generate a new mkv video file that is a copy of the original video file, with all the chapters that were detected embedded into the new mkv file.

# Environment Installation
 - Make sure you have python installed on your system
 - Download and install [ffmpeg](https://ffmpeg.org/download.html#build-windows)
 - - Add the absolute "bin" folder of the ffmpeg installation into the system PATH environment argument
 - Download and install [mkvtoolnix](https://mkvtoolnix.download/downloads.html#windows)
 - - Add the absolute folder of the program into the system PATH environment argument

# How to run
Simply execute the script file, giving it the input file absolute path as argument.

    DetectChaptersAndGenerateMkv.py input/file/full/path/input_video_file.mp4

Alternatively, on windows you can simply drag a video file onto the script file, which will do exactly the same thing

Also, its possible to specify the scene detection threshold by sending it after the first argument. (if not specified, the default is 0.3)

    DetectChaptersAndGenerateMkv.py input/file/full/path/input_video_file.mp4 scene_detection_threshold

# Results
If all runs correctly, a new mkv video file will be created at the same folder as the input file, as well as an xml chapters file that contains the detected chapters.
the xml file can be manually edited with "mkvtoolnix" to fine tune the results and re-generate the mkv file.
The chapters can be viewed and jump to by many video players. For me it seems that PotPlayer was the best one. it can show the chapters timestamp on the timeline scroll line.

# Modifying the Code
Possibly split the script into two steps. First will generate the chapters xml, which is then manually edited by the user.
The second script will take the same input video and a specified chapters xml file (edited by the user) and then generate the mkv file.

# Contributing
Pull requests are welcome. Make me smarted if you will ;)

# License
Allowed for use only if you are human
