"""
Response format:
- success|<message>|<delay in milliseconds>
- error|<message>|<delay in milliseconds>
"""

from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rpi_api.models import Image, Logs, Temperature, RegisteredSensor, Power, IRSend
from utils.camera import capture_and_detect_humans
from django.utils import timezone
from utils.ir import IR
import datetime


last_motion_detected = None
led_delay_start = None
led_light = None
allowed_ir_send_hours = list(range(7, 21)) 

@csrf_exempt
def initial_connection(request):
    """
    This view is used to test the connection between ESP8266 and Raspberry Pi.
    """
    if request.method != "POST":
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid request method',
            'data': ''
        }, status=405)
    
    name = request.POST.get('name', None)
    battery_level = request.POST.get('battery_level', None)
    sensor_type = request.POST.get('sensor_type', None)

    if name is None or battery_level is None or sensor_type is None:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid registration data',
            'data': ''
        }, status=400)

    if RegisteredSensor.objects.filter(name=name).exists() == False:
        sensor = RegisteredSensor(name=name, battery_level=battery_level, sensor_type=sensor_type)
        sensor.save()
        return JsonResponse({
            'status': 'success',
            'message': 'Sensor registered',
            'data': ''
        })
    else:
        sensor = RegisteredSensor.objects.get(name=name)
        sensor.battery_level = battery_level
        sensor.save()
        return HttpResponse(f"success|Sensor already registered|{sensor.delay}")

@csrf_exempt
def receive_power(request):
    """
    This view is used to receive power data from ESP8266.
    """

    if request.method != 'POST':
        log = Logs(severity='WARNING', message='Invalid request method from Power Meter')
        log.save()
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid request method',
            'data': ''
        }, status=405)
    
    voltage = request.POST.get('voltage', None)
    current = request.POST.get('current', None)
    power = request.POST.get('power', None)
    energy = request.POST.get('energy', None)
    frequency = request.POST.get('frequency', None)
    power_factor = request.POST.get('power_factor', None)
    name = request.POST.get('name', None)
    battery_level = request.POST.get('battery_level', None)

    if name is None:
        log = Logs(severity='ERROR', message='Sensor name not found from Power Meter')
        log.save()
        return HttpResponse(f"error|Sensor name not found|", 400)
    
    if battery_level is None:
        log = Logs(severity='ERROR', message='Battery level not found from Power Meter')
        log.save()
        return HttpResponse(f"error|Battery level not found|", 400)
    
    if voltage is None:
        log = Logs(severity='ERROR', message='Voltage data not found from Power Meter')
        log.save()
        return HttpResponse(f"error|Voltage data not found|", 400)
    
    if current is None:
        log = Logs(severity='ERROR', message='Current data not found from Power Meter')
        log.save()
        return HttpResponse(f"error|Current data not found|", 400)
    
    if power is None:
        log = Logs(severity='ERROR', message='Power data not found from Power Meter')
        log.save()
        return HttpResponse(f"error|Power data not found|", 400)
    
    if energy is None:
        log = Logs(severity='ERROR', message='Energy data not found from Power Meter')
        log.save()
        return HttpResponse(f"error|Energy data not found|", 400)
    
    if frequency is None:
        log = Logs(severity='ERROR', message='Frequency data not found from Power Meter')
        log.save()
        return HttpResponse(f"error|Frequency data not found|", 400)
    
    if power_factor is None:
        log = Logs(severity='ERROR', message='Power Factor data not found from Power Meter')
        log.save()
        return HttpResponse(f"error|Power Factor data not found|", 400)
    
    # check if sensor exists
    is_sensor_exists = RegisteredSensor.objects.filter(name=name).exists()
    if is_sensor_exists == False:
        log = Logs(severity='ERROR', message=f'{name} is not registered')
        log.save()
        return HttpResponse(f"error|Sensor not registered|", 400)
    
    sensor = RegisteredSensor.objects.get(name=name)

    if sensor is None:
        log = Logs(severity='ERROR', message=f'{name} is not registered')
        log.save()
        return HttpResponse(f"error|Sensor not registered|", 400)
    
    sensor.battery_level = battery_level
    sensor.last_seen = timezone.now()
    sensor.save()

    power = Power(
        voltage=voltage,
        current=current,
        power=power,
        energy=energy,
        frequency=frequency,
        power_factor=power_factor,
        sensor_name=name
    )
    power.save()

    log = Logs(severity='SUCCESS', message=f'Meter data received from {name}')
    log.save()

    return HttpResponse(f"success|Meter data received|{sensor.delay}")



