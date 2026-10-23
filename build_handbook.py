"""Build the student handbook PDF with ReportLab."""
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph,
    Spacer, Table, TableStyle, PageBreak, Preformatted, Flowable)

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "output" / "pdf" / "Conveyor_Belt_Monitoring_Control_Handbook.pdf"
NAVY, BLUE = colors.HexColor("#142B4A"), colors.HexColor("#1769AA")
TEAL, GOLD = colors.HexColor("#0D9488"), colors.HexColor("#E6A52E")
PALE, INK = colors.HexColor("#EEF5FB"), colors.HexColor("#18324B")
MUTED, RED, GREEN = colors.HexColor("#536579"), colors.HexColor("#B9473E"), colors.HexColor("#27835A")
W = A4[0] - 36 * mm
S = getSampleStyleSheet()
S.add(ParagraphStyle(name="Cover", parent=S["Title"], fontName="Helvetica-Bold", fontSize=27,
    leading=32, textColor=NAVY, alignment=0, spaceAfter=5*mm))
S.add(ParagraphStyle(name="H1x", parent=S["Heading1"], fontName="Helvetica-Bold", fontSize=19,
    leading=23, textColor=NAVY, spaceAfter=3*mm))
S.add(ParagraphStyle(name="H2x", parent=S["Heading2"], fontName="Helvetica-Bold", fontSize=11.5,
    leading=14, textColor=BLUE, spaceBefore=2*mm, spaceAfter=1.5*mm))
S.add(ParagraphStyle(name="Bodyx", parent=S["BodyText"], fontSize=9, leading=12.4,
    textColor=INK, spaceAfter=2*mm))
S.add(ParagraphStyle(name="Smallx", parent=S["BodyText"], fontSize=7.8, leading=9.7, textColor=INK))
S.add(ParagraphStyle(name="Thx", parent=S["BodyText"], fontName="Helvetica-Bold", fontSize=7.8,
    leading=9.5, textColor=colors.white))
S.add(ParagraphStyle(name="Callx", parent=S["BodyText"], fontSize=8.6, leading=12, textColor=INK))

def P(t, s="Bodyx"):
    return Paragraph(t, S[s])

def H(n, t, sub=None):
    a = [P(f'<font color="#0D9488">{n}</font>  {t}', "H1x")]
    if sub: a.append(P(sub))
    return a

def T(rows, widths, header=True):
    data = [[P(str(x), "Thx" if header and i == 0 else "Smallx") for x in row] for i, row in enumerate(rows)]
    t = Table(data, colWidths=widths, repeatRows=1 if header else 0, hAlign="LEFT")
    ts = [("VALIGN",(0,0),(-1,-1),"TOP"),("GRID",(0,0),(-1,-1),.4,colors.HexColor("#D5DFE8")),
          ("LEFTPADDING",(0,0),(-1,-1),5),("RIGHTPADDING",(0,0),(-1,-1),5),
          ("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4),
          ("ROWBACKGROUNDS",(0,1 if header else 0),(-1,-1),[colors.white,PALE])]
    if header: ts.append(("BACKGROUND",(0,0),(-1,0),BLUE))
    t.setStyle(TableStyle(ts)); return t

def note(title, body, color=GOLD):
    t=Table([[P(f"<b>{title}</b><br/>{body}","Callx")]],colWidths=[W])
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),colors.HexColor("#FFF6DF")),
        ("BOX",(0,0),(-1,-1),1,color),("LINEBEFORE",(0,0),(0,-1),4,color),
        ("LEFTPADDING",(0,0),(-1,-1),9),("RIGHTPADDING",(0,0),(-1,-1),8),
        ("TOPPADDING",(0,0),(-1,-1),7),("BOTTOMPADDING",(0,0),(-1,-1),7)])); return t

