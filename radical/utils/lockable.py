import threading 

def Lockable (cls):
    """ 
    This class decorator will add lock/unlock methods to the thusly decorated
    classes, which will be enacted via an also added `threading.RLock` member
    (`self._rlock`)::

        @Lockable
        class A (object) :
        
            def call (self) :
                print 'locked: %s' % self.locked
        
    The class instance can then be used like this::

        a = A    ()
        a.call   ()
        a.lock   ()
        a.call   ()
        a.lock   ()
        a.call   ()
        a.unlock ()
        a.call   ()
        with a :
          a.call ()
        a.call   ()
        a.unlock ()
        a.call   ()
    
    which will result in::

        locked: 0
        locked: 1
        locked: 2
        locked: 1
        locked: 2
        locked: 1
        locked: 0
    """

    if  hasattr (cls, '__enter__') :
        raise RuntimeError ("Cannot make '%s' lockable -- has __enter__" % cls)

    if  hasattr (cls, '__exit__') :
        raise RuntimeError ("Cannot make '%s' lockable -- has __exit__" % cls)

    if  hasattr (cls, '_rlock') :
        raise RuntimeError ("Cannot make '%s' lockable -- has _rlock" % cls)

    if  hasattr(cls, 'locked') :
        raise RuntimeError ("Cannot make '%s' lockable -- has locked" % cls)

    if  hasattr (cls, 'lock') :
        raise RuntimeError ("Cannot make '%s' lockable -- has lock()" % cls)

    if  hasattr (cls, 'unlock') :
        raise RuntimeError ("Cannot make '%s' lockable -- has unlock()" % cls)


    def locker   (self)        : self._rlock.acquire (); self.locked += 1
    def unlocker (self, *args) : self._rlock.release (); self.locked -= 1

    cls._rlock    = threading.RLock ()
    cls.locked    = 0
    cls.lock      = locker
    cls.unlock    = unlocker
    cls.__enter__ = locker
    cls.__exit__  = unlocker

    return cls



# @Lockable
# class A (object) :
# 
#     def call (self) :
#         print 'locked: %s' % self.locked
# 
# a = A()
# a.call ()
# a.lock ()
# a.call ()
# a.lock ()
# a.call ()
# a.unlock ()
# a.call ()
# with a :
#   a.call ()
# a.call ()
# a.unlock ()
# a.call ()

# ------------------------------------------------------------------------------

