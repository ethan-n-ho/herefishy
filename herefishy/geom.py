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


def rect_bounds(pts):

    x_min = np.min(pts[:,0])
    x_max = np.max(pts[:,0])
    y_min = np.min(pts[:,1])
    y_max = np.max(pts[:,1])
    return(x_min,x_max,y_min,y_max)


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
