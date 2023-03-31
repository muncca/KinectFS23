import cv2


def detect_area():
    # Open the default camera
    cap = cv2.VideoCapture(0)

    # Capture a frame from the camera
    ret, frame = cap.read()
    # Let the user select an ROI
    cv2.namedWindow("Select Object to Detect")
    cv2.resizeWindow("Select Object to Detect", 640, 480)
    roi = cv2.selectROI("Select Object to Detect", frame)

    # Crop the image to the selected ROI
    img_roi = frame[int(roi[1]):int(roi[1]+roi[3]), int(roi[0]):int(roi[0]+roi[2])]

    # Convert the cropped image to grayscale
    gray = cv2.cvtColor(img_roi, cv2.COLOR_BGR2GRAY)

    # Apply a threshold to the image
    ret, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)

    edges = cv2.Canny(gray, 100, 200)
    # Find contours in the image
    #edge detection with canny to esure that the contour is sharp
    contours, hierarchy = cv2.findContours(edges,thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Find the contour with the largest area
    max_area = 0
    max_contour = None
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > max_area:
            max_area = area
            max_contour = contour

    # Draw the contour with the largest area on the original image
    cv2.drawContours(img_roi, [max_contour], -1, (0, 255, 0), 2)

    # Show the original image with the selected ROI and the contour with the largest area
    cv2.imshow("Select Model", img_roi)
    cv2.waitKey(0)

    # Release the camera and close all windows
    cap.release()
    cv2.destroyAllWindows()

    return max_area
