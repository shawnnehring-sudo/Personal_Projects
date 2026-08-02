#include <iostream>
#include <deque>
#include <numeric>
#include <cmath>
#include <chrono>
#include <random>
#include <vector>

// Structure to store a single heartbeat reading
struct HeartReading {
    double timestamp; // Seconds
    double bpm;       // Heart rate in BPM
    double rr_ms;     // Interval between beats in milliseconds
};

// Feature vector ready for your DNN
struct HRVFeatures {
    double mean_hr   = 0.0;
    double std_hr    = 0.0;
    double mean_rr   = 0.0;
    double sdnn      = 0.0; // Standard deviation of RR intervals
    double rmssd     = 0.0; // Root Mean Square of Successive Differences

    // --- New features for mood/stress detection ---
    double pnn50        = 0.0; // % of successive RR diffs > 50ms (parasympathetic activity)
    double hr_slope      = 0.0; // BPM change per second across the window (trend direction)
    double instant_delta_bpm = 0.0; // BPM change from the previous single reading (sudden jump)
};

// --- MOCK SENSOR ---
// Swap this class out for real ADC reads from the DEVMO Pulse Sensor on your
// Arduino/Pi. Everything downstream (buffer, feature extraction) stays the same
// as long as you keep filling HeartReading structs the same way.
class MockHeartSensor {
private:
    std::default_random_engine generator;
    std::normal_distribution<double> noise; // reused instead of rebuilt every call
    double base_bpm;

public:
    MockHeartSensor(double initial_bpm = 72.0)
        : noise(0.0, 3.0), base_bpm(initial_bpm) {}

    HeartReading read() {
        double current_bpm = base_bpm + noise(generator);

        if (current_bpm < 40.0) current_bpm = 40.0;
        if (current_bpm > 180.0) current_bpm = 180.0;

        double rr_interval = (60.0 / current_bpm) * 1000.0;

        auto now = std::chrono::steady_clock::now().time_since_epoch();
        double timestamp = std::chrono::duration<double>(now).count();

        return {timestamp, current_bpm, rr_interval};
    }

    void setBaseBPM(double bpm) { base_bpm = bpm; }
};

// --- SLIDING WINDOW BUFFER ---
class HeartRateBuffer {
private:
    double window_duration_sec;
    std::deque<HeartReading> buffer;
    double last_bpm = 0.0;      // tracks previous single reading for instant_delta_bpm
    bool has_last_bpm = false;

    void cleanOldData(double current_time) {
        while (!buffer.empty() && (current_time - buffer.front().timestamp) > window_duration_sec) {
            buffer.pop_front();
        }
    }

    // Least-squares slope of bpm vs time across the current buffer.
    // Positive => heart rate trending up over the window; negative => trending down.
    double computeSlope() const {
        size_t n = buffer.size();
        double t0 = buffer.front().timestamp; // shift time to start at 0 for numerical stability
        double sum_x = 0, sum_y = 0, sum_xy = 0, sum_xx = 0;

        for (const auto& r : buffer) {
            double x = r.timestamp - t0;
            double y = r.bpm;
            sum_x  += x;
            sum_y  += y;
            sum_xy += x * y;
            sum_xx += x * x;
        }

        double denom = (n * sum_xx - sum_x * sum_x);
        if (std::abs(denom) < 1e-9) return 0.0; // avoid divide-by-zero if all timestamps equal
        return (n * sum_xy - sum_x * sum_y) / denom;
    }

public:
    HeartRateBuffer(double window_sec = 30.0) : window_duration_sec(window_sec) {}

    void addReading(const HeartReading& reading) {
        buffer.push_back(reading);
        cleanOldData(reading.timestamp);
    }

    bool extractFeatures(HRVFeatures& out_features) {
        if (buffer.size() < 10) return false;

        size_t n = buffer.size();
        double hr_sum = 0.0, rr_sum = 0.0;

        for (const auto& r : buffer) {
            hr_sum += r.bpm;
            rr_sum += r.rr_ms;
        }

        out_features.mean_hr = hr_sum / n;
        out_features.mean_rr = rr_sum / n;

        double hr_variance_sum = 0.0;
        double rr_variance_sum = 0.0;
        for (const auto& r : buffer) {
            hr_variance_sum += std::pow(r.bpm - out_features.mean_hr, 2);
            rr_variance_sum += std::pow(r.rr_ms - out_features.mean_rr, 2);
        }
        out_features.std_hr = std::sqrt(hr_variance_sum / n);
        out_features.sdnn   = std::sqrt(rr_variance_sum / n);

        // RMSSD + pNN50 both come from successive RR differences, so compute together
        double diff_sq_sum = 0.0;
        int nn50_count = 0;
        for (size_t i = 1; i < n; ++i) {
            double diff = buffer[i].rr_ms - buffer[i - 1].rr_ms;
            diff_sq_sum += diff * diff;
            if (std::abs(diff) > 50.0) nn50_count++;
        }
        out_features.rmssd = std::sqrt(diff_sq_sum / (n - 1));
        out_features.pnn50 = (100.0 * nn50_count) / static_cast<double>(n - 1);

        // Trend across the whole window: is HR climbing or dropping?
        out_features.hr_slope = computeSlope();

        // Sudden jump from the single most recent reading
        if (has_last_bpm) {
            out_features.instant_delta_bpm = buffer.back().bpm - last_bpm;
        } else {
            out_features.instant_delta_bpm = 0.0;
        }
        last_bpm = buffer.back().bpm;
        has_last_bpm = true;

        return true;
    }
};

int main() {
    MockHeartSensor sensor(75.0);
    HeartRateBuffer buffer(30.0);

    std::cout << "Simulating live heartbeat sensor input...\n\n";

    for (int i = 1; i <= 35; ++i) {
        HeartReading reading = sensor.read();
        buffer.addReading(reading);

        std::cout << "Sample " << i << " | BPM: " << reading.bpm
                  << " | RR: " << reading.rr_ms << " ms\n";

        HRVFeatures features;
        if (buffer.extractFeatures(features)) {
            std::cout << "  --> Mean HR: " << features.mean_hr
                      << " | SDNN: " << features.sdnn
                      << " | RMSSD: " << features.rmssd
                      << " | pNN50: " << features.pnn50 << "%"
                      << " | HR slope: " << features.hr_slope << " bpm/s"
                      << " | Instant delta: " << features.instant_delta_bpm << " bpm\n";
        } else {
            std::cout << "  --> [Buffering... need more samples]\n";
        }
    }

    return 0;
}