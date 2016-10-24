#define MSGLEN 5

#include <SPI.h>
#include <Mirf.h>
#include <nRF24L01.h>
#include <MirfHardwareSpiDriver.h>

const byte  headerChars[3]={255,254,100};

void setup(){
  Serial.begin(9600);
  Mirf.spi = &MirfHardwareSpi;
  Mirf.init();
  Mirf.setRADDR((byte *)"clie1");
  Mirf.payload = MSGLEN*sizeof(byte);
  Mirf.config();
  // Serial.println("Beginning ... "); 
  pinMode(6,OUTPUT);
  digitalWrite(6,LOW);
  Serial.println("Listening...");
}


void loop(){

  byte header[3]={0,0,0};
  char sendArray[MSGLEN];
  boolean  sendFlag=false;

  Mirf.setTADDR((byte *)"serv1");

  if (Serial.available() > 0) 
  {
     header[0] = (byte)Serial.read();
     Serial.println(header[0]);
if (header[0]== headerChars[0])
{
  
  while (Serial.available() <= 0) {  }
   header[1] =  (byte)Serial.read();
   Serial.println(header[1]);
  while (Serial.available() <= 0) {}
    header[2] =  (byte)Serial.read();
    Serial.println(header[2]);
    if (header[1] ==headerChars[1] &&   (header[2] ==headerChars[2] ))
    {
        
      
      int i=0;
      while(!sendFlag)
  {
    if (Serial.available() > 0) 
  {
        sendArray[i]= (byte)Serial.read();
        i++;
  }
    if (i>MSGLEN)
      sendFlag=true;
//  for (int zzz=0; zzz<3;zzz++)   Serial.print( (char)header[zzz] ); 
 //  for (int zzz=0; zzz<MSGLEN;zzz++)   Serial.print( (char)sendArray[zzz] ); 
    }
  }
  }
  }
  if (sendFlag)
  {
      digitalWrite(6,HIGH);
    Mirf.send((byte *)sendArray);
  //  for (int i=0; i<MSGLEN;i++)   Serial.print( sendArray[i] ); 
   //Serial.println( sendArray[4]);
    while(Mirf.isSending()){
    }
  }
}
