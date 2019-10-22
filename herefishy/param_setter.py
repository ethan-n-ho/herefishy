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
