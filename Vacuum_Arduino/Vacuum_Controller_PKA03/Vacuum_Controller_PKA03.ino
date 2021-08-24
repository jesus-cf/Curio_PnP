// Connections:
// Terminal connector 1: Solenoid Valve +
// Terminal connector 2: Solenoid Valve -
// Terminal connector 4: Vacuum +
// Terminal connector 3: Vacuum -
#define Vacuum 9 
#define Vacuum_Dir 8 
#define Valve 3
#define Valve_Dir 2
#define PushButton 12
#define uServo 5

#define ISR_FREQ 100000L // Interrupt service routine tick is 10 us
#define OCR1_RELOAD ((F_CPU/ISR_FREQ)-1) // must be <65536

volatile int ISR_cnt=0;
volatile unsigned char TickFlag=0; // Assuming access to unsigned char is atomic!
volatile unsigned char ISR_us_cnt=0;
volatile unsigned char ISR_pw=150;
volatile unsigned int ton_cnt=5000, toff_cnt=5000, vent_cnt=5000, ang_cnt=5000;

// 'Timer 1 output compare A' Interrupt Service Routine
// This ISR happens at a rate of 100kHz.  It is used
// to generate the standard servo 50Hz signal with
// a pulse width of 0.5ms to 2.5ms.
ISR(TIMER1_COMPA_vect)
{
  ISR_cnt++;
  if(ISR_cnt==ISR_pw)
  {
    digitalWrite(uServo, LOW); // WARNING: digitalWrite() takes a long time to execute
  }
  if(ISR_cnt>=2000)
  {
    digitalWrite(uServo, HIGH);
    ISR_cnt=0; // 2000 * 10us = 20ms
  }
  
  ISR_us_cnt++;
  if(ISR_us_cnt==100) // one mili second has passed
  {
    ISR_us_cnt=0;
    if(ton_cnt<5000) ton_cnt++;
    if(toff_cnt<5000) toff_cnt++;
    if(vent_cnt<5000) vent_cnt++;
    if(ang_cnt<5000) ang_cnt++;
    TickFlag=1;
  }
}

// The next two functions allow for safe access to volatile integers without disabling interrupts.

void Set_Volatile (unsigned int value, unsigned int * ptr)
{
  do {
    TickFlag=0;
    *ptr=value;
  } while (TickFlag==1);
}

unsigned int Get_Volatile (unsigned int * ptr)
{
  unsigned int value;
  do {
    TickFlag=0;
    value=*ptr;
  } while (TickFlag==1);
  return value;
}

void setup()
{
    Serial.begin(115200); // opens serial port, sets data rate to 115200 bps
    Serial.setTimeout(1000); // One second for serial timeout

    pinMode(Vacuum, OUTPUT);
    pinMode(Vacuum_Dir, OUTPUT);
    pinMode(Valve, OUTPUT);
    pinMode(Valve_Dir, OUTPUT);
    pinMode(uServo, OUTPUT);
    pinMode(PushButton, INPUT_PULLUP); // To manually turn the vacuum pump on

    digitalWrite(Vacuum, LOW); // Vacuum pump off
    digitalWrite(Vacuum_Dir, LOW);
    digitalWrite(Valve, LOW);  // Vent valve closed
    digitalWrite(Valve_Dir, LOW);

    cli();// disable global interupt
    TCCR1A = 0;
    TCCR1B = 0;
    TCNT1  = 0;   
    OCR1A = OCR1_RELOAD; // Set compare match register for 100khz increments
    TCCR1B |= (1 << WGM12); // Turn on CTC mode   
    TCCR1B |= (1 << CS10); // Set CS10 bit for 1 prescaler  
    TIMSK1 |= (1 << OCIE1A); // Enable timer compare interrupt    
    sei(); // enable global interupt
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
        Set_Volatile(0, &vent_cnt); // After some time vent output is set to low turning vent valve off
    }
}

