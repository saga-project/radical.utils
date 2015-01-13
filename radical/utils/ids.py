
__author__    = "Radical.Utils Development Team (Andre Merzky)"
__copyright__ = "Copyright 2013, RADICAL@Rutgers"
__license__   = "MIT"


import os
import datetime
import threading

import singleton


# ------------------------------------------------------------------------------
#
class _IDRegistry (object) :
    """
    This helper class (which is not exposed to any user of radical.utils)
    generates a sequence of continous numbers for each known ID prefix.  It is
    a singleton, and thread safe (assuming that the Singleton metaclass supports
    thread safe construction).
    """

    __metaclass__ = singleton.Singleton


    # --------------------------------------------------------------------------
    def __init__ (self) :
        """
        Initialized the registry dict and the threading lock
        """

        self._rlock    = threading.RLock ()
        self._registry = dict()


    # --------------------------------------------------------------------------
    def get_counter (self, prefix, mode='any') :
        """
        Obtain the next number in the sequence for the given prefix and mode.  
        If the mode or prefix are not known, a new registry counter is created.
        """

        with self._rlock :
    
            if  not mode in self._registry :
                self._registry[mode] =  dict()

            if  not prefix in self._registry[mode] :
                self._registry[mode][prefix] =  0
            
            self._registry[mode][prefix] += 1

            return int(self._registry[mode][prefix])


# ------------------------------------------------------------------------------
#
# we create on private singleton instance for the ID registry.
_id_registry = _IDRegistry ()


# ------------------------------------------------------------------------------
#
ID_SIMPLE  = 'simple'
ID_UNIQUE  = 'unique'
ID_PRIVATE = 'private'

# ------------------------------------------------------------------------------
#
def generate_id (prefix, mode=ID_SIMPLE) :
    """
    Generate a human readable, sequential ID for the given prefix.  
    
    The ID is by default very simple and thus very readable, but cannot be
    assumed to be globally unique -- simple ID uniqueness is only guaranteed
    within the scope of one python instance.  

    If `mode` is set to the non-default type `ID_UNIQUE`, an attempt is made to
    generate readable but globally unique IDs -- although the level of
    confidence for uniqueness is significantly smaller than for, say UUIDs.

    Examples::

        id_1 = radical.utils.generate_id ('item.')
        id_2 = radical.utils.generate_id ('item.')
        id_1 = radical.utils.generate_id ('item.', mode=radical.utils.ID_SIMPLE)
        id_2 = radical.utils.generate_id ('item.', mode=radical.utils.ID_SIMPLE)
        id_3 = radical.utils.generate_id ('item.', mode=radical.utils.ID_UNIQUE)
        id_4 = radical.utils.generate_id ('item.', mode=radical.utils.ID_UNIQUE)
        id_3 = radical.utils.generate_id ('item.', mode=radical.utils.ID_PRIVATE)
        id_4 = radical.utils.generate_id ('item.', mode=radical.utils.ID_PRIVATE)

    The above will generate the IDs:

        item.0001
        item.0002
        item.0003
        item.0004
        item.2014.07.30.13.13.44.0001
        item.2014.07.30.13.13.44.0002
        item.cameo.merzky.021342.0001
        item.cameo.merzky.021342.0002

    where 'cameo' is the (short) hostname, 'merzky' is the username, and '02134'
    is 'days since epoch'.  The last element, the counter is unique for each id
    type and item type, and restarts for each session (application process).  In
    the last case though (`ID_PRIVATE`), the counter is reset for every new day,
    and can thus span multiple applications.
    """

    if  not prefix or \
        not isinstance (prefix, basestring) :
        raise TypeError ("ID generation expect prefix in basestring type") 

    counter = _id_registry.get_counter (prefix, mode)

    if  mode  == ID_SIMPLE :
        return "%s%04d" % (prefix, counter)

    elif mode == ID_UNIQUE :

        now  = datetime.datetime.utcnow ()
        date = "%04d.%02d.%02d" % (now.year, now.month,  now.day)
        time = "%02d.%02d.%02d" % (now.hour, now.minute, now.second)
        pid  = os.getpid ()

        return "%s%s.%s.%06d.%04d" % (prefix, date, time, pid, counter)
      # return "%s%s.%s.%04d"      % (prefix, date, time,      counter)
      # return "%s%06d.%04d"       % (prefix,             pid, counter)

    elif mode == ID_PRIVATE :

        import time
        import socket
        import getpass

        now  = time.time ()              # seconds since epoch
        days = int(now / (60 * 60 * 24)) # full days since epoch
        host = socket.gethostname()      # local hostname
        user = getpass.getuser() 

        return "%s%s.%s.%06d.%04d" % (prefix, host, user, days, counter)

    else :
        raise ValueError ("mode '%s' not supported for ID generation", mode) 


# ------------------------------------------------------------------------------

