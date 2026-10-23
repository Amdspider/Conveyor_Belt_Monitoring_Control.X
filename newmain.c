/*
 * Project: Conveyor Belt Monitoring and Control System
 * Microcontroller: PIC16F877A
 * Compiler: MPLAB X with XC8
 * Clock: 20 MHz crystal
 *
 * Beginner note:
 * This program reads a digital object sensor, drives a motor-driver enable
 * input with PWM, and uses Timer1 to measure how long an object stays at the
 * sensor. If it stays longer than JAM_TIME_MS, the belt stops and a jam is
 * shown on the LCD. The PIC must drive a motor driver, never the motor itself.
 *
 * Pin connections:
 * RB0       Digital IR/proximity sensor output (active LOW by default)
 * RB1       Fault LED (through a current-limiting resistor)
 * RB2       Buzzer driver input
 * RB3       Stop / jam-reset push button (active LOW, external pull-up)
 * RC2/CCP1  PWM output to L293D/L298N enable input
 * RD2       Motor-driver IN1
 * RD3       Motor-driver IN2
 * RD0       LCD RS
 * RD1       LCD E
 * LCD R/W   Connect directly to GND
 * RD4-RD7   LCD D4-D7 (4-bit mode)
 *
 * Timer1 uses the 20 MHz instruction clock (Fosc/4) with a 1:8 prescaler.
 * One timer count is 1.6 us; 625 counts make approximately 1 ms.
 */

#pragma config FOSC = HS
#pragma config WDTE = OFF
#pragma config PWRTE = ON
#pragma config BOREN = OFF
#pragma config LVP = OFF
#pragma config CPD = OFF
#pragma config WRT = OFF
#pragma config CP = OFF

#include <xc.h>
#include <stdio.h>

#define _XTAL_FREQ 20000000UL

/* ----------------------- Changeable project settings -------------------- */
#define MOTOR_SPEED_PERCENT 60u
#define JAM_TIME_MS         5000u
#define SENSOR_ACTIVE_LEVEL 0u

/* ----------------------------- Pin names -------------------------------- */
#define OBJECT_SENSOR RB0
#define FAULT_LED      RB1
#define BUZZER         RB2
#define STOP_BUTTON    RB3
#define LCD_RS         RD0
#define LCD_E          RD1
#define MOTOR_IN1      RD2
#define MOTOR_IN2      RD3

/* Timer1 starts at 65536 - 625 = 64911 = 0xFD8F for a 1 ms interval. */
#define TIMER1_RELOAD_HIGH 0xFDu
#define TIMER1_RELOAD_LOW  0x8Fu

/* These values are shared between the interrupt and the main program. */
volatile unsigned int system_milliseconds = 0;

/* These variables hold the current state of the conveyor program. */
unsigned int object_count = 0;
unsigned int object_start_time = 0;
unsigned char previous_sensor_active = 0;
unsigned char jam_latched = 0;
unsigned char motor_running = 0;
unsigned int last_lcd_update = 0;
char lcd_text[17];

/* =============================== LCD ==================================== */

/* Send one group of four data bits to the LCD using RD4-RD7. */
void lcd_write_nibble(unsigned char value)
{
    PORTD = (PORTD & 0x0Fu) | (value & 0xF0u);
    LCD_E = 1;
    __delay_us(2);
    LCD_E = 0;
    __delay_us(50);
}

/* Send an instruction byte to the LCD. */
void lcd_write_command(unsigned char command)
{
    LCD_RS = 0;
    lcd_write_nibble(command);
    lcd_write_nibble((unsigned char)(command << 4));
    __delay_ms(2);
}

/* Send one character to the LCD. */
void lcd_write_character(char character)
{
    LCD_RS = 1;
    lcd_write_nibble((unsigned char)character);
    lcd_write_nibble((unsigned char)(character << 4));
}

/* Write a zero-terminated text string to the LCD. */
void lcd_write_text(const char *text)
{
    while (*text != '\0')
    {
        lcd_write_character(*text);
        text++;
    }
}

