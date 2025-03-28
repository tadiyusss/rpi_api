from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from rpi_api.forms import LoginForm, ManageSensor
from rpi_api.models import Image, Logs, Temperature, RegisteredSensor, Power
from django.shortcuts import get_object_or_404
import csv
from utils.ir import IR

def login(request):
    form = LoginForm()

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                log = Logs(severity='INFO', message=f'User {username} logged in')
                log.save()
                auth_login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid username or password')

    context = {
        'form': form
    }
        
    return render(request, 'login.html', context)

@login_required(login_url='/')
def manage_settings(request):
    context = {
        'ir_buttons': IR.commands
    }
    return render(request, 'dashboard/settings.html', context)

@login_required(login_url='/')
def dashboard(request):
    
    context = {
        'images': Image.objects.all().order_by('-timestamp'),
        'logs': Logs.objects.all().order_by('-timestamp'),
        'temperatures': Temperature.objects.all().order_by('-timestamp'),
        'registered_sensors': RegisteredSensor.objects.all().order_by('-last_seen'),
        'power_meter': Power.objects.all().order_by('-timestamp')
    }
    return render(request, 'dashboard/home.html', context)

@login_required(login_url='/')
def manage_sensor(request, sensor_name):
    sensor = get_object_or_404(RegisteredSensor, name=sensor_name)
    form = ManageSensor(instance=sensor)
    
    if sensor.sensor_type == 'temperature':
        logs = Temperature.objects.filter(sensor_name=sensor_name).order_by('-timestamp')
    elif sensor.sensor_type == 'motion':
        logs = Image.objects.filter(sensor_name=sensor_name).order_by('-timestamp')
    elif sensor.sensor_type == 'meter':
        logs = Power.objects.filter(sensor_name=sensor_name).order_by('-timestamp')
    else:
        logs = []
    if request.method == 'POST':
        form = ManageSensor(request.POST, instance=sensor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Delay updated successfully')
            return redirect('manage_sensor', sensor_name=sensor_name)
        else:
            messages.error(request, 'Invalid form data provided')

    context = {
        'sensor': sensor,
        'form': form,
        'logs': logs,
        'sensor_type': sensor.sensor_type
    }
    return render(request, 'dashboard/manage_sensor.html', context)


def export_temperatures(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="temperature_readings.csv"'

    writer = csv.writer(response)
    writer.writerow(['Temperature', 'Timestamp', 'Sensor Name'])

    for temperature in Temperature.objects.all().order_by('-timestamp'):
        writer.writerow([temperature.temperature, temperature.timestamp, temperature.sensor_name])

    return response

def export_power_meter(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="power_meter.csv"'

    writer = csv.writer(response)
    writer.writerow(['Voltage', 'Current', 'Power', 'Energy', 'Frequency', 'Power Factor', 'Timestamp', 'Sensor Name'])

    for power in Power.objects.all().order_by('-timestamp'):
        writer.writerow([power.voltage, power.current, power.power, power.energy, power.frequency, power.power_factor, power.timestamp, power.sensor_name])

    return response

def export_images(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="image_logs.csv"'

    writer = csv.writer(response)
    writer.writerow(['Image Name', 'Detected Humans', 'Processing Time', 'Timestamp', 'Sensor Name'])

    for image in Image.objects.all().order_by('-timestamp'):
        writer.writerow([image.image_name, image.detected_humans, image.processing_time, image.timestamp, image.sensor_name])

    return response

@login_required(login_url='/')
def logout(request):
    log = Logs(severity='INFO', message=f'User {request.user.username} logged out')
    auth_logout(request)
    return redirect('login')

