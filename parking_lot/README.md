# Parking Lot Motion Detector

This program detects motion in parking lots to identify vacant and occupied parking spaces.

## Requirements

- Python 3.x
- OpenCV
- PyYAML
- NumPy

## Installation

```bash
pip install opencv-python pyyaml numpy
```

## Quick Start Commands

```bash
# To generate coordinates and detect motion:
python main.py --image parking_lot.jpg --data coordinates.yml --video parking_lot_video.mp4

# To detect motion with existing coordinates:
python main.py --video parking_lot_video.mp4 --data coordinates.yml

# To start from a specific frame:
python main.py --video parking_lot_video.mp4 --data coordinates.yml --start-frame 100
```

## Usage

The program works in two steps:
1. Generate coordinates for parking spaces from an image
2. Detect motion in those spaces using a video file

### Step 1: Generate Coordinates

Run the program with an image file to define parking spaces:

```bash
python main.py --image [IMAGE_FILE] --data [DATA_FILE] --video [VIDEO_FILE]
```

When the image opens, follow these controls to mark parking spaces:

- **Click** to place points that define the parking space
- **M key** to switch between polygon and rectangle drawing modes
  - **Polygon mode**: Click at least 4 points to define a space
  - **Rectangle mode**: Click at two opposite corners to create a rectangle
- **Q key** to finish the current shape (in polygon mode)
- **R key** to reset the current shape if you make a mistake

Example:
```bash
python main.py --image parking_lot.jpg --data coordinates.yml --video parking_lot_video.mp4
```

### Step 2: Detect Motion

Once you have the coordinates file, you can run motion detection:

```bash
python main.py --video [VIDEO_FILE] --data [DATA_FILE]
```

During motion detection, you have these controls:
- **Q key** to exit the program
- **+ key** to increase detection sensitivity
- **- key** to decrease detection sensitivity
- **S key** to save the current frame as an image

Example:
```bash
python main.py --video parking_lot_video.mp4 --data coordinates.yml
```

### Additional Options

- Start from a specific frame in the video:
```bash
python main.py --video parking_lot_video.mp4 --data coordinates.yml --start-frame 100
```

Note: The script uses hyphen notation (--start-frame) for the starting frame parameter.

## File Paths

You can specify file paths in several ways:

1. **Relative paths**: If the files are in the same directory as main.py, just use the filename (e.g., `parking_lot.jpg`)
2. **Absolute paths**: For files in different locations, specify the full path (e.g., `/Users/username/Videos/parking_lot_video.mp4`)
3. **Path with spaces**: If your path contains spaces, enclose it in quotes (e.g., `"My Folder/parking_lot.jpg"`)

Example with absolute paths:
```bash
python main.py --image /Users/username/Pictures/parking_lot.jpg --data /Users/username/Documents/coordinates.yml --video /Users/username/Videos/parking_lot_video.mp4
```

## Troubleshooting

If the command doesn't work, check the following:

1. Ensure the video file and coordinates.yml are in the same directory as main.py or provide full paths
2. Verify that main.py has the correct argument parsing for `--start-frame` (with hyphen)
3. Check that the video file exists and is not corrupted
4. Run `python main.py --help` to see all available parameters and their correct format

## How It Works

1. The program uses the coordinates in the data file to identify parking spaces
2. It processes the video to detect motion in these spaces using Laplacian edge detection
3. It marks each space as vacant (green) or occupied (blue) based on the motion detected
4. Real-time statistics show the number of vacant and occupied spaces# Parking-detection
