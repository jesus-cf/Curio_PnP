#define Vacuum 2 
#define Valve 3
#define PushButton 4

int c = 0; // for incoming serial data
int ton=0;
int toff=0;
String incomingString;

void setup()
{
    Serial.begin(115200); // opens serial port, sets data rate to 115200 bps

    pinMode(Vacuum, OUTPUT);    // sets the digital pin 2 as output
    pinMode(Valve, OUTPUT);    // sets the digital pin 3 as output
    pinMode(PushButton, INPUT_PULLUP); // To manually turn the vacuum pump on

    digitalWrite(Vacuum, LOW); // Vacuum pump off
    digitalWrite(Valve, LOW); // Vent valve closed
}

void Pump (int value)
{
    if(value==1)
    {
        digitalWrite(Vacuum, HIGH); // Vacuum pump on
        digitalWrite(Valve, LOW); // Vent valve is closed
    }
    else
    {
        digitalWrite(Vacuum, LOW); // Vacuum pump off
        digitalWrite(Valve, HIGH); // Vent valve is open
        delay(250); // Wait for pressure to equalize
        digitalWrite(Valve, LOW); // Vent valve is closed
    }
}

void loop()
{
   if (Serial.available() > 0)
   {  
       c = Serial.read(); // read the incoming byte
       
       if(c=='0') // Vacuum off
       {
           if(toff!=0) delay(toff);
           Pump(0);
       }
       else if (c=='1') // Vacuum on
       {
           if(ton!=0) delay(ton);
           Pump(1);
       }
       else if (c=='t') // Delayed action 'off' time in ms
       {
           incomingString = Serial.readString();
           toff=incomingString.toInt();
       }
       else if (c=='T') // Delayed action 'on' time in ms
       {
           incomingString = Serial.readString();
           ton=incomingString.toInt();
       }   
       else if ((c=='I') || (c=='i')) // Identify command
       {
           Serial.write('P');
       }
    }
       
    if(digitalRead(PushButton)==LOW) // External push-button pressed?
    {
       delay(50); // Debounce time
       if (digitalRead(PushButton)==LOW)
       {
           Pump(1);
           while(1)
           {
               if(digitalRead(PushButton)==HIGH)
               {
                   delay(50); // Debounce time
                   if(digitalRead(PushButton)==HIGH) break;
               }
           }
           Pump(0);
        }
    }       
}
