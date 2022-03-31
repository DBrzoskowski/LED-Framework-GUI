#pragma once
#include "Arduino.h"


enum class Color {
  Red,
  Green,
  Blue
};

struct LED {
    unsigned short red = 0;
    unsigned short green = 0;
    unsigned short blue = 0;
};

struct RGB4x4x4_Layer {
  unsigned int red;   // 16 bit
  unsigned int green; // 16 bit
  unsigned int blue;  // 16 bit
};

struct RGB4x4x4Frame {
    LED allLeds[4][4][4] = {};

    void fillAllLedsWithRandomColors();
    
    void fillAllLedsWithSpecificColor(int r, int g, int b);

    void goThroughRgbPalette();

    void fillAllLedsWithRedColor(short brightness);

    void fillAllLedsWithGreenColor(short brightness);

    void fillAllLedsWithBlueColor(short brightness);

    void testPattern();
};

