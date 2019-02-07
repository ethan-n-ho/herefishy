#!/usr/bin/python

#Essential imports. HereFishy will absolutely not run without these installed
import time, math, os
from mss import mss
import numpy as np

#Necessary for some _dev functions
#from matplotlib import pyplot as plt
#import cv2
#from scipy.spatial import distance

#Import OS specific modules
if os.name == 'posix': #unix systems
    #import pyautogui #should be phased out by now
    from Quartz.CoreGraphics import CGEventCreateMouseEvent, CGEventPost, \
    kCGEventMouseMoved, kCGEventLeftMouseDown, kCGEventLeftMouseDown, \
    kCGEventLeftMouseUp, kCGMouseButtonLeft, kCGHIDEventTap, \
    kCGEventRightMouseDown, kCGEventRightMouseUp, CGEventCreateKeyboardEvent, \
    kCGSessionEventTap
elif os.name == 'nt': #windows systems
    pass
else:
    raise Exception("Operating system not supported. Please run in " + \
                    "Mac OS X or Windows (os.name='" + os.name + "').")

def show_img(img):
    '''
    Dev function to show image
    '''
    
    cv2.imshow('image',img)
    cv2.waitKey()
    cv2.destroyAllWindows()
    
#end function show_img

def is_like_rect(points,ang_range=(70,120)):
    '''
    Given four points as ndarray, determines if the shape is rectangle-like
    by calculating the angle between each of the polygon's sides.
    '''
    pts = np.concatenate([points,points],axis=0)
    for i in range(4):
        s1 = pts[i] - pts[i+1]
        s2 = pts[i+1] - pts[i+2]
        lower = (np.linalg.norm(s1) * np.linalg.norm(s2))
        if lower == 0:
            return False
        try:
            angle = np.degrees(math.acos(np.dot(s1,s2) / lower))
        except ValueError: #math domain error
            return False
        if angle < ang_range[0] or angle > ang_range[1]:
            return False
    return True
    
#end function is_like_rect 

def rect_bounds(pts):
    
    x_min = np.min(pts[:,0])
    x_max = np.max(pts[:,0])
    y_min = np.min(pts[:,1])
    y_max = np.max(pts[:,1])
    return(x_min,x_max,y_min,y_max)
    
#end function rect_bounds

def pts_in_box(query,subject):
    '''
    Determines which pts in query lie inside rectangle defined by
    subject
    '''

    x_min = np.min(subject[:,0])
    x_max = np.max(subject[:,0])
    y_min = np.min(subject[:,1])
    y_max = np.max(subject[:,1])
    return np.array([
        (x_min < pt[0] < x_max) and (y_min < pt[1] < y_max)
        for pt in query
    ])
    
#end function pts_in_box

def sortpts_clockwise(A):
    '''
    Given four 2D points in array A, sorts points clockwise.
    Taken from
    https://stackoverflow.com/questions/30088697/4-1-2-numpy-array-sort-clockwise
    '''
    # Sort A based on Y(col-2) coordinates
    sortedAc2 = A[np.argsort(A[:,1]),:]

    # Get top two and bottom two points
    top2 = sortedAc2[0:2,:]
    bottom2 = sortedAc2[2:,:]

    # Sort top2 points to have the first row as the top-left one
    sortedtop2c1 = top2[np.argsort(top2[:,0]),:]
    top_left = sortedtop2c1[0,:]

    # Use top left point as pivot & calculate sq-euclidean dist against
    # bottom2 points & thus get bottom-right, bottom-left sequentially
    sqdists = distance.cdist(top_left[None], bottom2, 'sqeuclidean')
    rest2 = bottom2[np.argsort(np.max(sqdists,0))[::-1],:]

    # Concatenate all these points for the final output
    return np.concatenate((sortedtop2c1,rest2),axis =0)

#end function

def approx_rect(poly,scale):
    '''
    Given polygon with four vertices poly, returns a rectangle approximation.
    '''
    
    pts = poly.reshape((4,2))
    cent = np.mean(pts,axis=0)
    to_cent_vect = np.array([
        (scale*(pt-cent))
        for pt in pts])
    rect = to_cent_vect + cent
    to_cent_sign = np.sign(to_cent_vect)
    to_cent_mean = np.mean(abs(to_cent_vect),axis=0)
    return (to_cent_sign*to_cent_mean) + cent
    
