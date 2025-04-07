import os
import shutil
from dotenv import load_dotenv
from django.template.loader import render_to_string
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.files import File
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings
from django.utils import timezone
from random import choices
from django.utils.html import strip_tags

import datetime
from . import forms
from .models import Model, Make, BodyStyle, TransmissionType, Fuel, Color, DoorCount, Condition, Picture, UploadImage, Ad, Category, CustomUser

load_dotenv()

def index_request(request):
    ads = Ad.objects.filter(date_expire__gte=timezone.now())

    if len(ads) >= 6:
        premium_ads = choices(ads, k=6)
    else:
        premium_ads = ads

    makes = Make.objects.order_by('name')

    context = {
        'title': 'Carstrucx | Vehicle Marketplace',
        'ad_count': len(ads),
        'user_count': int(len(ads) * 0.9),
        'premium_ads': premium_ads,
        'makes': makes
    }

    return render(request, 'index.html', context=context)

def contact_request(request):
    return render(request, 'contact.html', {'title': 'Contact Us | Carstrucx'})

def terms_request(request):
    return render(request, 'terms.html', {'title': 'Terms Of Use | Carstrucx'})

def safety_request(request):
    return render(request, 'safety.html', {'title': 'Safety | Carstrucx'})

def privacy_request(request):
    return render(request, 'privacy.html', {'title': 'Privacy Policy | Carstrucx'})

def login_request(request):
    if request.method == 'POST':
        next_url = request.POST.get('next')
        if next_url == None or next_url == '':
            next_url = 'cardealer:index'
        form = AuthenticationForm(request, data=request.POST)
        
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect(next_url)
        else:
            user = CustomUser.objects.filter(username=request.POST['username'])
            
            if len(user) > 0:
                if user[0].is_active == 0:
                    context = {
                        'title': 'Login | Carstrucx',
                        'all_error': 'Your account is not allowed yet. Please wait.'
                    }

                    return render(request, 'login.html', context=context)
        
            context = {
                'title': 'Login | Carstrucx',
                'username_error': form.errors.get('username'),
                'password_error': form.errors.get('password'),
                'all_error': form.errors.get('__all__')
            }
            return render(request, 'login.html', context=context)

    return render(request, 'login.html', {'title': 'Login | Carstrucx'})

def logout_request(request):
    logout(request)
    return redirect('cardealer:index')

def register_request(request):
    if request.method == 'POST':
        form = forms.RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.is_active = False
            user.save()
            
            return redirect('cardealer:index')
        else:
            context = {
                'title': 'Register | Carstrucx',
                'username_error': form.errors.get('username'),
                'email_error': form.errors.get('email'),
                'password1_error': form.errors.get('password1'),
                'password2_error': form.errors.get('password2'),
                'all_error': form.errors.get('__all__')
            }
            return render(request, 'register.html', context=context)
    else:
        return render(request, 'register.html', {'title': 'Register | Carstrucx'})

def listing_request(request):
    ad_list = Ad.objects.filter(date_expire__gte=timezone.now()).order_by('-date_posted')

    user = request.GET.get('user', '')
    if user != '':
        ad_list = ad_list.filter(user=user)

    category = request.GET.get('category', '')
    if category != '':
        ad_list = ad_list.filter(category=category)

    make = request.GET.get('make', '')
    if make != '':
        ad_list = ad_list.filter(make=make)

    title = request.GET.get('title', '')
    if title != '':
        ad_list = ad_list.filter(title__icontains=title)

    manufacture_year = request.GET.get('manufacture_year', '')
    if manufacture_year != '':
        ad_list = ad_list.filter(manufacture_year=manufacture_year)

    page = request.GET.get('page', 1)
    paginator = Paginator(ad_list, 50)
    try:
        ads = paginator.page(page)
    except PageNotAnInteger:
        ads = paginator.page(1)
    except EmptyPage:
        ads = paginator.page(paginator.num_pages)

    context = {
        'title': 'Listing | Carstrucx',
        'ads': ads,
        'makes': Make.objects.all(),
        'bodystyle': BodyStyle.objects.all(),
    }
    
    return render(request, 'listing.html', context=context)

def error_404(request, exception):
    return render(request, '404.html', {'title': 'Page Not Found | Carstrucx'})

