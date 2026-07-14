import os
import cv2
import numpy as np

FACES_FOLDER = "faces"
MODEL_FOLDER = "model"

CASCADE_FILE = os.path.join(
    cv2.data.haarcascades,
    "haarcascade_frontalface_default.xml"
)

MODEL_FILE = os.path.join(
    MODEL_FOLDER,
    "trainer.yml"
)

LABELS_FILE = os.path.join(
    MODEL_FOLDER,
    "labels.npy"
)

os.makedirs(FACES_FOLDER, exist_ok=True)
os.makedirs(MODEL_FOLDER, exist_ok=True)


class FaceAuth:

    def __init__(self):

        self.face_detector = cv2.CascadeClassifier(
            CASCADE_FILE
        )

        self.recognizer = cv2.face.LBPHFaceRecognizer_create()

    ##########################################################

    def user_folder(self, username):

        folder = os.path.join(
            FACES_FOLDER,
            username
        )

        os.makedirs(
            folder,
            exist_ok=True
        )

        return folder

    ##########################################################

    def register_face(self, username):

        folder = self.user_folder(username)

        camera = cv2.VideoCapture(0)

        if not camera.isOpened():

            return (
                False,
                "Unable to access camera."
            )

        count = 0

        while True:

            success, frame = camera.read()

            if not success:
                continue

            gray = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2GRAY
            )

            faces = self.face_detector.detectMultiScale(
                gray,
                scaleFactor=1.3,
                minNeighbors=5,
                minSize=(120, 120)
            )

            for (x, y, w, h) in faces:

                cv2.rectangle(
                    frame,
                    (x, y),
                    (x + w, y + h),
                    (0, 255, 0),
                    2
                )

                face = gray[
                    y:y + h,
                    x:x + w
                ]

                face = cv2.resize(
                    face,
                    (200, 200)
                )

                count += 1

                filename = os.path.join(
                    folder,
                    f"{count}.jpg"
                )

                cv2.imwrite(
                    filename,
                    face
                )

                cv2.putText(
                    frame,
                    f"Captured : {count}/40",
                    (20, 35),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 255, 0),
                    2
                )

                break

            cv2.imshow(
                "Register Face",
                frame
            )

            key = cv2.waitKey(1)

            if key == 27:

                camera.release()
                cv2.destroyAllWindows()

                return (
                    False,
                    "Registration cancelled."
                )

            if count >= 40:
                break

        camera.release()
        cv2.destroyAllWindows()

        self.train_model()

        return (
            True,
            "Face registered successfully."
        )

    ##########################################################

    def train_model(self):

        faces = []
        labels = []

        label_map = {}
        current_label = 0

        for username in sorted(os.listdir(FACES_FOLDER)):

            user_path = os.path.join(
                FACES_FOLDER,
                username
            )

            if not os.path.isdir(user_path):
                continue

            label_map[current_label] = username

            for image_name in os.listdir(user_path):

                image_path = os.path.join(
                    user_path,
                    image_name
                )

                image = cv2.imread(
                    image_path,
                    cv2.IMREAD_GRAYSCALE
                )

                if image is None:
                    continue

                faces.append(image)
                labels.append(current_label)

            current_label += 1

        if len(faces) == 0:
            return

        self.recognizer.train(
            faces,
            np.array(labels)
        )

        self.recognizer.save(
            MODEL_FILE
        )

        np.save(
            LABELS_FILE,
            label_map,
            allow_pickle=True
        )

    ##########################################################

    def verify_face(self, username):

        if not os.path.exists(MODEL_FILE):

            return (
                False,
                "No trained model found."
            )

        if not os.path.exists(LABELS_FILE):

            return (
                False,
                "Face database not found."
            )

        self.recognizer.read(
            MODEL_FILE
        )

        label_map = np.load(
            LABELS_FILE,
            allow_pickle=True
        ).item()

        camera = cv2.VideoCapture(0)

        if not camera.isOpened():

            return (
                False,
                "Unable to access camera."
            )

        while True:

            success, frame = camera.read()

            if not success:
                continue

            gray = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2GRAY
            )

            faces = self.face_detector.detectMultiScale(
                gray,
                scaleFactor=1.3,
                minNeighbors=5,
                minSize=(120, 120)
            )

            for (x, y, w, h) in faces:

                cv2.rectangle(
                    frame,
                    (x, y),
                    (x + w, y + h),
                    (0, 255, 0),
                    2
                )

                face = gray[
                    y:y + h,
                    x:x + w
                ]

                face = cv2.resize(
                    face,
                    (200, 200)
                )

                predicted_label, confidence = self.recognizer.predict(
                    face
                )
                predicted_user = label_map.get(
                    predicted_label
                )

                cv2.putText(
                    frame,
                    f"{predicted_user} ({confidence:.2f})",
                    (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 0),
                    2
                )

                cv2.imshow(
                    "Face Login",
                    frame
                )

                key = cv2.waitKey(0)

                camera.release()
                cv2.destroyAllWindows()

                if (
                    predicted_user == username
                    and confidence < 70
                ):

                    return (
                        True,
                        "Face verified successfully."
                    )

                return (
                    False,
                    "Face verification failed."
                )

            cv2.imshow(
                "Face Login",
                frame
            )

            key = cv2.waitKey(1)

            if key == 27:

                camera.release()
                cv2.destroyAllWindows()

                return (
                    False,
                    "Verification cancelled."
                )

        camera.release()
        cv2.destroyAllWindows()