@csrf_exempt
def receive_temperature(request):
    """
    This view is used to receive temperature data from ESP8266.
    """

    if request.method != 'POST':
        log = Logs(severity='WARNING', message='Invalid request method from Temperature Sensor')
        log.save()
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid request method',
            'data': ''
        }, status=405)
    
    temperature = request.POST.get('temperature', None)
    humidity = request.POST.get('humidity', None)
    name = request.POST.get('name', None)
    battery_level = request.POST.get('battery_level', None)

    if name is None:
        log = Logs(severity='ERROR', message='Sensor name not found')
        log.save()
        return HttpResponse(f"error|Sensor name not found|", 400)
    
    if battery_level is None:
        log = Logs(severity='ERROR', message='Battery level not found')
        log.save()
        return HttpResponse(f"error|Battery level not found|", 400)

    if temperature is None:
        log = Logs(severity='ERROR', message='Temperature data not found')
        log.save()
        return HttpResponse(f"error|Temperature data not found|", 400)
    
    if humidity is None:
        log = Logs(severity='ERROR', message='Humidity data not found')
        log.save()
        return HttpResponse(f"error|Humidity data not found|", 400)

    sensor = RegisteredSensor.objects.get(name=name)

    if sensor is None:
        log = Logs(severity='ERROR', message='Sensor not registered')
        log.save()
        return HttpResponse(f"error|Sensor not registered|", 400)
    
    sensor.battery_level = battery_level
    sensor.last_seen = timezone.now()
    sensor.save()

    time_in_hour = datetime.datetime.now().hour
    
    last_ir_sent = IRSend.objects.all().order_by('-timestamp').first()

    if time_in_hour not in allowed_ir_send_hours and last_ir_sent.name != 'POWER_ON': 
        ir_send = IRSend(name='POWER_ON')
        ir_send.save()
        logs = Logs(severity='INFO', message='Power OFF command sent to IR Sender')
        logs.save()
        return HttpResponse(f"success|Temperature data received|{sensor.delay}")

    log = Logs(severity='SUCCESS', message=f'Received {temperature}°C from {name}')
    log.save()

    temperature = Temperature(temperature=temperature, sensor_name=name, humidity=humidity)
    temperature.save()

    return HttpResponse(f"success|Temperature data received|{sensor.delay}")


@csrf_exempt
def receive_motion(request):
    """
    This view is used to receive PIR sensor data from ESP8266.
    """

    global led_delay_start
    global led_light
    global last_motion_detected

    if request.method != 'POST':
        log = Logs(severity='WARNING', message='Invalid request method from Motion Sensor')
        log.save()
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid request method',
            'data': ''
        }, status=405)

    name = request.POST.get('name', None)
    battery_level = request.POST.get('battery_level', None)
    motion = request.POST.get('motion', None)

    if name is None:
        log = Logs(severity='ERROR', message='Sensor name not found')
        log.save()
        return HttpResponse(f"error|Sensor name not found|", 400)
    
    if battery_level is None:
        log = Logs(severity='ERROR', message='Battery level not found')
        log.save()
        return HttpResponse(f"error|Battery level not found|", 400)
    
    sensor = RegisteredSensor.objects.get(name=name)

    if sensor is None:
        log = Logs(severity='ERROR', message='Sensor not registered')
        log.save()
        return HttpResponse(f"error|Sensor not registered|", 400)

    if motion is None:
        log = Logs(severity='ERROR', message='Motion data not found')
        log.save()
        return HttpResponse(f"error|Motion data not found|", 400)
    
    last_motion_detected = Image.objects.all().order_by('-timestamp').first()

    if motion == 'false' and last_motion_detected and (timezone.now() - last_motion_detected.timestamp).total_seconds() > 300:
        led_light = False
        log = Logs(severity='INFO', message=f'No motion detected for 5 minutes from {name}')
        log.save()
        return HttpResponse(f"success|No motion detected for 5 minutes|{sensor.delay}")

    detection_result = capture_and_detect_humans()
    if detection_result['status'] == 'error':
        log = Logs(severity='ERROR', message=detection_result['message'])
        return JsonResponse(detection_result, status=500)

    log = Logs(severity='SUCCESS', message=f'{detection_result["data"]["human_count"]} humans detected in {detection_result["data"]["processing_time"]:.2f} seconds triggered by {name}')
    log.save()

    save_image = Image(
        image_name = detection_result['data']['image_name'],
        unique_id = detection_result['data']['unique_id'],
        detected_humans=detection_result['data']['human_count'],
        processing_time=detection_result['data']['processing_time'],
        sensor_name=name
    )

    save_image.save()

    sensor.battery_level = battery_level
    sensor.last_seen = timezone.now()   
    sensor.save()

    # check if IRSend have a row

    if IRSend.objects.all().exists() == False:
        ir_send = IRSend(name='Initial', received=True)
        ir_send.save()

    last_ir_send = IRSend.objects.all().order_by('-timestamp').first()
    time_in_hour = datetime.datetime.now().hour

    if time_in_hour not in allowed_ir_send_hours:
        log = Logs(severity='SUCCESS', message=f'Motion data received but no action was sent due to time restrictions')
        log.save()
        return HttpResponse(f"error|Motion data received but no action was sent due to time restrictions|{sensor.delay}")
    if detection_result['data']['human_count'] in list(range(0,5)) and last_ir_send.name != 'SET_24':
        ir_send = IRSend(name='SET_24')
        ir_send.save()
    elif detection_result['data']['human_count'] in list(range(5,21)) and last_ir_send.name != 'SET_22':
        ir_send = IRSend(name='SET_22')
        ir_send.save()
    elif detection_result['data']['human_count'] >= 20 and last_ir_send.name != 'SET_19':
        ir_send = IRSend(name='SET_19')
        ir_send.save()
    return HttpResponse(f"success|Motion data received|{sensor.delay}")
        