def detail_request(request, pk):
    ad = Ad.objects.get(pk=pk)
    ad.views += 1
    ad.save()

    context = {
        'id': ad.id,
        'category': ad.category.name,
        'title': ad.title,
        'price': ad.price,
        'mileage': ad.mileage,
        'posted_date': ad.date_posted,
        'views': ad.views,
        'description': ad.description,
        'owner': ad.user,
        'email': ad.user.email,
        'bodystyle': ad.bodystyle,
        'color': ad.color,
        'condition': ad.condition,
        'fuel': ad.fuel,
        'make': ad.make,
        'model': ad.model,
        'transtype': ad.transtype,
        'manufacture_year': ad.manufacture_year,
        'doorcount': ad.doorcount,
        'state': ad.state,
        'city': ad.city,
        'zip': ad.zip,
        'pictures': Picture.objects.filter(ad=ad)
    }

    return render(request, 'detail.html', context=context)

def getmodels_request(request):
    if request.method == 'POST':
        make = request.POST['make']
        models = Model.objects.filter(make=make)
        result = []

        for model in models:
            result.append({'id': model.id, 'name': model.name})
        
        return JsonResponse(result, safe=False)

def sendmail_request(request):
    if request.method == 'POST':
        client = request.POST['client_name']
        subject = request.POST['subject']
        question = request.POST['message']
        sender = request.POST['email_from']
        receiver = request.POST['email_to']
        ad_link = request.POST['ad_link']
        
        body = render_to_string("email.html", {'question': question, 'ad_link': ad_link, 'email': sender})
        
        send_mail(
            subject=subject,
            message=strip_tags(body),
            from_email=f"{client} <{os.getenv('EMAIL_FROM')}>",
            recipient_list=[receiver],
            fail_silently=False,
            auth_user=os.getenv('EMAIL_USER'),
            auth_password=os.getenv('EMAIL_PASSWORD'),
            html_message=body
        )
        
        # msg = MIMEMultipart()
        # msg['From'] = f'{client} <no-reply@xethost.com>'
        # msg['To'] = receiver
        # msg['Subject'] = subject
        
        # body = render_to_string("email.html", {'question': question, 'ad_link': ad_link, 'email': sender})
        
        # msg.attach(MIMEText(body, 'html'))
        
        # EMAIL_HOST = os.getenv('EMAIL_HOST')
        # EMAIL_USER = os.getenv('EMAIL_HOST_USER')
        # EMAIL_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
        
        # with smtplib.SMTP_SSL(EMAIL_HOST, 465, ssl.create_default_context()) as server:
        #     server.login(EMAIL_USER, EMAIL_PASSWORD)
        #     server.sendmail(EMAIL_USER, receiver, msg.as_string())
        
        return HttpResponse('success')

def gettrovitxml_request(request):
    ads = Ad.objects.filter(date_expire__gte=timezone.now())

    context = {
        'ads': ads
    }

    return render(request, 'trovit_feed.xml', context=context, content_type='application/xhtml+xml')

def getoodlexml_request(request):
    ads = Ad.objects.filter(date_expire__gte=timezone.now())

    context = {
        'ads': ads
    }

    return render(request, 'oodle_feed.xml', context=context, content_type='application/xhtml+xml')

def getlocantoxml_request(request):
    ads = Ad.objects.filter(date_expire__gte=timezone.now())

    context = {
        'ads': ads
    }

    return render(request, 'locanto_feed.xml', context=context, content_type='application/xhtml+xml')

def getooyyoxml_request(request):
    ads = Ad.objects.filter(date_expire__gte=timezone.now())

    context = {
        'ads': ads
    }

    return render(request, 'ooyyo_feed.xml', context=context, content_type='application/xhtml+xml')

