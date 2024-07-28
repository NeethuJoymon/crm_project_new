from urllib import request
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .models import Customer,User
from .forms import CustomLoginForm,UploadFileForm
from django.core.paginator import Paginator
from django.contrib import messages
from django.utils.timezone import now
from django.http import JsonResponse
from django.http import HttpResponse
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from django.views.decorators.csrf import csrf_exempt
import json
from django.shortcuts import get_object_or_404
import pandas as pd # type: ignore
import pandas as pd
from datetime import datetime
from .forms import CustomUserCreationForm
from django.db.models import Max
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth import update_session_auth_hash

from django.core.exceptions import ValidationError

# -------Sign Up------------------

@csrf_exempt
def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            return render(request, 'customers/signup.html', {'error_message': 'Passwords do not match.'})

        if User.objects.filter(username=username).exists():
            return render(request, 'customers/signup.html', {'error_message': 'Username already exists.'})

        if User.objects.filter(email=email).exists():
            return render(request, 'customers/signup.html', {'error_message': 'Email already exists.'})

        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()
            login(request, user)
            messages.success(request, 'Sign up successful. You are now logged in.')
            return redirect('customer_list')  # Redirect to a home page or another page after sign-up
        except ValidationError as e:
            return render(request, 'customers/signup.html', {'error_message': str(e)})

    return render(request, 'customers/signup.html')

# ---------------------------------Admin Login----------------------------

def admin_login(request):
    error_message = None
    if request.method == 'POST':
        form = CustomLoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username,password=password)
            # checking if user exist and is admin
            if user is not None and user.is_staff: 
                login(request, user)
                return redirect('customer_list')
            else:
                 error_message = 'Only Admins can Log in'
                
        else:
            error_message = 'Invalid credentials or not an admin user'
    else:

        form = CustomLoginForm()
    return render(request,'customers/login.html',{'form': form,'error_message': error_message})


#----------------------------Add User ---------------------------------------------------------------

@login_required
def user_add(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()  # Save the user and hash the password
            # Redirect with success indicator
            return render(request, 'customers/user_add.html', {
                'form': form,
                'user_added': True
            })
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'customers/user_add.html', {
        'form': form,
        'user_added': False
    })

# ------------------------- List User----------------------------

@login_required
def user_list(request):
    users = User.objects.all()  # Fetch all users

    context = {
        'users': users
    }
    return render(request, 'customers/user_list.html', context)



# --------------------------- Edit User --------------------------------


@login_required
def user_edit(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user_list')  # Redirect to the user list page or any other page
    else:
        form = CustomUserCreationForm(instance=user)

    return render(request, 'customers/user_edit.html', {'form': form, 'user_id': user_id})

#----------------------------- View User ---------------------------------------------------

@login_required
def user_view(request, user_id):
    user = get_object_or_404(User, id=user_id)
    return render(request, 'customers/user_view.html', {'user': user})


#---------------------------------------------- List CUstomer--------------------------------------------

@login_required
def customer_list(request):
    user = request.user
    customer_list = Customer.objects.all()
    # adding paginator for customer list display
    paginator = Paginator(customer_list, 10)  # Show 10 customers per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    data = {
        "username": user,
        "id": id,
        "page_obj": page_obj,
    }
    return render(request,'customers/index.html',data)


#---------------------------------------- Add Customer --------------------------------------------------------

@login_required
def customer_add(request):
    if request.method == 'POST':

        customer_id = request.POST.get('customer_id')
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        dob = request.POST.get('dob')
        product_id = request.POST.get('product_id')
        product_name = request.POST.get('product_name')
        purchase_date = request.POST.get('purchase_date') 
        address =request.POST.get('address') 
        
        image = request.FILES.get('image')
        customer = Customer(
            customer_id=customer_id,
            name=name,
            address=address,
            email=email,
            phone=phone,
            dob=dob,
            image=image,
            product_id=product_id,
            product_name=product_name,
            purchase_date=purchase_date
        )
        customer.save()


        request.session['customer_added'] = True  # Set a session flag
        return redirect('customer_add')

    # Clear the flag from the session if it's set
    customer_added = request.session.pop('customer_added', False)

    today = now().strftime('%d%m%Y')
    sequence_number = Customer.objects.filter(customer_id__startswith=f'CST{today}').count() + 1
    customer_id = f'CST{today}{str(sequence_number).zfill(3)}'

    return render(request, 'customers/customer_add.html', {'customer_id': customer_id,'customer_added': customer_added})


#----------------------------------------Customer Details--------------------------------------------------------

@login_required
def get_customer_details(request):
    customer_id = request.GET.get('id')
    if customer_id:
        try:
            customers = Customer.objects.get(id=customer_id)
            data = {
                'customer_id': customers.customer_id,
                'name': customers.name,
                'address': customers.address,
                'email': customers.email,
                'phone': customers.phone,
                'image':customers.image.url if customers.image else '',
                'dob': customers.dob,
                'product_id':customers.product_id,
                'productName': customers.product_name,
                'purchaseDate': customers.purchase_date,
            }

            return JsonResponse(data)
        except Customer.DoesNotExist:
            return JsonResponse({'error': 'Customer not found'}, status=404)
    return JsonResponse({'error': 'Invalid request'}, status=400)
