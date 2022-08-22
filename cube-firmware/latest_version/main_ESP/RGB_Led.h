#pragma once
#include "Arduino.h"
#include "config.h"

enum class Color {
  Red,
  Green,
  Blue
};

struct LED {
    unsigned char red : 4;
    unsigned char green : 4;
    unsigned char blue : 4;
};

struct RGB_Layer {
  byte red[CUBE_DIMENSION];
  byte green[CUBE_DIMENSION];
  byte blue[CUBE_DIMENSION];

  IRAM_ATTR void clear(){
    memset(&red[0], 0, CUBE_DIMENSION);
    memset(&green[0], 0, CUBE_DIMENSION);
    memset(&blue[0], 0, CUBE_DIMENSION);
  }

  RGB_Layer(){
    clear();
  }
};

struct RGBColor {
  byte bam[4][64];
};

struct RGBFrame {
  RGBColor redLeds;
  RGBColor greenLeds;
  RGBColor blueLeds;

  void setRed() {
    for(int i = 0; i < 4; i++) {
      memset(&redLeds.bam[i][0], 0xFF, 64);
      memset(&greenLeds.bam[i][0], 0x0, 64);
      memset(&blueLeds.bam[i][0], 0x0, 64);
    }

  }

  void setGreen() {
    for(int i = 0; i < 4; i++) {
      memset(&redLeds.bam[i][0], 0x0, 64);
      memset(&greenLeds.bam[i][0], 0xFF, 64);
      memset(&blueLeds.bam[i][0], 0x0, 64);
    }
  }

  void setBlue() {
    for(int i = 0; i < 4; i++) {
      memset(&redLeds.bam[i][0], 0x0, 64);
      memset(&greenLeds.bam[i][0], 0x0, 64);
      memset(&blueLeds.bam[i][0], 0xFF, 64);
    } 
  }

  void setWhite() {
    for(int i = 0; i < 4; i++) {
      memset(&redLeds.bam[i][0], 0x1, 64);
      memset(&greenLeds.bam[i][0], 0x1, 64);
      memset(&blueLeds.bam[i][0], 0x1, 64);
    } 
  }

  void clear() {
    for(int i = 0; i < 4; i++) {
      memset(&redLeds.bam[i][0], 0x0, 64);
      memset(&greenLeds.bam[i][0], 0x0, 64);
      memset(&blueLeds.bam[i][0], 0x0, 64);
    }
  }

  LED rgb(byte minimum, byte maximum, byte value) {
    float ratio = 2 * float((value-minimum)) / float((maximum - minimum));
    LED led = LED();
    led.blue = int(max(float(0), 255*(1 - ratio)));
    led.red = int(max(float(0), 255*(ratio - 1)));
    led.green = 255 - led.blue - led.red;
    return led;
  }

  void drawColumn(byte x, byte y, byte level) {

    LED led = LED();//rgb(0 + 20, 63, (x * 8) + y);
    
    if (x == 0) {
      led.red = 1;
      led.green = 1;
      led.blue = 8;
    }
    else if (x == 1) {
      led.red = 5;
      led.green = 1;
      led.blue = 10;
    }
    else if (x == 2) {
      led.red = 8;
      led.green = 1;
      led.blue = 17;
    }
    else if (x == 3) {
      led.red = 11;
      led.green = 3;
      led.blue = 9;
    }
    else if (x == 4) {
      led.red = 13;
      led.green = 5;
      led.blue = 7;
    }
    else if (x == 5) {
      led.red = 14;
      led.green = 7;
      led.blue = 6;
    }
    else if (x == 6) {
      led.red = 15;
      led.green = 9;
      led.blue = 4;
    }
    else if (x == 7) {
      led.red = 14;
      led.green = 15;
      led.blue = 3;
    }

    // 0 - 12/7/134 - 1/1/8
    // 1 - 76/2/161 - 5/1/10
    // 2 - 126/3/167 - 8/1/17
    // 3 - 170/36/148 - 11/3/9
    // 4 - 204/72/118 - 13/5/7

    // 5 - 230/109/90 - 14/7/6
    // 6 - 248/152/62 - 15/9/4
    // 7 - 239/248/33 - 14/15/3

    for (int z = 0; z < level; z++) {
      turnOnLed(x, y, z, led.red, led.green, led.blue);
    }

    if (level == 7) {
      turnOnLed(x, y, 7, led.red, led.green, led.blue);
    }
  }

