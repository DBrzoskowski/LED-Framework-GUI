const char* ssid = "Testowy maszt 5G 500% mocy";
const char* password = "Harnaskrol1337";

WiFiUDP Udp;
unsigned int UDP_PORT = 4210;  // local port to listen on

void setupWifi() {
  WiFi.begin(ssid, password);

  Serial.printf("Connecting to %s ", ssid);
  while (WiFi.status() != WL_CONNECTED)
  {
    delay(500);
    Serial.print(".");
  }
  Serial.println(" connected");

  Udp.begin(UDP_PORT);
  Serial.printf("Now listening at IP %s, UDP port %d", WiFi.localIP().toString().c_str(), UDP_PORT);
}

byte buffer[255];  // buffer for incoming packets

struct PacketHeader {
  byte PacketType;
  byte Version;
  byte Type;
  short BodySize;

  PacketHeader(void* addr) {
    PacketType = *reinterpret_cast<byte*>(addr);
    Version = *reinterpret_cast<byte*>(addr + 1);
    Type = *reinterpret_cast<byte*>(addr + 2);
    BodySize = (*reinterpret_cast<byte*>(addr + 3) << 8) | *reinterpret_cast<byte*>(addr + 4);
  }
};

struct PacketBody {

};

struct PacketSpectrum {
  byte PacketType;
  byte* Bars;

  PacketSpectrum(void* addr) {
    PacketType = *reinterpret_cast<byte*>(addr);
    Bars = reinterpret_cast<byte*>(addr + 1);
  }
};

enum class PacketType {
  Header = 0xFE,
  Body = 0xBB,
  Spectrum = 0xAB
};

bool waitingForBodies = false;
int bytesToRead = 0;
int bytesRead = 0;
byte tempBuffer[1024];

IRAM_ATTR void verifyPacket(byte packet_size) {
  PacketType packetType = PacketType(buffer[0]);
  LOG_PARAMS("PacketType=%d", packetType);

  switch(packetType) {
    case PacketType::Header: { 
      if (waitingForBodies) {
        LOG("[ERROR] Received header packet not expected");
        bytesToRead = 0;
        bytesRead = 0;
        //delete[] tempBuffer;
        memset(&tempBuffer, 0, 1024);
        waitingForBodies = false;
        //return;
      }

      LOG("Received header packet");

      auto header = PacketHeader(buffer);

      LOG_PARAMS("PacketType: %d\nVersion: %d\nType: %d\nBodySize: %d", header.PacketType, header.Version, header.Type, header.BodySize);

      waitingForBodies = true;
      bytesToRead = header.BodySize;
      //tempBuffer = new byte[bytesToRead];
      memset(&tempBuffer, 0, 1024);

      break;
    }
    case PacketType::Body: { 
      if (!waitingForBodies) {
        LOG("[ERROR] Received body packet not expected");

        return;
      }

      LOG("Received body packet");
      bytesToRead -= packet_size - 1;

      memcpy(tempBuffer + bytesRead, buffer + 1, packet_size - 1);

      bytesRead += packet_size - 1;

      LOG_PARAMS("Bytes to read=%d, bytes read=%d, packet_size=%d", bytesToRead, bytesRead, packet_size);

      if (bytesToRead <= 0) {
        waitingForBodies = false;
        memcpy(&frame_new, tempBuffer, bytesRead);
     
        bytesToRead = 0;
        bytesRead = 0;
        
        //delete[] tempBuffer;
        memset(&tempBuffer, 0, 1024);
        LOG("Completed receiving packets");
      }
      break;
    }
    case PacketType::Spectrum: {
      LOG("Received spectrum packet");

      if (packet_size != 33) {
        LOG("[ERROR] Wrong spectrum packet size");
      }

      if (waitingForBodies) {
        LOG("[ERROR] Received header packet not expected");
        bytesToRead = 0;
        bytesRead = 0;
        memset(&tempBuffer, 0, 1024);
        waitingForBodies = false;
      }

      auto spectrum = PacketSpectrum(buffer);

      frame_new.clear();

      for (int x = 0; x < 8; x++) {
        for (int y = 0; y < 8; y++) {
          byte index = ((x * 8) + y) / 2;
          byte position = ((x * 8) + y) % 2;

          byte barLevel = 0;

          if (position == 0){
            barLevel = spectrum.Bars[index] & 0b00001111;
          }
          else {
            barLevel = (spectrum.Bars[index] & 0b11110000) >> 4;
          }

          if (barLevel < 0 || barLevel > 7) {
            LOG("[ERROR] Wrong bar level");
          } 

          frame_new.drawColumn(x, y, barLevel);
        }
      }
      break;
    }
  }
}

int bytes_to_read = 0;
IRAM_ATTR void checkUdpPackets() {
  //wifiTicker.detach();
  do {
    bytes_to_read = Udp.parsePacket();

    if(bytes_to_read > 0) {
      byte bytes_read = Udp.read(&buffer[0], bytes_to_read);

      verifyPacket(bytes_read);

      Udp.endPacket();
    }
  }
  while(bytes_to_read > 0);
  
  //wifiTicker.attach(0.03, checkUdpPackets);
  wifiTicker.once_ms(3, checkUdpPackets); // Initialize Ticker every 0.005s
}