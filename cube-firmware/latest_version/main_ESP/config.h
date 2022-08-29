#ifndef GUARD
#define GUARD
constexpr int CUBE_DIMENSION = 8;

constexpr int latchPinLeds = 15; // Pin connected to ST_CP of 74HC595
constexpr int dataPinLeds = 13; // Pin connected to DS of 74HC595
constexpr int clockPinLeds = 14; // Pin connected to SH_CP of 74HC595


#define INTERVAL_IN_US 6400 * 1.5 //24000// TIM_DIV1: 12,5ns -> 1 tick // 120us
//#define TIMER_FREQ_HZ        (1000000.0f / INTERVAL_IN_US)
#endif