#end function approx_rect

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
        
    #end method presskey
    
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

class GUIParamSet(object):
    '''
    Requires OpenCV (cv2 module)
    '''
    
    def __init__(self,og_sct):
        '''
        Responsible for retrieving params from the user via OpenCV GUI.
        
        Arguments:
            cv2.img og_sct - OpenCV (cv2) type image to display in GUI screen
        '''
        
        self.og_sct = og_sct
        self.usr_rect = ((0,0),(0,0)) #rectangle defined by the user
        self.window_text = 'HereFishy  |  Select bobber...'
        
        #messages displayed in each view
        self.nozoom_txt = [
            "Please inscribe bobber in as tight a box as possible",
            "Mouse=select box  [Esc]=close  [Enter]=accept box",
            "[z]=zoom to box  [shift+z]=reset zoom"]
        self.zoom_txt = "zoom mode: shift+z to reset"
        
        
    #end function __init__
    
    def get_usr_rect(self):
        '''
        Instantiates OpenCV GUI window with self.og_sct image. Tracks the
        rectangle that the user draws, and changes self.usr_rect with every
        mouse up event. Returns self.usr_rect as tuple of tuples.
        
        Arguments:
            none
        Returns:
            tuple self.usr_rect - tuple of tuples defining the rectangle drawn
                by user. Formatted as ((x_min,x_max),(y_min,y_max)).
        '''
        
        def draw_rect(event,x,y,flags,param):
            '''
            Mouse callback function
            '''
            if event == cv2.EVENT_LBUTTONDOWN:
                self.drawing = True
                self.ix,self.iy = x,y
            elif event == cv2.EVENT_MOUSEMOVE:
                if self.drawing == True:
                    self.temp_sct = np.copy(self.sct)
                    cv2.rectangle(self.temp_sct,(self.ix,self.iy),(x,y),(200,200,200),1)
            elif event == cv2.EVENT_LBUTTONUP:
                self.drawing = False
                self.temp_sct = np.copy(self.sct)
                cv2.rectangle(self.temp_sct,(self.ix,self.iy),(x,y),(0,255,0),1)
                self.temp_rect = ((self.ix,x),(self.iy,y))
        #end function draw_rect
        
        def add_text(img,text,pos=(20,50)):
            '''
            Adds black str text to top left corner of img. Copies img and
            returns modified img with text.
            '''
            
            img_mod = np.copy(img)
            if type(text) == str:
                text = [text]
            elif type(text) == list:
                pass
            else:
                raise TypeError("Invalid str type")
            x, y = pos
            for line in text:
                cv2.putText(
                    img_mod,line,(x,y),cv2.FONT_HERSHEY_SIMPLEX,1, (255,255,255),2)
                y += 40
            return img_mod
        #end function show_text
        
        #Initialization attrs
        self.sct = add_text(self.og_sct,self.nozoom_txt) #shallow copy of original image with txt
        self.temp_sct = np.copy(self.sct) #shallow copy of current image
        self.temp_rect = self.usr_rect #temporary copy
        self.drawing = False # true if mouse is pressed
        self.ix,self.iy = -1,-1 # initial rectangle origin
        zoomed = False #true if z has been pressed
        
        #Transform values after a zoom event. These are applied to
        #self.usr_rect upon ENTER keypress. xform_sc is the x and y scaling
        #factors, and xform_pt
        xform_sc = 1.
        xform_pt = (0,0)
        
        #Instantiate window and track keypresses
        cv2.namedWindow(self.window_text)
        while(1):
            cv2.setMouseCallback(self.window_text,draw_rect)
            cv2.imshow(self.window_text,self.temp_sct)
            k = cv2.waitKey(1) & 0xFF
            if k == 27: #esc key
                print("Set param cancelled")
                break
            elif k == 255: #no keypress
                pass
            elif k == 13: #enter key
                no_xform = np.array([sorted(x) for x in self.temp_rect])
                self.usr_rect = [ #add scaling and translation vectors
                    [int(y) for y in x] for x in 
                    (no_xform*xform_sc) + np.array(xform_pt)]
                print("Rectangle drawn at " + str(self.usr_rect))
                break
            elif k == ord('z'): #z key for zoom
                if self.temp_rect == ((0,0),(0,0)):
                    print("No rectangle to zoom on!")
                    continue
                if zoomed == True:
                    print("Can only zoom once. shift+z to reset zoom")
                    continue
                #Get translation transform
                ((x_min,x_max),(y_min,y_max)) = [
                    sorted(x) for x in self.temp_rect]
                xform_pt = (x_min,y_min)
                #Get scaling transform
                h, w, channels = self.og_sct.shape
                xform_sc = min([(x_max-x_min)/w,(y_max-y_min)/h])
                #resize cropped image, zooming by xform_sc in both x and y dims
                self.sct = cv2.resize(
                    self.og_sct[y_min:y_max,x_min:x_max],
                    None,
                    fx=(1/xform_sc),
                    fy=(1/xform_sc),
                    interpolation=cv2.INTER_LINEAR)
                self.sct = add_text(self.sct,self.zoom_txt) #add zoomed text
                self.temp_sct = np.copy(self.sct)
                zoomed = True
            elif k == 90: #shift+z to reset zoom
                zoomed = False
                self.temp_rect = self.usr_rect
                self.sct = add_text(self.og_sct,self.nozoom_txt)
                self.temp_sct = np.copy(self.sct)
                xform_sc = 1.
                xform_pt = (0,0)
        cv2.destroyAllWindows()
        return self.usr_rect
        
    #end method _dev_draw
    
