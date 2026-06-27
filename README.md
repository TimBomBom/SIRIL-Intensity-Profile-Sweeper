# Profile Sweep Script (GUI)

This python script is for SIRIL which allows users to make multiple intensity profiles at once between a start and end lines. The user specifies a starting vector (V1) and an end vector (V2) along with a number of profiles, *n*, to generate between those lines. The program will then call SIRIL's intensity profile tool *n* times starting along V1 and ending along V2, interpolating the path in-between.

Fair warning: I am not a great coder and despise python, so there might be a bit of instability in edge cases and the GUI isn't the prettiest. It was built as a solution to a project of mine, but am publishing for public use. Hopefully it is useful for *someone*. Also, zero AI was used in generating code for this plugin. As mentioned, it was made as part of a passion project and I don't want it tainted by something incapable of holding passion. It makes my life harder, sure, but I prefer to actually write my own code, even if it's crappy.

Feel free to change any of the settings in the code for your use cases (e.g. if you need to generate more than 100 profiles for some reason, just change the range from 2-100 to be whatever you want).

## Instructions for installation

Download the script `Profile_Sweep.py` to a directory of your choosing.
In SIRIL, open Preferences from the hamburger menu > Scripts. Paste the directory you saved the file to in `Scripts Storage Directories` and hit the rescan button. Click `Apply` and you are done.

Alternatively, you can look at the existing default directories listed in the text window and save the .py file to one of those. Refresh scripts after as well.


## Instructions for Use

First, select SIRIL's working/home directory to the place you wish files to be saved. The script will save .dat and .png versions of each profile to the working directory. It is recommended to make a dedicated folder where files will go and not let them save to the same place you keep the image.

Next, run the script in SIRIL's script dropdown menu. This will open the GUI (pictured below). There are three main sections: V1 Coordinates, V2 Coordinates, and Options. Each option/element has a tooltip visible upon hovering to explain what it does.


![photo of GUI](https://github.com/TimBomBom/SIRIL-Intensity-Profile-Sweeper/blob/main/images/Pasted%20image%2020260627161359.png)

*This is the script window that appears upon running with the default settings.*

## Specifying Coordinates

Both vectors have a starting coordinate `(x1, y1)` and an end coordinate `(x2, y2)` aka "from" and "to". You may enter their coordinates manually by typing them in, or employ the `Use Selection` feature. 

To use `Use Selection`, draw a selection in the image window in SIRIL and click the `Use Selection` button for the desired vector. The script will use the corners from the beginning and end of your selection and extract the coordinates to specify the start and end automatically. This is much quicker and easier than manually typing 4 coordinates.

![Photo of selection in SIRIL](https://github.com/TimBomBom/SIRIL-Intensity-Profile-Sweeper/blob/main/images/Pasted%20image%2020260627151138.png)
![Illustration of how the script uses the selection to determine start and end coords](https://github.com/TimBomBom/SIRIL-Intensity-Profile-Sweeper/blob/main/images/Pasted%20image%2020260627151537.png)

*After making a selection (top) the program will use the corners as the coordinates for either the start or end vector (bottom)*

Making new selections will overwrite the current values, however if you wish, you may also reset the coordinates to all zeroes by clicking the `Reset` button. This will only affect the vector you click it for.


## Options

`Colour Profile` specifies whether SIRIL draws a profile in Color or Mono mode. By default, it is enabled. Currently, CFA and tri-profile (mono) options are not included as I had no need for them.

`Number of Steps` is simply the number of profiles generated. By default, it is 2 (meaning it will create 2 profiles along V1 and V2), with values clamped from 2-100. 

`Filename Offset` tells the script what number to start naming saved files from. This is to prevent overwriting existing files. For example, if you generated 5 profiles (named `profile_1, profile_2, ..., profile_5`) and wanted to keep them, but generate 5 more from different coordinates, set `Filename Offset` to 6 so that subsequent files will be generated as `profile_6, profile_7, ..., profile_10`. It is set to 1 by default.



## Next Steps/Todo

I hope to add a feature to generate the maximum number of profiles between two vectors instead of specifying a number of steps. What I mean is the user can generate like 10 profiles along two vectors that are only 5px separated. This leads to a bunch of duplicate profiles generated along identical coordinates. To fix this, I might implement a feature to see how many lines could be interpolated and then generate that many profiles. It shouldn't be too hard to implement, but it might take a while as I work up to getting around to it.


