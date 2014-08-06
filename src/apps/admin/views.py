#!/usr/bin/env python
# -*- coding: utf-8 -*-
import subprocess
from django.core.management import call_command
from django.http import HttpResponse

from os import environ
from django.conf import settings
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect
from django.contrib.auth.decorators import login_required


def home(request):
    """
    重定向到login页面
    """
    site_name = settings.SITE_NAME
    if request.user.is_authenticated():
        if not request.user.is_staff:
            return redirect(reverse('website:home'))
        return render_to_response('admin/home.html',
                                  locals(),
                                  context_instance=RequestContext(request))

    # 如果没有登陆，返回默认的主页
    return redirect(reverse('admin:account:login'))


@login_required()
def dashboard(request):
    try:
        env_settings = environ['DJANGO_SETTINGS_MODULE']
    except KeyError:
        env_settings = "not define in env"

    # get which tag is using in current branch
    #cmd = 'cd %s && git describe --abbrev=0 --tags' % settings.SITE_ROOT
    cmd = 'cd %s && git rev-list --date-order -n 1 --format=%%d HEAD' % settings.SITE_ROOT
    git_tag = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)

    active_settings = settings.SETTINGS_MODULE

    return render_to_response('admin/dashboard.inc.html',
                              locals(),
                              context_instance=RequestContext(request))


@login_required()
def loaddata(request, filename):
    call_command("loaddata", filename, settings=settings.SETTINGS_MODULE, traceback=True, verbosity=0)
    return HttpResponse(content='load data %s success' % filename)

