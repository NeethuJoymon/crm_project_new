from django.db import models
from django.contrib.auth.models import User



class Customer(models.Model):
    customer_id = models.CharField(max_length=20, unique=True,default='DEFAULT_ID')
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    address =  models.CharField(max_length=100,null=True)
    image = models.ImageField(upload_to='customer_images/',blank = True)
    created_on = models.DateTimeField(auto_now_add=True) 
    updated_on = models.DateTimeField(auto_now=True)
    dob = models.DateField(null=True, blank=True, help_text='Date of Birth')
    product_id = models.CharField(max_length=20,default='DEFAULT_ID')
    product_name = models.CharField(max_length=255)
    purchase_date = models.DateField(auto_now_add=True)


    def __str__(self):
        return f"{self.name} (ID:{self.id})"
    
class AdminUser(models.Model):
    user = models
