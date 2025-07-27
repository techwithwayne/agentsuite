from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from webdoctor.models import UserInteraction, AgentResponse, DiagnosticReport
from webdoctor.ai_agent import get_agent_response
import json
import re

def webdoctor_home(request):
    return render(request, 'webdoctor/chat_widget.html')

@csrf_exempt
def chat_widget(request):
    return render(request, 'webdoctor/chat_widget.html')

@csrf_exempt
def handle_message(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except (json.JSONDecodeError, ValueError) as e:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)
            
        message = data.get('message', '')
        lang = data.get('lang', 'en')

        # Validate required fields
        if not message.strip():
            return JsonResponse({'error': 'Message cannot be empty'}, status=400)

        session = request.session
        conversation = session.get("conversation", {
            "history": [],
            "stage": "initial",
            "category": None,
            "clarifications": 0
        })

        # Store current user message
        conversation["history"].append({"role": "user", "content": message})

        try:
            # Get AI-generated response
            ai_response = get_agent_response(
                history=conversation["history"],
                stage=conversation["stage"],
                category=conversation["category"],
                clarifications=conversation["clarifications"],
                lang=lang
            )
        except Exception as e:
            # Log the error in a real application
            return JsonResponse({'error': 'Unable to process request at this time'}, status=500)

        # Update session state
        conversation["history"].append({"role": "assistant", "content": ai_response["response"]})
        conversation["stage"] = ai_response["next_stage"]
        conversation["category"] = ai_response.get("category", conversation["category"])
        conversation["clarifications"] = ai_response.get("clarifications", conversation["clarifications"])
        session["conversation"] = conversation
        session.modified = True

        # Store response if unique
        AgentResponse.get_or_create_response(ai_response["response"])

        return JsonResponse({
            "response": ai_response["response"],
            "typing_delay": ai_response.get("typing_delay", 4),
            "stage": ai_response.get("next_stage", "initial")
        })

    return JsonResponse({'error': 'Invalid method'}, status=405)

@csrf_exempt
def submit_form(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except (json.JSONDecodeError, ValueError) as e:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)
            
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        issue = data.get('issue', '').strip()

        # Validate required fields
        if not all([name, email, issue]):
            return JsonResponse({'error': 'All fields are required'}, status=400)

        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            return JsonResponse({'error': 'Invalid email format'}, status=400)

        try:
            UserInteraction.objects.create(name=name, email=email, issue_description=issue)

            report_content = (
                f"Diagnostic Report for {name}\n"
                f"Issue: {issue}\n"
                f"Suggested Actions: Check hosting performance, optimize images, or contact Wayne's team for a free consultation."
            )

            DiagnosticReport.objects.create(
                user_email=email,
                issue_details=issue,
                report_content=report_content
            )
        except Exception as e:
            # Log the error in a real application
            return JsonResponse({'error': 'Unable to save report at this time'}, status=500)

        return JsonResponse({'message': 'Report sent to your email!'})

    return JsonResponse({'error': 'Invalid method'}, status=405)
