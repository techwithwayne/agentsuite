import os
from django.conf import settings

def get_openai_client():
    from openai import OpenAI
    api_key = os.getenv("OPENAI_API_KEY", getattr(settings, "OPENAI_API_KEY", None))
    if not api_key:
        raise ValueError("OpenAI API key not found. Please set OPENAI_API_KEY environment variable or in Django settings.")
    return OpenAI(api_key=api_key)

DIAGNOSTIC_CATEGORIES = {
    "Performance": ["slow", "lag", "takes forever", "8 seconds", "load time"],
    "Design/Layout": ["broken", "misaligned", "mobile", "images", "fonts", "responsive"],
    "Functionality": ["form", "button", "submit", "not working", "doesn't work"],
    "Access/Errors": ["403", "404", "500", "white screen", "can't log in", "error"],
    "Update/Plugin": ["plugin", "update", "theme", "broke", "conflict"],
    "Security/Hack": ["hacked", "spam", "malware", "injected", "redirect"],
    "Hosting/DNS": ["dns", "hosting", "cloudflare", "propagation", "server"]
}

def get_clarifying_questions(category):
    fallback = [
        "Can you clarify the problem a bit more?",
        "What exactly happens when the issue occurs?",
        "When did the issue start and how often does it happen?"
    ]
    question_bank = {
        "Performance": [
            "Is your site slow to load on all devices and browsers, or only some?",
            "Does it load slowly on both Wi-Fi and mobile data?",
            "Has anything recently changed on your site before it got slow?"
        ],
        "Design/Layout": [
            "What part of the design looks broken or off?",
            "Is the issue happening on mobile, desktop, or both?",
            "Has the layout issue always been there or did it just start recently?"
        ],
        "Functionality": [
            "Which feature or page isn't working as expected?",
            "What do you expect to happen vs what actually happens?",
            "Have you tested this in multiple browsers?"
        ],
        "Access/Errors": [
            "What error are you seeing (e.g. 403, 404, white screen)?",
            "When does the error appear — right when loading the site or after clicking something?",
            "Are others also seeing this error, or just you?"
        ],
        "Update/Plugin": [
            "Did the problem start after installing or updating a plugin or theme?",
            "Which plugins/themes have you recently changed?",
            "Have you tried deactivating plugins to see if one causes it?"
        ],
        "Security/Hack": [
            "What makes you think the site was hacked?",
            "Are you seeing popups, redirects, or strange content?",
            "Have you recently changed passwords or installed security tools?"
        ],
        "Hosting/DNS": [
            "Have you recently switched hosting providers or made DNS changes?",
            "Is your domain showing any errors in DNS tools?",
            "Have you contacted your hosting provider about this?"
        ]
    }
    return question_bank.get(category, fallback)

def classify_issue(user_input):
    if not user_input or not user_input.strip():
        return "Unclassified", 0, "Can you describe the issue a bit more so I can help?"
    
    prompt = f"""
You are a helpful support agent. Categorize the user's website issue into one of these diagnostic categories:
{", ".join(DIAGNOSTIC_CATEGORIES.keys())}

Respond in this format:
Category: <CATEGORY>
Confidence: <0–100>
ClarifyingQuestion: <QUESTION to understand issue better>

User Input:
\"{user_input}\"
"""
    
    try:
        client = get_openai_client()
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You classify website problems into categories and ask clarifying questions."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4
        )

        result = response.choices[0].message.content.strip()
        lines = result.splitlines()
        category = "Unclassified"
        confidence = 0
        clarifying_question = "Can you describe the issue a bit more so I can help?"

        for line in lines:
            line = line.strip()
            if line.startswith("Category:"):
                category = line.replace("Category:", "").strip()
            elif line.startswith("Confidence:"):
                try:
                    confidence_str = line.replace("Confidence:", "").strip()
                    confidence = int(confidence_str)
                    # Ensure confidence is within valid range
                    confidence = max(0, min(100, confidence))
                except (ValueError, TypeError):
                    confidence = 50
            elif line.startswith("ClarifyingQuestion:"):
                clarifying_question = line.replace("ClarifyingQuestion:", "").strip()

        return category, confidence, clarifying_question
    
    except Exception as e:
        # Log the error in a real application
        print(f"Error in classify_issue: {e}")
        return "Unclassified", 0, "I'm having trouble processing your request. Can you describe the issue a bit more?"

def summarize_issue(history, category):
    if not history:
        return "I don't have enough information about your issue yet."
    
    user_messages = [m['content'] for m in history if m.get('role') == 'user' and m.get('content')]
    
    if not user_messages:
        return "I don't have enough information about your issue yet."
    
    summary_prompt = f"""
You are a helpful AI support agent. Summarize the user's issue based on this conversation in a friendly and clear way.

Category: {category}
Conversation:
{chr(10).join(user_messages)}

Respond in 1–3 sentences like a website doctor would explain it to the user.
"""
    
    try:
        client = get_openai_client()
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You summarize website problems conversationally, like a helpful doctor."},
                {"role": "user", "content": summary_prompt}
            ],
            temperature=0.6
        )
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        # Log the error in a real application
        print(f"Error in summarize_issue: {e}")
        return f"Based on our conversation, you're experiencing a {category.lower()} issue with your website."

