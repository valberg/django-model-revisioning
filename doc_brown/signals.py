# coding: utf-8
import django.dispatch

pre_revision = django.dispatch.Signal(
    providing_args=['instance']
)

post_revision = django.dispatch.Signal(
    providing_args=['instance', 'revision']
)

pre_change_head = django.dispatch.Signal(
    providing_args=['instance', 'current_head', 'future_head']
)

post_change_head = django.dispatch.Signal(
    providing_args=['instance', 'current_head']
)