#end class GUIParamSet

class NatPagle(object):
    
    def __init__(self,params):
        '''
        Instantiates NatPagle object, which handles the central processes
        of HereFishy. He oversees iterative calls to Mouser, BobTracker,
        GUIParamSet, and ParamStat objects. 
        '''
        
        self.params = params
    
    #end method __init__
    
    def get_search_area(self):
        '''
        Takes screenshot using MSS and uses GUIParamSet to retrieve user-defined
        search area. Updates self.search_area attr and returns search area.
        '''
        
        with mss() as sct:
            img = np.array(sct.grab(sct.monitors[1]))
        area_getter = GUIParamSet(img)
        area_getter.window_text = "HereFishy  |  Select search area..."
        area_getter.nozoom_txt = [
            "Select area in which bobber will definitely land",
            "Mouse=select box  [Esc]=close  [Enter]=accept box",
            "[z]=zoom to box  [shift+z]=reset zoom"]
        self.search_area = area_getter.get_usr_rect()
        return self.search_area
        
    #end method get_search_area
    
    def gofishin(self):
        '''
        Iteratively presses '1' key, waits a few seconds, instantiates
        BobTracker, listens for splash event, shift-right clicks, waits a few
        seconds, and repeats.
        '''
        
        #Instantiate Mouser object based on os
        if os.name == 'posix': #unix systems
            mouser = MacMouser()
        elif os.name == 'nt': #windows
            pass
        else:
            raise Exception("Operating system not supported. Please run in " + \
                            "Mac OS X or Windows (os.name='" + os.name + "').")
        
        #Give user some time to navigate to the WoW window
        for ct in range(self.params['init_wait_time']):
            print('|-- Enter WoW in the next ' + \
                  str(self.params['init_wait_time']-ct) + " seconds...\r",end='')
            time.sleep(1)
        print()
        
        try:
            while True:
                
                # instantiate BobTracker
                for ct in range(self.params['init_wait_time']):
                    print("Casting line in " + \
                          str(self.params['init_wait_time']-ct) + "...\r",end='')
                    time.sleep(1)
                tracker = BobTracker(self.params)
                
                # press 1 key to cast and find bobber using difference map
                bob_loc = tracker.find_bob(self.params['bob_track_probe'])
                
                # recast line if bobber was not found
                if not bob_loc:
                    print("|-- No bobber was found. Recasting...")
                    continue
                
                # draw box around bobber and wait for color value in box to spike,
                # which indicates splash event
                print("|-- Waiting for splash...")
                splashing = tracker.wait_for_splash(bob_loc[0],bob_loc[1])
                if splashing:
                    time.sleep(.4)
                    mouser.mousemove(bob_loc[0],bob_loc[1])
                    time.sleep(.3)
                    mouser.shiftrightclick(bob_loc[0],bob_loc[1])
        except KeyboardInterrupt:
            print("Aborted Nat Pagle")
            return
        #end try
        
    #end method gofishin
    
