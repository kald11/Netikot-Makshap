import cv2


def watch_rtsp_stream(rtsp_url: str):
    """Stream and display video from an RTSP URL using OpenCV."""
    cap = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)  # Force FFmpeg

    if not cap.isOpened():
        print("Failed to open the RTSP stream. Check the URL, authentication, and network.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Stream ended or failed to retrieve frame.")
            break

        cv2.imshow("Hikvision RTSP Playback", frame)

        # Press 'q' to exit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


# Example RTSP URL (Replace with correct credentials if needed)
rtsp_url = "rtsp://username:YytdBr!583@192.168.1.64/Streaming/tracks/101?starttime=20250309T000000Z&endtime=20250309T002737Z"

# Start Playback
watch_rtsp_stream(rtsp_url)