  void turnOnLed(byte x, byte y, byte z, byte r, byte g, byte b) {
        if (x < 0)
            x = 0;
        if (x > 7)
            x = 7;
        if (y < 0)
            y = 0;
        if (y > 7)
            y = 7;
        if (z < 0)
            z = 0;
        if (z > 7)
            z = 7;
        if (r < 0)
            r = 0;
        if (r > 15)
            r = 15;
        if (g < 0)
            g = 0;
        if (g > 15)
            g = 15;
        if (b < 0)
            b = 0;
        if (b > 15)
            b = 15;

        unsigned char index = ((64 * z) + (y * 8) + x) / 8;
        unsigned char position = ((64 * z) + (y * 8) + x) % 8;

        // red
        if ((r & 0b0001) > 0)
            redLeds.bam[0][index] = redLeds.bam[0][index] | (1 << position);
        else
            redLeds.bam[0][index] = redLeds.bam[0][index] & ~(1 << position);

        if (((r & 0b0010) >> 1) > 0)
            redLeds.bam[1][index] = redLeds.bam[1][index] | (1 << position);
        else
            redLeds.bam[1][index] = redLeds.bam[1][index] & ~(1 << position);

        if (((r & 0b0100) >> 2) > 0)
            redLeds.bam[2][index] = redLeds.bam[2][index] | (1 << position);
        else
            redLeds.bam[2][index] = redLeds.bam[2][index] & ~(1 << position);

        if (((r & 0b1000) >> 3) > 0)
            redLeds.bam[3][index] = redLeds.bam[3][index] | (1 << position);
        else
            redLeds.bam[3][index] = redLeds.bam[3][index] & ~(1 << position);

        // green
        if ((g & 0b0001) > 0)
            greenLeds.bam[0][index] = greenLeds.bam[0][index] | (1 << position);
        else
            greenLeds.bam[0][index] = greenLeds.bam[0][index]& ~(1 << position);

        if (((g & 0b0010) >> 1) > 0)
            greenLeds.bam[1][index] = greenLeds.bam[1][index] | (1 << position);
        else
            greenLeds.bam[1][index] = greenLeds.bam[1][index] & ~(1 << position);

        if (((g & 0b0100) >> 2) > 0)
            greenLeds.bam[2][index] = greenLeds.bam[2][index] | (1 << position);
        else
            greenLeds.bam[2][index] = greenLeds.bam[2][index] & ~(1 << position);

        if (((g & 0b1000) >> 3) > 0)
            greenLeds.bam[3][index] = greenLeds.bam[3][index] | (1 << position);
        else
            greenLeds.bam[3][index] = greenLeds.bam[3][index] & ~(1 << position);

        // blue
        if ((b & 0b0001) > 0)
            blueLeds.bam[0][index] = blueLeds.bam[0][index] | (1 << position);
        else
            blueLeds.bam[0][index] = blueLeds.bam[0][index] & ~(1 << position);

        if (((b & 0b0010) >> 1) > 0)
            blueLeds.bam[1][index] = blueLeds.bam[1][index] | (1 << position);
        else
            blueLeds.bam[1][index] = blueLeds.bam[1][index] & ~(1 << position);

        if (((b & 0b0100) >> 2) > 0)
            blueLeds.bam[2][index] = blueLeds.bam[2][index] | (1 << position);
        else
            blueLeds.bam[2][index] = blueLeds.bam[2][index] & ~(1 << position);

        if (((b & 0b1000) >> 3) > 0)
            blueLeds.bam[3][index] = blueLeds.bam[3][index] | (1 << position);
        else
            blueLeds.bam[3][index] = blueLeds.bam[3][index] & ~(1 << position);
  }
};
