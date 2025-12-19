#include <opencv2/opencv.hpp>
#include <iostream>
#include <filesystem>

using namespace cv;
using namespace std;
namespace fs = std::filesystem;

int main() {
    string imagePath = "fish1.jpg";
    fs::create_directories("green");
    fs::create_directories("red");

    // 1. Pop up the photo
    Mat img = imread(imagePath);
    if (img.empty()) {
        cout << "Could not find the image!" << endl;
        return -1;
    }
    namedWindow("Reviewing Image", WINDOW_AUTOSIZE);
    imshow("Reviewing Image", img);
    moveWindow("Reviewing Image", 50, 50); // Position on left
    waitKey(1000);

    VideoCapture cap(0);
    Mat frame, gray, prevGray, diff, thresh;
    Point2f initialPos(-1, -1), currentPos(-1, -1);
    bool fishMoved = false;

    cout << "Looking for the fish..." << endl;

    auto startTime = chrono::steady_clock::now();
    while (chrono::steady_clock::now() - startTime < chrono::seconds(5)) {
        cap >> frame;
        if (frame.empty()) break;

        cvtColor(frame, gray, COLOR_BGR2GRAY);
        GaussianBlur(gray, gray, Size(21, 21), 0); // Smooth out water ripples

        if (prevGray.empty()) {
            prevGray = gray.clone();
            continue;
        }

        // Detect the movement "blobs"
        absdiff(prevGray, gray, diff);
        threshold(diff, thresh, 25, 255, THRESH_BINARY);
        dilate(thresh, thresh, Mat(), Point(-1, -1), 2); // Make the fish "thicker"

        vector<vector<Point>> contours;
        findContours(thresh, contours, RETR_EXTERNAL, CHAIN_APPROX_SIMPLE);

        for (const auto& contour : contours) {
            if (contourArea(contour) > 1000) { // Only track things "fish-sized"
                // Get the center of the fish
                Moments m = moments(contour);
                currentPos = Point2f(m.m10 / m.m00, m.m01 / m.m00);

                // Set the starting position if it's the first time seeing the fish
                if (initialPos.x == -1) {
                    initialPos = currentPos;
                }

                // Calculate distance from start
                float dist = norm(initialPos - currentPos);
                
                // Draw the tracking visuals
                rectangle(frame, boundingRect(contour), Scalar(0, 255, 0), 2);
                line(frame, initialPos, currentPos, Scalar(0, 0, 255), 2);
                
                if (dist > 50) { // If fish moved 50 pixels from start
                    fishMoved = true;
                }
            }
        }

        imshow("Fish Tracker", frame);
        if (fishMoved || waitKey(30) == 27) break;
        prevGray = gray.clone();
    }

    // 3. Sorting Result
    string destination = (fishMoved ? "green/" : "red/") + imagePath;
    try {
        if (fs::exists(imagePath)) {
            fs::rename(imagePath, destination);
            cout << (fishMoved ? "FISH MOVED: Saved to Green" : "STAYED STILL: Saved to Red") << endl;
        }
    } catch (...) {}

    destroyAllWindows();
    return 0;
}