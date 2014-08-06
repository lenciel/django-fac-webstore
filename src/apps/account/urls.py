#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
from apps.account import views


urlpatterns = patterns('',
    url(r'^login$', views.login_view, name='login'),
    url(r'^logout$', views.LogoutView.as_view(), name='logout'),

    url(r'^user/list$', views.UserListView.as_view(), name='user_list'),
    url(r'^user/list.datatables$', views.UserListDatatablesView.as_view(), name='user_list.datatables'),
    url(r'^user/create$', views.UserCreateView.as_view(), name='user_create'),
    url(r'^user/(?P<pk>\d+)/edit$', views.UserEditView.as_view(), name='user_edit'),
    url(r'^user/(?P<pk>\d+)/unlock', views.UserLockView.as_view(), name='user_lock'),
    url(r'^user/(?P<pk>\d+)/lock', views.UserUnlockView.as_view(), name='user_unlock'),
    url(r'^user/(?P<pk>\d+)/change_password$', views.UserChangePasswordView.as_view(), name='change_password'),
)

urlpatterns += patterns('',
    url(r'^group/list$', views.GroupListView.as_view(), name='group_list'),
    url(r'^group/list.datatables$', views.GroupListDatatablesView.as_view(), name='group_list.datatables'),
    url(r'^group/create$', views.GroupCreateView.as_view(), name='group_create'),
    url(r'^group/(?P<pk>\d+)/edit$', views.GroupEditView.as_view(), name='group_edit'),
    url(r'^group/(?P<pk>\d+)/delete$', views.GroupDeleteView.as_view(), name='group_delete'),
)

urlpatterns += patterns('',
    url(r'^user/password_reset/',  views.UserResetPasswordView.as_view(),
        # We can't use reverse() because django failed to lookup the url name which is defined in same list also.
        # At this moment, this url name is not available to global url cache.
        {'post_reset_redirect': '/admin/account/user/password_reset_done/',
        'email_template_name': 'account/password_reset_email.html',
        'subject_template_name': 'account/password_reset_subject.txt'},
        name='password_reset'),
    url(r'^user/password_reset_confirm/(?P<uidb36>[0-9A-Za-z]{1,13})-(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        'django.contrib.auth.views.password_reset_confirm',
        {'template_name': 'account/password_reset_confirm.html',
         'post_reset_redirect': '/admin/account/user/password_reset_complete/'},
        name='password_reset_confirm'),
    url(r'^user/password_reset_complete/', 'django.contrib.auth.views.password_reset_complete',
        {'template_name': 'account/password_reset_complete.html'},
        name='password_reset_complete'),
)