#end class NatPagle

class BobTracker(object):
    
    def __init__(self,params,paramtracker):
        '''
        Instantiates BobTracker, which is responsible for finding the bobber
        on the screen and waiting for a splash event.
        '''
        
        # parameter dictionary
        self.params = params

        # mouse handler
        if params['os'] == "posix": #Mac OS X
            self.mouser = MacMouser()
        else:
            raise Exception("No OS other than Mac OS X supported at this time.")
        
        # takes a ParamTracker object
        self.pt = paramtracker
        
    #end method __init__
    
    def find_bob(self,res=40):
        '''
        Finds the bobber via difference map method. Takes an initial screenshot
        in area defined by arg cap_area before bobber is on screen. Then presses
        '1' to cast line, waits 2 seconds, and starts sampling 2D points in the
        cap_area grid. find_bob takes a square screenshot with sides 2*res at
        every sample point. Each sample point is separated by res in both x and
        y axes. Calculates the mean color values of the screenshot at the
        sample point, and of the cropped initial screenshot. If the
        difference between the mean color values of the sample point screenshot
        and the initial screenshot is above UD param bob_color_diff, find_bob
        logs a hit at coordinates x and y. In the past, find_bob has found false
        positives if there are other changes to the cap_area, such as a player
        passing by, another fisher, or a water effect. To mitigate this, find_bob
        takes UD param sct_check_iters more screenshots and only logs a hit if
        all of them pass the difference threshold. Calculates the arithmetic
        mean point of all the hits, weighted by the magnitude of the difference
        of means, moves the mouse to this mean location, and returns these
        coordinates as tuple.
        
        Arguments:
            dict cap_area - dictionary defining the screenshot capture area. See
                params section of herefishy.py for details.
            int res[=40] - probe size in pixels. Determines grid spacing as
                well as the size of the screenshot taken at each sample point
        Returns:
            tuple - coordinates of find_bob's best guess of the bobber location
        '''
        
        # pre-calculate the screen capture area (cap_area) in forms that are
        # convenient for MSS, Numpy array splicing, and for loops
        cap_area = self.params['cap_area']
        area_pts = np.array([
            [cap_area['left'], cap_area['top']],
            [cap_area['left'] + cap_area['width'],cap_area['top'] + cap_area['height']]
            ])
        bounds = rect_bounds(area_pts)
        
        # list of points where color difference above the threshold was detected
        bob_loc_lst = []
        # color difference indices corresponding to each point in bob_loc_lst
        weight_lst = []
        with mss() as sct: # start taking screenshots
            # initial screenshot of cap_area
            init_sct = np.array(sct.grab(cap_area))
            self.mouser.presskey(0x12) # press '1' key using Quartz CoreGraphics
            time.sleep(2) #wait for bobber to appear
            for x in range(bounds[0],bounds[1],res): # scroll down screen
                for y in range(bounds[2],bounds[3],res): # scroll across screen
                    # moves mouse if in dev mode. slower this way
                    if self.params['_dev_mode']:
                        self.mouser.mousemove(x,y)
                    # take local screenshot in square with sides 2*res around
                    # each x,y point.
                    lsct = np.array(sct.grab({
                        "top": y-res,
                        "left": x-res,
                        "width": 2*res,
                        "height": 2*res}))
                    # crop the init_sct to the same size and location as lsct
                    cropped = init_sct[
                        y-res-cap_area['top']:y+res-cap_area['top'],
                        x-res-cap_area['left']:x+res-cap_area['left']]
                    # if near edge of screen, shapes will likely be different,
                    # and the arrays cannot be compared
                    if lsct.shape != cropped.shape:
                        continue
                    mean_diff = [np.mean(lsct) - np.mean(cropped)]
                    # more dev mode printing
                    if self.params['_dev_mode']:
                        print(mean_diff[0])
                    # asks if the difference in means is above the param color
                    # value threshold
                    if mean_diff[0] > self.params['bob_color_diff']:
                        # bool marking valid bob_loc coordinates
                        is_valid_pt = True
                        # color difference passed the threshold. This may be the
                        # bobber, but could also be a water effect or a passing
                        # player. Take params['sct_check_iters'] more screen-
                        # -shots and skip this point if not all of them are
                        # above the threshold. Sleeps for
                        # params['sct_check_pause'] seconds after each shot.
                        for i in range(self.params['sct_check_iters']):
                            lsct = np.array(sct.grab({
                                "top": y-res,
                                "left": x-res,
                                "width": 2*res,
                                "height": 2*res}))
                            new_diff = np.mean(lsct) - np.mean(cropped)
                            if new_diff < self.params['bob_color_diff']:
                                is_valid_pt = False
                                break
                            mean_diff.append(new_diff)
                            time.sleep(self.params['sct_check_pause'])
                        # check the bob_loc_bool switch. Should be False if
                        # any of the screenshot checks were below threshold
                        if is_valid_pt:
                            print("|-- Color difference of " + \
                                  str(np.mean(mean_diff)) + " detected")
                            bob_loc_lst.append([x,y])
                            # appends the mean color difference of all verifying
                            # screenshots
                            weight_lst.append(np.mean(mean_diff))
                            self.mouser.mousemove(x,y)
                            # noticeable pause for each hit in dev mode
                            if self.params['_dev_mode']:
                                time.sleep(.1)
        # return false if no color difference was detected
        if len(bob_loc_lst) == len(weight_lst) == 0:
            return False
        # convert to arrays
        bob_loc_arr = np.array(bob_loc_lst)
        weight_arr = np.array(weight_lst)
        # calculate the weighted average of the difference map
        x = np.sum(np.multiply(weight_arr,bob_loc_arr[:,0]))/np.sum(weight_arr)
        y = np.sum(np.multiply(weight_arr,bob_loc_arr[:,1]))/np.sum(weight_arr)
        # move mouse to estimated location and return tuple coords
        self.mouser.mousemove(x,y)
        return (x,y)
        
    #end method find_bob
    
    def wait_for_splash(self,x,y):
        '''
        Waits for splash event at estimated bobber location x,y. Takes an
        initial screenshot and tracks the change in the mean color value
        in a square area with sides splash_radius around x,y. Similar algorighm
        to find_bob (see above docs). Returns True when difference of mean color
        value surpasses param splash_diff_thresh, or False if it falls below
        param bob_fade_thresh.
        
        Arguments:
            float x - x coordinate of estimated bobber location
            float y - y coordinate of estimated bobber location
        Returns:
            boolean - see above
        '''
        
        # pre-arrange cap_area in most convenient format for MSS and
        # Numpy array slicing
        srad = self.params['splash_radius']
        cap_area = {
            "top": y-srad,
            "left": x-srad,
            "width": 2*srad,
            "height": 2*srad}
        bob_box = [
            [x-srad,y-srad],
            [x-srad,y+srad],
            [x+srad,y+srad],
            [x+srad,y-srad]]
        
        # DEV: loop around box once
        for pt in bob_box:
            time.sleep(.2)
            self.mouser.mousemove(pt[0],pt[1])
        time.sleep(.2)
        
        # start taking screenshots
        with mss() as sct:
            # get cursor out of the way
            self.mouser.mousemove(x-200,y-200)
            # takes initial screenshot and calculates the mean
            init_mean = np.mean(np.array(sct.grab(cap_area)))
            start = time.time()
            # sets a hard time cap on how long to wait for splash
            while time.time() - start < self.params['max_wait_time']:
                cur_sct = np.array(sct.grab(cap_area))
                cur_mean = np.mean(cur_sct)
                print(cur_mean-init_mean)
                if (cur_mean-init_mean) > self.params['splash_diff_thresh']:
                    print("|-- Splash detected!")
                    return True # splash event detected
                elif (cur_mean-init_mean) < self.params['bob_fade_thresh']:
                    print("|-- Bobber fade away detected")
                    return False # bobber has faded away
        print("|-- Waiting for splash timed out")
        return False
    
    #end method wait_for_splash
    
#end class BobTracker

class ParamTracker(object):
    
    def __init__(self,params):
        '''
        In charge of logging and relaying cast history, as well as recommending
        parameters based on previous successes.
        '''
        
        self.params = params
        
    #end method __init__
    
    def log_find_bob(self,thing):
        '''
        docs
        '''
        
    #end method log_find_bob
    
    def log_splash_detect(self,thing):
        '''
        docs
        '''
        
    #end method log_find_bob
    
#end class ParamStat