class MacMouser(object):
    '''
    Handles mouse events on Mac OS X. Developed and tested on OS X 10.11
    '''

    def mouseEvent(self,evt_type,posx,posy):
        theEvent = CGEventCreateMouseEvent(
            None,
            evt_type,
            (posx,posy),
            kCGMouseButtonLeft)
        CGEventPost(kCGHIDEventTap, theEvent)
    #end method mouseEvent

    def mousemove(self,posx,posy):
        self.mouseEvent(kCGEventMouseMoved, posx,posy)
    #end method mousemove

    def leftclick(self,posx,posy):
        # uncomment this line if you want to force the mouse
        # to MOVE to the click location first (I found it was not necessary).
        self.mouseEvent(kCGEventMouseMoved, posx,posy)
        self.mouseEvent(kCGEventLeftMouseDown, posx,posy)
        self.mouseEvent(kCGEventLeftMouseUp, posx,posy)
    #end method leftclick

    def rightclick(self,posx,posy):
        # uncomment this line if you want to force the mouse
        # to MOVE to the click location first (I found it was not necessary).
        self.mouseEvent(kCGEventMouseMoved, posx,posy)
        self.mouseEvent(kCGEventRightMouseDown, posx,posy)
        self.mouseEvent(kCGEventRightMouseUp, posx,posy)
    #end method rightclick

    def shiftrightclick(self,posx,posy,speed=0.1):
        '''
        Shift right clicks using Quartz CoreGraphics. If shift does not appear
        to be
        '''

        CGEventPost(kCGHIDEventTap, CGEventCreateKeyboardEvent(None, 0x38, True))
        time.sleep(speed)
        self.rightclick(posx,posy)
        time.sleep(speed)
        CGEventPost(kCGHIDEventTap, CGEventCreateKeyboardEvent(None, 0x38, False))

    #end method shiftrightclick

    def presskey(self,code,speed=0.1):
        '''
        Uses Quartz CoreGraphics to press key with arg code.
        '''

        CGEventPost(kCGHIDEventTap, CGEventCreateKeyboardEvent(None, code, True))
        time.sleep(speed)
        CGEventPost(kCGHIDEventTap, CGEventCreateKeyboardEvent(None, code, False))

    # old/dev functions
    def _dev_get_pos(self):
        '''
        Returns (x,y) current position of the mouse using pyautogui.
        '''
        return pyautogui.position()
    #end method get_pos

    def _old_shiftrightclick(self,posx,posy):
        '''
        Shift right clicks using pyautogui.
        '''

        pyautogui.keyDown('shift')
        pyautogui.press('right')
        pyautogui.keyUp('shift')

    #end method _old_shiftrightclick

#end class MacMouser

class WinMouser(object):
    '''
    Handles mouse events on Windows 10. Developed and tested on Windows
    10.*******
    '''

    def get_pos(self):
        '''
        Returns (x,y) current position of the mouse using pyautogui.
        '''
        #return pyautogui.position()
        pass
    #end method get_pos

    def mousemove(self,posx,posy):
        pass
        #self.mouseEvent(kCGEventMouseMoved, posx,posy)
    #end method mousemove

    def leftclick(self,posx,posy):
        pass
    #end method leftclick

    def rightclick(self,posx,posy):
        pass
    #end method rightclick

#end class MacMouser
