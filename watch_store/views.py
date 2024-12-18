from django.shortcuts import render, get_object_or_404, redirect
from .models import Watch, Cart, UserProfile
from .forms import SignUpForm
from django.contrib.auth.views import LoginView
from django.contrib.auth.views import PasswordResetView
from django.contrib.auth import logout
from django.urls import reverse_lazy


def custom_watch(request):
    context = {
        'message': 'Welcome to the custom watch configurator!',
    }
    return render(request, 'shop/configurator.html', context)
def home_page(request):
    featured_watches = Watch.objects.all()[:3]  # Get the first 3 watches
    return render(request, 'shop/index.html', {'featured_watches': featured_watches})

def product_list(request):
    watches = Watch.objects.all()
    return render(request, 'shop/watches.html', {'watches': watches})

def product_detail(request, pk):
    watch = get_object_or_404(Watch, pk=pk)
    return render(request, 'shop/product_detail.html', {'watch': watch})

# Add an item to the cart or increase quantity
def add_to_cart(request, pk):
    watch = get_object_or_404(Watch, pk=pk)

    # Retrieve or create a cart item for the selected watch
    cart_item, created = Cart.objects.get_or_create(watch=watch)

    # Update the quantity and total price
    if not created:
        cart_item.quantity += 1
    else:
        cart_item.quantity = 1

    # Ensure quantity does not exceed stock
    cart_item.quantity = min(cart_item.quantity, watch.stock)

    # Update total price
    cart_item.total_price = cart_item.quantity * watch.price
    cart_item.save()

    return redirect('cart_view')


# Remove an item from the cart
def remove_from_cart(request, pk):
    cart_item = get_object_or_404(Cart, watch_id=pk)
    cart_item.delete()
    return redirect('cart_view')


# Update item quantity in the cart (increase or decrease)
def update_cart_quantity(request, pk, action):
    cart_item = get_object_or_404(Cart, watch_id=pk)

    if action == 'increase':
        if cart_item.quantity < cart_item.watch.stock:
            cart_item.quantity += 1
    elif action == 'decrease':
        cart_item.quantity -= 1
        if cart_item.quantity <= 0:
            cart_item.delete()
            return redirect('cart_view')

    # Update total price
    cart_item.total_price = cart_item.quantity * cart_item.watch.price
    cart_item.save()
    return redirect('cart_view')


# View to display the cart
def cart_view(request):
    cart_items = Cart.objects.all()  # Fetch all items in the cart
    total_price = sum(item.total_price for item in cart_items)  # Calculate overall total price
    return render(request, 'shop/cart.html', {'cart_items': cart_items, 'total_price': total_price})

def checkout(request):
    # Dummy checkout functionality
    Cart.objects.all().delete()  # Clear the cart after checkout
    return render(request, 'shop/checkout.html')

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()  # Save the user with email, first name, last name, etc.
            # Save the additional fields in the UserProfile model
            user_profile = UserProfile.objects.create(
                user=user,
                address=form.cleaned_data['address'],
                city=form.cleaned_data['city'],
                state=form.cleaned_data['state'],
                zip_code=form.cleaned_data['zip_code']
            )
            return redirect('login')  # Redirect to login page after successful signup
    else:
        form = SignUpForm()
    return render(request, 'shop/signup.html', {'form': form})

class CustomLoginView(LoginView):
    template_name = 'shop/login.html'  # Your custom login template

    def get_success_url(self):
        # Redirect logged-in users to the dashboard
        return '/'  # Change this to wherever you want the user to go

class CustomPasswordResetView(PasswordResetView):
    template_name = 'shop/reset_password.html'
    email_template_name = 'shop/password_reset_email.html'
    subject_template_name = 'shop/password_reset_subject.txt'
    success_url = reverse_lazy('password_reset_done')  # Redirect to the done page after success

def custom_logout(request):
    logout(request)
    return redirect('home')  # Redirect to the login page after logout


def profile(request):
    return render(request, 'shop/profile.html', {'user': request.user})