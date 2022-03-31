#pragma once


class CubeManager {
public:
    RGB4x4x4Frame* current_frame = nullptr;
    
    unsigned char latchPin = 0;
    unsigned char clockPin = 0;
    unsigned char dataPin = 0;

    int layer_num = 0;
    int BAM_Brightness_Bit, BAM_Counter = 0; // Bit Angle Modulation variables to keep track of things
    int test = 1;

    CubeManager(unsigned char latch, unsigned char clock, unsigned char data) {
      latchPin = latch;
      clockPin = clock;
      dataPin = data;
    }

    void loadFrame(RGB4x4x4Frame* frame) {
      current_frame = frame;
    }

    void initializeISR() {
      noInterrupts(); // disable global interrupts
      TCCR1A = 0;     // set entire TCCR1A register to 0
      TCCR1B = 0;     // same for TCCR1B
#ifdef DEBUG
      OCR1A = 1000 * 8 * 30;
#else
      OCR1A = 30; // you can play with this, but I set it to 30, which means:
                  // our clock runs at 250kHz, which is 1/250kHz = 4us
                  // with OCR1A set to 30, this means the interrupt will be called every (30+1)x4us=124us, 
                  // which gives a multiplex frequency of about 8kHz
#endif
      // turn on CTC mode:
      TCCR1B |= (1 << WGM12); // CTC mode, will call an interrupt on a counter match
      // set to divide the clock by 64, so 16MHz/64=250kHz
      //TCCR1B |= (1 << CS11);
      TCCR1B |= (1 << CS12);
      // enable timer compare interrupt:
      TIMSK1 |= (1 << OCIE1A); // call the interrupt on an OCR1A match
      // enable global interrupts:
      interrupts();
    }

    void initializeLedsShiftRegisters() {
      pinMode(latchPin, OUTPUT);
      pinMode(clockPin, OUTPUT);
      pinMode(dataPin, OUTPUT);
    }

    void processISR() {
      if(BAM_Counter == (4 * test)) {
        BAM_Brightness_Bit++;
      }
      else if (BAM_Counter == (8 * test)) {
        BAM_Brightness_Bit++;
      }
      else if (BAM_Counter == (16 * test)) {
        BAM_Brightness_Bit++;
      }


      processLayer(layer_num, BAM_Brightness_Bit);


      BAM_Counter++; //Here is where we increment the BAM counter
      if(BAM_Counter == (32 * test)){
        BAM_Counter=0;
        BAM_Brightness_Bit=0;
      }
      if (layer_num < 3){
        layer_num++;
      } else {
        layer_num = 0;
      }

    }

    void initializeSPI() {
      SPI.begin();
    }

    void initialize() {
      initializeLedsShiftRegisters();
      initializeISR();
      initializeSPI();
    }

    void setLed(struct RGB4x4x4_Layer mask2, unsigned short layer) {
      const int SHIFT_REGISTERS_8_BITS = 6;
      mask2.red = ~mask2.red;
      mask2.green = ~mask2.green;
      mask2.blue = ~mask2.blue;
      byte mask[SHIFT_REGISTERS_8_BITS]= {};
      mask[0] = mask2.red & 0x000000FF;        // czerwone
      mask[1] = mask2.red >> 8 & 0x000000FF;   // czerwone
      mask[2] = mask2.green & 0x000000FF;      // zielone
      mask[3] = mask2.green >> 8 & 0x000000FF; // zielone
      mask[4] = mask2.blue & 0x000000FF;       // niebieskie
      mask[5] = mask2.blue >> 8 & 0x000000FF;  // niebieskie
#ifdef DEBUG
      Serial.print("red[0]=");
      Serial.print(mask[0]);
      Serial.print(", red[1]=");
      Serial.print(mask[1]);
      Serial.print(", green[2]=");
      Serial.print(mask[2]);
      Serial.print(", green[3]=");
      Serial.print(mask[3]);
      Serial.print(", blue[4]=");
      Serial.print(mask[4]);
      Serial.print(", blue[5]=");
      Serial.println(mask[5]);
#endif
      PORTD &= 0 << latchPinLeds; // Latch pin LOW

      byte layer_val = 0;
      layer_val = 1 << layer;

      SPI.transfer(layer_val);
      SPI.transfer(mask[5]);
      SPI.transfer(mask[4]);
      SPI.transfer(mask[3]);
      SPI.transfer(mask[2]);
      SPI.transfer(mask[1]);
      SPI.transfer(mask[0]);

      PORTD |= 1 << latchPinLeds; // Latch pin HIGH
    }

    void workaroundHwBug(RGB4x4x4_Layer& layer, Color before, Color after, int i) {
      switch(before) {
        case Color::Red: {
          layer.red = layer.red & ~(1 << i);
          break;
        }
        case Color::Green: {
          layer.green = layer.green & ~(1 << i);
          break;
        }
        case Color::Blue: {
          layer.blue = layer.blue & ~(1 << i);
          break;
        }
      }
      switch(after) {
        case Color::Red: {
          layer.red = layer.red | (1 << i);
          break;
        }
        case Color::Green: {
          layer.green = layer.green | (1 << i);
          break;
        }
        case Color::Blue: {
          layer.blue = layer.blue | (1 << i);
          break;
        }
      }
    }

    void checkForWorkarounds(int x, int y, int z, int i, RGB4x4x4Frame* frame, RGB4x4x4_Layer& layer) {
      
      if (i == 0 && z == 1 && (((layer.red >> i) & 1) == 1)) {
        // replace red with blue
        workaroundHwBug(layer, Color::Red, Color::Blue, i);
      }
      else if (i == 0 && z == 1 && (((layer.blue >> i) & 1) == 1)) {
        // replace blue with red
        workaroundHwBug(layer, Color::Blue, Color::Red, i);
      }
      else if (i == 2 && z == 1 && (((layer.red >> i) & 1) == 1)) {
        // replace red with blue
        workaroundHwBug(layer, Color::Red, Color::Blue, i);
      }
      else if(i == 2 && z == 1 && (((layer.blue >> i) & 1) == 1)) {
        // replace blue with red
        workaroundHwBug(layer, Color::Blue, Color::Red, i);
      }
    }

    void processLayer(int z, int BAM_Bit) {
      RGB4x4x4_Layer layer = {};
      for(int i = 0, x = 0; x < 4; x++, i++) {
        for(int y = 0; y < 4; y++, i++) {
          layer.red = layer.red | (((current_frame->allLeds[x][y][z].red >> BAM_Bit) & 1) << i);
          layer.green = layer.green | (((current_frame->allLeds[x][y][z].green >> BAM_Bit) & 1) << i);
          layer.blue = layer.blue | (((current_frame->allLeds[x][y][z].blue >> BAM_Bit) & 1) << i);

          checkForWorkarounds(x, y, z, i, current_frame, layer);
        }
      }

      setLed(layer, z);
#ifdef DEBUG
      Serial.print("Current layer: ");
      Serial.println(z);
      Serial.print("Current layer: ");
      Serial.println(z);
      Serial.print("Current BAM_Bit: ");
      Serial.println(BAM_Bit);
      Serial.print("layer.red = ");
      Serial.println(layer.red, BIN);
      Serial.print("layer.green = ");
      Serial.println(layer.green, BIN);
      Serial.print("layer.blue = ");
      Serial.println(layer.blue, BIN);
      Serial.print("Actual layer: ");
      Serial.println(z);
#endif
    }
};