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
