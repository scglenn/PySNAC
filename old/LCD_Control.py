import time
#This is a class for use in conjunction with the Adafruit_CharLCD library
# given an input list of possible characters
class LCD_Control:
    # Initialize the LCD using the pins
    
    #make a list of characters to scroll through   (I MAY KEEP AS PARAMETER)
    characters = ['0','1','2','3','4','5','6',
                         '7','8','9','.','!','?',' ',  #space is 13
                         'A','B','C','D','E','F','G',
                         'H','I','J','K','L','M','N',
                         'O','P','Q','R','S','T','U',
                         'V','W','X','Y','Z','(',')']

    
#Constructor for initializing an instance of LCD_Control
    def __init__(self,LCD):
        self.LCD = LCD
        self.lcd = LCD.Adafruit_CharLCDPlate()
    #make a couple checkmarks
    #normal checkmark; call with '\x01'
        self.lcd.create_char(1,[0,1,3,22,28,8,0,0])
    #shaded checkmark; call with '\x02'
        self.lcd.create_char(2,[31,31,28,9,3,23,31,31])
    #For keeping track of what user typed (Stores char index in characters array
        self.user_phrase = []
    #For exiting the while loop
        self.gotValue = True
    #For keep track of your current character default to space
        self.currChar = 13
    #For keeping track of LCD pos
        self.position = 0
    #For ending the call when the other user hangs up
        self.callOver = False
        
#(Private) returns converted user entered phrase as a string
    def getPhrase(self):
        output = []
        for val in self.user_phrase:
            output.append(self.characters[val])
        return ''.join(output).rstrip()


#(Public) for incrementing a counter within set bounds with rollover
#Inputs : pos = "The current value of the index in what is being scrolled through
#         max_val = "The maximum possible index value
#Outputs : updated pos
    def scroll_up(self,pos,max_val):
        if (pos == max_val):
            pos = 0
        else:
            pos = pos + 1
        return pos


#(Public) for decrementing a counter within set of bounds with rollover
#Inputs : pos = "The current value of the index in what is being scrolled through
#         max_val = "The maximum possible index value
#Outputs : updated pos
    def scroll_down(self,pos,max_val):
        if (pos == 0):
            pos = max_val
        else:
            pos = pos - 1
        return pos

#(Private) for determining what char shows up when cursor moves left or right
#Inputs : pos = "The current value of the index in what is being scrolled through
#         phrase = "The list that is storing the current user input phrase"
#Outputs : The designated char (either the one used previously or a space if nothing)
    def getChar(self,pos,phrase):
        if(pos == 0 and (pos >= len(phrase))):
           return 13
        elif(pos == len(phrase)):
           return phrase[pos-1]
        else:
            return phrase[pos]
        
#(Public) Gets user input from LCD and buttons
#Outputs : String input by the user
    def getUserInputInit(self):
        self.lcd.home()
        self.lcd.clear()
        #self.lcd.message('Hit Select on \x01')
        self.lcd.message('This is PySNAC')   #
        time.sleep(0.3)
        self.lcd.set_cursor(1,1)        #
        #self.lcd.message('When Finished')
        self.lcd.message('by !False')
        time.sleep(1)
        self.lcd.clear()
        self.lcd.message('Hit Select to')  #
        self.lcd.set_cursor(15,0)
        self.lcd.message('\x01')
        self.lcd.set_cursor(1,1)        #
        self.lcd.message('make a call')  #
        self.lcd.set_cursor(15,0)           #
        #self.lcd.home()
        self.lcd.show_cursor(True)
        while True:
            #Loop for entering somthing in the LCD
            #grab next char
            if (self.lcd.is_pressed(self.LCD.UP) and self.position <15):
                self.currChar = self.scroll_up(self.currChar,len(self.characters)-1)
                self.lcd.message(self.characters[self.currChar])
                self.lcd.set_cursor(self.position,0)
                time.sleep(0.2)
                
            #grab previous char    
            elif (self.lcd.is_pressed(self.LCD.DOWN) and self.position <15):
                self.currChar = self.scroll_down(self.currChar,41)
                self.lcd.message(self.characters[self.currChar])
                self.lcd.set_cursor(self.position,0)
                time.sleep(0.2)
                
            #Move cursor right and store prev character  
            elif self.lcd.is_pressed(self.LCD.RIGHT):             #move right
                self.position = self.scroll_up(self.position,15)             
                self.lcd.set_cursor(self.position,0)
                if((self.position<15) and (self.position-1 <= len(self.user_phrase))):
                    if(self.position-1 == len(self.user_phrase)):
                        self.user_phrase.append(self.currChar) 
                    elif(self.position-1 < len(self.user_phrase) and self.position > 0):
                        self.user_phrase[self.position-1] = self.currChar              #save last char
                    self.currChar = self.getChar(self.position,self.user_phrase)
                    self.lcd.message(self.characters[self.currChar])
                    self.lcd.set_cursor(self.position,0)
                time.sleep(0.2)
                
            #move cursor left
            elif self.lcd.is_pressed(self.LCD.LEFT):
                self.position = self.scroll_down(self.position,15)
                self.lcd.set_cursor(self.position,0)
                if((self.position<14) and (self.position <= len(self.user_phrase))):
                    self.currChar = self.user_phrase[self.position]
                    self.lcd.message(self.characters[self.currChar])
                    self.lcd.set_cursor(self.position,0)
                time.sleep(0.2)
            #if cursor on checkmark, save user input string
            elif self.lcd.is_pressed(self.LCD.SELECT):
                if self.position == 15:
                    self.gotValue = False
                time.sleep(0.2)
                return self.getPhrase()

#(Public): displays for call in progress
    def displayUserInputDuringCall(self):
        self.lcd.clear()
        self.lcd.message('Connected. Hit')
        self.lcd.set_cursor(1,1)
        self.lcd.message('Select to end')
        self.lcd.set_cursor(15,1)
        self.lcd.message('\x01')
        self.lcd.set_cursor(15,1)           #
        self.lcd.show_cursor(True)

#(Public): displays call in progress
    def getUserInput(self):
        while True:
            if self.lcd.is_pressed(self.LCD.SELECT) or self.callOver:
                return True

#(Public): brief display that call ended
    def displayEndMessage(self):
        self.lcd.clear()
        self.lcd.message('Call ended.')
        self.lcd.set_cursor(0,1)
        self.lcd.message('Please power off')
        self.callOver = True
        
