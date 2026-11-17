
import cv2
import numpy as np


def preprocess_image(image: np.ndarray) -> np.ndarray:
    """
    Preprocess a document image for improved OCR.

    Operations:
    1. Grayscale conversion
    2. Denoising
    3. Deskewing
    4. Adaptive thresholding
    """

    # 1. Convert to grayscale
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()

    # 2. Remove noise while preserving text edges
    denoised = cv2.fastNlMeansDenoising(
        gray,
        None,
        h=10,
        templateWindowSize=7,
        searchWindowSize=21,
    )

    # 3. Detect the skew angle using foreground pixels
    binary = cv2.threshold(
        denoised,
        0,
        255,
        cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU,
    )[1]

    coordinates = np.column_stack(np.where(binary > 0))

    if len(coordinates) > 0:
        angle = cv2.minAreaRect(coordinates)[-1]

        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle

        # Avoid unnecessary rotation for nearly straight documents
        if abs(angle) > 0.5:
            height, width = denoised.shape
            center = (width // 2, height // 2)

            rotation_matrix = cv2.getRotationMatrix2D(
                center,
                angle,
                1.0,
            )

            denoised = cv2.warpAffine(
                denoised,
                rotation_matrix,
                (width, height),
                flags=cv2.INTER_CUBIC,
                borderMode=cv2.BORDER_REPLICATE,
            )

    # 4. Adaptive thresholding
    processed = cv2.adaptiveThreshold(
        denoised,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        11,
    )

    return processed
