#include <deque>
#include <stdio.h>

// std::deque is pure C++, so it's OUTSIDE the "C" external block. This allows us to use C++ features internally while still exposing a C-compatible interface.
std::deque<int> my_fifo;

// The external "C" tells the compiler: don't change the names of these functions, so they can be called from C code (or other languages that can call C functions).
extern "C" {

    void cpp_write(int data) {
        my_fifo.push_back(data);
    }

    int cpp_read() {
        if (my_fifo.empty()) {
            printf("[CPP-MODEL] Error: Empty read\n");
            return -1;
        }
        int data = my_fifo.front();
        my_fifo.pop_front();
        return data;
    }

    int cpp_get_size() {
        return my_fifo.size();
    }
    
    void cpp_clear() {
        my_fifo.clear();
    }
}