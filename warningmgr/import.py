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
    parser.add_argument('sincerevision', nargs='?', help='Starting revision in buildhistory repo (defaults to last revision)')
    parser.add_argument('torevision', nargs='?', default='HEAD', help='Ending revision in buildhistory repo (defaults to HEAD)')
    parser.add_argument('-m', '--build-name', help='Associated name for the build')
    parser.add_argument('-u', '--build-url', help='Associated URL for the build')
    parser.add_argument('-b', '--branch', help='Branch in the buildhistory repository to use (defaults to currently checked out branch)')
    parser.add_argument('-n', '--dry-run', help="Don't write any data back to the database", action="store_true")
    parser.add_argument('--iterate', help="Iterate over commits rather than just taking the difference between them", action="store_true")
    args = parser.parse_args()

    # Get access to our Django model
    newpath = os.path.abspath(os.path.dirname(os.path.abspath(sys.argv[0])) + '/..')
    sys.path.append(newpath)
    os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

    from django.core.management import setup_environ
    from django.db import transaction
    from warningmgr.models import WarningItem, Build
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

    if args.branch:
        repo.git.checkout(args.branch)

    sincerevision = args.sincerevision or ''
    if not sincerevision:
        # Find most recent commit
        res = list(Build.objects.filter(vcs_branch=repo.head.reference).order_by('-created_date')[:1])
        if res:
            sincerevision = res[0].vcs_rev
    if not sincerevision:
        # We need to find the first revision, this is crude but works
        for commit in repo.iter_commits(args.torevision):
            sincerevision = commit.hexsha

    transaction.enter_transaction_management()
    transaction.managed(True)
    try:
        # Create a build
        b = Build()
        b.created_date = datetime.now()
        b.vcs_branch = repo.head.reference
        b.vcs_rev = repo.commit(args.torevision).hexsha
        if args.build_name:
            b.name = args.build_name
        if args.build_url:
            b.build_url = args.build_url
        b.save()
        # Import items
        def process_changes(proc_start, proc_end):
            print('Processing changes from %s to %s...' % (proc_start, proc_end))
            changes = oe.buildhistory_analysis.process_changes(args.buildhistorypath, proc_start, proc_end)
            for chg in changes:
                wi = WarningItem()
                wi.build = b
                wi.package = 'unknown'
                desc = str(chg)
                wi.description = desc
                wi.summary = desc.split('\n', 1)[0]
                print("Creating: %s" % wi.summary)
                wi.vcs_rev = commit.hexsha
                wi.save()

        if args.iterate:
            for commit in repo.iter_commits("%s..%s" % (sincerevision, args.torevision), reverse=True):
                print("Processing revision %s..." % commit.hexsha)
                process_changes("%s^" % commit, commit)
        else:
            process_changes(sincerevision, args.torevision)

        if args.dry_run:
            transaction.rollback()
        else:
            transaction.commit()
    except KeyboardInterrupt:
        transaction.rollback()
        print("Update interrupted, changes rolled back")
    except:
        import traceback
        traceback.print_exc()
        transaction.rollback()
    finally:
        transaction.leave_transaction_management()

    sys.exit(0)


if __name__ == "__main__":
    main()