class Diagram(Flowable):
    def __init__(self): super().__init__(); self.width=W; self.height=58*mm
    def draw(self):
        c=self.canv
        boxes=[(2,34,34,17,"OBJECT","sensor",BLUE),(44,28,52,29,"PIC16F877A","RB0 + Timer1",NAVY),
               (107,34,27,17,"LCD","status",TEAL),(140,34,31,17,"FAULT","LED + buzzer",RED),
               (107,4,64,18,"PWM DRIVER + MOTOR","RC2 / CCP1",GREEN)]
        c.setLineWidth(1.6); c.setStrokeColor(BLUE); c.line(36*mm,42*mm,44*mm,42*mm)
        c.line(96*mm,42*mm,107*mm,42*mm); c.setStrokeColor(RED); c.line(96*mm,42*mm,140*mm,42*mm)
        c.setStrokeColor(GREEN); c.line(96*mm,34*mm,107*mm,18*mm)
        for x,y,w,h,a,b,col in boxes:
            c.setFillColor(col); c.roundRect(x*mm,y*mm,w*mm,h*mm,2*mm,fill=1,stroke=0)
            c.setFillColor(colors.white); c.setFont("Helvetica-Bold",7.5); c.drawCentredString((x+w/2)*mm,(y+h*.62)*mm,a)
            c.setFont("Helvetica",6.5); c.drawCentredString((x+w/2)*mm,(y+h*.30)*mm,b)
        c.setFillColor(MUTED); c.setFont("Helvetica",6.5); c.drawString(108*mm,1*mm,"Motor current comes from the driver, not the PIC")

class Doc(BaseDocTemplate):
    def __init__(self,path):
        super().__init__(path,pagesize=A4,title="PIC16F877A Conveyor Belt Monitoring and Control Handbook",
                         author="Educational PIC16F877A project")
        f=Frame(18*mm,18*mm,A4[0]-36*mm,A4[1]-37*mm,leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)
        self.addPageTemplates([PageTemplate(id="all",frames=[f],onPage=self.chrome)])
    def chrome(self,c,d):
        c.saveState(); pw,ph=A4
        if d.page>1:
            c.setFillColor(NAVY); c.rect(0,ph-13*mm,pw,13*mm,fill=1,stroke=0)
            c.setFillColor(colors.white); c.setFont("Helvetica-Bold",8); c.drawString(18*mm,ph-8.5*mm,"PIC16F877A  |  CONVEYOR BELT MONITOR")
        c.setStrokeColor(colors.HexColor("#D9E3ED")); c.line(18*mm,14*mm,pw-18*mm,14*mm)
        c.setFillColor(MUTED); c.setFont("Helvetica",7.5); c.drawString(18*mm,9*mm,"Student handbook  |  20 MHz  |  MPLAB X + XC8")
        c.drawRightString(pw-18*mm,9*mm,f"Page {d.page}"); c.restoreState()

def code(txt):
    st=ParagraphStyle("code",fontName="Courier",fontSize=7.1,leading=9,textColor=INK,
       backColor=PALE,borderColor=colors.HexColor("#D5DFE8"),borderWidth=.5,borderPadding=6,
       leftIndent=5,rightIndent=5,spaceBefore=1.5*mm,spaceAfter=2.5*mm)
    return Preformatted(txt.strip(),st)

story=[]
# Cover
story += [Spacer(1,20*mm),P("PIC16F877A","H2x"),P("Conveyor Belt<br/>Monitoring &amp; Control","Cover"),
 P("A beginner-friendly guide to object sensing, PWM motor control, Timer1, and jam shutdown.","Bodyx"),
 Spacer(1,5*mm),Diagram(),Spacer(1,8*mm),
 T([["WHAT YOU WILL LEARN","HOW THE EXAMPLE BEHAVES"],
   ["Digital inputs, port direction, LCD, PWM, timer interrupts, and a simple jam response.",
    "Count an arriving object. If it stays at the checkpoint too long, stop PWM and latch a fault."],["CLOCK","PROJECT FILE"],
   ["20 MHz crystal / _XTAL_FREQ","newmain.c | PIC16F877A | MPLAB X / XC8"]],[87*mm,87*mm]),
 Spacer(1,7*mm),note("Project scope","This is a classroom example, not a certified safety controller. Match the Proteus or hardware clock to 20 MHz."),PageBreak()]
# 1 overview
story += H("01","Project overview","The program supervises one conveyor checkpoint using a PIC16F877A.")
story += [P("A digital IR/proximity module tells the PIC whether an object is at the sensor. CCP1 creates PWM for a motor driver. Timer1 measures how long the sensor stays blocked. If the object lingers, the firmware stops PWM, shows a jam, and turns on fault outputs."),
 T([["INPUT / OUTPUT","JOB"],["RB0 sensor","Detect object present (active LOW by default)."],
 ["Timer1 interrupt","Build an approximate millisecond counter."],["RC2 / CCP1 PWM","Set motor-driver enable duty; default is 60%."],
 ["LCD, RB1, RB2","Show state and indicate a jam."],["RB3 button","Stop belt; acknowledge jam only after sensor clears."]],[47*mm,127*mm]),
 P("Main-loop sequence","H2x"),T([["STEP","PROGRAM ACTION"],["1","Read the sensor and detect a clear-to-blocked transition."],
 ["2","Increment object count once and remember start time."],["3","Compare elapsed time with JAM_TIME_MS (5,000 ms by default)."],
 ["4","Latch a jam; otherwise run unless STOP is held."],["5","Update fault outputs and refresh the LCD about every 200 ms."]],[22*mm,152*mm]),
 Spacer(1,3*mm),note("Safety","The RB3 push-button is not an emergency stop. Real conveyors require guards and independent safety-rated shutdown controls.",RED),PageBreak()]
