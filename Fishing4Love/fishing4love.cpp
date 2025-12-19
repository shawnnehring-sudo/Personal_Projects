#include <opencv2/opencv.hpp>
#include <iostream>
#include <filesystem>

using namespace cv;
using namespace std;

int main() {
    // 1. Initialize camera ONCE outside the loop
    VideoCapture cap(0); 
    
    // Check if the camera actually opened
    if (!cap.isOpened()) {
        cout << "ERROR: Could not open camera! Trying index 1..." << endl;
        cap.open(1); // Try the next index if 0 fails
        if (!cap.isOpened()) {
            cout << "CRITICAL ERROR: No camera found." << endl;
            return -1;
        }
    }

    // Give the camera a moment to warm up/auto-focus
    Mat warmup;
    for(int i=0; i<10; i++) cap >> warmup;

    for (int i = 0; i < 10; i++) {
        // ... [Your Filename and Big Image Popup Logic] ...

        Mat frame, gray, prevGray, diff, thresh;
        auto startTime = chrono::steady_clock::now();

        cout << "Starting tracking for Beta " << (i+1) << "..." << endl;

        while (chrono::steady_clock::now() - startTime < chrono::seconds(5)) {
            cap >> frame; // Grab current frame
            if (frame.empty()) {
                cout << "Lost camera feed!" << endl;
                break;
            }

            // ... [Your Motion Tracking Logic] ...

            imshow("Fish Tracker", frame);
            if (waitKey(30) == 27) return 0; // Esc to quit entirely
            prevGray = gray.clone();
        }

        // ... [Your Sorting Logic] ...
    }

    cap.release(); // Explicitly close the camera when done
    return 0;
}