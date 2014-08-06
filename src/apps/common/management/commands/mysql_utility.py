#!/usr/bin/env python
# -*- coding: utf-8 -*-
import subprocess
from optparse import make_option

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

# not use option "--lock-all-tables" to mysqldump because it will require "FLUSH_TABLE" permission for mysql user
BACKUP_CMD = 'mkdir -p %s && mysqldump -u%s -p%s -hlocalhost %s > %s/%s_%s_%s.sql'
LOAD_CMD = 'mysql -u%s -p%s -hlocalhost %s < %s'
DEL_OLD_CMD = 'find %s -mtime +%d -name "*.sql" -exec rm -f {} \\;'


class Command(BaseCommand):
    """
    run it with "crone" like below
    crone -e
        5 2 * * * workon fac-mcrm && cd /var/www/fac-mcrm/src/ && python manage.py mysql_utility >> /var/log/mysql_utility.log 2>&1
    python manage.py mysql_utility -t 1.0.0.0

    导入格式
    python manage.py mysql_utility -t 1.0.0.0 -a load -f sql_file
    """
    option_list = BaseCommand.option_list + (
        make_option('-d', '--backup_dir',
                    action='store',
                    dest='backup_dir',
                    default="~/mysql_backup",
                    help='db backup dir'),
        make_option('-t', '--git_tag',
                    action='store',
                    dest='tag',
                    default="daily",
                    help='related source code tag'),
        make_option('-k', '--keep_days',
                    action='store',
                    dest='keep_days',
                    default=30,
                    help='keep backup day'),
        make_option('-a', '--action',
                    action='store',
                    dest='action',
                    default="dump",
                    help='dump or load data'),
        make_option('-f', '--file',
                    action='store',
                    dest='file',
                    default="",
                    help='file path'),
    )

    def handle(self, *args, **options):
        print str(options)
        if options['action'] == 'dump':
            return self.dump_data(options)
        else:
            return self.load_data(options)

    def load_data(self, options):
        cmd = LOAD_CMD % (
            settings.DATABASES['default']['USER'],
            settings.DATABASES['default']['PASSWORD'],
            settings.DATABASES['default']['NAME'],
            options['file']
            )
        print "[cmd] %s" % cmd
        ret_code = subprocess.call(cmd, shell=True)
        if ret_code != 0:
            print "[ERROR] failed to load with cmd \n %s" % cmd
        return ret_code

    def dump_data(self, options):
        backup_dir = options['backup_dir']
        cmd = BACKUP_CMD % (backup_dir,
                        settings.DATABASES['default']['USER'],
                        settings.DATABASES['default']['PASSWORD'],
                        settings.DATABASES['default']['NAME'],
                        backup_dir,
                        settings.DATABASES['default']['NAME'],
                        timezone.now().strftime('%Y%m%d%H%M%S'),
                        options['tag'])
        print "[cmd] %s" % cmd
        ret_code = subprocess.call(cmd, shell=True)
        if ret_code != 0:
            print "[ERROR] failed to backup with cmd \n %s" % cmd

        cmd = DEL_OLD_CMD % (backup_dir, options['keep_days'])
        print "[cmd] %s" % cmd
        ret_code = subprocess.call(cmd, shell=True)
        if ret_code != 0:
            print "[ERROR] failed to clean old files with cmd \n %s" % cmd
        return ret_code
