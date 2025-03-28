from utils.camera import capture_and_detect_humans
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from rpi_api.models import IRSend
from django.contrib import messages
from utils.ir import IR

@login_required(login_url='/')
def test_camera(request):
    """
    This view is used to test the camera and human detection.
    """
    detection_result = capture_and_detect_humans()
    if detection_result['status'] == 'error':
        context = {
            'message': detection_result['message'],
            'data': detection_result['data'],
            'status': detection_result['status']
        }
    else:
        context = {
            'message': detection_result['message'],
            'data': detection_result['data'],
            'image': detection_result['data']['image_name'],
            'status': detection_result['status']
        }
    return render(request, 'tests/camera.html', context)

@login_required(login_url='/')
def test_ir(request, command):
    """
    This view is used to test the IR reader.
    """

    if command not in IR.commands:
        context = {
            'message': 'Command does not exists',
            'status': 'error'
        }
    else:
        # Clear all previous signals
        ir_send = IRSend.objects.filter(received=False)
        if ir_send.exists():
            for ir in ir_send:
                ir.received = True
                ir.save()
        
        # Create new signal
        ir = IRSend(name=command)
        ir.save()
        context = {
            'message': f'Signal {command} sent',
            'status': 'success'
        }
    return render(request, 'tests/ir.html', context)