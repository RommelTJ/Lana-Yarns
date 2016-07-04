from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import render

from products.models import Product, ProductFeatured
from .forms import ContactForm, SignUpForm
from .models import SignUp

# Create your views here.


def home(request):
    title = 'Sign Up Now'
    featured_product = ProductFeatured.objects.filter(active=True).order_by('-timestamp').first()
    products = Product.objects.all().order_by('?')[:4]
    form = SignUpForm(request.POST or None)
    context = {
        "title": title,
        "form": form,
        'featured_product': featured_product,
        'products': products,
    }
    if form.is_valid():
        instance = form.save(commit=False)

        full_name = form.cleaned_data.get("full_name")
        if not full_name:
            full_name = "New full name"
        instance.full_name = full_name
        instance.save()
        context = {
            "title": "Thank you"
        }

    return render(request, "home.html", context)


def contact(request):
    title = 'Contact Us'
    title_align_center = True
    form = ContactForm(request.POST or None)
    if form.is_valid():
        form_email = form.cleaned_data.get("email")
        form_message = form.cleaned_data.get("message")
        form_full_name = form.cleaned_data.get("full_name")
        subject = 'Site contact form'
        from_email = settings.EMAIL_HOST_USER
        to_email = [from_email, 'lana@lanayarns.com']
        contact_message = "%s: %s via %s"%(
            form_full_name,
            form_message,
            form_email)
        some_html_message = """
        <h1>hello</h1>
        """
        send_mail(subject,
                  contact_message,
                  from_email,
                  to_email,
                  html_message=some_html_message,
                  fail_silently=True)

    context = {
        "form": form,
        "title": title,
        "title_align_center": title_align_center,
    }
    return render(request, "forms.html", context)
