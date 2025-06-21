import os
import re
import pytesseract
import cv2


def extract_title(text: str) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    noise_patterns = [
        r"mosh hamedani",
        r"codewithmosh\.com",
        r"^eo eoe$",
        r"^\d+.*",
        r"^age.*",
        r"^1 i.*",
        r"Ged",
        r"@moshhamedani",
        r"brine .oo\) Crops",
    ]

    meaningful_lines = [
        line
        for line in lines
        if not any(re.search(pat, line, re.IGNORECASE) for pat in noise_patterns)
    ]

    # Take the first remaining meaningful line
    result = meaningful_lines[0] if meaningful_lines else ""

    return result


def main():
    for root, _directories, files in os.walk("./codewithmoshVideos"):
        for f in files:
            if f.endswith(".mp4"):
                filepath = os.path.join(root, f)
                video_title = capture_title(filepath, starting_frame=5)
                print(f"{video_title} - {filepath}")
                if video_title:
                    os.rename(filepath, os.path.join(root, f"{video_title}.mp4"))


def capture_title(video_path: str, show_frames: bool = False, starting_frame: int = 0):
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.set(cv2.CAP_PROP_POS_FRAMES, starting_frame)

    video_title = None
    frame_ct = 0

    while not video_title and frame_ct < 20:
        if frame_ct == 10:
            # if we don't have a title after the first 10 frames then jump to the middle of the video
            cap.set(cv2.CAP_PROP_POS_FRAMES, total_frames // 2)
        ret, frame = cap.read()

        if not ret:
            break

        if show_frames:
            cv2.imshow("Camera", frame)
            if cv2.waitKey(0) == ord("q"):
                break

        frame_ct += 1
        inverted_img = cv2.bitwise_not(frame)
        gray_inverted_img = cv2.cvtColor(inverted_img, cv2.COLOR_BGR2GRAY)
        thresh = cv2.threshold(
            gray_inverted_img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
        )[1]
        text: str = pytesseract.image_to_string(thresh)
        if text:
            video_title = extract_title(text)

    cap.release()
    return video_title


if __name__ == "__main__":
    main()
