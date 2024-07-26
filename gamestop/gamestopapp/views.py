import random
from django.shortcuts import render, redirect,HttpResponse
from gamestopapp.models import Cart, Product, orders, Review
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.mail import get_connection, EmailMessage
from django.conf import settings


# Create your views here.
def index(request):
    return render(request, 'index.html')

def create_product(request):
    if request.method == "GET":
        return render(request, 'createproduct.html')
    else:

        name = request.POST['name']
        description = request.POST['description']
        manufacturer = request.POST['manufacturer']
        category = request.POST['category']
        price = request.POST['price']
        image = request.FILES['image']

        p = Product.objects.create(name=name, description= description, manufacturer= manufacturer, category= category, price= price, image= image)

        p.save()
        return redirect('/readproduct')


def read_product(request):
    p = Product.objects.all()

    context= {}

    context['data'] = p
    return render(request, 'readproduct.html', context)



def delete_product(request, rid):
    p = Product.objects.filter(id=rid)
    p.delete()
    return redirect('/readproduct')

def update_product(request, rid):
    if request.method == "GET":

        p = Product.objects.filter(id=rid)
        context = {}
        context['data'] = p

        return render(request, 'update_product.html', context)
    
    else:
        name = request.POST['name']
        description = request.POST['description']
        manufacturer = request.POST['manufacturer']
        category = request.POST['category']
        price = request.POST['price']

        p = Product.objects.filter(id = rid)

        p.update(name=name, description= description, manufacturer= manufacturer, category= category, price= price)
        return redirect('/read_product')



def user_register(request):
    if request.method == "GET":

        return render(request, 'register.html')
    
    else:
        username = request.POST['username']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
       
        if password == confirm_password:
            u = User.objects.create(username=username, first_name=first_name, last_name=last_name, email= email)

            u.set_password(password)
            u.save()
            return redirect('/login')
        
        else:
            context = {}
            context['error'] = "Password and Confirm Password does not match"
            return render(request, 'register.html', context)



def user_login(request):
    if request.method == "GET":
        return render(request, 'login.html')
    
    else:
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)

            return redirect('/')
        
        else:
            context = {}
            context['error'] = "Invalid Username or Password"

            return render(request, 'login.html',context)
        


def user_logout(request):
    logout(request)
    return redirect('/')



@login_required(login_url="/login")
def create_cart(request, rid):

    prod = Product.objects.get(id = rid)
    
    cart = Cart.objects.filter(user = request.user, product = prod).exists()

    if cart:

        return redirect("/read_cart")
    
    else:

         user = User.objects.get(username = request.user)

         total_price = prod.price

         c = Cart.objects.create(product = prod, user = user, quantity = 1, total_price = total_price)

         c.save()
         return redirect("/login")



@login_required(login_url="/login")
def read_cart(request):

    c = Cart.objects.filter(user = request.user)
    
    context = {}

    context['data'] = c

    return render(request, 'readcart.html', context)



def delete_cart(request, rid):
    cart = Cart.objects.filter(id = rid)

    cart.delete()

    return redirect("/read_cart")


def update_cart(request, rid,q):
    Carts = Cart.objects.filter(id= rid)
    c = Cart.objects.get(id =rid)
    quantity = int(q)
    price = int(c.product.price)*quantity
    Carts.update(quantity=q, total_price=price)
    return redirect("/read_cart")


def create_orders(request, rid):
    cart = Cart.objects.get(id = rid)
    order = orders.objects.create(product = cart.product, user= request.user, quantity= cart.quantity, total_price= cart.total_price)
    order.save()
    cart.delete()
    return redirect('/read_cart')



def read_orders(request):
    order = orders.objects.filter(user = request.user)
    context = {}
    context['data'] = order
    return render(request, 'readorders.html', context)


def create_review(request, rid):
    if request.method == "GET":

        return render(request, 'createreview.html')
    else:
        title = request.POST['title']
        content = request.POST['content']
        rating = request.POST['rate']
        image = request.FILES['image']
        product = Product.objects.get(id = rid)
        review = Review.objects.create(product= product, user = request.user, title=title, content=content, rating=rating, image=image)
        review.save()
        return HttpResponse("Review Added")
        


def read_product_details(request, rid):
    prod= Product.objects.filter(id = rid)
    p = Product.objects.gte(id= rid)
    n = Review.objects.filter(product = p).count()
    rev = Review.objects.filter(product = p)
    sum = 0

    for x in rev:
        sum += x.rating

    try:
        avg=int(sum/n)
        avg_r = sum/n

    except:
        print("No review")

    context={}
    context['data'] = prod
    if n==0:
         context['avg'] = 'no review'
    else:
        context['avg_rating'] = avg
        context['avg']= avg_r
    return render(request, 'readproductdetails.html', context)
   

def forgot_password(request):
        if request.method == "GET":
            return render(request, 'forgotpassword.html')
        else:
            email = request.POST['email']

            request.session['email'] = email
            user = User.objects.filter(email = email).exists()
            if user:
                otp = random.randint(1000, 9999)
                request.session['otp'] = otp

            with get_connection(
                host = settings.EMAIL_HOST,
                port = settings.EMAIL_PORT,
                username = settings.EMAIL_HOST_USER,
                password = settings.EMAIL_HOST_PASSWORD,
                use_tls = settings.EMAIL_USE_TLS
            ) as connection :
                
                subject = " OTP Verification"
                email_from = settings.EMAIL_HOST_USER
                recipient_list = [email]
                message = f"OTP is {otp}"

                EmailMessage(subject, message, email_from, recipient_list, connection=connection
        ).send()
                return  redirect('/otp_verification')




def otp_verification(request):
    if request.method == "GET":
        return render(request, 'otp.html')
    else:
        otp = int(request.POST['otp'])
        email_otp = int(request.session['otp'])
        if otp == email_otp:
            return redirect('/newpassword')
        else:
             context = {}

             context['error']  = "OTP Does not match"
             return render(request, 'forgotpassword.html', context)


def new_password(request):
    if request.method == "GET":
        return render(request, 'newpassword.html')
    
    else:

        email = request.session['email']

        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        user = User.objects.get(email = email)

        if password == confirm_password:

            user.set_password(password)

            user.save()

            return redirect("/login")
        
        else:

            context = {}

            context['error'] = "Password and confirm password does not exist"

            return render(request, 'newpassword.html', context)