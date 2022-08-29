#pragma once

#include "config.h"
#include <SPI.h>
#include "RGB_Led.h"
#include "WifiManager.h"

IRAM_ATTR void ISR_Callback(void);

class CubeManager {
public:
    int test = 0;
    RGBFrame* current_frame = nullptr;
    RGB_Layer current_layer = RGB_Layer();

    unsigned char latchPin = 0;
    unsigned char clockPin = 0;
    unsigned char dataPin = 0;

    int layer_num = 0;
    int BAM_Brightness_Bit, BAM_Counter = 0; // Bit Angle Modulation variables to keep track of things

    CubeManager(unsigned char latch, unsigned char clock, unsigned char data){
      latchPin = latch;
      clockPin = clock;
      dataPin = data;
    }

    void loadFrame(RGBFrame* frame) {
      current_frame = frame;
    }
    
    void initializeLedsShiftRegisters() {
      pinMode(latchPin, OUTPUT);
      pinMode(clockPin, OUTPUT);
      pinMode(dataPin, OUTPUT);
    }

    IRAM_ATTR void processISR() {
      if(BAM_Counter == CUBE_DIMENSION) {
        BAM_Brightness_Bit++;
      }
      else if(BAM_Counter == (CUBE_DIMENSION * 3)){
        BAM_Brightness_Bit++;
      }
      else if(BAM_Counter == (CUBE_DIMENSION * 7)){
        BAM_Brightness_Bit++;
      }

      processLayer(layer_num, BAM_Brightness_Bit);

      BAM_Counter++; //Here is where we increment the BAM counter

      if(BAM_Counter >= (CUBE_DIMENSION * 15)){
        BAM_Counter = 0;
        BAM_Brightness_Bit = 0;
      }

      layer_num++;

      if (layer_num >= CUBE_DIMENSION){
        layer_num = 0;
      }

    }
    
    void initializeISR() {
      timer1_isr_init();
      timer1_attachInterrupt(ISR_Callback);
      timer1_enable(TIM_DIV1, TIM_EDGE, TIM_SINGLE);
      timer1_write(INTERVAL_IN_US);
    }

    void initialize() {
      initializeLedsShiftRegisters();
      initializeISR();
    }
    
    
    IRAM_ATTR void DIY_shiftOut(uint8_t DATA)
    {
      byte val = 0;
      for (uint8_t i = 0; i < 8; i++) {
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

    IRAM_ATTR void setLed(RGB_Layer layer, unsigned short layerIndex) {
      GPOC = (1 << latchPin); // Latch pin LOW

      byte layer_val = 1 << layerIndex;

      DIY_shiftOut(layer_val);

      DIY_shiftOut(~layer.blue[7]);
      DIY_shiftOut(~layer.blue[6]);
      DIY_shiftOut(~layer.blue[5]);
      DIY_shiftOut(~layer.blue[4]);
      DIY_shiftOut(~layer.blue[3]);
      DIY_shiftOut(~layer.blue[2]);
      DIY_shiftOut(~layer.blue[1]);
      DIY_shiftOut(~layer.blue[0]);

      DIY_shiftOut(~layer.green[7]);
      DIY_shiftOut(~layer.green[6]);
      DIY_shiftOut(~layer.green[5]);
      DIY_shiftOut(~layer.green[4]);
      DIY_shiftOut(~layer.green[3]);
      DIY_shiftOut(~layer.green[2]);
      DIY_shiftOut(~layer.green[1]);
      DIY_shiftOut(~layer.green[0]);

      DIY_shiftOut(~layer.red[7]);
      DIY_shiftOut(~layer.red[6]);
      DIY_shiftOut(~layer.red[5]);
      DIY_shiftOut(~layer.red[4]);
      DIY_shiftOut(~layer.red[3]);
      DIY_shiftOut(~layer.red[2]);
      DIY_shiftOut(~layer.red[1]);
      DIY_shiftOut(~layer.red[0]);


      GPOS = (1 << latchPin); // Latch pin LOW
    }

    IRAM_ATTR void processLayer(int layer, int BAM_Bit) {
      byte layer_val = 1 << layer;

      GPOC = (1 << latchPin); // Latch pin LOW

      DIY_shiftOut(layer_val);
      
      DIY_shiftOut(~current_frame->blueLeds.bam[BAM_Bit][(layer * 8) + 7]);
      DIY_shiftOut(~current_frame->blueLeds.bam[BAM_Bit][(layer * 8) + 6]);
      DIY_shiftOut(~current_frame->blueLeds.bam[BAM_Bit][(layer * 8) + 5]);
      DIY_shiftOut(~current_frame->blueLeds.bam[BAM_Bit][(layer * 8) + 4]);
      DIY_shiftOut(~current_frame->blueLeds.bam[BAM_Bit][(layer * 8) + 3]);
      DIY_shiftOut(~current_frame->blueLeds.bam[BAM_Bit][(layer * 8) + 2]);
      DIY_shiftOut(~current_frame->blueLeds.bam[BAM_Bit][(layer * 8) + 1]);
      DIY_shiftOut(~current_frame->blueLeds.bam[BAM_Bit][(layer * 8) + 0]);

      DIY_shiftOut(~current_frame->greenLeds.bam[BAM_Bit][(layer * 8) + 7]);
      DIY_shiftOut(~current_frame->greenLeds.bam[BAM_Bit][(layer * 8) + 6]);
      DIY_shiftOut(~current_frame->greenLeds.bam[BAM_Bit][(layer * 8) + 5]);
      DIY_shiftOut(~current_frame->greenLeds.bam[BAM_Bit][(layer * 8) + 4]);
      DIY_shiftOut(~current_frame->greenLeds.bam[BAM_Bit][(layer * 8) + 3]);
      DIY_shiftOut(~current_frame->greenLeds.bam[BAM_Bit][(layer * 8) + 2]);
      DIY_shiftOut(~current_frame->greenLeds.bam[BAM_Bit][(layer * 8) + 1]);
      DIY_shiftOut(~current_frame->greenLeds.bam[BAM_Bit][(layer * 8) + 0]);

      DIY_shiftOut(~current_frame->redLeds.bam[BAM_Bit][(layer * 8) + 7]);
      DIY_shiftOut(~current_frame->redLeds.bam[BAM_Bit][(layer * 8) + 6]);
      DIY_shiftOut(~current_frame->redLeds.bam[BAM_Bit][(layer * 8) + 5]);
      DIY_shiftOut(~current_frame->redLeds.bam[BAM_Bit][(layer * 8) + 4]);
      DIY_shiftOut(~current_frame->redLeds.bam[BAM_Bit][(layer * 8) + 3]);
      DIY_shiftOut(~current_frame->redLeds.bam[BAM_Bit][(layer * 8) + 2]);
      DIY_shiftOut(~current_frame->redLeds.bam[BAM_Bit][(layer * 8) + 1]);
      DIY_shiftOut(~current_frame->redLeds.bam[BAM_Bit][(layer * 8) + 0]);
    
      GPOS = (1 << latchPin); // Latch pin LOW
    }
};
