import io
import random
from django.db import models
from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont

class Project(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    tech_stack = models.CharField(max_length=200)
    github_url = models.URLField(blank=True)
    image = models.ImageField(upload_to='projects/', blank=True, null=True)
    presentation_file = models.FileField(upload_to='presentations/', blank=True, null=True)
    order = models.PositiveIntegerField(default=0, db_index=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # 1. Try to extract thumbnail from PowerPoint if no image is provided
        if not self.image and self.presentation_file and self.is_ppt():
            try:
                import win32com.client
                import pythoncom
                import os
                
                # Initialize COM for the current thread
                pythoncom.CoInitialize()
                
                ppt_path = os.path.abspath(self.presentation_file.path)
                # Use a temp path for the export
                temp_thumb = os.path.join(os.path.dirname(ppt_path), f"temp_{self.pk}.png")
                
                powerpoint = win32com.client.Dispatch("PowerPoint.Application")
                # WithWindow=False (msoFalse) is 0
                presentation = powerpoint.Presentations.Open(ppt_path, WithWindow=0, ReadOnly=1, Untitled=0)
                
                if presentation.Slides.Count > 0:
                    slide = presentation.Slides(1)
                    slide.Export(temp_thumb, "PNG")
                    
                    with open(temp_thumb, 'rb') as f:
                        filename = f"thumb_{self.title.replace(' ', '_')}.png"
                        self.image.save(filename, ContentFile(f.read()), save=False)
                    
                    # Cleanup temp file
                    presentation.Close()
                    # Only quit if no other presentations are open? 
                    # Usually better to just close the one we opened.
                    # powerpoint.Quit() 
                
                if os.path.exists(temp_thumb):
                    os.remove(temp_thumb)
                    
            except Exception as e:
                print(f"Error extracting PPT thumbnail via COM: {e}")
            finally:
                try:
                    # Uninitialize COM
                    pythoncom.CoUninitialize()
                except:
                    pass

        # 2. Fallback to placeholder if still no image
        if not self.image:
            # Generate a placeholder image
            width, height = 800, 500
            # Generate a random background color
            bg_color = (random.randint(50, 200), random.randint(50, 200), random.randint(50, 200))
            img = Image.new('RGB', (width, height), color=bg_color)
            draw = ImageDraw.Draw(img)
            
            # Use initials or first few letters for the text
            text = self.title[:2].upper() if self.title else "PR"
            
            # Try to use a font, fallback to default
            try:
                # Use a larger font size for the placeholder
                font = ImageFont.truetype("arial.ttf", 150)
            except:
                font = ImageFont.load_default()

            # Center the text
            if hasattr(draw, 'textbbox'): # Pillow 10+
                bbox = draw.textbbox((0, 0), text, font=font)
                w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
            else:
                w, h = draw.textsize(text, font=font)
                
            draw.text(((width-w)/2, (height-h)/2), text, fill=(255, 255, 255), font=font)
            
            # Save the generated image to a ContentFile
            buffer = io.BytesIO()
            img.save(buffer, format='JPEG')
            filename = f"placeholder_{self.title.replace(' ', '_')}.jpg"
            self.image.save(filename, ContentFile(buffer.getvalue()), save=False)

        super().save(*args, **kwargs)

    @property
    def tech_list(self):
        if not self.tech_stack:
            return []
        return [item.strip() for item in self.tech_stack.split(',')]

    def is_ppt(self):
        if not self.presentation_file:
            return False
        return self.presentation_file.name.lower().endswith(('.ppt', '.pptx'))

    def is_pdf(self):
        if not self.presentation_file:
            return False
        return self.presentation_file.name.lower().endswith('.pdf')

    def __str__(self):
        return self.title

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name} - {self.email}"

class UserProfile(models.Model):
    name = models.CharField(max_length=100)
    bio_title = models.CharField(max_length=200, blank=True)
    profile_picture = models.ImageField(upload_to='profile/', blank=True, null=True)
    resume_file = models.FileField(upload_to='resumes/', blank=True, null=True)
    
    def __str__(self):
        return f"Profile: {self.name}"
    
    class Meta:
        verbose_name_plural = "User Profile"
