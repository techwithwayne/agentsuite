from django.db import models
import hashlib

class Conversation(models.Model):
    session_id = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    subject = models.CharField(max_length=255, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        who = self.name or self.email or "Anonymous"
        return f"{who} - {self.subject or 'No Subject'} at {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"

    class Meta:
        db_table = 'webdoctor_conversations'
        ordering = ['-timestamp']  # Most recent first
        indexes = [
            models.Index(fields=['session_id']),
            models.Index(fields=['email']),
            models.Index(fields=['timestamp']),
        ]

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.CharField(max_length=20, choices=[('user', 'User'), ('agent', 'Agent')])
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.capitalize()} at {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"

    class Meta:
        ordering = ['timestamp']
        db_table = 'webdoctor_messages'
        indexes = [
            models.Index(fields=['conversation', 'timestamp']),
        ]

class AgentResponse(models.Model):
    response_text = models.TextField()
    response_hash = models.CharField(max_length=64, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Generate hash if not already set
        if not self.response_hash:
            self.response_hash = hashlib.sha256(self.response_text.encode('utf-8')).hexdigest()
        super().save(*args, **kwargs)

    @classmethod
    def get_or_create_response(cls, response_text):
        """
        Get or create a response based on the text content.
        Returns tuple (instance, created) like get_or_create.
        """
        if not response_text:
            raise ValueError("Response text cannot be empty")
        
        response_hash = hashlib.sha256(response_text.encode('utf-8')).hexdigest()
        try:
            return cls.objects.get_or_create(
                response_hash=response_hash,
                defaults={'response_text': response_text}
            )
        except Exception as e:
            # Handle potential database errors gracefully
            raise ValueError(f"Error creating/retrieving response: {str(e)}")

    def __str__(self):
        return f"Response {self.response_hash[:8]}... ({self.created_at.strftime('%Y-%m-%d %H:%M:%S')})"

    class Meta:
        db_table = 'webdoctor_responses'
        ordering = ['-created_at']

class UserInteraction(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    issue_description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.email}) - {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"

    class Meta:
        db_table = 'webdoctor_interactions'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['timestamp']),
        ]

class DiagnosticReport(models.Model):
    user_email = models.EmailField()
    issue_details = models.TextField()
    report_content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report for {self.user_email} - {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"

    class Meta:
        db_table = 'webdoctor_reports'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user_email']),
            models.Index(fields=['created_at']),
        ]