def translate(text, lang):
    if not text or lang == "en":
        return text
    
    # Add validation for supported languages
    supported_languages = {
        "es": "Spanish", "fr": "French", "de": "German", "it": "Italian", 
        "pt": "Portuguese", "nl": "Dutch", "pl": "Polish", "ru": "Russian",
        "ja": "Japanese", "ko": "Korean", "zh": "Chinese", "ar": "Arabic"
    }
    
    if lang not in supported_languages:
        return text  # Return original text if language not supported
    
    prompt = f"Translate the following message into {supported_languages[lang]}:\n\n{text}"
    
    try:
        client = get_openai_client()
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a professional translator."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        # Log the error in a real application
        print(f"Error in translate: {e}")
        return text  # Return original text if translation fails

def get_agent_response(history, stage="initial", category=None, clarifications=0, lang="en"):
    if not history:
        return {
            "response": translate("Hello! I'm here to help you with your website issue. Can you describe what's happening?", lang),
            "next_stage": "initial",
            "category": None,
            "clarifications": 0,
            "typing_delay": 3
        }
    
    last_user_input = history[-1].get('content', '') if history else ""
    user_input = last_user_input.lower().strip()

    closing_phrases = ["thanks", "thank you", "bye", "goodbye", "that's all", "got it", "appreciate it", "ok cool"]
    if stage in ["offered_report", "report_sent"] and any(phrase in user_input for phrase in closing_phrases):
        final_msg = "You're very welcome! 😊 If you ever need more help, I'm just a click away. Take care!"
        return {
            "response": translate(final_msg, lang),
            "next_stage": "closed",
            "category": category,
            "clarifications": clarifications,
            "typing_delay": 3
        }

    if stage == "initial":
        category, confidence, question = classify_issue(last_user_input)
        response_text = question if confidence >= 70 else "Hmm, I'm not quite sure yet — could you describe that a bit differently?"
        return {
            "response": translate(response_text, lang),
            "next_stage": "clarifying" if confidence >= 70 else "initial",
            "category": category if confidence >= 70 else None,
            "clarifications": 1 if confidence >= 70 else clarifications + 1,
            "typing_delay": 4
        }

    elif stage == "clarifying":
        # Ensure clarifications is a positive number
        clarifications = max(0, clarifications)
        
        # Get the last few assistant messages to avoid repeating questions
        recent_assistant_messages = []
        if clarifications > 0 and len(history) >= clarifications:
            recent_messages = history[-clarifications:]
            recent_assistant_messages = [m.get('content', '') for m in recent_messages if m.get('role') == 'assistant']
        
        clarifying_set = get_clarifying_questions(category)
        remaining = [q for q in clarifying_set if q not in recent_assistant_messages]

        if clarifications >= 2 or not remaining:
            summary = summarize_issue(history, category)
            response_text = f"{summary} Would you like me to email you a full diagnostic report with tips to fix it?"
            return {
                "response": translate(response_text, lang),
                "next_stage": "summarize",
                "category": category,
                "clarifications": clarifications,
                "typing_delay": 4
            }

        batch_size = min(3, len(remaining))
        batch = remaining[:batch_size]
        return {
            "response": translate("\n\n".join(batch), lang),
            "next_stage": "clarifying",
            "category": category,
            "clarifications": clarifications + 1,
            "typing_delay": 4
        }

    elif stage == "summarize":
        if user_input in ["yes", "sure", "okay", "ok", "yep", "yeah"]:
            return {
                "response": translate("No problem. Just enter your name and email below to get a report. It's free and tailored to your issue.", lang),
                "next_stage": "offered_report",
                "category": category,
                "clarifications": clarifications,
                "typing_delay": 4
            }
        elif user_input in ["no", "not now", "maybe later"]:
            return {
                "response": translate("Totally fine! If you change your mind, just let me know and I'll prepare a report for you.", lang),
                "next_stage": "summarize",
                "category": category,
                "clarifications": clarifications,
                "typing_delay": 4
            }
        else:
            return {
                "response": translate("Would you like me to email you a full diagnostic report with tips to fix it?", lang),
                "next_stage": "summarize",
                "category": category,
                "clarifications": clarifications,
                "typing_delay": 4
            }

    elif stage == "offered_report":
        return {
            "response": translate("Awesome. Just fill out your name and email below and I'll generate your custom report. 📬", lang),
            "next_stage": "offered_report",
            "category": category,
            "clarifications": clarifications,
            "typing_delay": 4
        }

    # Default fallback
    fallback = "Let's take another look together. Could you explain a bit more?"
    return {
        "response": translate(fallback, lang),
        "next_stage": "initial",
        "category": None,
        "clarifications": 0,
        "typing_delay": 4
    }