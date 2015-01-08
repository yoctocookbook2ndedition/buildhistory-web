#!/usr/bin/env python

# Report significant differences in the buildhistory repository since a specific revision
#
# Copyright (C) 2012-2015 Intel Corporation
# Author: Paul Eggleton <paul.eggleton@linux.intel.com>
#
# Licensed under the MIT license, see COPYING.MIT for details


import sys
import os.path
from datetime import datetime
import argparse

# Ensure PythonGit is installed (buildhistory_analysis needs it)
try:
    import git
except ImportError:
    print("Please install PythonGit 0.3.1 or later in order to use this script")
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="buildhistory-web import tool")
    parser.add_argument('corebasepath', help='Path to OE-Core base directory')
    parser.add_argument('buildhistorypath', help='Path to buildhistory directory')
    parser.add_argument('sincerevision', help='Starting revision in buildhistory repo')
    parser.add_argument('torevision', nargs='?', default='HEAD', help='Ending revision in buildhistory repo (defaults to HEAD)')
    args = parser.parse_args()

    # Get access to our Django model
    newpath = os.path.abspath(os.path.dirname(os.path.abspath(sys.argv[0])) + '/..')
    sys.path.append(newpath)
    os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

    from django.core.management import setup_environ
    from warningmgr.models import WarningItem
    import settings

    setup_environ(settings)

    # Set path to OE lib dir so we can import the buildhistory_analysis module
    basepath = os.path.abspath(args.corebasepath)
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

    repo = git.Repo(args.buildhistorypath)
    assert repo.bare == False

    # Import items
    for commit in repo.iter_commits("%s..%s" % (args.sincerevision, args.torevision)):
        print("Processing revision %s..." % commit.hexsha)
        changes = oe.buildhistory_analysis.process_changes(args.buildhistorypath, "%s^" % commit, commit)
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
