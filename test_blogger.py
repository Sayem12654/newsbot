import blogger_poster

# টেস্ট পোস্ট
result = blogger_poster.create_post(
    title="Test Post from Python",
    content="This is a test post from our automated system",
    image_url="https://via.placeholder.com/600x400"
)

if result['success']:
    print(f"✅ সফলভাবে পোস্ট করা হয়েছে!\nলিংক: {result['url']}")
else:
    print(f"❌ ত্রুটি: {result['error']}")