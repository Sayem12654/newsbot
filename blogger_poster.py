from google.oauth2 import service_account
from googleapiclient.discovery import build
import config
import logging

logger = logging.getLogger(__name__)

def create_post(title, content, image_url=None):
    try:
        creds = service_account.Credentials.from_service_account_file(
            config.BLOGGER_CREDENTIALS,
            scopes=['https://www.googleapis.com/auth/blogger']
        )
        
        service = build('blogger', 'v3', credentials=creds)
        
        # Add image if available
        html_content = content
        if image_url:
            html_content = f'<div style="text-align:center"><img src="{image_url}" alt="{title}" style="max-width:100%"></div><br>{content}'
        
        body = {
            "title": title,
            "content": html_content,
            "labels": ["AI-Generated", "News", "Automation"]
        }
        
        blog_id = "3485902611847122452"  # Replace with your actual blog ID
        post = service.posts().insert(blogId=blog_id, body=body).execute()
        
        return {
            'success': True,
            'url': post['url'],
            'title': title
        }
    except Exception as e:
        logger.error(f"Blogger Error: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }