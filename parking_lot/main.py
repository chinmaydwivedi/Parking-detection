import argparse
import yaml
import os
import sys
from coordinates_generator import CoordinatesGenerator
from motion_detector import MotionDetector
from colors import *
import logging


def main():
    logging.basicConfig(level=logging.INFO)
    
    try:
        args = parse_args()
        
        image_file = args.image_file
        data_file = args.data_file
        video_file = args.video_file
        start_frame = args.start_frame
        
        # Print file path information for the user
        print_file_info(image_file, data_file, video_file)
        
        # Check if video file exists
        if not os.path.isfile(video_file):
            logging.error(f"Video file '{video_file}' not found. Please check the file path.")
            logging.info(f"Try creating the directory if it doesn't exist: {os.path.dirname(os.path.abspath(video_file))}")
            if os.path.basename(video_file) != video_file:  # If it looks like a path with directories
                logging.info(f"Make sure the directory exists: {os.path.dirname(os.path.abspath(video_file))}")
            return
        
        if image_file is not None:
            # Check if image file exists before proceeding
            if not os.path.isfile(image_file):
                logging.error(f"Image file '{image_file}' not found. Please check the file path.")
                if os.path.basename(image_file) != image_file:  # If it looks like a path with directories
                    logging.info(f"Make sure the directory exists: {os.path.dirname(os.path.abspath(image_file))}")
                return
                
            with open(data_file, "w+") as points:
                try:
                    generator = CoordinatesGenerator(image_file, points, COLOR_RED)
                    generator.generate()
                except Exception as e:
                    logging.error(f"Error generating coordinates: {str(e)}")
                    return

        try:
            with open(data_file, "r") as data:
                points = yaml.safe_load(data)
                if points is None:
                    logging.error(f"No data found in {data_file}. Make sure the file is not empty.")
                    return
                detector = MotionDetector(video_file, points, int(start_frame))
                detector.detect_motion()
        except FileNotFoundError:
            logging.error(f"Data file '{data_file}' not found. Please check the file path.")
        except Exception as e:
            logging.error(f"Error during motion detection: {str(e)}")
    
    except Exception as e:
        logging.error(f"An unexpected error occurred: {str(e)}")
        logging.info("Make sure you're using the correct command format:")
        logging.info("python main.py --image <image_file> --data <data_file> --video <video_file> [--start-frame <frame_number>]")
        logging.info("Note: --video is singular, not plural (--videos)")


def print_file_info(image_file, data_file, video_file):
    """Print information about file locations to help users understand paths."""
    logging.info(f"Current working directory: {os.getcwd()}")
    logging.info("Using the following file paths:")
    
    if image_file:
        abs_image_path = os.path.abspath(image_file)
        logging.info(f"Image file: {abs_image_path}")
        if not os.path.isfile(image_file):
            logging.warning(f"⚠️ Image file does not exist at the specified path")
    
    abs_data_path = os.path.abspath(data_file)
    logging.info(f"Data file: {abs_data_path}")
    
    abs_video_path = os.path.abspath(video_file)
    logging.info(f"Video file: {abs_video_path}")
    if not os.path.isfile(video_file):
        logging.warning(f"⚠️ Video file does not exist at the specified path")


def parse_args():
    parser = argparse.ArgumentParser(description='Parking Lot Space Detector')

    parser.add_argument("--image",
                        dest="image_file",
                        required=False,
                        help="Image file to generate coordinates on")

    parser.add_argument("--video",
                        dest="video_file",
                        required=True,
                        help="Video file to detect motion on")

    parser.add_argument("--data",
                        dest="data_file",
                        required=True,
                        help="Data file to be used with OpenCV")

    parser.add_argument("--start-frame",
                        dest="start_frame",
                        required=False,
                        default=1,
                        help="Starting frame on the video")
    
    # Check for common errors in command line arguments
    if '--videos' in sys.argv and '--video' not in sys.argv:
        logging.error("Error: Used '--videos' instead of '--video'")
        logging.info("Correct usage is '--video', not '--videos'")
        raise ValueError("Invalid argument: Use '--video' instead of '--videos'")
        
    return parser.parse_args()


if __name__ == '__main__':
    main()
