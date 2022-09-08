// #define DEBUG

#ifdef DEBUG
#define LOG_PARAMS(msg, args...) Serial.printf((msg "\n"), args);
#define LOG(msg) Serial.printf((msg "\n"));
#else
#define LOG_PARAMS(msg, args...) ;
#define LOG(msg) ;
#endif

#include <ESP8266WiFi.h>
#include <WiFiUdp.h>
#include <avr/pgmspace.h>
#include "RGB_Led.h"
#include <Ticker.h>
RGBFrame frame_new = RGBFrame();
Ticker wifiTicker;
#include "CubeManager.h"



CubeManager gCubeManager = CubeManager(latchPinLeds, clockPinLeds, dataPinLeds);



#ifdef DEBUG
volatile unsigned int avg = 0, minimum = 9999999, maximum = 0;
#endif

IRAM_ATTR void ISR_Callback(void)
{ 
#ifdef DEBUG
  auto t_start = micros();
#endif
  gCubeManager.processISR();
  timer1_write(INTERVAL_IN_US);
#ifdef DEBUG
  auto t_end = micros();

  auto diff = t_end - t_start;
  avg = (avg + diff) / 2;
  if (diff > maximum){
    maximum = diff;
  }
  if (diff < minimum){
    minimum = diff;  
  }
#endif
}

void setup() {  
  gCubeManager.initialize();
  gCubeManager.loadFrame(&frame_new);
  
  Serial.begin(115200);
  
  setupWifi();
  //wifiTicker.attach(0.03, checkUdpPackets); // Initialize Ticker every 0.5s
  wifiTicker.once_ms(30, checkUdpPackets); // Initialize Ticker every 0.5
}

void DIY_shiftOut(uint8_t DATA)
{
  byte val = 0;
  //for (int i = 7; i >= 0; i--) {
  for (int i = 0; i < 8; i++) { 
    val = DATA & (1 << i);
    if (val > 0){
      GPOS = (1 << dataPinLeds); // set data HIGH
    } else {
      GPOC = (1 << dataPinLeds); // set data LOW
    }
    
    GPOS = (1 << clockPinLeds); // set clock HIGH      
    GPOC = (1 << clockPinLeds); // set clock LOW 
  }
}

struct LedRain {
public:
  int index;
  int current_layer;

  unsigned int colors;

  LedRain(int _index, unsigned int _colors) {
    index = _index;
    colors = _colors;

    current_layer = random(5, 8);
  }
};


void animateRain() {
  constexpr int RAINS_COUNT = 5;
  LedRain* allRains[RAINS_COUNT];

  // generate rains
  for(int i = 0; i < RAINS_COUNT; i++) {
    int randIndex = random(0, 64); // 0 - 63

    unsigned int colors = 0xFFF; // white
    LedRain* temp = new LedRain(randIndex, colors);

    allRains[i] = temp;
  }

  // process rains
  for (int layer = 100; layer > 0; layer--) {
    gCubeManager.current_frame->clear();

    for (int i = 0; i < RAINS_COUNT; i++) {
      int led_index = allRains[i]->index;
      int led_layer = allRains[i]->current_layer;
      int index = (led_index + (led_layer * 64)) / 8;

      if (allRains[i]->current_layer == 0){
        allRains[i]->index  = random(0, 64);

        int col = random(0, 3);
        int colors = 0;
        switch (col) {
          case 0:
            colors = 0xF;
            break;
          case 1:
            colors = 0xF0;
            break;
          case 2:
            //colors = 0xF00;
            break;
        }
        allRains[i]->colors = 0xFFF;
        allRains[i]->current_layer = 7;
      }

      int value = 1 << (led_index % 8);

      gCubeManager.current_frame->redLeds.bam[0][index] |= (((allRains[i]->colors & 0xF) >> 3) & 1) << (led_index % 8);
      gCubeManager.current_frame->redLeds.bam[1][index] |= (((allRains[i]->colors & 0xF) >> 2) & 1) << (led_index % 8);
      gCubeManager.current_frame->redLeds.bam[2][index] |= (((allRains[i]->colors & 0xF) >> 1) & 1) << (led_index % 8);
      gCubeManager.current_frame->redLeds.bam[3][index] |= ((allRains[i]->colors & 0xF) & 1) << (led_index % 8);

      gCubeManager.current_frame->greenLeds.bam[0][index] |= ((((allRains[i]->colors & 0xF0) >> 4) >> 3) & 1) << (led_index % 8);
      gCubeManager.current_frame->greenLeds.bam[1][index] |= ((((allRains[i]->colors & 0xF0) >> 4) >> 2) & 1) << (led_index % 8);
      gCubeManager.current_frame->greenLeds.bam[2][index] |= ((((allRains[i]->colors & 0xF0) >> 4) >> 1) & 1) << (led_index % 8);
      gCubeManager.current_frame->greenLeds.bam[3][index] |= (((allRains[i]->colors & 0xF0) >> 4) & 1) << (led_index % 8);

      gCubeManager.current_frame->blueLeds.bam[0][index] |= ((((allRains[i]->colors & 0xF00) >> 8) >> 3) & 1) << (led_index % 8);
      gCubeManager.current_frame->blueLeds.bam[1][index] |= ((((allRains[i]->colors & 0xF00) >> 8) >> 2) & 1) << (led_index % 8);
      gCubeManager.current_frame->blueLeds.bam[2][index] |= ((((allRains[i]->colors & 0xF00) >> 8) >> 1) & 1) << (led_index % 8);
      gCubeManager.current_frame->blueLeds.bam[3][index] |= (((allRains[i]->colors & 0xF00) >> 8) & 1) << (led_index % 8);

      allRains[i]->current_layer--;
    }

    delay(100);
  }

  for(int i = (RAINS_COUNT - 1); i > 0; i--) {
    delete allRains[i];
  }

}

void loop() {

  //animateRain();
/*
  LOG("clear");
  frame_new.clear();
  delay(1000);

  LOG("white");
  frame_new.setWhite();
  delay(1000);

  LOG("red");
  frame_new.setRed();
  delay(1000);

  LOG("green");
  frame_new.setGreen();
  delay(1000);

  LOG("blue");
  frame_new.setBlue();
  delay(1000);
*/
delay(500);
#ifdef DEBUG
  LOG_PARAMS("ISR duration: avg=%d, min=%d, max=%d", avg, minimum, maximum);
  avg = 0; 
  minimum = 9999999; 
  maximum = 0;
#endif

}
