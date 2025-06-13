from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse, Http404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from .models import Message
from .forms import MessageForm

@login_required
def inbox(request):
    """
    Display a list of received messages for the logged-in user.
    """
    messages = Message.objects.filter(recipient=request.user).order_by('-created_at')
    paginator = Paginator(messages, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'communication/inbox.html', {'page_obj': page_obj})

@login_required
def sent_messages(request):
    """
    Display a list of sent messages for the logged-in user.
    """
    messages = Message.objects.filter(sender=request.user).order_by('-created_at')
    paginator = Paginator(messages, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'communication/sent_messages.html', {'page_obj': page_obj})

@login_required
def message_detail(request, pk):
    """
    Display the details of a single message.
    """
    message = get_object_or_404(Message, pk=pk)
    if message.recipient != request.user and message.sender != request.user:
        raise Http404("You do not have permission to view this message.")
    return render(request, 'communication/message_detail.html', {'message': message})

@login_required
def compose_message(request):
    """
    Compose and send a new message.
    """
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.sender = request.user
            msg.save()
            return redirect('communication:sent_messages')
    else:
        form = MessageForm()
    return render(request, 'communication/compose_message.html', {'form': form})

@login_required
@require_POST
def delete_message(request, pk):
    """
    Delete a message (only by sender or recipient).
    """
    message = get_object_or_404(Message, pk=pk)
    if message.recipient == request.user or message.sender == request.user:
        message.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Permission denied.'}, status=403)
