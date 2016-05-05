
 /*
  if(keyPressed) {
       port.write (key);
}
*/
import processing.serial.*;

Serial port;
String portname = "COM10";  
int baudrate = 9600;
int value = 0;  
 
float bx;
float by;
int boxSize = 20;
boolean overBox = false;
boolean locked = false;
boolean pinFlag = false;
float xOffset = 0.0; 
float yOffset = 0.0; 
float radius = 0.0;
final char maxSpeed=254;
int car_id = 1;
void setup() 
{
    port = new Serial(this, portname, baudrate);
  println(port);
  size(480, 640);
  bx = width/2.0;
  by = height/2.0;
  rectMode(RADIUS);  
  ellipseMode(RADIUS);
}

void draw() 
{ 
  background(0);
  if(locked) { 

  char dirType = 0;
  char xPower = 150;
  char yPower = 150;
  char r = 0;
  char g = 0;
  char b = 0;
  boolean rgb_func = false;
    switch (key) {
     case 'w':
        dirType = 1;
        break;
     case 'a':
        dirType = 4;
      break;
     case 'd':
        dirType = 3;
      break;
     case 's':
        dirType = 2;
     break;
      case '4':
        println("4");
        if (car_id == 4){
          rgb_func = true;
          r = 255;
          b = 0;
          g = 0;
        }
        car_id = 4;
        break;
      case '5':
      println("5");
        if (car_id == 5){
          rgb_func = true;
          r = 0;
          b = 0;
          g = 255;
        }
        car_id = 5;
        break;
        
       default: 
    locked=false;
    }

  if (((xPower>20 || yPower > 20) && locked ) || rgb_func) {
    
  port.write(255);
  port.write(254);
  port.write(100);
  port.write(car_id);
  if (!rgb_func){
    port.write(dirType);
    port.write(xPower);
    port.write(yPower);
    port.write(0);
  } else {
    port.write(6);
    port.write(r);
    port.write(g);
    port.write(b);
    rgb_func = false;
    println("RGB function");
  }
   while (port.available() > 0) {
    int inByte = port.read();
    println(inByte);
  }
  }
//    println("X:" + (int)xPower + "(" + (int)xDir + ")" + " Y:" + (int)yPower + "(" + (int)yDir + ")"  );
    println("dir:" + (int)dirType + " X:" + (int)xPower + " Y:" + (int)yPower  );

  }
}

void mousePressed() {
  if(overBox) { 
    locked = true; 
    fill(255, 255, 255);
  } else {
    locked = false;
  }
  xOffset = mouseX-bx; 
  yOffset = mouseY-by; 
  
    if (mouseButton == LEFT)
  pinFlag=true;
  if (mouseButton == RIGHT)
  pinFlag=false;

}

void mouseDragged() {
  if(locked) {
    bx = mouseX-xOffset; 
    by = mouseY-yOffset; 
  }
}

void mouseReleased() {
  locked = false;
}

void keyPressed()
{
 locked = true; 
 // println((int)key);
}

void keyReleased()
{
 locked = false; 
}