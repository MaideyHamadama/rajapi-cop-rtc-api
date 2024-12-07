from django.db import models
from django.conf import settings
    
class Message(models.Model):
    recipient = models.IntegerField() # Reference to the user authentication API's user_id
    sender = models.IntegerField() 
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Message from {self.sender} to {self.recipient}"