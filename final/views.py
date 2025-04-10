from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse

CHATBOT_API_URL = "http://127.0.0.1:8001/chatbot/ask/"

def chatbot_view(request):
    return render(request, 'scholarships/chatbot.html')

import requests
from django.http import JsonResponse

CHATBOT_API_URL = "http://127.0.0.1:8001/chatbot/ask/"

def send_question_to_chatbot(request):
    print("Received request to /chatbot/ask...")
    
    if request.method == 'POST':
        try:
            # Parse the JSON data from the request body
            data = json.loads(request.body)
            question = data.get('question', '')
            print(f"Received question: {question}")  # Debugging print

            if not question:
                return JsonResponse({'error': 'No question provided'}, status=400)

            try:
                # Send the question to the FastAPI chatbot API
                response = requests.post(CHATBOT_API_URL, json={'question': question})
                print(f"FastAPI response status: {response.status_code}")
                print(f"FastAPI response content: {response.content}")

                if response.status_code == 200:
                    data = response.json()
                    return JsonResponse({'answer': data.get('answer', '')})
                else:
                    return JsonResponse({'error': 'Error from chatbot API'}, status=response.status_code)
            except Exception as e:
                print(f"Error during FastAPI request: {e}")
                return JsonResponse({'error': str(e)}, status=500)

        except json.JSONDecodeError:
            print("Error decoding JSON.")
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)

    return JsonResponse({'error': 'Invalid HTTP method'}, status=405)
def home(request):
    return render(request, 'scholarships/home.html')

# Signup view
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('home')  # Redirect to home after successful login
    else:
        form = UserCreationForm()
    return render(request, 'scholarships/signup.html', {'form': form})

# Login view
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')  # Redirect to home after login
        else:
            # Add error handling here
            messages.error(request, 'Invalid credentials, please try again.')
    return render(request, 'scholarships/login.html')

@login_required(login_url='login')
def dashboard(request):
    print(f"User: {request.user.username} logged in successfully.")
    return render(request, 'scholarships/dashboard.html')

