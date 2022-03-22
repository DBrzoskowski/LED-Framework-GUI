#include <avr/io.h>
#include <avr/interrupt.h>
#include <SPI.h> // SPI Library used to clock data out to the shift registers

constexpr int latchPinLeds = 2; // Pin connected to ST_CP of 74HC595
constexpr int clockPinLeds = 13; // Pin connected to SH_CP of 74HC595
constexpr int dataPinLeds = 11; // Pin connected to DS of 74HC595

#include "RGB_Led.h"
#include "CubeManager.h"


// #define DEBUG


CubeManager gCubeManager = CubeManager(latchPinLeds, clockPinLeds, dataPinLeds);

void setup() {
  gCubeManager.initialize();

  Serial.begin(115200);
}

void loop() {
  RGB4x4x4Frame frame = {}; 

  gCubeManager.loadFrame(&frame);
  frame.goThroughRgbPalette();
  delay(125);
  
  for(int i = 0; i < 32; i++) {
    frame.fillAllLedsWithRandomColors();
    gCubeManager.loadFrame(&frame);
    delay(50);
  }

  // red
  for(int i = 0; i < 16; i++) {
    frame.fillAllLedsWithRedColor(i);
    gCubeManager.loadFrame(&frame);
    delay(50);
  }
  for(int i = 15; i > 0; i--) {
    frame.fillAllLedsWithRedColor(i);
    gCubeManager.loadFrame(&frame);
    delay(50);
  }
  
  // green
  for(int i = 0; i < 16; i++) {
    frame.fillAllLedsWithGreenColor(i);
    gCubeManager.loadFrame(&frame);
    delay(50);
  }
  for(int i = 15; i > 0; i--) {
    frame.fillAllLedsWithGreenColor(i);
    gCubeManager.loadFrame(&frame);
    delay(50);
  }
  
  // blue
  for(int i = 0; i < 16; i++) {
    frame.fillAllLedsWithBlueColor(i);
    gCubeManager.loadFrame(&frame);
    delay(50);
  }
  for(int i = 15; i > 0; i--) {
    frame.fillAllLedsWithBlueColor(i);
    gCubeManager.loadFrame(&frame);
    delay(50);
  }
  
}

ISR(TIMER1_COMPA_vect) {
  gCubeManager.processISR();
}
