# doyle-background-subtraction
This is command line based Python 3 program that reimplements an algorithm developed by the Doyle group at MIT to assist in the background removal of fluorescence microscopy images.

If you use this implementation, please cite the original paper:

**Revisiting the Conformation and Dynamics of DNA in Slitlike Confinement Jing Tang, Stephen L. Levy, Daniel W. Trahan, Jeremy J. Jones, Harold G. Craighead, and Patrick S. Doyle Macromolecules 2010 43 (17), 7368-7377 DOI: 10.1021/ma101157x**
```
@article {tang2010revisiting,
  title={Revisiting the Conformation and Dynamics of DNA in Slitlike Confinement},
  volume={43},
  ISSN={1520-5835},
  url={http://dx.doi.org/10.1021/ma101157x},
  DOI={10.1021/ma101157x},
  number={17},
  journal={Macromolecules},
  publisher={American Chemical Society (ACS)},
  author={Tang, Jing and Levy, Stephen L. and Trahan, Daniel W. and Jones, Jeremy   J. and Craighead, Harold G. and Doyle, Patrick S.},
  year={2010},
  month={Sep},
  pages={7368–7377}}
}
```
Additionally, please cite this project:

**Luc Capaldi. Python 3 Implementation of the Doyle Background Subtraction Algorithm. https://github.com/luccapaldi/doyle-background-subtraction, 2020. Accessed YYYY-MM-DD.**
```
@Misc{doyle-background-subtract-subtraction,
  author = {Luc Capaldi},
  title = {Python 3 Implementation of the Doyle Background Subtraction Algorithm},
  howpublished = {\url{https://github.com/luccapaldi/doyle-background-subtraction}},
  note = {Accessed YYYY-MM-DD},
  year = 2020,
}
```
Finally, if your workflow includes the use of **ImageJ/Fiji**, I strongly recommend using the plugin implemented [here](https://github.com/xcapaldi/imagej_noise-subtract).

## Background/Algorithm
The algorithm perform a background subtraction on a single channel of an image. It was designed specifically to process raw, high contrast (fluorescent) images of DNA but may be applied to any high contrast image (with mixed results). There are two steps:
1. **Initial subtraction**: The mean and standard deviation of the the boundary pixel intensities are calculated and the mean is subtracted from each pixel in the image; negative values are rounded up to zero.
2. **Individual noise spot removal**: Each pixel in the image, excluding those in the two outermost layers, is iterated. For each, the mean intensity of the boundary pixels for the 3x3 and 5x5 region surrounding regions are computed. If this value is less than the cutoff (3 by default) times the standard deviation of the boundary pixels for the entire image, the pixel intensity is set to 0.

            3x3:                   5x5:
       O O O O O O O          O O O O O O O
       O O O O O O O          O X X X X X O
       O O X X X O O          O X O O O X O
       O O X P X O O          O X O P O X O
       O O X X X O O          O X O O O X O
       O O O O O O O          O X X X X X O
       O O O O O O O          O O O O O O O

Be aware that the final image size will be reduced by 4 pixels in each direction due to individual noise spot removal described above.

## Requirements
Python 3 is required, as well as the following packages:
1. argparse
2. numpy
3. tifffile
4. scikit-image
Note: tifffile is only required if you need to background subtract tiff image stacks.

## Usage
```
usage: doyle_background_subtract.py [-h] [-s [SOURCE [SOURCE ...]]]
                                    [-o [OUTPUT [OUTPUT ...]]] [-c [CLOSE]]
                                    [-f [FAR]] [-cs CUTOFF] [-st [STACK]]

Perform Doyle background subtraction.

optional arguments:
  -h, --help            show this help message and exit
  -s [SOURCE [SOURCE ...]], --source [SOURCE [SOURCE ...]]
                        path to source file
  -o [OUTPUT [OUTPUT ...]], --output [OUTPUT [OUTPUT ...]]
                        path to output file
  -c [CLOSE], --close [CLOSE]
                        use 3x3 bound (default True)
  -f [FAR], --far [FAR]
                        use 5x5 bound (default True)
  -cs CUTOFF, --cutoff CUTOFF
                        multiple of SD used as cutoff for subtraction
  -st [STACK], --stack [STACK]
                        specify if source is a tiff image stack
```
### -s, --source
N paths are accepted as source locations for the background subtraction.

### -o, --output
N paths are accepted as destination location for the background subtraction. You do not need to specify a destination for each source. Each destination will be paired with the corresponding source. If there are more sources than destinations, the excess files will be saved in the script folder and assigned their original filename, appended with "-subtracted".

### -c, --close
Use the 3x3 region in the algorithm implementation. It is used by default.

### -f, --far
Use the 5x5 region in the algorithm implementation. It is used by default.

### -cs, --cutoff
Specify the multiple of the boundary standard devation that defines the pixel cutoff during the individual noise spot removal. For fluorescent microscopy images, a cutoff of 3.00 (the default) is recommended. For irregular use cases, such as for images with low contrast, a very low value (e.g. 0.01) is preferable.

### -st, --stack
Specify that the input file is a tiff image stack.

## Examples
```
python doyle-background-subtraction.py -s source_image.png -o destination_image.png
python doyle-background-subtraction.py -s ~/files/data/images/image1.jpg test_image.jpg -o ~/files/results/images/image1_result.jpg image2_test.jpg
python doyle-background-subtraction.py -s stack.tiff -o stack_subtracted.tiff --stack
python doyle-background-subtraction.py -s in.png -c True -f False -cs 0.05
```

## Contributing
This is an ongoing project and likely contains bugs and other issues. There are a variety of features that have not yet been implemented. If you want to contribute, or require some feature for a project, please contact me.

## License
This work is freely available under the MIT License.
