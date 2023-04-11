import pyk4a
from helpers import colorize
from pyk4a import Config, PyK4A, connected_device_count
import numpy as np
import pandas as pd
import cv2


class Detection:
    def __init__(self):
        self.device_id = self.get_device_id()

    @staticmethod
    def get_device_id():
        cnt = connected_device_count()
        if not cnt:
            print("No devices available")
            exit()
        print(f"Available devices: {cnt}")
        for device_id in range(cnt):
            device = PyK4A(device_id=device_id)
            device.open()
            print(f"{device_id}: {device.serial}")
            device.close()
            return device_id
    @staticmethod
    def detect_objects( image_path, accuracy_threshold, max_size_ratio):
        # ChatGPT
        image = cv2.imread(image_path)

        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Threshold the image
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        # Find contours in the image
        contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # Create a list to store the size, centerpoint, and accuracy of each object
        objects = []

        # Iterate through the contours and append the size, centerpoint, and accuracy to the objects list
        for contour in contours:
            # Get the area of the contour
            area = cv2.contourArea(contour)

            # Skip contours with zero area
            if area == 0:
                continue

            # Get the moments of the contour
            moments = cv2.moments(contour)

            # Calculate the centroid of the contour
            cx = int(moments['m10'] / moments['m00'])
            cy = int(moments['m01'] / moments['m00'])

            # Get the perimeter of the contour
            perimeter = cv2.arcLength(contour, True)

            # Approximate the shape of the contour as a polygon
            approx = cv2.approxPolyDP(contour, 0.04 * perimeter, True)

            # Calculate the number of vertices in the polygon
            vertices = len(approx)

            # Calculate the accuracy of the polygon to a square
            accuracy = abs(1 - (area / (perimeter ** 2 / 4)))

            # Check if the object is too large
            height, width = image.shape[:2]
            size_ratio = area / (height * width)
            if size_ratio > max_size_ratio:
                continue

            # Append the size, centerpoint, and accuracy to the objects list
            objects.append([area, (cx, cy), accuracy])

            # Draw the contour and centerpoint if the accuracy is above the threshold
            if accuracy > accuracy_threshold:
                cv2.drawContours(image, [contour], -1, (255, 255, 255), 2)
                cv2.drawMarker(image, (cx, cy), (0, 0, 255), cv2.MARKER_CROSS, 10, 2)
                # add area to contour on image
                cv2.putText(image, str(area), (cx, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        # Create a Pandas dataframe from the objects list
        df = pd.DataFrame
        df = pd.DataFrame(objects, columns=['area', 'centerpoint', 'accuracy'])
        
        return df, image

    @staticmethod
    def live_depth():

        #Modifikation of viewer depth
        k4a = PyK4A(
            Config(
                color_resolution=pyk4a.ColorResolution.OFF,
                depth_mode=pyk4a.DepthMode.NFOV_UNBINNED,
                synchronized_images_only=False,
            )
        )
        k4a.start()

        # getters and setters directly get and set on device
        k4a.whitebalance = 4500
        assert k4a.whitebalance == 4500
        k4a.whitebalance = 4510
        assert k4a.whitebalance == 4510

        while True:
            capture = k4a.get_capture()
            if np.any(capture.depth):
                # Convert depth image to a normalized 8-bit image
                depth_norm = cv2.normalize(capture.depth, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8UC1)

                # Apply a threshold to create a binary image
                _, threshold = cv2.threshold(depth_norm, 100, 255, cv2.THRESH_BINARY)

                # Find contours in the binary image
                contours, _ = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                closest_depth = float('inf')

                # Loop through each contour
                for contour in contours:
                    # Calculate the depth of the object by finding the mean depth value within the contour
                    mask = np.zeros_like(capture.depth)
                    cv2.drawContours(mask, [contour], 0, 255, -1)
                    depth_values = capture.depth[np.where(mask > 0)]
                    depth = np.mean(depth_values)

                    if depth < closest_depth:
                        closest_depth = depth

                # Write the closest depth in black
                cv2.putText(depth_norm, f"Depth: {closest_depth:.2f} mm", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

                cv2.imshow("k4a", colorize(depth_norm, (None, 5000), cv2.COLORMAP_HSV))
                key = cv2.waitKey(10)
                if key != -1:
                    cv2.destroyAllWindows()
                    break

        k4a.stop()

    @staticmethod
    def largest_rectangle():
        #Generated by CHATGPT
        k4a = PyK4A(
            Config(
                color_resolution=pyk4a.ColorResolution.RES_720P,
                depth_mode=pyk4a.DepthMode.NFOV_UNBINNED,
                synchronized_images_only=True,
            )
        )
        k4a.start()

        # getters and setters directly get and set on device
        k4a.whitebalance = 4500
        assert k4a.whitebalance == 4500
        k4a.whitebalance = 4510
        assert k4a.whitebalance == 4510

        max_rect_area = 0  # Variable to store the largest rectangle area found
        while True:
            capture = k4a.get_capture()
            if np.any(capture.color):
                # Convert the color image to grayscale
                gray = cv2.cvtColor(capture.color, cv2.COLOR_BGR2GRAY)

                # Apply Canny edge detection to the grayscale image
                edges = cv2.Canny(gray, 100, 200)

                # Find contours in the edge map
                contours, hierarchy = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

                # Loop over the contours and find rectangular ones
                for cnt in contours:
                    # Approximate the contour to a polygon
                    approx = cv2.approxPolyDP(cnt, 0.01 * cv2.arcLength(cnt, True), True)

                    # If the polygon has 4 vertices, it is likely a rectangle
                    if len(approx) == 4:
                        # Calculate the area of the rectangle
                        rect_area = cv2.contourArea(approx)

                        # If the area is larger than the previous largest, update the largest area and rectangle
                        if rect_area > max_rect_area:
                            max_rect_area = rect_area
                            max_rect = approx

                # Draw the largest rectangle on the color image
                if max_rect_area > 0:
                    cv2.drawContours(capture.color, [max_rect], 0, (0, 255, 0), 3)
                    print("Largest rectangle area:", max_rect_area)
                else:
                    print("No rectangular object found.")

                # Display the color image with the largest rectangle
                cv2.imshow("k4a", capture.color)

                # Exit if any key is pressed
                key = cv2.waitKey(10)
                if key != -1:
                    cv2.destroyAllWindows()
                    break

        k4a.stop()

        

def test_match(max_area, max_contour):
    # Initialize K4A camera
    k4a = PyK4A(
        Config(
            color_resolution=pyk4a.ColorResolution.RES_1080P,
            depth_mode=pyk4a.DepthMode.NFOV_UNBINNED,
            synchronized_images_only=True,
        )
    )
    k4a.start()

    while True:
        # Get a capture from the camera
        capture = k4a.get_capture()
        frame = capture.color[:, :, :3]
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

        # Convert the input image to 8-bit single channel image
        img_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        img_gray = cv2.GaussianBlur(img_gray, (5, 5), 0)

        # Apply a threshold to the image
        ret, thresh = cv2.threshold(img_gray, 0, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)

        # Find contours in the image
        contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Iterate over all contours and compute their similarity to the max_contour
        for contour in contours:
            # Compute the similarity between the current contour and the max_contour
            similarity = cv2.matchShapes(max_contour, contour, cv2.CONTOURS_MATCH_I3, 0)
            # Print the similarity score and draw the contour on the image
            print(f"Contour similarity: {similarity}")
            cv2.drawContours(frame, [contour], -1, (0, 0, 255), 2)

        # Show the image with all the detected contours
        cv2.imshow("Contour detection", frame)

        # Exit the loop if the user presses the 'q' key
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the camera and close all windows
    k4a.stop()
    cv2.destroyAllWindows()