from django.db import models
from django.urls import reverse
from django.contrib.auth.models import AbstractUser
from django.conf import settings

import uuid
import os
from PIL import Image

class CustomUser(AbstractUser):
    def __str__(self):
        return self.username

class Category(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name

class BodyStyle(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name

class Make(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name

class Model(models.Model):
    make = models.ForeignKey(to=Make, on_delete=models.CASCADE)
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name

class TransmissionType(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name

class Fuel(models.Model):
    name = models.CharField(max_length=64)
    
    def __str__(self):
        return self.name

class Color(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name

class DoorCount(models.Model):
    count = models.IntegerField()

    def __str__(self):
        return str(self.count)

class Condition(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name

class Ad(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    user = models.ForeignKey(to=CustomUser, on_delete=models.CASCADE)
    category = models.ForeignKey(to=Category, on_delete=models.CASCADE)
    title = models.CharField(max_length=150)
    price = models.FloatField()
    mileage = models.FloatField()
    bodystyle = models.ForeignKey(to=BodyStyle, on_delete=models.CASCADE, blank=True, null=True)
    make = models.ForeignKey(to=Make, on_delete=models.CASCADE)
    model = models.ForeignKey(to=Model, on_delete=models.CASCADE)
    transtype = models.ForeignKey(to=TransmissionType, on_delete=models.CASCADE, blank=True, null=True)
    fuel = models.ForeignKey(to=Fuel, on_delete=models.CASCADE, blank=True, null=True)
    color = models.ForeignKey(to=Color, on_delete=models.CASCADE, blank=True, null=True)
    doorcount = models.ForeignKey(to=DoorCount, on_delete=models.CASCADE, blank=True, null=True)
    description = models.TextField()
    condition = models.ForeignKey(to=Condition, on_delete=models.CASCADE, blank=True, null=True)
    manufacture_year = models.IntegerField()
    state = models.CharField(max_length=64)
    city = models.CharField(max_length=64)
    zip = models.IntegerField()
    views = models.IntegerField(default=0)
    date_posted = models.DateTimeField()
    date_expire = models.DateTimeField()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("cardealer:detail", kwargs={"pk": self.id})
    

class Picture(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    ad = models.ForeignKey(to=Ad, on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    image = models.ImageField(upload_to='images/', max_length=200)
    thumb_big = models.ImageField(upload_to='images/', max_length=200)
    thumb_med = models.ImageField(upload_to='images/', max_length=200)
    thumb_small = models.ImageField(upload_to='images/', max_length=200)

    def make_square(self, im, size=(750, 420), fill_color=(220, 220, 220)):
        (width, height) = im.size
        ratio = width / height
        new_width = ratio * size[1]
        new_height = size[1]

        if new_width > size[0]:
            ratio = size[1] / new_width
            new_width = size[0]
            new_height = ratio * size[0]

        resized_im = im.resize((int(new_width), int(new_height))) # Remove Resampling attribute in server
        new_im = Image.new('RGB', size, fill_color)
        new_im.paste(resized_im, (int((size[0] - resized_im.width) / 2), int((size[1] - resized_im.height) / 2)))
        return new_im

    def save(self):
        super().save()

        if self.image:
            origin_image = Image.open(self.image.path)
            mark_image = Image.open(os.path.join(settings.BASE_DIR, 'mark.png'))
            (o_width, o_height) = origin_image.size
            (m_width, m_height) = mark_image.size
            origin_image.paste(mark_image, (o_width - m_width, o_height - m_height), mark_image)
            origin_image.save(self.image.path)

        if self.thumb_big:
            origin_image = Image.open(self.image.path)
            new_image = self.make_square(origin_image)
            new_image.save(self.thumb_big.path)
        
        if self.thumb_med:
            origin_image = Image.open(self.image.path)
            new_image = self.make_square(origin_image, size=(360, 270))
            new_image.save(self.thumb_med.path)

        if self.thumb_small:
            origin_image = Image.open(self.image.path)
            new_image = self.make_square(origin_image, size=(200, 112))
            new_image.save(self.thumb_small.path)

class UploadImage(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    user = models.ForeignKey(to=CustomUser, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='temp/')

    def delete(self, using=None):
        name = self.image.name
        super(UploadImage, self).delete(using)
        self.image.storage.delete(name)
