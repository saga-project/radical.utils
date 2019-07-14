#!/usr/bin/env python

__author__    = "Andre Merzky"
__copyright__ = "Copyright 2012-2013, The SAGA Project"
__license__   = "MIT"


import os
import time

import radical.utils as ru

os.environ['RADICAL_UTILS_PROFILE'] = 'True'


# ------------------------------------------------------------------------------
#
def _cmd(cmd):

    out, err, ret = ru.sh_callout(cmd)

    return not bool(ret)


# ------------------------------------------------------------------------------
#
def test_profiler():
    '''
    create and check profile timestamps
    '''


    pname = 'ru.%d'        % os.getpid()
    fname = '/tmp/%s.prof' % pname
    now   = time.time()

    try:
        prof = ru.Profiler(name=pname, ns='radical.utils', path='/tmp/')

        prof.prof('foo')
        prof.prof('bar', uid='baz')
        prof.prof('buz', timestamp=now)

        assert(os.path.isfile(fname))

        def _grep(pat):
            return _cmd('grep -e "%s" %s' % (pat, fname))

        assert(_grep('^[0-9\\.]*,foo,%s,MainThread,,,$'    %       pname ))
        assert(_grep('^[0-9\\.]*,bar,%s,MainThread,baz,,$' %       pname ))
        assert(_grep('^%.7f,buz,%s,MainThread,,,$'         % (now, pname)))

    finally:
        try   : os.unlink(fname)
        except: pass


# ------------------------------------------------------------------------------
#
def test_env():
    '''
    Print out some messages with different log levels
    '''

    # --------------------------------------------------------------------------
    #
    def _assert_profiler(key, val, res):

        pname = 'ru.%d'        % os.getpid()
        fname = '/tmp/%s.prof' % pname
        prof  = ru.Profiler(name=pname, ns='radical.utils.test', path='/tmp/')
        prof.prof('foo')

        assert(res == os.path.isfile(fname))
        assert(res == _cmd('grep -e "^[0-9\\.]*,foo,%s," %s' % (pname, fname)))

        try   : os.unlink(fname)
        except: pass


    # --------------------------------------------------------------------------
    #
    for key in ['RADICAL_PROFILE',
                'RADICAL_UTILS_PROFILE',
                'RADICAL_UTILS_TEST_PROFILE']:

        for k in list(os.environ.keys()):
            if k.startswith('RADICAL'):
                del(os.environ[k])

        _assert_profiler('', '', True)

        for val, res in [
                         ['false', False],
                         ['',      True ],
                         ['1',     True ],
                         ['true',  True ],
                         ['True',  True ],
                         ['TRUE',  True ],
                         ['false', False],
                         ['False', False],
                         ['FALSE', False],
                         ['0',     False]]:

            for k in list(os.environ.keys()):
                if k.startswith('RADICAL'):
                    del(os.environ[k])

            os.environ[key] = val
            _assert_profiler(key, val, res)


# ------------------------------------------------------------------------------
#
if __name__ == '__main__':

    test_profiler()
    test_env()


# ------------------------------------------------------------------------------