# 2 wiring
story += H("02","Wiring and PIC pins","Connect as shown by the source. Confirm sensor polarity before operation.")
story += [T([["PIC PIN","SIGNAL","CONNECTION / NOTE"],["RB0","Object sensor","Digital output; active LOW by default."],
 ["RB1","Fault LED","Use a series current-limiting resistor."],["RB2","Buzzer","Use a transistor or driver module."],
 ["RB3","Stop / acknowledge","Button to GND; external pull-up required."],["RC2/CCP1","PWM","Connect to motor-driver enable/PWM input."],
 ["RD2, RD3","IN1, IN2","Direction inputs; source selects one direction."],["RD0, RD1","LCD RS, E","LCD control."],
 ["RD4-RD7","LCD D4-D7","4-bit data bus; LCD R/W tied to GND."],["VSS / VDD","PIC supply","Use correct regulated supply; share logic ground."]],
 [26*mm,33*mm,115*mm]),P("Signal path","H2x"),
 T([["SENSOR OUT","RB0"],["RC2 PWM","Driver EN/PWM"],["RD2 + RD3","Driver IN1 + IN2"],
 ["Driver OUT","Low-voltage DC motor"],["LCD","RS=RD0, E=RD1, D4-D7=RD4-RD7, R/W=GND"]],[52*mm,122*mm],False),
 Spacer(1,4*mm),note("Motor connection","Never connect a motor directly to a PIC pin. Use a driver rated for motor voltage and current, suitable protection, and a common signal ground.",RED),
 P("Clock and reset wiring","H2x"),
 T([["OSC1 / OSC2","Connect the 20 MHz crystal across the PIC oscillator pins; choose loading capacitors from the crystal and device requirements."],
 ["MCLR / VPP","Keep reset inactive with a pull-up to the PIC supply, following the PIC data sheet."],
 ["Power-up check","Confirm VDD/VSS pins, local decoupling, and common logic ground before enabling the motor driver."]],[36*mm,138*mm],False),PageBreak()]
# 3 registers
story += H("03","Ports and registers","A register is a control or data location inside the PIC.")
story += [T([["REGISTER","PURPOSE","PLAIN-LANGUAGE VIEW"],["TRISB","RB0/RB3 inputs; RB1/RB2 outputs.","Pin direction: 1=input, 0=output."],
 ["PORTB","Read inputs and set output levels.","The pin HIGH/LOW values."],["TRISC2","Set RC2 as PWM output.","Direction of the CCP1 pin."],
 ["TRISD / PORTD","LCD and motor direction signals.","Low bits control, high bits carry LCD data."],["ADCON1","Select digital I/O behavior.","Turns analog-capable pins into digital pins here."],
 ["CCP1CON","Select PWM mode and low duty bits.","Configure CCP to generate pulses."],["PR2 / T2CON","Set PWM period; start Timer2.","Choose pulse repetition rate."],
 ["CCPR1L","Upper PWM duty bits.","Set fraction of the period ON."],["T1CON","Timer1 clock and prescaler.","Choose timer clock, divider, and run state."],
 ["TMR1H / L","Timer1 count and reload.","The 16-bit timer value."],["PIE1 / PIR1","Enable and detect Timer1 event.","Interrupt enable and event flag."],
 ["INTCON","Enable interrupt response.","Master interrupt switches."]],[29*mm,66*mm,79*mm]),
 Spacer(1,4*mm),note("TRISB example","TRISB = 0x09 = 0000 1001 binary. Bits RB0 and RB3 are 1, so they are inputs; other PORTB bits are outputs."),
 P("Read the bit pattern","H2x"),
 T([["BIT","RB7 ... RB4","RB3","RB2","RB1","RB0"],["TRISB","0000","1","0","0","1"],["Meaning","not used here","button input","buzzer output","LED output","sensor input"]],
 [24*mm,31*mm,24*mm,24*mm,24*mm,24*mm]),
 P("Peripheral setup examples","H2x"),
 T([["SETTING","EFFECT"],["ADCON1 = 0x06","Use the shared pins as digital I/O for this design."],
 ["T1CON = 0x30","Timer1 is configured with its internal clock and 1:8 prescaler while initially stopped."],
 ["T1CONbits.TMR1ON = 1","Start Timer1 after loading the counter."],
 ["PIE1bits.TMR1IE = 1","Allow Timer1 overflow to request an interrupt."],
 ["INTCONbits.PEIE / GIE","Enable peripheral and global interrupt handling."]],[56*mm,118*mm]),PageBreak()]
