#!/usr/bin/env python

# Report significant differences in the buildhistory repository since a specific revision
#
# Copyright (C) 2012 Intel Corporation
# Author: Paul Eggleton <paul.eggleton@linux.intel.com>

import sys
import os.path
from datetime import datetime

# Ensure PythonGit is installed (buildhistory_analysis needs it)
try:
    import git
except ImportError:
    print("Please install PythonGit 0.3.1 or later in order to use this script")
    sys.exit(1)


def main():
    if (len(sys.argv) < 4):
        print("Import significant differences in the buildhistory repository into the buildhistory web interface")
        print("Syntax: %s <corebasepath> <buildhistory-path> <since-revision> [to-revision]" % os.path.basename(sys.argv[0]))
        print("If to-revision is not specified, it defaults to HEAD")
        sys.exit(1)

    # Get access to our Django model
    newpath = os.path.abspath(os.path.dirname(os.path.abspath(sys.argv[0])) + '/../..')
    sys.path.append(newpath)
    os.environ['DJANGO_SETTINGS_MODULE'] = 'warningmanager.settings'

    from django.core.management import setup_environ
    from warningmanager.warningmgr.models import WarningItem
    from warningmanager import settings

    setup_environ(settings)

    # Set path to OE lib dir so we can import the buildhistory_analysis module
    basepath = os.path.abspath(sys.argv[1])
    newpath = basepath + '/meta/lib'
    # Set path to bitbake lib dir so the buildhistory_analysis module can load bb.utils
    bitbakedir_env = os.environ.get('BITBAKEDIR', '')
    if bitbakedir_env and os.path.exists(bitbakedir_env + '/lib/bb'):
        bitbakepath = bitbakedir_env
    elif os.path.exists(basepath + '/bitbake/lib/bb'):
        bitbakepath = basepath + '/bitbake'
    elif os.path.exists(basepath + '/../bitbake/lib/bb'):
        bitbakepath = os.path.abspath(basepath + '/../bitbake')
    else:
        # look for bitbake/bin dir in PATH
        bitbakepath = None
        for pth in os.environ['PATH'].split(':'):
            if os.path.exists(os.path.join(pth, '../lib/bb')):
                bitbakepath = os.path.abspath(os.path.join(pth, '..'))
                break
        if not bitbakepath:
            print("Unable to find bitbake by searching BITBAKEDIR, specified path '%s' or its parent, or PATH" % basepath)
            sys.exit(1)

    sys.path.extend([newpath, bitbakepath + '/lib'])
    import oe.buildhistory_analysis

    repo = git.Repo(sys.argv[2])
    assert repo.bare == False

    # Import items
    if len(sys.argv) > 4:
        torev = sys.argv[4]
    else:
        torev = 'HEAD'

    for commit in repo.iter_commits("%s..%s" % (sys.argv[3], torev)):
        print("Processing revision %s..." % commit.hexsha)
        changes = oe.buildhistory_analysis.process_changes(sys.argv[2], "%s^" % commit, commit)
        for chg in changes:
            wi = WarningItem()
            wi.created_date = datetime.now()
            wi.package = 'unknown'
            desc = str(chg)
            wi.description = desc
            wi.summary = desc.split('\n', 1)[0]
            print("Creating: %s" % wi.summary)
            wi.vcs_rev = commit.hexsha
            wi.save()

    sys.exit(0)


if __name__ == "__main__":
    main()
