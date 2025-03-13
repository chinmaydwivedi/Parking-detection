import cv2 as open_cv
import numpy as np
import logging
import time
from datetime import datetime
from drawing_utils import draw_contours
from colors import COLOR_GREEN, COLOR_WHITE, COLOR_BLUE, COLOR_RED


class MotionDetector:
    LAPLACIAN = 1.4  # Threshold for motion detection
    DETECT_DELAY = 1  # Delay in seconds before confirming status change

    def __init__(self, video, coordinates, start_frame):
        self.video = video
        self.coordinates_data = coordinates
        self.start_frame = start_frame
        self.contours = []
        self.bounds = []
        self.mask = []
        
        # Statistics
        self.total_spaces = len(coordinates)
        self.vacant_spaces = 0
        self.occupied_spaces = 0
        self.last_update = time.time()
        self.vacancy_history = []
        self.detection_sensitivity = self.LAPLACIAN
        
        # Reference frames for better comparison
        self.reference_frames = []
        self.frame_count = 0
        self.is_reference_set = False

    def detect_motion(self):
        capture = open_cv.VideoCapture(self.video)
        capture.set(open_cv.CAP_PROP_POS_FRAMES, self.start_frame)
        
        # Check if video opened successfully
        if not capture.isOpened():
            raise IOError(f"Cannot open video file {self.video}")

        coordinates_data = self.coordinates_data
        logging.debug("coordinates data: %s", coordinates_data)

        # Process all parking spaces and prepare detection data
        for p in coordinates_data:
            coordinates = self._coordinates(p)
            logging.debug("coordinates: %s", coordinates)

            rect = open_cv.boundingRect(coordinates)
            logging.debug("rect: %s", rect)

            new_coordinates = coordinates.copy()
            new_coordinates[:, 0] = coordinates[:, 0] - rect[0]
            new_coordinates[:, 1] = coordinates[:, 1] - rect[1]
            logging.debug("new_coordinates: %s", new_coordinates)

            self.contours.append(coordinates)
            self.bounds.append(rect)

            # Create mask for the parking space
            mask = open_cv.drawContours(
                np.zeros((rect[3], rect[2]), dtype=np.uint8),
                [new_coordinates],
                contourIdx=-1,
                color=255,
                thickness=-1,
                lineType=open_cv.LINE_8)

            mask = mask == 255
            self.mask.append(mask)
            logging.debug("mask: %s", self.mask)
            
            # Initialize reference frames
            self.reference_frames.append(None)

        statuses = [False] * len(coordinates_data)  # False = vacant, True = occupied
        times = [None] * len(coordinates_data)

        # Display controls
        print("Controls:")
        print("- Press 'q' to exit")
        print("- Press '+' to increase detection sensitivity")
        print("- Press '-' to decrease detection sensitivity")
        print("- Press 's' to save current frame")
        print("Motion detection started...")

        # Skip first few frames to stabilize camera and collect reference frames
        for _ in range(20):
            result, _ = capture.read()
            if not result:
                break

        while capture.isOpened():
            result, frame = capture.read()
            if frame is None:
                break

            if not result:
                raise CaptureReadError("Error reading video capture on frame %s" % str(frame))

            # Process the frame
            blurred = open_cv.GaussianBlur(frame.copy(), (5, 5), 3)
            grayed = open_cv.cvtColor(blurred, open_cv.COLOR_BGR2GRAY)
            new_frame = frame.copy()
            
            position_in_seconds = capture.get(open_cv.CAP_PROP_POS_MSEC) / 1000.0
            
            # Collect reference frames during first 30 frames
            if self.frame_count < 30 and not self.is_reference_set:
                self._collect_reference_frames(grayed)
                self.frame_count += 1
                
                # Show progress during initialization
                cv_text = f"Initializing: {int(self.frame_count/30*100)}%"
                open_cv.putText(new_frame, cv_text, (10, 30), 
                             open_cv.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
                open_cv.imshow(str(self.video), new_frame)
                open_cv.waitKey(1)
                continue
            
            self.is_reference_set = True
            
            # Process each parking space
            for index, c in enumerate(coordinates_data):
                status = self.__apply(grayed, index, c)

                # Handle status changes with delay to avoid flickering
                if times[index] is not None and self.same_status(statuses, index, status):
                    times[index] = None
                    continue

                if times[index] is not None and self.status_changed(statuses, index, status):
                    if position_in_seconds - times[index] >= MotionDetector.DETECT_DELAY:
                        statuses[index] = status
                        times[index] = None
                    continue

                if times[index] is None and self.status_changed(statuses, index, status):
                    times[index] = position_in_seconds

            # Update statistics
            self.vacant_spaces = statuses.count(False)  # Count vacant spaces
            self.occupied_spaces = statuses.count(True)  # Count occupied spaces
            
            # Add stats to history every 5 seconds
            current_time = time.time()
            if current_time - self.last_update > 5:
                self.vacancy_history.append((datetime.now(), self.vacant_spaces, self.occupied_spaces))
                self.last_update = current_time

            # Add parking space markers with status indicators
            for index, p in enumerate(coordinates_data):
                coordinates = self._coordinates(p)
                
                # Green for vacant, Blue for occupied
                color = COLOR_GREEN if not statuses[index] else COLOR_BLUE
                space_id = str(p["id"] + 1)
                
                # Draw the parking space contour
                draw_contours(new_frame, coordinates, space_id, COLOR_WHITE, color)

            # Display statistics on frame
            self.__draw_stats(new_frame)
            
            # Show the frame
            open_cv.imshow(str(self.video), new_frame)
            
            # Process keypresses
            k = open_cv.waitKey(1)
            if k == ord("q"):
                break
            elif k == ord("+") or k == ord("="):  # Increase sensitivity
                self.detection_sensitivity -= 0.1
                if self.detection_sensitivity < 0.1:
                    self.detection_sensitivity = 0.1
                print(f"Sensitivity increased: {self.detection_sensitivity:.1f}")
            elif k == ord("-") or k == ord("_"):  # Decrease sensitivity
                self.detection_sensitivity += 0.1
                print(f"Sensitivity decreased: {self.detection_sensitivity:.1f}")
            elif k == ord("s"):  # Save current frame
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"parking_status_{timestamp}.jpg"
                open_cv.imwrite(filename, new_frame)
                print(f"Saved frame as {filename}")
                
        # Clean up
        capture.release()
        open_cv.destroyAllWindows()
        
        # Print final statistics
        print("\nFinal Statistics:")
        print(f"Total spaces: {self.total_spaces}")
        print(f"Vacant spaces: {self.vacant_spaces}")
        print(f"Occupied spaces: {self.occupied_spaces}")
    
    def _collect_reference_frames(self, grayed):
        """Collect reference frames for better comparison"""
        for index, p in enumerate(self.coordinates_data):
            if self.reference_frames[index] is None:
                coordinates = self._coordinates(p)
                rect = self.bounds[index]
                roi_gray = grayed[rect[1]:(rect[1] + rect[3]), rect[0]:(rect[0] + rect[2])]
                self.reference_frames[index] = roi_gray

    def __apply(self, grayed, index, p):
        """Apply motion detection to a specific parking space"""
        coordinates = self._coordinates(p)
        rect = self.bounds[index]

        # Extract the region of interest (ROI) for this parking space
        roi_gray = grayed[rect[1]:(rect[1] + rect[3]), rect[0]:(rect[0] + rect[2])]
        
        # Compare against reference frame if available
        if self.reference_frames[index] is not None:
            # Calculate absolute difference between current frame and reference
            absdiff = open_cv.absdiff(roi_gray, self.reference_frames[index])
            _, thresholded = open_cv.threshold(absdiff, 30, 255, open_cv.THRESH_BINARY)
            
            # Apply laplacian for edge detection
            laplacian = open_cv.Laplacian(roi_gray, open_cv.CV_64F)
            
            # Calculate metrics
            motion_value = np.mean(np.abs(laplacian * self.mask[index]))
            diff_value = np.mean(thresholded * self.mask[index]) / 255.0
            
            # Combined metric
            combined_value = motion_value * 0.3 + diff_value * 10
            
            # FIXED LOGIC: Lower values mean less change (vacant), higher values mean more change (occupied)
            status = combined_value > self.detection_sensitivity
            
            logging.debug(f"Space {index}: motion value: {motion_value:.2f}, diff: {diff_value:.2f}, "
                         f"combined: {combined_value:.2f}, threshold: {self.detection_sensitivity:.2f}, "
                         f"occupied: {status}")
            
            return status
        else:
            # Fallback to just laplacian if no reference frame
            laplacian = open_cv.Laplacian(roi_gray, open_cv.CV_64F)
            motion_value = np.mean(np.abs(laplacian * self.mask[index]))
            
            # FIXED LOGIC: Lower values mean less change (vacant), higher values mean more change (occupied)
            # Higher threshold means more sensitivity (more likely to mark as vacant)
            status = motion_value > self.detection_sensitivity
            
            logging.debug(f"Space {index}: motion value: {motion_value:.2f}, threshold: {self.detection_sensitivity:.2f}, "
                         f"occupied: {status}")
            
            return status

    def __draw_stats(self, frame):
        """Draw statistics on the frame"""
        # Get frame dimensions
        height, width = frame.shape[:2]
        
        # Create semi-transparent overlay for the stats panel
        overlay = frame.copy()
        open_cv.rectangle(overlay, (10, 10), (250, 120), (0, 0, 0), -1)
        open_cv.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        
        # Add text for statistics
        open_cv.putText(frame, f"Parking Status", (20, 30), 
                      open_cv.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        open_cv.putText(frame, f"Total spaces: {self.total_spaces}", (20, 60), 
                      open_cv.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        # Vacant spaces in green
        open_cv.putText(frame, f"Vacant: {self.vacant_spaces}", (20, 85), 
                      open_cv.FONT_HERSHEY_SIMPLEX, 0.6, COLOR_GREEN, 2)
        
        # Occupied spaces in red
        open_cv.putText(frame, f"Occupied: {self.occupied_spaces}", (20, 110), 
                      open_cv.FONT_HERSHEY_SIMPLEX, 0.6, COLOR_RED, 2)
        
        # Add video time
        video_time = open_cv.getTickCount() / open_cv.getTickFrequency()
        open_cv.putText(frame, f"Time: {video_time:.1f}s", (width - 150, 30),
                      open_cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    @staticmethod
    def _coordinates(p):
        return np.array(p["coordinates"])

    @staticmethod
    def same_status(coordinates_status, index, status):
        return status == coordinates_status[index]

    @staticmethod
    def status_changed(coordinates_status, index, status):
        return status != coordinates_status[index]


class CaptureReadError(Exception):
    pass
