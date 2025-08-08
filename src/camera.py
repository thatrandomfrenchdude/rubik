import cv2 as cv
cap = cv.VideoCapture(2)       # try 1 or 2 if the feed stays black
while cap.isOpened():
    ok, frame = cap.read()
    if not ok: break
    cv.imshow("Arducam 3", frame)
    if cv.waitKey(1) == ord('q'):
        break
cap.release(); cv.destroyAllWindows()