# Parking Space Detection in OpenCV

A computer vision project that detects available parking spaces in video footage using OpenCV.

## Table of Contents
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Process](#process)
- [Future Work](#future-work)

## Overview
[![Unedited parking lot](https://s3-us-west-2.amazonaws.com/parkinglot-opencv/parking_shot.png)](https://www.youtube.com/watch?v=SszV59YBn_o)

This project uses OpenCV to detect available parking spaces in a parking lot video. The system allows users to mark parking spaces and then automatically tracks whether these spaces are occupied or available throughout the video.

### Features
- Interactive selection of parking spaces to track
- Real-time detection of occupied and available spaces
- Visual indication of space status (green for available, red for occupied)
- Frame-by-frame analysis of parking lot status

## Installation

### Prerequisites
- Python 3.6 or higher
- OpenCV 4.x
- NumPy
- PyYAML

### Setup
1. Clone this repository:
   ```bash
   git clone https://github.com/chinmaydwivedi/Parking-detection.git
   cd Parking-detection
   ```

2. Install the required dependencies:
   ```bash
   pip install opencv-python numpy pyyaml
   ```

## Usage

### Basic Usage
```bash
python main.py --image images/parking_lot_1.png --data data/coordinates_1.yml --video videos/parking_lot_1.mp4 --start-frame 400
```

### Command Line Arguments
- `--image`: Path to a still image of the parking lot
- `--data`: Path to save/load the parking space coordinates
- `--video`: Path to the video file of the parking lot
- `--start-frame`: (Optional) Frame number to start from in the video

### Marking Parking Spaces
1. Run the program with the arguments above
2. Click on the 4 corners of each parking space you want to track
3. Press 'q' when you've finished marking all desired spaces
4. The program will begin analyzing the video with the marked spaces

### Controls During Video Playback
- Press 'q' to quit
- Press 'p' to pause/resume

## Project Structure
```
Parking-detection/
├── main.py                  # Main entry point
├── motion_detector.py       # Motion detection functionality
├── images/                  # Sample images
│   └── parking_lot_1.png
├── videos/                  # Sample videos
│   └── parking_lot_1.mp4
└── data/                    # Saved parking space coordinates
    └── coordinates_1.yml
```

## Process
### The beginning
My first thought was how can I tell whether a parking space is empty?

Well, if a space is empty, it would be the color of the pavement. Otherwise, it wouldn't be.

I also knew that I needed a way to mark the boundaries of the space, so that I could return the number of spots available.

Let's grab an image and head to the OpenCV docs!

### Line Detection
To detect the parking spots, I knew I could take advantage of the lines demarking the boundaries.

The Hough Transform is a popular feature extraction technique for detecting lines. OpenCV encapsulates the math of the Hough Transform into HoughLines(). Further abstraction in captured in HoughLinesP(), which is the probabilistic model of creating lines with the points that HoughLines() returns. For more info, check out the [OpenCV Hough Lines tutorial.](https://docs.opencv.org/3.0-beta/doc/py_tutorials/py_imgproc/py_houghlines/py_houghlines.html)

The following is a walkthrough to prepare an image to detect lines with the Hough Transform. Links point to OpenCV documentation for each function. Arguments for each function are given as keyword args for clarity.

[Reading](https://docs.opencv.org/master/d4/da8/group__imgcodecs.html#ga288b8b3da0892bd651fce07b3bbd3a56) in this image:
```python
img = cv2.imread(filename='examples/hough_lines/p_lots.jpg')
```
![Org_hough](https://s3-us-west-2.amazonaws.com/parkinglot-opencv/org.png)



I [converted it to gray scale](https://docs.opencv.org/master/d7/d1b/group__imgproc__misc.html#ga397ae87e1288a81d2363b61574eb8cab) to reduce the info in the photo:
```python
gray = cv2.cvtColor(src=img, code=cv2.COLOR_BGR2GRAY)
```

![Gray_hough](https://s3-us-west-2.amazonaws.com/parkinglot-opencv/s_gray.png)



Gave it a good [Gaussian blur](https://docs.opencv.org/master/d4/d86/group__imgproc__filter.html#gaabe8c836e97159a9193fb0b11ac52cf1) to remove even more unnecessary noise:
```python
blur_gray = cv2.GaussianBlur(src=gray, ksize=(5, 5), sigmaX=0)
```
![Blur_hough](https://s3-us-west-2.amazonaws.com/parkinglot-opencv/s_blur.png)



Detected the edges with [Canny](https://docs.opencv.org/master/dd/d1a/group__imgproc__feature.html#ga04723e007ed888ddf11d9ba04e2232de):
```python
edges = cv2.Canny(image=blur_gray, threshold1=50, threshold1=150, apertureSize=3)
```
![Canny_hough](https://s3-us-west-2.amazonaws.com/parkinglot-opencv/s_canny.png)


And then, a few behind-the-scenes rhos and thetas later, we have our [Hough Line](https://docs.opencv.org/master/dd/d1a/group__imgproc__feature.html#ga8618180a5948286384e3b7ca02f6feeb) results.

```python
lines = cv2.HoughLinesP(image=edges, rho=1, theta=np.pi/180, threshold=80, minLineLength=15, maxLineGap=5)
for x1,y1,x2,y2 in lines[0]:
    cv2.line(img,(x1,y1),(x2,y2),(0,255,0),2)
```
![Hough_transform](https://s3-us-west-2.amazonaws.com/parkinglot-opencv/s_line.png)




Well that wasn't quite what I expected.

I experimented a bit with the hough line, but toggling the parameters kept getting me the same one line.

A bit of digging and I found a [promising post on StackOverflow](https://stackoverflow.com/questions/45322630/how-to-detect-lines-in-opencv)

After following the directions of the top answer, I got this:

![SO_transform](https://s3-us-west-2.amazonaws.com/parkinglot-opencv/stack_overflow_lines.png)


Which gave me more lines, but I still had to figure out which lines were part of the parking space and which weren't. Then, I would also need to detect when a car moved from a spot.

I was running into a challenge; with this approach, I needed an empty parking lot to overlay with an image of a non-empty lot. Which would also call for a mask to cover unimportant information (trees, light posts, etc.)

Given my scope for the weekend, it was time to find another approach.

### Drawing Rectangles

If my program wasn't able to detect parking spots on it's own, maybe it was reasonable to expect that the user give positions for each of the parking spots.

Now, the goal was to find a way to click on the parking lot image and to store the 4 points that made up a parking space for all of the spaces in the lot.

I discovered that I could do this using a [mouse as a "paintbrush"](https://docs.opencv.org/3.0-beta/doc/py_tutorials/py_gui/py_mouse_handling/py_mouse_handling.html)

After some calculations for the center of the rectangle (to label each space), I got this:

![Drawn Rectangles](https://s3-us-west-2.amazonaws.com/parkinglot-opencv/draw_rectangles.png)

### Finishing touches

After drawing the rectangles, all there was left to do was examine the area of each rectangle to see if there was a car in there or not.

By taking each (filtered and blurred) rectangle, determining the area, and doing an average on the pixels, I was able to tell when there wasn't a car in the spot if the average was high (more dark pixels). I changed the color of the bounding box accordingly and viola, a parking detection program!

The code for drawing the rectangles and motion detection is pretty generic. It's separated out into classes and should be reusable outside of the context of a parking lot. I have tested this with two different parking lot videos and it worked pretty well. I plan to make other improvements and try to separate OpenCV references to make code easier to test. I'm open to ideas and feedback.

## Future work
- Hook up a webcam to a Raspberry Pi and have live parking monitoring at home!
- [Transform parking lot video to have overview perspective](http://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_geometric_transformations/py_geometric_transformations.html) (for clearer rectangles)
- Experiment with [HOG descriptors](https://gurus.pyimagesearch.com/lesson-sample-histogram-of-oriented-gradients-and-car-logo-recognition/) to detect people or other objects of interest
- Add a web interface for remote monitoring
- Implement a more robust detection algorithm for different lighting conditions
- Create a database to track historical parking data

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## License
This project is open source and available under the [MIT License](LICENSE).
