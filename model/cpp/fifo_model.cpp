// model/cpp/fifo_model.cpp
#include <deque>
#include <stdio.h>

// We use std::deque as the standard data structure for a queue
std::deque<int> my_fifo;

// extern "C" is required to prevent C++ name mangling, 
// allowing SystemVerilog DPI to link correctly.
extern "C" {

    // Function to write to the FIFO (called by SV Write Monitor)
    void cpp_write(int data) {
        my_fifo.push_back(data);
        // printf("[CPP-MODEL] Wrote data: %0x\n", data); // Uncomment for debug
    }

    // Function to read from the FIFO (called by SV Scoreboard)
    // Returns -1 if the FIFO is empty (indicates a test failure)
    int cpp_read() {
        if (my_fifo.empty()) {
            printf("[CPP-MODEL] Error: Attempting to read from empty FIFO!\n");
            return -1;
        }
        
        int data = my_fifo.front();
        my_fifo.pop_front();
        // printf("[CPP-MODEL] Read data: %0x\n", data);
        return data;
    }

    // Helper function to check current size
    int cpp_get_size() {
        return my_fifo.size();
    }
    
    // Clear the FIFO during reset phase
    void cpp_clear() {
        my_fifo.clear();
    }
}