# 4 timing and PWM
story += H("04","Timer1 and PWM calculations","The timing follows from the 20 MHz crystal and the selected prescalers.")
story += [P("Timer1: approximate 1 ms tick","H2x"),T([["CALCULATION","RESULT"],["Oscillator Fosc","20,000,000 cycles/s"],
 ["Instruction clock Fosc / 4","5,000,000 ticks/s"],["Timer1 prescaler","1:8; one count = 8/5,000,000 = 1.6 us"],
 ["Counts per 1 ms","1,000 / 1.6 = 625 counts"],["Preload","65,536 - 625 = 64,911 = 0xFD8F"]],[64*mm,110*mm]),
 P("Timer1 overflows, the interrupt reloads 0xFD8F, then increments system_milliseconds. Five thousand ticks represent about five seconds. ISR execution adds a small timing error."),
 P("CCP1 PWM: approximately 5 kHz","H2x"),code("PWM frequency = Fosc / (4 x Timer2 prescaler x (PR2 + 1))\n               = 20,000,000 / (4 x 4 x 250) = 5,000 Hz\n\nPR2 = 249; Timer2 prescaler = 1:4\nDefault duty = MOTOR_SPEED_PERCENT = 60%"),
 P("The duty helper converts a 0-100 percentage into a 10-bit CCP value. At 0%, no ON time is sent to the driver. At 60%, the PWM signal is ON for about 60% of each cycle. Actual belt speed depends on motor, driver, supply, and load."),
 Spacer(1,4*mm),note("Timing is approximate","This software timebase is suitable for the learning timeout. Precision industrial timing needs measurement and calibration."),
 P("What happens during one timer tick","H2x"),
 T([["1. Count","Timer1 advances at one count per 1.6 us."],["2. Overflow","After 625 counts from the preload, Timer1 sets its interrupt flag."],
 ["3. Interrupt","The CPU briefly runs timer1_interrupt()."],["4. Reload","The handler loads 0xFD8F again and increments system_milliseconds."],
 ["5. Compare","The main loop subtracts object_start_time from current_time."]],[40*mm,134*mm],False),
 P("Example: if an object started at 12,400 ms and the current reading is 16,900 ms, elapsed time is 4,500 ms, so a 5,000 ms jam threshold has not yet been reached. At 17,400 ms, elapsed time is 5,000 ms and the jam is latched."),PageBreak()]
# 5 code walkthrough
story += H("05","Program walkthrough","Follow main(), then open each helper function it calls.")
story += [T([["FUNCTION / SECTION","WHAT IT DOES"],["Settings and pin names","Set 20 MHz, sensor polarity, 60% PWM, jam time, and readable pin aliases."],
 ["LCD functions","Initialize 4-bit mode and send commands/characters."],["motor_set_speed","Convert requested percentage into CCP duty bits."],
 ["pwm_initialize","Set PR2, CCP1 PWM mode, and Timer2."],["conveyor_set_running","Apply selected duty or set duty to zero."],
 ["timer1_interrupt","Reload Timer1 and add one to software time."],["timer1_get_milliseconds","Safely copy the shared 16-bit time value."],
 ["update_object_and_jam_status","Count sensor edges and latch a long detection."],["display_status / update_fault_outputs","Show state and control LED/buzzer."],
 ["main","Configure I/O, start peripherals, repeat the control loop."]],[62*mm,112*mm]),
 P("Jam test, in plain language","H2x"),code("if (sensor_active && !jam_latched)\n{\n    if ((current_time - object_start_time) >= JAM_TIME_MS)\n    {\n        jam_latched = 1;\n    }\n}"),
 P("Elapsed time is current time minus object start time. The jam flag stays set after the sensor clears. It is acknowledged only if RB3 is pressed while the sensor is clear."),
 note("Motor power","RC2 is a logic signal. The external driver switches motor current; the PIC does not power the motor.",RED),
 P("Important program variables","H2x"),
 T([["VARIABLE","PURPOSE"],["system_milliseconds","Volatile time counter updated by Timer1 interrupt."],
 ["object_start_time","Timestamp captured when the sensor first detects an object."],
 ["previous_sensor_active","Remembers the previous sensor state so one object is counted once."],
 ["object_count","Number of clear-to-active transitions; display rolls through 000-999."],
 ["jam_latched","Keeps a jam active until the sensor is clear and STOP is pressed."],
 ["motor_running","Records whether the program has applied nonzero PWM."]],[56*mm,118*mm]),PageBreak()]
