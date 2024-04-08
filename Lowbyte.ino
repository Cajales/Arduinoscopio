int V=0;
byte Vl;
byte Vh;
byte lb;
int i;
void setup() {
  // put your setup code here, to run once:
Serial.begin(115200);
}

void loop() {
  V= analogRead(A0);
  lb=lowByte(0);
  Serial.write(lb);
  Vh=highByte(V<<3);
  Serial.write(Vh|0b11100000);
  Vl=(lowByte(V))&0b00011111;   
  Serial.write(Vl|0b01100000);

}
