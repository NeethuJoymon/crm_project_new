from django.urls import path
from . import views

urlpatterns = [
path('', views.admin_login, name='admin_login'),
path('signup', views.signup, name='signup'),    
path('customer_list/', views.customer_list, name='customer_list'),  # Customer list 
path('customer_add/', views.customer_add, name='customer_add'),  # Customer add
path('get_customer_details', views.get_customer_details, name='get_customer_details'),
path('download_customer_pdf', views.download_customer_pdf, name='download_customer_pdf'),
path('delete_customer/<int:customer_id>/', views.delete_customer, name='delete_customer'),
path('update_customer/', views.update_customer, name='update_customer'),
path('upload_customers/', views.upload_customers, name='upload_customers'),
path('user_list/', views.user_list, name='user_list'),  # user list 
path('user_add/', views.user_add, name='user_add'),  # user list
path('user/edit/<int:user_id>/', views.user_edit, name='user_edit'),
path('user/view/<int:user_id>/', views.user_view, name='user_view'),

]
