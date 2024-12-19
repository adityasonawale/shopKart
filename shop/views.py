from http.client import HTTPResponse
import json
from django.http import JsonResponse
from django.shortcuts import render, redirect
from .models import *
from django.contrib import messages
from shop.form import CustomUserForm
from django.contrib.auth import authenticate, login, logout


def home(request) :
    products = Product.objects.filter(trending=1)
    return render(request, "shop/index.html", {"products" : products}) 

def favviewpage(request) :
    if request.user.is_authenticated :
        fav = Favorite.objects.filter(user = request.user)
        return render(request, 'shop/fav.html', {"fav" : fav})
    else :
        return redirect("/")

def cart_page(request) :
    if request.user.is_authenticated :
        cart = Cart.objects.filter(user = request.user)
        return render(request, 'shop/cart.html', {"cart" : cart})
    else :
        return redirect("/")
    
def remove_fav(request, fid) :
    item = Favorite.objects.get(id = fid)
    item.delete()
    return redirect("/favviewpage")
    
def remove_cart(request, cid) :
    cartitem = Cart.objects.get(id = cid)
    cartitem.delete()
    return redirect("/cart")

def fav_page(request) :
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' :
        if request.user.is_authenticated :
            data = json.load(request)
            product_id = data['pid']
            product_status = Product.objects.get(id = product_id)
            if product_status :
                if Favorite.objects.filter(user = request.user.id, product_id = product_id) :
                    return JsonResponse({'status' : 'product already in favorite !'}, status = 200)
                else :
                    Favorite.objects.create(user = request.user, product_id = product_id)
                    return JsonResponse({'status' : 'Product added to favorite'}, status = 200)
        else :
            return JsonResponse({'status' : 'LogIn to add cart'}, status = 200)
    else :
        return JsonResponse({'status' : 'Invalid Access'}, status = 200)

def add_to_cart(request) :
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' :
        if request.user.is_authenticated :
            data = json.load(request)
            product_qty = data['product_qty']
            product_id = data['pid']
            product_status = Product.objects.get(id = product_id)
            if product_status :
                if Cart.objects.filter(user = request.user.id, product_id = product_id) :
                    return JsonResponse({'status' : 'product already in cart !'}, status = 200)
                else :
                    if product_status.quantity >= product_qty :
                        Cart.objects.create(user = request.user, product_id = product_id, product_qty = product_qty)
                        return JsonResponse({'status' : 'product added to cart !'}, status = 200)
                    else :
                        return JsonResponse({'status' : 'product stock not available !'}, status = 200)
            return JsonResponse({'status' : 'product added successfully !'}, status = 200)
        else :
            return JsonResponse({'status' : 'LogIn to add cart'}, status = 200)
    else :
        return JsonResponse({'status' : 'Invalid Access'}, status = 200)

def logout_page(request) :
    if request.user.is_authenticated :
        logout(request)
        messages.success(request, "Logged Out Successfully !")
    return redirect('/')

def login_page(request) :
    if request.user.is_authenticated :
        return redirect('/')
    else :
        if request.method == 'POST' :
            name = request.POST.get('username')
            pwd = request.POST.get('password')
            user = authenticate(request, username = name, password = pwd)
            if user is not None :
                login(request, user)
                messages.success(request, "Logged In Successfully !")
                return redirect('/')
            else :
                messages.error(request, "Invalid Username OR Password")
                return redirect('/login')
    return render(request, "shop/login.html") 

def register(request) :
    form = CustomUserForm()
    if request.method == 'POST' :
        form = CustomUserForm(request.POST)
        if form.is_valid() :
            form.save()
            messages.success(request, "Registration Successful !")
            return redirect('login')
    return render(request, "shop/register.html", {"form" : form}) 

def collections(request) :
    category = Category.objects.filter(status=0)
    return render(request, "shop/collections.html", {"category" : category})

def collectionsview(request, name) :
    if(Category.objects.filter(name = name, status=0)) :
        products = Product.objects.filter(category__name = name)
        return render(request, "shop/products/index.html", {"products" : products, "category_name" : name})
    else:
        messages.warning(request, "No such category found !")
        return redirect('collections')
    
def product_details(request, cname, pname) :
    if(Category.objects.filter(name = cname, status=0)) :
        if(Product.objects.filter(name = pname, status=0)) :
            products = Product.objects.filter(name = pname, status = 0).first()
            return render(request, "shop/products/product_details.html", {"products" : products})
        else:
            messages.warning(request, "No such category found !")
            return redirect('collections')
    else:
            messages.warning(request, "No such category found !")
            return redirect('collections')