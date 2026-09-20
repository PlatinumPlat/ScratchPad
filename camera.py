import cv2


class ScratchPadCamera:

    def __init__(self, camera_index=0):
        self.camera = cv2.VideoCapture(
            camera_index,
            cv2.CAP_DSHOW
        )

        if not self.camera.isOpened():
            raise RuntimeError("Could not open the Logitech camera.")

    def capture(self):
        print("Press R to run | Q to quit")

        while True:
            success, frame = self.camera.read()

            if not success:
                print("Could not read camera frame.")
                return None

            cv2.imshow("ScratchPad Camera", frame)

            key = cv2.waitKey(1) & 0xFF

            if key == ord("r"):
                cv2.imwrite("paper.jpg", frame)

                print("✓ Paper captured!")
                return "paper.jpg"

            elif key == ord("q"):
                return None

    def close(self):
        self.camera.release()
        cv2.destroyAllWindows()