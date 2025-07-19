import cohere
import config

co = cohere.Client(config.COHERE_API_KEY)

def generate_seo_article(title, summary, region):
    # Region-specific SEO instructions
    region_tips = {
        'usa': "Focus on Google E-E-A-T guidelines. Use US English spelling and cultural references.",
        'eu': "Include GDPR-compliant content. Mention .eu domains and European market trends."
    }
    
    prompt = f"""
    **নিউজ টাইটেল**: {title}
    **সারাংশ**: {summary}
    
    **নির্দেশনা**:
    - লিখুন একটি SEO-অপটিমাইজড ব্লগ পোস্ট (800-1000 শব্দ)
    - লক্ষ্য বাজার: {region.upper()}
    - {region_tips.get(region, '')}
    - ব্যবহার করুন এইচটিএমএল ফরম্যাটিং (H2, H3, বোল্ড)
    - প্রাসঙ্গিক কীওয়ার্ড অন্তর্ভুক্ত করুন (অন্তত 5টি)
    - মানবিক এবং আকর্ষণীয় ভাষা ব্যবহার করুন
    """
    
    response = co.generate(
        model='command',
        prompt=prompt,
        max_tokens=1500,
        temperature=0.7,
        truncate='END'
    )
    return response.generations[0].text