void loop()
{ 
   // If these variables are not 'static' they will initialized everytime loop() is re-run
   static int c = 0; // for incoming serial data
   static int ton=0, toff=0, vent=250, ang=200;
   static int uServo_min=55, uServo_max=230;
   static int temp, angle, new_ISR_pw;
   String incomingString;

   if (Serial.available() > 0)
   {  
       c = Serial.read(); // read the incoming byte
       
       if(c=='0') // Vacuum off
       {
           Set_Volatile(0, &toff_cnt);
       }
       else if (c=='1') // Vacuum on
       {
           Set_Volatile(0, &ton_cnt);
       }
       else if (c=='t') // Delayed action 'off' time in ms
       {
           incomingString = Serial.readStringUntil('\n');
           toff=incomingString.toInt();
       }
       else if (c=='T') // Delayed action 'on' time in ms
       {
           incomingString = Serial.readStringUntil('\n');
           ton=incomingString.toInt();
       }
       else if (c=='v') // vent time
       {
           incomingString = Serial.readStringUntil('\n');
           vent=incomingString.toInt();
       }   
       else if (c=='X') // servo action delay time
       {
           incomingString = Serial.readStringUntil('\n');
           ang=incomingString.toInt();
       }   
       else if ( (c=='S') || (c=='s') ) // Servo
       {
           incomingString = Serial.readStringUntil('\n');
           angle=incomingString.toInt();
           if(angle<40) angle=40;
           if(angle>250) angle=250;
           ISR_pw=angle;
       }
       else if ( (c=='Z') || (c=='z') )
       {
           while(1)
           {
               for (temp=uServo_min; temp<uServo_max; temp++)
               {
                   if (Serial.available() > 0) break;
                   ISR_pw=temp;
                   delay(10);
               }
               for (temp=uServo_max; temp>uServo_min; temp--)
               {
                   if (Serial.available() > 0) break;
                   ISR_pw=temp;
                   delay(10);
               }
               if(Serial.available() > 0) break;
           }
       }
       else if ( (c=='A') || (c=='a') ) // Angle
       {
           incomingString = Serial.readStringUntil('\n');
           angle=incomingString.toInt();
           if (angle>180) angle=180;
           if (angle<0) angle=0;
           new_ISR_pw=(((180.0-(float)angle)*(float)(uServo_max-uServo_min))/180.0)+(float)uServo_min; // Do multiplication first
           Set_Volatile(0, &ang_cnt);
       }   
       else if (c=='M') // Max, the servo value that sets the angle to 0 deg
       {
           incomingString = Serial.readStringUntil('\n');
           uServo_max=incomingString.toInt();
           if (uServo_max<40) uServo_max=40;     
           if (uServo_max>250) uServo_max=250;     
       }   
       else if (c=='m') // min, the servo value that sets the angle to 180 deg
       {
           incomingString = Serial.readStringUntil('\n');
           uServo_min=incomingString.toInt();
           if (uServo_min<40) uServo_min=40;     
           if (uServo_min>250) uServo_min=250;     
       }
       else if ((c=='I') || (c=='i')) // Identify command
       {
           Serial.write('P');
       }
    }

    temp=Get_Volatile(&toff_cnt);
    if((temp>toff) && (temp<5000))
    {
      Set_Volatile(5000, &toff_cnt);
      Pump(0);
    }
    
    temp=Get_Volatile(&ton_cnt);
    if((temp>ton) && (temp<5000))
    {
      Set_Volatile(5000, &ton_cnt);
      Pump(1);
    }

    temp=Get_Volatile(&vent_cnt);
    if((temp>vent) && (temp<5000))
    {
      Set_Volatile(5000, &vent_cnt);
      digitalWrite(Valve, LOW); // Vent valve is closed
    }

    temp=Get_Volatile(&ang_cnt);
    if((temp>ang) && (temp<5000))
    {
      Set_Volatile(5000, &ang_cnt);
      ISR_pw=new_ISR_pw;
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
