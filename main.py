import logging
import html
import database
import rss_processor
import cohere_generator
import blogger_poster
import config
from telegram import (
    Update,
    KeyboardButton,
    ReplyKeyboardMarkup
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# লগিং সেটআপ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# মেইন কিবোর্ড
def get_main_keyboard():
    keyboard = [
        [KeyboardButton("📝 Generate Post")],
        [KeyboardButton("➕ Add Feed"), KeyboardButton("🛠️ Help")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# /start কমান্ড
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    welcome_msg = (
        f"🤖 <b>স্বাগতম {user.first_name}!</b>\n\n"
        "🚀 আমি AutoBloggerBot - আপনার AI-পাওয়ার্ড ব্লগিং সহকারী\n\n"
        "📌 আমি যা করতে পারি:\n"
        "• RSS ফিড থেকে নিউজ সংগ্রহ\n"
        "• Cohere AI দিয়ে SEO-অপটিমাইজড আর্টিকেল তৈরি\n"
        "• ব্লগারে স্বয়ংক্রিয়ভাবে পোস্ট\n\n"
        "👇 নিচের বাটন ব্যবহার শুরু করুন"
    )
    await update.message.reply_text(
        welcome_msg,
        parse_mode='HTML',
        reply_markup=get_main_keyboard()
    )

# হেল্প কমান্ড
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = (
        "🆘 <b>সাহায্য কেন্দ্র</b>\n\n"
        "📝 <b>Generate Post</b>\n"
        "- র‍্যান্ডম RSS নিউজ থেকে আর্টিকেল তৈরি করে ব্লগারে পোস্ট করে\n\n"
        "➕ <b>Add Feed</b>\n"
        "- নতুন RSS ফিড যোগ করে (ফরম্যাট: URL এবং region)\n\n"
        "⚙️ <b>কমান্ড লিস্ট</b>\n"
        "/set_blog [ID] - ব্লগার ব্লগ আইডি সেট করুন\n"
        "/list_feeds - সেভ করা ফিডগুলো দেখুন\n"
        "/help - এই সাহায্য মেনু\n\n"
        "ℹ️ <i>USA/EU মার্কেটের জন্য বিশেষ SEO অপ্টিমাইজেশন</i>"
    )
    await update.message.reply_text(
        help_text,
        parse_mode='HTML',
        reply_markup=get_main_keyboard()
    )

# পোস্ট জেনারেশন হ্যান্ডলার
async def generate_post(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        # Step 1: Get news
        await update.message.reply_text(
            "🔍 সর্বশেষ নিউজ খুঁজছি...",
            reply_markup=get_main_keyboard()
        )
        news = rss_processor.get_latest_news()
        
        if not news:
            await update.message.reply_text(
                "⚠️ কোন নিউজ পাওয়া যায়নি! নতুন RSS ফিড যোগ করুন।",
                reply_markup=get_main_keyboard()
            )
            return
        
        # Step 2: Generate article
        await update.message.reply_text(
            f"📰 <b>নিউজ পেয়েছি:</b>\n\n{html.escape(news['title'])}\n\n"
            f"🌍 Region: {news['region'].upper()}",
            parse_mode='HTML',
            reply_markup=get_main_keyboard()
        )
        await update.message.reply_text(
            "🤖 AI দিয়ে SEO-অপটিমাইজড আর্টিকেল তৈরি করা হচ্ছে...",
            reply_markup=get_main_keyboard()
        )
        
        article = cohere_generator.generate_seo_article(
            news['title'], 
            news['summary'], 
            news['region']
        )
        
        # Step 3: Post to Blogger
        await update.message.reply_text(
            "✅ আর্টিকেল তৈরি হয়েছে!\n\n"
            "🚀 ব্লগারে পোস্ট করা হচ্ছে...",
            reply_markup=get_main_keyboard()
        )
        
        result = blogger_poster.create_post(
            news['title'], 
            article, 
            news.get('image')
        )
        
        if result['success']:
            await update.message.reply_text(
                f"🎉 <b>সফলভাবে পোস্ট করা হয়েছে!</b>\n\n"
                f"📝 {html.escape(result['title'])}\n"
                f"🔗 <a href='{result['url']}'>ব্লগে দেখুন</a>",
                parse_mode='HTML',
                reply_markup=get_main_keyboard()
            )
        else:
            await update.message.reply_text(
                f"❌ ব্লগারে পোস্ট করতে সমস্যা:\n{result['error']}",
                reply_markup=get_main_keyboard()
            )
            
    except Exception as e:
        logger.error(f"Generate Post Error: {str(e)}")
        await update.message.reply_text(
            f"⚠️ ত্রুটি: {str(e)}",
            reply_markup=get_main_keyboard()
        )

# ফিড যোগ করার কমান্ড
async def add_feed_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    args = context.args
    if len(args) < 2:
        await update.message.reply_text(
            "❌ ভুল ফরম্যাট!\n\n"
            "সঠিক ফরম্যাট: <code>/add_feed [URL] [region]</code>\n\n"
            "Region: <code>usa</code> বা <code>eu</code>",
            parse_mode='HTML',
            reply_markup=get_main_keyboard()
        )
        return
    
    url, region = args[0], args[1].lower()
    if region not in ['usa', 'eu']:
        await update.message.reply_text(
            "❌ ভুল রিজন! শুধুমাত্র <code>usa</code> বা <code>eu</code> ব্যবহার করুন",
            parse_mode='HTML',
            reply_markup=get_main_keyboard()
        )
        return
    
    if database.add_feed(url, region):
        await update.message.reply_text(
            f"✅ সফলভাবে {region.upper()} ফিড যোগ করা হয়েছে!",
            reply_markup=get_main_keyboard()
        )
    else:
        await update.message.reply_text(
            "⚠️ এই ফিডটি ইতিমধ্যে ডাটাবেজে আছে!",
            reply_markup=get_main_keyboard()
        )

# ব্লগ সেট কমান্ড
async def set_blog(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    args = context.args
    if not args:
        await update.message.reply_text(
            "❌ ভুল ফরম্যাট!\n\n"
            "সঠিক ফরম্যাট: <code>/set_blog [BLOG_ID]</code>\n\n"
            "আপনার ব্লগ আইডি পাওয়ার জন্য: https://YOURBLOG.blogspot.com/",
            parse_mode='HTML',
            reply_markup=get_main_keyboard()
        )
        return
    
    blog_id = args[0]
    database.set_blog(blog_id)
    await update.message.reply_text(
        f"✅ ব্লগ আইডি সেট করা হয়েছে: {blog_id}",
        reply_markup=get_main_keyboard()
    )

# ফিড লিস্ট কমান্ড
async def list_feeds(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    feeds = database.get_feeds()
    if not feeds:
        await update.message.reply_text(
            "⚠️ কোন ফিড যোগ করা হয়নি!",
            reply_markup=get_main_keyboard()
        )
        return
    
    feed_list = "\n".join([f"• {url} ({region.upper()})" for url, region in feeds])
    await update.message.reply_text(
        f"📋 সেভ করা ফিড লিস্ট:\n\n{feed_list}",
        reply_markup=get_main_keyboard()
    )

# বাটন হ্যান্ডলার
async def handle_post_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await generate_post(update, context)

async def handle_add_feed_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "➕ নতুন RSS ফিড যোগ করুন:\n\n"
        "ফরম্যাট: <code>/add_feed [URL] [region]</code>\n\n"
        "উদাহরণ:\n<code>/add_feed https://example.com/rss.xml usa</code>\n\n"
        "Region: <code>usa</code> বা <code>eu</code>",
        parse_mode='HTML',
        reply_markup=get_main_keyboard()
    )

async def handle_help_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await help_command(update, context)

def main() -> None:
    # PTB 20.0+ Application বিল্ডার
    application = Application.builder().token(config.TELEGRAM_TOKEN).build()
    
    # কমান্ড হ্যান্ডলার
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("add_feed", add_feed_command))
    application.add_handler(CommandHandler("set_blog", set_blog))
    application.add_handler(CommandHandler("generate_post", generate_post))
    application.add_handler(CommandHandler("list_feeds", list_feeds))
    
    # বাটন হ্যান্ডলার (PTB 20.0+ style)
    application.add_handler(MessageHandler(filters.Regex(r'^📝 Generate Post$'), handle_post_button))
    application.add_handler(MessageHandler(filters.Regex(r'^➕ Add Feed$'), handle_add_feed_button))
    application.add_handler(MessageHandler(filters.Regex(r'^🛠️ Help$'), handle_help_button))
    
    # ডিফল্ট মেসেজ হ্যান্ডলার
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, start))
    
    # বট স্টার্ট
    application.run_polling()
    logger.info("🤖 বট সচল... প্রেস Ctrl+C বন্ধ করার জন্য")

if __name__ == '__main__':
    main()