@csrf_exempt
@login_required


#------------------------------------- Update Customer ----------------------------------------------
def update_customer(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        customer_id = request.POST.get('customer_id')
        name = request.POST.get('name')
        address = request.POST.get('address')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        dob = request.POST.get('dob')
        product_id = request.POST.get('product_id')
        product_name = request.POST.get('product_name')
        purchase_date = request.POST.get('purchase_date')

        try:
            customer = Customer.objects.get(id=id)
            customer.name = name
            customer.address = address
            customer.email = email
            customer.phone = phone
            customer.dob = dob
            customer.product_id = product_id
            customer.product_name = product_name
            customer.purchase_date = purchase_date
            customer.save()
            return JsonResponse({'status': 'success', 'message': 'Customer updated successfully'})
        except Customer.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Customer not found'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


#----------------------------------------- Delete Customer --------------------------------------------

@csrf_exempt
def delete_customer(request, customer_id):
    if request.method == 'DELETE':
        try:
            customer = Customer.objects.get(id=customer_id)
            customer.delete()
            return JsonResponse({'status': 'success'})
        except Customer.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Customer not found'}, status=404)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)


#----------------------------------------- Upload (BULK)----------------------------------------------
def upload_customers(request):
    if request.method == 'POST':
        file = request.FILES.get('file')
        if file:
            try:
                handle_uploaded_file(file)
                return JsonResponse({'status': 'success', 'message': 'File uploaded and processed successfully.'})

            except Exception as e:
                return JsonResponse({'status': 'error', 'message': str(e)})
        else:
            return JsonResponse({'status': 'Error', 'message': 'No file Uploaded'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})

def handle_uploaded_file(uploaded_file):
    try:

        # Check file type
        if not uploaded_file.name.endswith(('.xls', '.xlsx')):
            raise ValidationError("Invalid file format. Only .xls and .xlsx files are supported.")
        

        df = pd.read_excel(uploaded_file)
        
        for index, row in df.iterrows():
            # Generate a new customer ID for each row
            customer_id = generate_customer_id()
            name = row.get('Name')
            address = row.get('Address')
            email = row.get('Email')
            phone = row.get('Phone')
            dob = row.get('Date of Birth')
            product_id = row.get('Product ID')
            product_name = row.get('Product Name')
            purchase_date = row.get('Purchase Date')

            Customer.objects.update_or_create(
                customer_id=customer_id,
                defaults={
                    'name': name,
                    'address': address,
                    'email': email,
                    'phone': phone,
                    'dob': dob,
                    'product_id': product_id,
                    'product_name': product_name,
                    'purchase_date': purchase_date,
                }
            )
    except Exception as e:
        raise e
    
# -------------------------- Generate Customer ID----------------------------------------------

def generate_customer_id():
    today = datetime.now().strftime('%Y%m%d')  # Format date as YYYYMMDD
    prefix = 'CST'
    
    # Get the sequence number for today
    last_customer = Customer.objects.filter(customer_id__startswith=f'{prefix}{today}').order_by('-customer_id').first()
    
    if last_customer:
        # Extract the sequence number from the last customer ID
        last_sequence = int(last_customer.customer_id[len(prefix) + len(today):])  # Exclude prefix and date
        new_sequence = last_sequence + 1
    else:
        # Start with sequence number 1 if no previous record
        new_sequence = 1
    
    # Format sequence number with leading zeros if needed
    sequence_str = str(new_sequence).zfill(4)  # Example: 0001
    
    return f'{prefix}{today}{sequence_str}'

#--------------------------------- Customer -------------------------------------------------

@login_required
def get_customer(request, customer_id):
    # Fetch the customer from the database or return a 404 if not found
    customer = get_object_or_404(Customer, pk=customer_id)

    # Serialize the customer data
    customer_data = {
        'id': customer.id,
        'name': customer.name,
        'address': customer.address,
        'email': customer.email,
        'phone': customer.phone,
        'dob': customer.dob,
        'product_id': customer.product_id,
        'product_name': customer.product_name,
        'purchase_date': customer.purchase_date,
        'profile_picture': customer.profile_picture.url if customer.profile_picture else ''  # Adjust if necessary
    }

    # Return the customer data as JSON
    return JsonResponse({'success': True, 'customer': customer_data})


#--------------------------------- PDF -------------------------------------------------


@login_required
def render_to_pdf(template_src, context_dict):
    """ Convert HTML to PDF """
    template = render_to_string(template_src, context_dict)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="customer_details.pdf"'
    result = pisa.CreatePDF(template, dest=response)
    if result.err:
        return HttpResponse('Error generating PDF', status=500)
    return response

#--------------------------------- Download PDF -------------------------------------------------


@login_required
def download_customer_pdf(request, customer_id):
    """ View to generate and download PDF for customer details """
    try:
        customer = Customer.objects.get(id=customer_id)
    except Customer.DoesNotExist:
        return HttpResponse('Customer not found', status=404)
    
    context = {
        'customer': customer,
    }
    return render_to_pdf('customers/pdf_template.html', context)


    