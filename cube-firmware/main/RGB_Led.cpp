#include "RGB_Led.h"


void RGB4x4x4Frame::fillAllLedsWithRandomColors() {
    for (int z = 0; z < 4; z++) {
        for (int x = 0; x < 4; x++) {
            for (int y = 0; y < 4; y++) {
                int temp_x = random(0, 4);
                int temp_y = random(0, 4);
                allLeds[temp_x][temp_y][z].red = random(0, 15);
                allLeds[temp_x][temp_y][z].green = random(0, 15);
                allLeds[temp_x][temp_y][z].blue = random(0, 15);
            }
        }
    }
}

void RGB4x4x4Frame::fillAllLedsWithSpecificColor(int r, int g, int b) {
    for (int z = 0; z < 4; z++) {
        for (int x = 0; x < 4; x++) {
            for (int y = 0; y < 4; y++) {
                int temp_x = random(0, 4);
                int temp_y = random(0, 4);
                allLeds[temp_x][temp_y][z].red = r;
                allLeds[temp_x][temp_y][z].green = g;
                allLeds[temp_x][temp_y][z].blue = b;
            }
        }
    }
}

void RGB4x4x4Frame::goThroughRgbPalette() {
    // 15:0:0 -> 15:15:0 -> 0:15:0 -> 0:15:15 -> 0:0:15 -> 15:0:15 -> 15:0:0

    int r = 15, g = 0, b = 0;

    for (int stage = 0; stage < 6; stage++) {
        for (int i = 0; i < 15; i++) {
            switch (stage) {
            case 0: {
                // 15:0:0 -> 15:15:0
                g++;
                break;
            }
            case 1: {
                // 15:15:0 -> 0:15:0
                r--;
                break;
            }
            case 2: {
                b++;
                // 0:15:0 -> 0:15:15
                break;
            }
            case 3: {
                // 0:15:15 -> 0:0:15
                g--;
                break;
            }
            case 4: {
                // 0:0:15 -> 15:0:15
                r++;
                break;
            }
            case 5: {
                b--;
                // 15:0:15 -> 15:0:0
                break;
            }
            }
            fillAllLedsWithSpecificColor(r, g, b);
            delay(100);
        }
    }

}

void RGB4x4x4Frame::fillAllLedsWithRedColor(short brightness) {
    for (int z = 0; z < 4; z++) {
        for (int x = 0; x < 4; x++) {
            for (int y = 0; y < 4; y++) {
                allLeds[x][y][z].red = brightness;
            }
        }
    }
}

void RGB4x4x4Frame::fillAllLedsWithGreenColor(short brightness) {
    for (int z = 0; z < 4; z++) {
        for (int x = 0; x < 4; x++) {
            for (int y = 0; y < 4; y++) {
                allLeds[x][y][z].green = brightness;
            }
        }
    }
}

void RGB4x4x4Frame::fillAllLedsWithBlueColor(short brightness) {
    for (int z = 0; z < 4; z++) {
        for (int x = 0; x < 4; x++) {
            for (int y = 0; y < 4; y++) {
                allLeds[x][y][z].blue = brightness;
            }
        }
    }
}

void RGB4x4x4Frame::testPattern() {
    for (int z = 0; z < 4; z++) {
        for (int x = 0; x < 4; x++) {
            for (int y = 0; y < 4; y++) {

                allLeds[x][y][z].green = 15;
                
                delay(100);
            }
        }
    }
}

