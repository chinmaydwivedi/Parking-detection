import cv2 as open_cv
import numpy as np
import os
import sys

from colors import COLOR_WHITE, COLOR_RED, COLOR_GREEN, COLOR_BLUE
from drawing_utils import draw_contours


class CoordinatesGenerator:
    KEY_RESET = ord("r")
    KEY_QUIT = ord("q")
    KEY_SWITCH_MODE = ord("m")

    def __init__(self, image, output, color):
        self.output = output
        self.caption = image
        self.color = color

        # Check if the image file exists and is accessible
        if not os.path.isfile(image):
            print(f"Error: Image file '{image}' not found. Please check the file path.")
            sys.exit(1)
        
        # Load the image and check if it was loaded successfully
        self.image = open_cv.imread(image)
        if self.image is None:
            print(f"Error: Failed to load image file '{image}'. The file might be corrupted or in an unsupported format.")
            sys.exit(1)
            
        self.original_image = self.image.copy()  # Keep original image for reset
        self.temp_image = self.image.copy()  # For drawing temporary shapes
        self.click_count = 0
        self.ids = 0
        self.coordinates = []
        self.drawing_mode = "polygon"  # Default mode: "polygon" or "rectangle"
        self.current_position = (0, 0)  # To track current mouse position for preview

        # Display instructions on image
        self.__add_instructions()

        open_cv.namedWindow(self.caption, open_cv.WINDOW_GUI_EXPANDED)
        open_cv.setMouseCallback(self.caption, self.__mouse_callback)

    def __add_instructions(self):
        # Add instructions text on top of the image
        instructions = [
            "Instructions:",
            "- Click to select points",
            "- Press 'q' to finish current shape",
            "- Press 'm' to switch between polygon/rectangle mode",
            "- Press 'r' to reset",
            f"- Current mode: {self.drawing_mode.upper()}"
        ]
        
        y = 30
        for text in instructions:
            open_cv.putText(self.image, text, (10, y), open_cv.FONT_HERSHEY_SIMPLEX, 
                          0.6, (0, 255, 255), 2)
            y += 25

    def generate(self):
        print("Coordinates Generator Started")
        print("- Click to define parking space corners")
        print("- Press 'm' to switch between polygon and rectangle modes")
        print("- Press 'r' to reset current shape")
        print("- Press 'q' when finished with all spaces")
        
        while True:
            # Show image with preview shape if needed
            display_image = self.temp_image.copy()
            
            # In rectangle mode, show preview of rectangle while moving mouse
            if self.drawing_mode == "rectangle" and self.click_count == 1:
                pt1 = self.coordinates[0]
                pt2 = self.current_position
                open_cv.rectangle(display_image, pt1, pt2, (0, 255, 255), 2)
                
            open_cv.imshow(self.caption, display_image)
            key = open_cv.waitKey(1)  # Update more frequently for smooth preview

            if key == CoordinatesGenerator.KEY_RESET:
                self.__reset_current()
            elif key == CoordinatesGenerator.KEY_QUIT:
                if self.click_count > 0:  # If we have a shape in progress, finish it
                    self.__handle_done()
                else:
                    break  # Otherwise, exit the program
            elif key == CoordinatesGenerator.KEY_SWITCH_MODE:
                self.__switch_mode()
                
        open_cv.destroyWindow(self.caption)

    def __switch_mode(self):
        """Switch between polygon and rectangle drawing modes"""
        self.__reset_current()  # Reset current shape
        if self.drawing_mode == "polygon":
            self.drawing_mode = "rectangle"
        else:
            self.drawing_mode = "polygon"
            
        # Update image with new mode info
        self.image = self.original_image.copy()
        self.temp_image = self.image.copy()
        self.__add_instructions()
        print(f"Switched to {self.drawing_mode.upper()} mode")

    def __reset_current(self):
        """Reset the current shape being drawn"""
        self.click_count = 0
        self.coordinates = []
        self.temp_image = self.image.copy()  # Reset temporary image
        print("Reset current shape")

    def __mouse_callback(self, event, x, y, flags, params):
        self.current_position = (x, y)
        self.temp_image = self.image.copy()  # Reset temporary image for drawing
        
        # Always draw preview in rectangle mode if one point selected
        if self.drawing_mode == "rectangle" and self.click_count == 1:
            pt1 = self.coordinates[0]
            pt2 = self.current_position
            open_cv.rectangle(self.temp_image, pt1, pt2, (0, 255, 255), 2)

        if event == open_cv.EVENT_LBUTTONDOWN:
            self.coordinates.append((x, y))
            self.click_count += 1
            
            # Handle based on mode
            if self.drawing_mode == "rectangle" and self.click_count == 2:
                # For rectangle mode, we only need 2 points (top-left and bottom-right)
                # Convert to 4 points for consistency
                x1, y1 = self.coordinates[0]
                x2, y2 = self.coordinates[1]
                
                # Create 4 corners from the 2 points
                self.coordinates = [
                    (min(x1, x2), min(y1, y2)),  # top-left
                    (max(x1, x2), min(y1, y2)),  # top-right
                    (max(x1, x2), max(y1, y2)),  # bottom-right
                    (min(x1, x2), max(y1, y2))   # bottom-left
                ]
                self.__handle_done()
                
            elif self.drawing_mode == "polygon" and self.click_count >= 4:
                # In polygon mode, require at least 4 points before allowing completion
                if flags & open_cv.EVENT_FLAG_CTRLKEY:  # Hold CTRL to auto-complete
                    self.__handle_done()
                else:
                    self.__handle_click_progress()
                    
            elif self.click_count > 1:
                self.__handle_click_progress()

        open_cv.imshow(self.caption, self.temp_image)

    def __handle_click_progress(self):
        """Draw lines between points as they're being added"""
        # Draw all lines connecting sequential points
        for i in range(1, len(self.coordinates)):
            open_cv.line(self.temp_image, 
                       self.coordinates[i-1], 
                       self.coordinates[i], 
                       (255, 0, 0), 2)
            
        # Draw points as small circles
        for point in self.coordinates:
            open_cv.circle(self.temp_image, point, 3, COLOR_RED, -1)

    def __handle_done(self):
        """Finalize the current shape being drawn"""
        # If in polygon mode, ensure we have at least 4 points
        if self.drawing_mode == "polygon" and self.click_count < 4:
            print("Need at least 4 points to complete a polygon")
            return
            
        # In polygon mode, close the shape by connecting last point to first
        if self.drawing_mode == "polygon":
            # Draw the closing line
            open_cv.line(self.temp_image,
                       self.coordinates[-1],
                       self.coordinates[0],
                       self.color,
                       2)

        # Create numpy array for drawing
        coordinates_array = np.array(self.coordinates)
        
        # Write coordinates to YAML output
        self.output.write("-\n          id: " + str(self.ids) + "\n          coordinates: [")
        for i, point in enumerate(self.coordinates):
            self.output.write("[" + str(point[0]) + "," + str(point[1]) + "]")
            if i < len(self.coordinates) - 1:
                self.output.write(",")
        self.output.write("]\n")

        # Draw the final contour on the image
        draw_contours(self.temp_image, coordinates_array, str(self.ids + 1), COLOR_WHITE)
        
        # Update the base image to include this shape
        self.image = self.temp_image.copy()
        
        print(f"Added space #{self.ids + 1}")
        self.ids += 1
        self.click_count = 0
        self.coordinates = []
