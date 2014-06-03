nose-picker
===========

**nose-picker** is a plugin that picks a subset of your unit tests (in django
too!)

This plugin modifies nose's unit test discovery to only pick a (1/N) subset of
unit tests to run. By passing in the ``--total-processes`` arguments, you pick
the denominator (the N above) which you want to run. The ``--which-process``
argument controls which part of that subset to run, so if you had 5 subsets you
could pick 0, 1, 2, 3, or 4.

How does it work? Very simple! It hashes the filenames that nose is
running through, does a modulo division by N, then sees if this file is "its".
Very simple, but it lets you run multiple of these **nose-picker** enabled
runners in parallel, each running a separate subset of the unit tests!

Motivation
----------

The nose multiprocess plugin takes over the test runner when it runs, and thus
is not amenable to environments where you need a custom test runner.
**nose-picker** lets you keep your test runner!

Installing
----------

Through ``pip``::

    pip install --user nose-picker

Sample Multiprocess Script
--------------------------

Something like::

    def main():
        num_processes = int(multiprocessing.cpu_count() * 2.5)
        tests = []
        for i in range(num_processes):
            test_command = TEST_CMD_TEMPLATE % (
                i,
                num_processes,
            )
            tests.append(TestWatcher(test_command))

        returncode = 0
        for test_watcher in tests:
            test_watcher.join()
            if test_watcher.returncode > 0:
                returncode += test_watcher.returncode
            for line in test_watcher.stderr.splitlines():
                if not (
                    line.endswith(' ... ok') or
                    '... SKIP' in line
                ):
                    sys.stderr.write(line + '\n')

        return returncode


    class TestWatcher(threading.Thread):
        def __init__(self, command):
            super(TestWatcher, self).__init__()
            self.command = command
            self.stdout = ''
            self.stderr = ''
            self.start()
            self.returncode = 0

        def run(self):
            p = subprocess.Popen(
                self.command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            self.stdout, self.stderr = p.communicate()
            self.returncode = p.returncode

License
-------

**nose-picker** is copyright 2014 Eventbrite and Contributors, and is made
available under BSD-style license; see LICENSE for details.
