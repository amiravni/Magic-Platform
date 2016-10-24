
#define MYID 1
#define DEBUG 1

#define MTRLFTPIN1 9
#define MTRLFTPIN2 10
#define MTRGHTPIN1 5
#define MTRGHTPIN2 6
#define LEDPIN 4

#define MSGLEN 5
#define DT2STOP 400


#include <SPI.h>
#include <Mirf.h>
#include <nRF24L01.h>
#include <MirfHardwareSpiDriver.h>

unsigned long TimeNoComm = 0;
// —————————————————————————  Motors
int motor_left[] = {  MTRLFTPIN1, MTRLFTPIN2};
int motor_right[] = {  MTRGHTPIN1, MTRGHTPIN2};

int leftDir = 0;
int rightDir = 0;
byte dataDirLast = 0;

int leftPowerLast = 0;
int rightPowerLast = 0;
int leftPower = 0;
int rightPower = 0;
int realPowerLeft = 0;
int realPowerRight = 0;

int stepPower = 1;
int gap = 0;

volatile long encLeft = 0;
volatile long encRight = 0;

// ————————————————————————— Setup
void setup() {
  if (DEBUG) Serial.begin(9600);
  if (DEBUG) stepPower = 5;
   pinMode(LEDPIN, OUTPUT);
   digitalWrite(LEDPIN, HIGH);
  // Setup motors
  int i;
  for (i = 0; i < 2; i++) {
    pinMode(motor_left[i], OUTPUT);
    pinMode(motor_right[i], OUTPUT);
  }

  Mirf.spi = &MirfHardwareSpi;
  Mirf.init();
  Mirf.setRADDR((byte *)"serv1");
  Mirf.payload = MSGLEN * sizeof(byte);
  Mirf.config();

  TimeNoComm = millis();

  /*
    TCCR1A = _BV(COM1A1) | _BV(COM1B1) | _BV(WGM11) | _BV(WGM10);
    TCCR1B = _BV(CS12);
    OCR1A = 0;
    OCR1B = 0;*/

  attachInterrupt(0, intRight, FALLING );
  attachInterrupt(1, intLeft, FALLING );
  digitalWrite(LEDPIN, LOW);
}

void loop() {

  byte data[Mirf.payload];
  if (!Mirf.isSending() && Mirf.dataReady()) {
    Mirf.getData(data);
    if (DEBUG)  Serial.println(":");
    // if (DEBUG) { for (int i=0; i<MSGLEN;i++)   Serial.println( (int)data[i] ); }

    if (data[0] == MYID ||  data[0] == 0 ) {

      if (data[1] >= 1 && data[1] <= 4 ) {
        TimeNoComm = millis();
        dataDirLast = data[1];
        switchData1(data[1], false);
      }

      leftPowerLast  = updatePower(leftPowerLast ,  leftDir * (int)data[2],true);
      rightPowerLast = updatePower(rightPowerLast, rightDir * (int)data[3],true);
/*    if (DEBUG)
    {
      Serial.print( leftPowerLast);
      Serial.print(" , ");
      Serial.println( rightPowerLast);
    }*/

      leftPower = abs(leftPowerLast);
      rightPower = abs(rightPowerLast);


      gap = (int)(encLeft - encRight);
      if ( encLeft > encRight && encLeft - encRight > 127 ) {
        realPowerLeft = 0;
        realPowerRight = rightPower;
      }
      else if ( encRight > encLeft && encRight - encLeft > 127 ) {
        realPowerLeft = leftPower;
        realPowerRight = 0;
      }
      else {
        if (gap > 0) {
          realPowerLeft = leftPower - 2 * abs(gap);
          realPowerRight = rightPower;
        }
        else {
          realPowerLeft = leftPower;
          realPowerRight = rightPower - 2 * abs(gap);
        }
      }

      switchData1(data[1], true);

    }

  }

  if ( (millis() - TimeNoComm) > DT2STOP)
  {

    if (dataDirLast >= 1 && dataDirLast <= 4 && (millis() - TimeNoComm) < 3 * DT2STOP ) {
      leftPowerLast = updatePower(leftPowerLast, 0,false);
      rightPowerLast = updatePower(rightPowerLast, 0,false);
      realPowerLeft = abs(leftPowerLast);
      realPowerRight = abs(rightPowerLast);
      switchData1(dataDirLast, true);
    }
    else {
      motor_stop();
    }

    if (encLeft > 100000) {
      gap = (int)(encLeft - encRight);
      if (gap >= 0) {
        encLeft = abs(gap);
        encRight = 0;
      }
      else {
        encLeft = 0;
        encRight = abs(gap);
      }

    }
  }


}

