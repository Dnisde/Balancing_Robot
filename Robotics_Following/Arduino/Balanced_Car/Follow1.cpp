#include "Follow1.h"
#include <stdio.h>
#include <stdlib.h>

IR IR;
Ultrasonic Ultrasonic;
extern Balanced Balanced;
extern Function Function;

uint8_t cntr1 = 0xff;
uint8_t cntr2 = 0xff;
uint16_t cntr3 = 0xff;

void Ultrasonic::Pin_init()
{
  pinMode(ECHO_PIN, INPUT);
  pinMode(TRIG_PIN, OUTPUT);
}


char Ultrasonic ::measure_flag=0;
unsigned long Ultrasonic ::measure_prev_time=0;
double Ultrasonic ::distance_value;
double Ultrasonic ::errorValue;

void Function::Follow_Mode1()
{
  // PhotoElectric signal Checking:
  IR.Send();

  // Ultrasonic signal checking:
  Ultrasonic.Get_Distance();

  if (millis() - follow_prev_time >= 100)
  {
    // Serial.println(String(FineTuning()));
    // Judge move between IR and Ultrasonic:
    If_IR_TRIGGERED ? IR.Check() : Ultrasonic.Check();
    
    // Ultrasonic.Check(power);
    
    follow_prev_time = millis();
  }
     
}

// Calculate the Fine Tunning power of the Turning Speed, and plug into the function.
// Motion control by the Camera Tunning:
int Function::FineTuning() {
  
  // Serial.println(String(Ultrasonic::errorValue));  
  int motion = 0;
  double percentage = 0.0;
  double threshold = 0.25;
  double motor_threshold = 5;
  // Left: positive, Right: Negative.

  // Object is too left, tunnning to left side:
  if (Ultrasonic::errorValue > threshold) {
    percentage = (Ultrasonic::errorValue - threshold) / threshold;
    // How much tune should motor given:
    motion = motor_threshold * percentage;
  }
  
  // Object is too right, tunning to right side:
  else if (Ultrasonic::errorValue < -threshold) {
    percentage = (Ultrasonic::errorValue + threshold) / threshold;
    // How much tune should motor given:
    motion = motor_threshold * percentage;
  }

  else {
    motion = 0;
  }

  return motion;
}

//  delayfor(80);//about 2 seconds
//  delayfor(39);//about 1 seconds
//  delayfor(11);//about 0.3 seconds
//  delayfor(5);//about 0.03seconds
//  delayfor(1);//about 0.01seconds !! MOST SHORTEST delay for function
void Function::delayfor(int delay){
  for(cntr1 = 0;cntr1 < 255;cntr1++){
    for(cntr2 = 0;cntr2 < 255;cntr2++){
      for(cntr3 = 0;cntr3 < delay;cntr3++){
        asm("nop"); // Do nothing but only cost an execution time.
      }
    }
  }
}

void IR::Check()
{
    int motion = left_is_obstacle + right_is_obstacle;

    switch(motion)
    {
      // Only Left side Detect obstacles.
      case FOLLOW_LEFT:
        // Balanced.Motion_Control(LEFT, 30);
        // Balanced.Motion_Control(S_BACK_RIGHT, 30);
        Balanced.Stop();
        left_is_obstacle=0;break;

      // Only Right side Detect obstacles.
      case FOLLOW_RIGHT:
        // Balanced.Motion_Control(RIGHT, 30);
        // Balanced.Motion_Control(S_BACK_LEFT, 30);
        Balanced.Stop();
        right_is_obstacle=0;break;                      
      
      // Both side detect obstacles:
      case FOLLOW_BACK:
        Balanced.Motion_Control(BACK, 35);
        right_is_obstacle=0;
        left_is_obstacle=0;break; 
    }
}

void Ultrasonic::Check()
{
  int power = Function.FineTuning();

  Serial.println(String(power));

  int motion = 0;

  if (power > 0) // Tunning the angle of robot to "LEFT" based on Camera error range.
  {
    motion = 1; 
  } 
  else if (power < 0) // Tunning the angle of robot to "RIGHT" based on Camera error range.
  {
    motion = 2;
  }   
  else // Default: Keep following
  { 
    motion = 0;
  }
  
  switch(motion)
  {
    case 1:
      // errorValue ? Balanced.Motion_Control(LEFT, power) : Balanced.Stop();
      DISTANCE_JUDAGEMENT ? Balanced.Motion_Control(SLIGHT_LEFT, power) : Balanced.Stop();
      // Balanced.Motion_Control(LEFT, power);
      break;

    case 2:
      // errorValue ? Balanced.Motion_Control(RIGHT, power) : Balanced.Stop();
      DISTANCE_JUDAGEMENT ? Balanced.Motion_Control(SLIGHT_RIGHT, -power) : Balanced.Stop();
      // Balanced.Motion_Control(RIGHT, power);
      break;
    
    default:  
      DISTANCE_JUDAGEMENT ? Balanced.Motion_Control(FORWARD, power) : Balanced.Stop();
  }
  
}

void IR::Send()
{
  static unsigned long ir_send_time;

  if (millis() - ir_send_time > 15)
  {
    for (int i = 0; i < 39; i++)
    { 
      digitalWrite(IR_SEND_PIN, LOW);
      delayMicroseconds(9);
      digitalWrite(IR_SEND_PIN, HIGH);
      delayMicroseconds(9);
    }
    ir_send_time=millis();
  }
}