/* Start the LCD in 4-bit, two-line mode. */
void lcd_initialize(void)
{
    __delay_ms(50);
    LCD_RS = 0;
    LCD_E = 0;

    lcd_write_nibble(0x30u);
    __delay_ms(5);
    lcd_write_nibble(0x30u);
    __delay_us(200);
    lcd_write_nibble(0x30u);
    __delay_us(200);
    lcd_write_nibble(0x20u);

    lcd_write_command(0x28u); /* 4-bit interface, 2 display lines */
    lcd_write_command(0x0Cu); /* Display on, cursor off */
    lcd_write_command(0x06u); /* Move cursor right after each character */
    lcd_write_command(0x01u); /* Clear display */
}

/* ============================ PWM motor ================================= */

/* Set the PWM duty cycle. 0 means stopped; 100 means full speed. */
void motor_set_speed(unsigned char speed_percent)
{
    unsigned int duty_value;

    if (speed_percent > 100u)
    {
        speed_percent = 100u;
    }

    /* Timer2 period is 249; the PWM duty register uses four times this value. */
    duty_value = (unsigned int)speed_percent * 4u * (249u + 1u) / 100u;
    CCPR1L = (unsigned char)(duty_value >> 2);
    CCP1CON = (unsigned char)((CCP1CON & 0xCFu) | ((duty_value & 0x03u) << 4));
}

/* Configure CCP1 and Timer2 for approximately 5 kHz PWM at 20 MHz. */
void pwm_initialize(void)
{
    TRISC2 = 0;           /* RC2/CCP1 is an output */
    PR2 = 249u;           /* PWM period register */
    CCP1CON = 0x0Cu;      /* CCP1 in PWM mode */
    T2CON = 0x05u;        /* Timer2 ON, prescaler 1:4, postscaler 1:1 */
    motor_set_speed(0u);  /* Start safely with zero motor duty */
}

/* Turn the motor driver on or off without changing its selected speed. */
void conveyor_set_running(unsigned char should_run)
{
    if (should_run != 0u)
    {
        motor_set_speed(MOTOR_SPEED_PERCENT);
        motor_running = 1u;
    }
    else
    {
        motor_set_speed(0u);
        motor_running = 0u;
    }
}

/* ============================= Timer1 =================================== */

/* Timer1 interrupt: add one millisecond to the software time counter. */
void __interrupt() timer1_interrupt(void)
{
    if (PIR1bits.TMR1IF != 0)
    {
        TMR1H = TIMER1_RELOAD_HIGH;
        TMR1L = TIMER1_RELOAD_LOW;
        PIR1bits.TMR1IF = 0;
        system_milliseconds++;
    }
}

/* Start Timer1 and enable its interrupt. */
void timer1_initialize(void)
{
    T1CON = 0x30u;        /* Timer1 off, internal clock, prescaler 1:8 */
    TMR1H = TIMER1_RELOAD_HIGH;
    TMR1L = TIMER1_RELOAD_LOW;
    PIR1bits.TMR1IF = 0;
    PIE1bits.TMR1IE = 1;
    INTCONbits.PEIE = 1;
    INTCONbits.GIE = 1;
    T1CONbits.TMR1ON = 1;
}

/* Safely copy the 16-bit timer value while the interrupt is paused. */
unsigned int timer1_get_milliseconds(void)
{
    unsigned int copy;
    unsigned char interrupts_were_enabled = INTCONbits.GIE;

    INTCONbits.GIE = 0;
    copy = system_milliseconds;
    INTCONbits.GIE = interrupts_were_enabled;
    return copy;
}

/* ========================= Object and jam logic ========================== */

/* Return 1 when the sensor says an object is present, otherwise return 0. */
unsigned char object_is_present(void)
{
    return (OBJECT_SENSOR == SENSOR_ACTIVE_LEVEL) ? 1u : 0u;
}