void intLeft() {
  encLeft++;
}

void intRight() {
  encRight++;
}

void motor_stop() {

  digitalWrite(motor_left[0], LOW);
  digitalWrite(motor_left[1], LOW);
  digitalWrite(motor_right[0], LOW);
  digitalWrite(motor_right[1], LOW);
  digitalWrite(LEDPIN, LOW);

}

void drive_forward() {

  analogWrite(motor_left[0], realPowerLeft);
  digitalWrite(motor_left[1], LOW);

  analogWrite(motor_right[0], realPowerRight);
  digitalWrite(motor_right[1], LOW);
  digitalWrite(LEDPIN, HIGH);
}

void drive_backward() {
  digitalWrite(motor_left[0], LOW);
  analogWrite(motor_left[1], realPowerLeft);

  digitalWrite(motor_right[0], LOW);
  analogWrite(motor_right[1], realPowerRight);
  digitalWrite(LEDPIN, HIGH);
}

void turn_left() {
  digitalWrite(motor_left[0], LOW);
  analogWrite(motor_left[1], realPowerLeft);

  digitalWrite(motor_right[1], LOW);
  analogWrite(motor_right[0], realPowerRight);
  digitalWrite(LEDPIN, HIGH);
}

void turn_right() {
  digitalWrite(motor_left[1], LOW);
  analogWrite(motor_left[0], realPowerLeft);

  digitalWrite(motor_right[0], LOW);
  analogWrite(motor_right[1], realPowerRight);
  digitalWrite(LEDPIN, HIGH);
}

int updatePower(int lastVal, int currVal, bool sw) {

if (sw) {
  if( currVal > 0 && lastVal < 130) lastVal = 130;
  if( currVal < 0 && lastVal > -130) lastVal = -130; 
}

  if (lastVal - stepPower > currVal ) return (lastVal - stepPower);
  if (lastVal + stepPower < currVal ) return (lastVal + stepPower);
  return lastVal;

}


void switchData1(byte data1, boolean sw) {
  if (sw) {
    if (DEBUG)
    {
      Serial.print( realPowerLeft);
      Serial.print(" , ");
      Serial.print( realPowerRight);
      Serial.print(" Gap =  ");
      Serial.println( gap);
    }
  }

  switch (data1)
  {
    case 0: // INIT
      break;
    case 1: // FW
      if (sw)
        drive_forward();
      else {
        leftDir = 1;
        rightDir = 1;
      }
      break;
    case 2: // BW
      if (sw)
        drive_backward();
      else {
        leftDir = -1;
        rightDir = -1;
      }
      break;
    case 3: // Right
      if (sw)
        turn_right();
      else {
        leftDir = 1;
        rightDir = -1;
      }
      break;
    case 4: // Left
      if (sw)
        turn_left();
      else {
        leftDir = -1;
        rightDir = 1;
      }
      break;
    case 5: // Stop  +  Stop procedure
      motor_stop();
      break;
    case 6: // All LEDs one Color
         digitalWrite(LEDPIN, HIGH);
         delay(100);
    //   colorWipe(strip.Color(data[2], data[3], data[4]), 0);
      break;
    case 7: // All LEDs one Color
      //colorWipe(strip.Color(data[2], data[3], data[4]), 100);
      //  colorWipe(strip.Color(255, 0, 255), 100);
      break;
    default:
      break;
  }
}

