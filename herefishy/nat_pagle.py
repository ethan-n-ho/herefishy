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