/* Read the sensor, count arriving objects, and detect a long-lasting object. */
void update_object_and_jam_status(void)
{
    unsigned char sensor_active = object_is_present();
    unsigned int current_time = timer1_get_milliseconds();

    /* Count only the change from clear to blocked, not every loop. */
    if ((sensor_active != 0u) && (previous_sensor_active == 0u))
    {
        object_count++;
        object_start_time = current_time;
    }

    /* If the object leaves, the next object gets a fresh timing period. */
    if (sensor_active == 0u)
    {
        object_start_time = current_time;
    }

    /* A jam remains latched until STOP is pressed after the sensor clears. */
    if ((sensor_active != 0u) && (jam_latched == 0u))
    {
        if ((unsigned int)(current_time - object_start_time) >= JAM_TIME_MS)
        {
            jam_latched = 1u;
        }
    }

    previous_sensor_active = sensor_active;
}

/* ========================= LCD and indicators ============================ */

/* Show belt state and object count on row one, speed and jam state on row two. */
void display_status(void)
{
    lcd_write_command(0x80u);

    if (jam_latched != 0u)
    {
        sprintf(lcd_text, "BELT:JAM OBJ:%03u", object_count % 1000u);
    }
    else if (STOP_BUTTON == 0)
    {
        sprintf(lcd_text, "STOPPED OBJ:%03u", object_count % 1000u);
    }
    else
    {
        sprintf(lcd_text, "BELT:RUN OBJ:%03u", object_count % 1000u);
    }
    lcd_write_text(lcd_text);

    lcd_write_command(0xC0u);
    if (jam_latched != 0u)
    {
        lcd_write_text("STOP:PRESS RESET");
    }
    else
    {
        sprintf(lcd_text, "SPD:%03u%% JAM:OFF", MOTOR_SPEED_PERCENT);
        lcd_write_text(lcd_text);
    }
}

/* Set the LED and buzzer whenever a jam has been detected. */
void update_fault_outputs(void)
{
    if (jam_latched != 0u)
    {
        FAULT_LED = 1;
        BUZZER = 1;
    }
    else
    {
        FAULT_LED = 0;
        BUZZER = 0;
    }
}

/* ================================ Main =================================== */

void main(void)
{
    unsigned char sensor_active;
    unsigned int current_time;

    /* Disable analog functions on PORTA and PORT E; pins are digital here. */
    ADCON1 = 0x06u;

    /* Configure the object sensor and button as inputs; indicators as outputs. */
    TRISB = 0x09u; /* RB0 sensor input, RB3 button input */
    PORTB = 0x00u;

    /* UART pins are not used in this project; RC2 is the PWM output. */
    TRISC = 0x00u;
    PORTC = 0x00u;

    /* RD0-RD3 are controls/direction; RD4-RD7 connect to LCD data. */
    TRISD = 0x00u;
    PORTD = 0x00u;

    /* Run the motor in one direction through an H-bridge driver. */
    MOTOR_IN1 = 1;
    MOTOR_IN2 = 0;
    FAULT_LED = 0;
    BUZZER = 0;

    lcd_initialize();
    pwm_initialize();
    timer1_initialize();

    lcd_write_command(0x80u);
    lcd_write_text("CONVEYOR SYSTEM ");
    lcd_write_command(0xC0u);
    lcd_write_text("Starting...     ");
    __delay_ms(1000);

    while (1)
    {
        update_object_and_jam_status();

        sensor_active = object_is_present();

        /* Press STOP to halt the belt. After a jam, clear the sensor first,
         * then press STOP to acknowledge the jam. Releasing resumes operation. */
        if ((jam_latched != 0u) && (STOP_BUTTON == 0) && (sensor_active == 0u))
        {
            jam_latched = 0u;
        }

        if ((jam_latched == 0u) && (STOP_BUTTON != 0))
        {
            conveyor_set_running(1u);
        }
        else
        {
            conveyor_set_running(0u);
        }

        update_fault_outputs();

        /* Refresh the LCD five times per second. */
        current_time = timer1_get_milliseconds();
        if ((unsigned int)(current_time - last_lcd_update) >= 200u)
        {
            last_lcd_update = current_time;
            display_status();
        }

        __delay_ms(10);
    }
}
