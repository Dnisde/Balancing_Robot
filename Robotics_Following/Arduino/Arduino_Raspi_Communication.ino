// Send to Raspberry Pi
/*
Program: Send Strings to Raspberry Pi
File: send_string_to_raspberrypi.ino
Description: Send strings from Arduino to a Raspberry Pi
Author: Addison Sears-Collins
Website: https://automaticaddison.com
Date: July 5, 2020
*/
 
// void setup(){
   
//   // Set the baud rate  
//   Serial.begin(9600);
   
// }
 
// void loop(){
   
//   // Print "Hello World" every second
//   // We do println to add a new line character '\n' at the end
//   // of the string.
//   Serial.println("Hello! My name is Arduino.");
//   Serial.write("Hey");
//   delay(1000);
// }


// -----------------------------------------
// Received from Raspberry Pi
/*
Program: Receive Strings From Raspberry Pi
File: receive_string_from_raspberrypi.ino
Description: Receive strings from a Raspberry Pi
Author: Addison Sears-Collins
Website: https://automaticaddison.com
Date: July 5
*/
 
void setup(){
   
  // Set the baud rate  
  Serial.begin(9600);
   
}

 
void loop(){
  
  if (Serial.available() > 0) {
    String data = Serial.readStringUntil('\n');
    // Received from Raspberry pi: 
    Serial.println(data); 
  }
  Serial.flush();

}