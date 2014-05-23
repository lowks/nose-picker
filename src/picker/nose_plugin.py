import logging
import os

from nose.plugins import Plugin


class NosePicker(Plugin):
    name = 'nose-picker'

    def __init__(self, *args, **kwargs):
        self.output = True
        self.enableOpt = 'with-nose-picker'
        self.logger = logging.getLogger('nose.plugins.picker')

    def options(self, parser, env=os.environ):
        parser.add_option(
            '--which-process',
            type='int',
            dest='which_process',
            help='Which process number this is of the total.',
        )
        parser.add_option(
            '--futz-with-django',
            action='store_true',
            dest='futz_with_django',
            help='Whether to futz with the django configuration.',
        )
        parser.add_option(
            '--total-processes',
            type='int',
            dest='total_processes',
            help='How many total processes to run with.',
        )
        super(NosePicker, self).options(parser, env=env)

    def configure(self, options, config):
        self.enabled = getattr(options, self.enableOpt)
        self.total_processes = options.total_processes
        self.which_process = options.which_process
        if options.futz_with_django:
            from django.db import connections
            for alias in connections:
                connection = connections[alias]
                creation = connection.creation
                connection.settings_dict['TEST_NAME'] = (
                    'test_' +
                    connection.settings_dict['NAME'] +
                    '__' + str(self.which_process)
                )

        super(NosePicker, self).configure(options, config)

    def wantFile(self, fullpath):
        """
        Do we want to run this file?  See _should_run.
        """
        return self._should_run(fullpath)

    def _should_run(self, name):
        if self.enabled:
            hashed_value = hash(name) % self.total_processes
            if hashed_value == self.which_process:
                return None
            return False

        return None