@csrf_exempt
def send_ir_data(request):
    """
    This view is used to send IR data to ESP8266.
    """
    
    if request.method != 'POST':
        log = Logs(severity='WARNING', message='Invalid request method from IR Sender')
        log.save()
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid request method',
            'data': ''
        }, status=405)
    
    battery_level = request.POST.get('battery_level', None)
    name = request.POST.get('name', None)

    if name is None:
        log = Logs(severity='ERROR', message='Sensor name not found')
        log.save()
        return HttpResponse(f"error|Sensor name not found|", 400)
    
    if battery_level is None:
        log = Logs(severity='ERROR', message='Battery level not found')
        log.save()
        return HttpResponse(f"error|Battery level not found|", 400)
    
    sensor = RegisteredSensor.objects.get(name=name)

    if sensor is None:
        log = Logs(severity='ERROR', message='Sensor not registered')
        log.save()
        return HttpResponse(f"error|Sensor not registered|", 400)
    
    sensor.battery_level = battery_level
    sensor.last_seen = timezone.now()
    sensor.save()

    ir_data = IRSend.objects.all().filter(received=False).first()
    if ir_data is None:
        return HttpResponse(f"error|No IR data available|{sensor.delay}", 400)

    ir_data.received = True
    ir_data.save()
    log = Logs(severity='SUCCESS', message=f'Sent IR data to {name}')
    log.save()
    return HttpResponse(f"success|{ir_data.name}|{sensor.delay}")


@csrf_exempt
def send_led_signal(request):
    """
    This view is used to send LED signal to ESP8266.
    """

    global led_delay_start
    global led_light
    global last_motion_detected

    if request.method != 'POST':
        log = Logs(severity='WARNING', message='Invalid request method from LED Sender')
        log.save()
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid request method',
            'data': ''
        }, status=405)
    
    battery_level = request.POST.get('battery_level', None)
    name = request.POST.get('name', None)

    if name is None:
        log = Logs(severity='ERROR', message='Sensor name not found')
        log.save()
        return HttpResponse(f"error|Sensor name not found|", 400)
    
    if battery_level is None:
        log = Logs(severity='ERROR', message='Battery level not found')
        log.save()
        return HttpResponse(f"error|Battery level not found|", 400)
    
    sensor = RegisteredSensor.objects.get(name=name)

    if sensor is None:
        log = Logs(severity='ERROR', message='Sensor not registered')
        log.save()
        return HttpResponse(f"error|Sensor not registered|", 400)
    
    sensor.battery_level = battery_level
    sensor.last_seen = timezone.now()
    sensor.save()

    image_data = Image.objects.all().order_by('-timestamp').first()
    if image_data is None:
        return HttpResponse(f"error|No image data available|{sensor.delay}", 400)
    
    if (timezone.now() - image_data.timestamp).total_seconds() > 1200:
        return HttpResponse(f"error|LOW|{sensor.delay}", 400)

    if image_data.detected_humans <= 0:
        return HttpResponse(f"error|LOW|{sensor.delay}", 400)
    
    return HttpResponse(f"success|HIGH|{sensor.delay}")
