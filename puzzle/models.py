from django.db import models
from django.conf import settings

# Create your models here.

import json

class Level(models.Model):
    name = models.CharField(max_length = 255)

    moves = models.IntegerField(default = 0)
    configurations = models.IntegerField(default = 0)

    data = models.CharField(max_length = 2047)

    width = models.IntegerField(default = 310)
    height = models.IntegerField(default = 310)

    cars = models.IntegerField(default = 0)
    square_width = models.IntegerField(default = 0)
    square_height = models.IntegerField(default = 0)

    points = models.FloatField(default = 2)

    def __setattr__(self, attrname, val):
        super(Level, self).__setattr__(attrname, val)
        
        if attrname == "data":
            self._data_dirty = True


    def save(self, *args, **kwargs):
        if getattr(self, '_data_dirty', False):
            self.recalcData()
            self._data_dirty = False

        super(Level, self).save(*args, **kwargs)


    def recalcData(self):
        data = json.loads(self.data)

        self.square_width = data["width"]
        self.square_height = data["height"]
        self.cars = len(data["cars"])

        self.width = 10 + 50 * self.square_width
        self.height = 10 + 50 * self.square_height


    @property
    def clears(self):
        if not hasattr(self, "_clears"):
            self._clears = Clear.objects.filter(level = self).count()

        return self._clears
    
    @clears.setter
    def clears(self, value):
        self._clears = value
    

    def recalcPoints(self):
        self.points = (20 + self.moves * 2)  / (9 + max(1, self.clears))

    def __str__(self):
        return self.name


class Clear(models.Model):
    level = models.ForeignKey(Level, on_delete = models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE)

    date = models.DateTimeField(auto_now_add=True)
    data = models.TextField()

    def __str__(self):
        return f"{self.level} cleared by {self.user}"
