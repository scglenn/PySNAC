# Example using a character LCD plate.
import time

import Adafruit_CharLCD as LCD


# Initialize the LCD using the pins
lcd = LCD.Adafruit_CharLCDPlate()
#Setting the LCD to Green
lcd.set_color(0.0, 1.0, 0.0)  



#make a couple checkmarks
#normal checkmark; call with '\x01'
lcd.create_char(1,[0,1,3,22,28,8,0,0])
#shaded checkmark; call with '\x02'
lcd.create_char(2,[31,31,28,9,3,23,31,31])
#make a list of characters to scroll through
characters = ['0','1','2','3','4','5','6',
                     '7','8','9','.','!','?',' ',  #space is 13
                     'A','B','C','D','E','F','G',
                     'H','I','J','K','L','M','N',
                     'O','P','Q','R','S','T','U',
                     'V','W','X','Y','Z','(',')']

#For keeping track of what user typed (Stores char index in characters array
user_phrase = []

#For exiting the while loop
gotValue = True
#For keep track of your current character default to space
currChar = 13
#For keeping track of LCD pos
position = 0 

#(Private) returns converted user entered phrase as a string
def getPhrase(phrase,chars):
    output = []
    for val in phrase:
        output.append(chars[val])
    return ''.join(output).rstrip()

#(Public) for incrementing a counter within set bounds with rollover
#Inputs : pos = "The current value of the index in what is being scrolled through
#         max_val = "The maximum possible index value
#Outputs : updated pos
def scroll_up(pos,max_val):
    if (pos == max_val):
        pos = 0
    else:
        pos = pos + 1
    return pos

#(Public) for decrementing a counter within set of bounds with rollover
#Inputs : pos = "The current value of the index in what is being scrolled through
#         max_val = "The maximum possible index value
#Outputs : updated pos
def scroll_down(pos,max_val):
    if (pos == 0):
        pos = max_val
    else:
        pos = pos - 1
    return pos

    

#(Private) for determining what char shows up when cursor moves left or right 
def getChar(pos,phrase):
    if(pos == 0 and (pos >= len(phrase))):
       return 13
    elif(pos == len(phrase)):
       return phrase[pos-1]
    else:
        return phrase[pos]


menu = ['Enter String','See old String']    

scroll = 0
lcd.show_cursor(True)
lcd.home
lcd.message('\x01')
lcd.set_cursor(1,0)
lcd.message(menu[scroll])
scroll = scroll_up(scroll,1)
lcd.set_cursor(1,1)
lcd.message(menu[scroll])
while True:
    
    if(lcd.is_pressed(LCD.UP)):
        scroll=scroll_up(scroll,1)
        lcd.clear()
        lcd.home
        lcd.set_cursor(1,0)
        lcd.message(menu[scroll])
        scroll=scroll_up(scroll,1)
        lcd.set_cursor(1,1)
        lcd.message(menu[scroll])
        lcd.set_cursor(0,1)
        lcd.message('\x01')
        lcd.set_cursor(0,1)
    elif(lcd.is_pressed(LCD.DOWN)):    
        scroll= scroll_down(scroll,1)
        lcd.clear()
        lcd.home
        lcd.set_cursor(1,0)
        lcd.message(menu[scroll])
        scroll = scroll_down(scroll,1)
        lcd.set_cursor(1,1)
        lcd.message(menu[scroll])
        lcd.set_cursor(0,1)
        lcd.message('\x01')
        lcd.set_cursor(0,1)
    elif lcd.is_pressed(LCD.SELECT):
        if(scroll == 0):
           ########### beginning of grabbing user input ###########
            lcd.home()
            lcd.clear()
            lcd.message('Hit Select on \x01')
            time.sleep(0.3)
            lcd.set_cursor(1,1)
            lcd.message('When Finished')
            time.sleep(1)
            lcd.clear()
            lcd.set_cursor(15,0)
            lcd.message('\x01')
            lcd.home()
            
            while gotValue:
                #Loop for entering somthing in the LCD

                #grab next char
                if (lcd.is_pressed(LCD.UP) and position <15):
                    currChar = scroll_up(currChar,41)
                    lcd.message(characters[currChar])
                    lcd.set_cursor(position,0)
                    time.sleep(0.2)
                    
                #grab previous char    
                elif (lcd.is_pressed(LCD.DOWN) and position <15):
                    currChar = scroll_down(currChar,41)
                    lcd.message(characters[currChar])
                    lcd.set_cursor(position,0)
                    time.sleep(0.2)
                    
                #Move cursor right and store prev character  
                elif lcd.is_pressed(LCD.RIGHT):             #move right
                    position = scroll_up(position,15)             
                    lcd.set_cursor(position,0)
                    if((position<15) and (position-1 <= len(user_phrase))):
                        if(position-1 == len(user_phrase)):
                            user_phrase.append(currChar) 
                        elif(position-1 < len(user_phrase) and position > 0):
                            user_phrase[position-1] = currChar              #save last char
                        currChar = getChar(position,user_phrase)
                        lcd.message(characters[currChar])
                        lcd.set_cursor(position,0)
                    time.sleep(0.2)
                    
                #move cursor left
                elif lcd.is_pressed(LCD.LEFT):
                    position = scroll_down(position,15)
                    lcd.set_cursor(position,0)
                    if((position<14) and (position <= len(user_phrase))):
                        currChar = user_phrase[position]
                        lcd.message(characters[currChar])
                        lcd.set_cursor(position,0)
                    time.sleep(0.2)
                #if cursor on checkmark, save user input string
                elif lcd.is_pressed(LCD.SELECT):
                    if position == 15:
                        gotValue = False
                    time.sleep(0.2)
                        
            ########## End of grabbing user input############

            lcd.clear()
            lcd.home()
            lcd.show_cursor(False)
            lcd.message('User entered')
            lcd.set_cursor(0,1)
            lcd.message(getPhrase(user_phrase,characters))
            time.sleep(1.5)
            gotValue = True
            lcd.set_cursor(1,0)
            lcd.message(menu[scroll])
            scroll=scroll_up(scroll,2)
            lcd.set_cursor(1,1)
            lcd.message(menu[scroll])
            lcd.set_cursor(0,1)
            lcd.message('\x01')
            lcd.set_cursor(0,1)
        elif(scroll == 1):
            lcd.clear()
            lcd.home()
            lcd.show_cursor(False)    
            lcd.message('User String: ')
            lcd.set_cursor(0,1)
            lcd.message(getPhrase(user_phrase,characters))
            time.sleep(1.5)
            lcd.clear()
            lcd.set_cursor(1,0)
            lcd.message(menu[scroll])
            scroll=scroll_up(scroll,2)
            lcd.set_cursor(1,1)
            lcd.message(menu[scroll])
            lcd.set_cursor(0,1)
            lcd.message('\x01')
            lcd.set_cursor(0,1)
        
    

