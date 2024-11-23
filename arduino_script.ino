#include <RCSwitch.h>

RCSwitch mySwitch = RCSwitch();

void setup() {
  Serial.begin(9600);
  mySwitch.enableReceive(0);  // Configura o pino de recepção como 0 (ajuste conforme necessário)
}

void loop() {
  if (mySwitch.available()) {
    long code = mySwitch.getReceivedValue();
    if (code == 0) {
      Serial.println("Código desconhecido");
    } else {
      Serial.println(code);  // Envia o código para a serial
    }
    mySwitch.resetAvailable();
  }
}