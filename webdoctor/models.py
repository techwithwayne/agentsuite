from django.db import models
import hashlib

class Conversation(models.Model):
    session_id = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True, db_index=True)
    subject = models.CharField(max_length=255, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    def __str__(self):
        who = self.name or self.email or "Anonymous"
        return f"{who} - {self.subject or 'No Subject'} at {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"

    class Meta:
        db_table = 'webdoctor_conversations'
        indexes = [
            models.Index(fields=['timestamp', 'email']),
            models.Index(fields=['session_id', 'timestamp']),
        ]

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.CharField(max_length=20, choices=[('user', 'User'), ('agent', 'Agent')], db_index=True)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    def __str__(self):
        return f"{self.sender.capitalize()} at {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"

    class Meta:
        ordering = ['timestamp']
        db_table = 'webdoctor_messages'
        indexes = [
            models.Index(fields=['conversation', 'timestamp']),
            models.Index(fields=['sender', 'timestamp']),
        ]

class AgentResponse(models.Model):
    response_text = models.TextField()
    response_hash = models.CharField(max_length=64, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    def save(self, *args, **kwargs):
        if not self.response_hash:
            self.response_hash = hashlib.sha256(self.response_text.encode()).hexdigest()
        super().save(*args, **kwargs)

    @classmethod
    def get_or_create_response(cls, response_text):
        response_hash = hashlib.sha256(response_text.encode()).hexdigest()
        try:
            # Use get() first for better performance
            return cls.objects.get(response_hash=response_hash), False
        except cls.DoesNotExist:
            # Only create if it doesn't exist
            return cls.objects.get_or_create(
                response_hash=response_hash,
                defaults={'response_text': response_text}
            )

    class Meta:
        db_table = 'webdoctor_responses'
        indexes = [
            models.Index(fields=['response_hash']),
            models.Index(fields=['created_at']),
        ]

class UserInteraction(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(db_index=True)
    issue_description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'webdoctor_interactions'
        indexes = [
            models.Index(fields=['email', 'timestamp']),
            models.Index(fields=['timestamp']),
        ]

class DiagnosticReport(models.Model):
    user_email = models.EmailField(db_index=True)
    issue_details = models.TextField()
    report_content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'webdoctor_reports'
        indexes = [
            models.Index(fields=['user_email', 'created_at']),
            models.Index(fields=['created_at']),
        ]
