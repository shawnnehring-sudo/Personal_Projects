#include <iostream>
#include <cstdlib> // Required for std::system
#include <thread>
#include <chrono>

int main() {

    // 1. Run the first Python script
    // Note: Use "python" instead of "python3" if you are on Windows
    std::thread flaskThread(int result1 = std::system("python RecordData.py"));
    flaskThread.detach(); // Detach to let it run independently
    if (result1 != 0) {
        std::cerr << "Error: script1.py failed to execute.\n";
        return 1; 
    }

    // 2. Run the second Python script
    if (training_enabled){
        int result2 = std::system("python MoodModel.py");
        if (result2 != 0) {
            std::cerr << "Error: script2.py failed to execute.\n";
            return 1;
        }
    }
    return 0;
}