# 6 behavior / test
story += H("06","LCD states and safe test sequence","Test sensor and jam behavior before connecting a motor.")
story += [T([["DISPLAY / OUTPUT","MEANING"],["BELT:RUN OBJ:nnn","Belt enabled; object count shown."],
 ["STOPPED OBJ:nnn","RB3 is held low; PWM is off."],["BELT:JAM OBJ:nnn","Dwell threshold exceeded; fault is latched."],
 ["STOP:PRESS RESET","Clear sensor, then press RB3 to acknowledge."],["RB1 + RB2","LED and buzzer outputs on during latched jam."]],[61*mm,113*mm]),
 P("Suggested lab sequence","H2x"),T([["TEST","EXPECTED RESULT"],["Power on with sensor clear","Startup message, then BELT:RUN."],
 ["Block sensor briefly then clear","Object count goes up once; no jam."],["Hold sensor active for over 5 s","PWM stops, JAM appears, LED/buzzer turn on."],
 ["Clear sensor and press RB3","Jam latch clears; releasing button restarts belt."],["Hold RB3 during normal operation","PWM stops and STOPPED is displayed."]],[65*mm,109*mm]),
 P("Before the motor: use simulation or an LED stand-in for PWM. Verify sensor logic polarity, clock setting, LCD wiring, driver logic voltage, common ground, motor current, and driver rating. RB3 is a normal input, not an emergency-stop circuit."),
 P("Jam recovery state","H2x"),
 T([["SENSOR","RB3 BUTTON","RESULT"],["Blocked","Any","Jam remains latched; PWM stays off."],
 ["Clear","Released","Jam remains latched until acknowledged."],["Clear","Pressed (LOW)","Jam latch clears; button still holds the belt stopped."],
 ["Clear","Released again","Belt may run again."]],[43*mm,48*mm,83*mm]),PageBreak()]
# 7 settings and glossary
story += H("07","Settings, common mistakes, glossary","Quick reference while studying or changing the example.")
story += [T([["SETTING","DEFAULT","CHANGE WHEN"],["_XTAL_FREQ","20,000,000UL","Oscillator frequency changes."],
 ["MOTOR_SPEED_PERCENT","60","Choose another 0-100% duty."],["JAM_TIME_MS","5,000","Change allowed object dwell time."],
 ["SENSOR_ACTIVE_LEVEL","0 (LOW)","Sensor output is HIGH during detection."],["Timer1 preload","0xFD8F","Clock or prescaler changes."]],[46*mm,34*mm,94*mm]),
 P("Common mistakes","H2x"),P("- Driving motor/buzzer directly from a PIC pin.<br/>- Forgetting shared ground between PIC and driver logic.<br/>- Wrong sensor active level or missing RB3 pull-up.<br/>- Proteus clock differs from _XTAL_FREQ.<br/>- Assuming 60% PWM means a fixed mechanical speed.<br/>- Treating the button as a safety-rated emergency stop."),
 P("Glossary","H2x"),T([["TERM","MEANING"],["GPIO","General-purpose input/output pin."],
 ["PWM","Pulse-width modulation: ON/OFF pulses with adjustable duty."],["Duty cycle","Percent of a PWM period spent ON."],
 ["Prescaler","Divider that slows a clock before a timer."],["Interrupt","Hardware event that runs a short handler."],
 ["Latch","Stored state that remains until an explicit reset condition."],["H-bridge","Driver circuit that switches motor current and direction."]],[37*mm,137*mm]),
 P("Source and verification note","H2x"),P("This handbook follows newmain.c and explains its intended operation. The firmware has not been compiled or hardware-tested in this handbook workflow. Build it with your MPLAB X / XC8 installation and verify it on a safe setup before use."),
 note("Educational use","Production machinery requires a risk assessment, proper guarding, a safety-rated emergency stop, and independent safety controls.",RED)]

if __name__ == "__main__":
    OUT.parent.mkdir(parents=True,exist_ok=True)
    Doc(str(OUT)).build(story)
    print(OUT)
