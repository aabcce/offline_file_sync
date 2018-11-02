# coding=utf-8

from __future__ import unicode_literals
import sys
from django.shortcuts import render
from models import File
import json
from django.http import HttpRequest
from django.http import JsonResponse
from django.http import HttpResponse
from django.core import serializers

def screen(request):
    return render(request, "exportfile/screen.html", {})


def list(request):
    items = File.objects.all()

    obj_arr = []
    for o in items:
        obj_arr.append(o.toDict())

    return JsonResponse(obj_arr, safe=False)


def doDelete(request):
    ids = request.GET.getlist("id[]")

    try:
        for id in ids:
            File.objects.get(pk=id).delete()
    except:
        err = sys.exc_info()
        print(err[1].message)
        return JsonResponse({"code": 1, "msg": err[1].message})

    return JsonResponse({"code": 0, "msg": "Operation success !"})