@login_required
def post_ad_request(request):
    if request.method == 'POST':
        form = forms.PostAdForm(request.POST)
        
        if form.is_valid():
            ad = form.save(commit=False)
            ad.user = request.user
            ad.user.save()
            
            date_posted = timezone.now()
            date_expire = date_posted + datetime.timedelta(days=30)
            ad.date_posted = date_posted
            ad.date_expire = date_expire
            ad.save()
            
            uploaded_images = UploadImage.objects.filter(user=request.user)
            for uploaded_image in uploaded_images:
                ad_image = Picture()
                ad_image.ad = ad

                ad_image.image = File(uploaded_image.image, f'{ad.id}/full/{ad.title}_{os.path.basename(uploaded_image.image.name)}')
                ad_image.thumb_big = File(uploaded_image.image, f'{ad.id}/big/{ad.title}_{os.path.basename(uploaded_image.image.name)}')
                ad_image.thumb_med = File(uploaded_image.image, f'{ad.id}/med/{ad.title}_{os.path.basename(uploaded_image.image.name)}')
                ad_image.thumb_small = File(uploaded_image.image, f'{ad.id}/small/{ad.title}_{os.path.basename(uploaded_image.image.name)}')

                ad_image.name = f'{ad.title}_{os.path.basename(uploaded_image.image.name)}'
                ad_image.save()
                uploaded_image.image.close()
                uploaded_image.delete()

            return redirect('cardealer:detail', pk=ad.id)
        else:
            makes = Make.objects.all()

            context = {
                'title': 'Post Ad | Carstrucx',
                'styles': BodyStyle.objects.all(),
                'makes': Make.objects.all(),
                'models': Model.objects.filter(make=makes[0]),
                'transtypes': TransmissionType.objects.all(),
                'fuels': Fuel.objects.all(),
                'colors': Color.objects.all(),
                'doorcounts': DoorCount.objects.all(),
                'conditions': Condition.objects.all(),
                'categories': Category.objects.all(),
                'description_error': form.errors.get('description')
            }

            uploaded_images = UploadImage.objects.filter(user=request.user)
            for uploaded_image in uploaded_images:
                uploaded_image.delete()
                
            return render(request, 'post-ad.html', context=context)
    else:
        makes = Make.objects.all()

        context = {
            'title': 'Post Ad | Carstrucx',
            'styles': BodyStyle.objects.all(),
            'makes': Make.objects.all(),
            'models': Model.objects.filter(make=makes[0]),
            'transtypes': TransmissionType.objects.all(),
            'fuels': Fuel.objects.all(),
            'colors': Color.objects.all(),
            'doorcounts': DoorCount.objects.all(),
            'conditions': Condition.objects.all(),
            'categories': Category.objects.all(),
        }
        
        return render(request, 'post-ad.html', context=context)

@login_required
def upload_request(request):
    if request.method == 'POST':
        my_file = request.FILES.get('file')
        my_file.name = f'{request.user.id}_{my_file.name}'
        UploadImage.objects.create(user=request.user, image=my_file)
        return JsonResponse({'status': 'success'})

@login_required
def profile_request(request):
    ads = Ad.objects.filter(date_expire__gte=timezone.now())
    visits = 0

    for ad in ads:
        visits += ad.views

    context = {
        'title': 'Profile | Carstrucx',
        'count': len(Ad.objects.filter(date_expire__gte=timezone.now()).filter(user=request.user)),
        'visits': visits
    }

    if request.method == 'POST':
        form = forms.CustomUserChangeForm(request.POST, instance=request.user)
        
        if form.is_valid():
            form.save()

        return redirect('cardealer:profile')

    return render(request, 'profile.html', context=context)

@login_required
def deactive_request(request):
    return render(request, 'deactive.html')

@login_required
def delete_request(request, pk):
    ad = Ad.objects.get(pk=pk)

    if ad.user == request.user or request.user.username == 'admin':
        pictures = Picture.objects.filter(ad=ad)

        for picture in pictures:
            picture.delete()

        shutil.rmtree(os.path.join(settings.MEDIA_ROOT, 'images', str(ad.id)), ignore_errors=True)
        ad.delete()

    return redirect('cardealer:index')

@login_required
def edit_request(request, pk):
    ad = Ad.objects.get(pk=pk)

    if request.method == 'POST':
        if ad.user == request.user:
            form = forms.PostAdForm(request.POST, instance=ad)
            
            if form.is_valid():
                form.save()
            else:
                context = {
                    'ad': ad,
                    'title': 'Edit Ad | Carstrucx',
                    'styles': BodyStyle.objects.all(),
                    'makes': Make.objects.all(),
                    'models': Model.objects.all(),
                    'transtypes': TransmissionType.objects.all(),
                    'fuels': Fuel.objects.all(),
                    'colors': Color.objects.all(),
                    'doorcounts': DoorCount.objects.all(),
                    'conditions': Condition.objects.all(),
                    'categories': Category.objects.all(),
                    'description_error': form.errors.get('description')
                }

                return render(request, 'post-ad.html', context=context)
    else:
        if ad.user == request.user:
            context = {
                'ad': ad,
                'title': 'Edit Ad | Carstrucx',
                'styles': BodyStyle.objects.all(),
                'makes': Make.objects.all(),
                'models': Model.objects.all(),
                'transtypes': TransmissionType.objects.all(),
                'fuels': Fuel.objects.all(),
                'colors': Color.objects.all(),
                'doorcounts': DoorCount.objects.all(),
                'conditions': Condition.objects.all(),
                'categories': Category.objects.all(),
            }

            return render(request, 'post-ad.html', context=context)

    return redirect('cardealer:detail', pk=pk)
