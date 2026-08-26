import os
import threading
import discord
from discord.ext import commands
from flask import Flask
from google import genai
from google.genai import types

# ================= 1. WEB SERVER KEEPALIVE (FLASK) =================
app = Flask(__name__)

@app.route('/')
def home():
    return "Jiego Nguyễn đang hoạt động..."

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

def keep_alive():
    server_thread = threading.Thread(target=run_flask)
    server_thread.daemon = True
    server_thread.start()

# ================= 2. CẤU HÌNH BOT & GEMINI =================
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "YOUR_DISCORD_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY")

ai_client = genai.Client(api_key=GEMINI_API_KEY)

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# Prompt định hình tính cách cho Jiego Nguyễn
SYSTEM_INSTRUCTION = (
    "Bạn tên là Jiego Nguyễn. Tính cách của bạn rất thẳng thắn, pha chút châm biếm, "
    "hài hước đen (dark humor) và NSFW nhẹ nhưng đầy thực tế. "
    "Mục tiêu cốt lõi: Tất cả câu trả lời BẮT BUỘC chỉ dài đúng 1 CÂU duy nhất. "
    "Câu nói đó có thể là một lời truyền động lực thực tế, một trò đùa dark humor, "
    "hoặc một câu châm ngôn châm biếm sâu sắc. Tuyệt đối không chào hỏi dài dòng, "
    "không giải thích thêm, luôn vào thẳng vấn đề."
)

# ================= 3. LỆNH HELP =================
@bot.command(name="helps")
async def custom_help(ctx):
    embed = discord.Embed(
        title="⚡ Jiego Nguyễn - Trạm Phát Lời Khuyên & Dark Humor",
        description="Mọi câu trả lời từ Jiego Nguyễn đều ngắn gọn đúng 1 câu.",
        color=discord.Color.from_rgb(30, 30, 30)
    )
    embed.add_field(
        name="📌 Lệnh chính",
        value="`!jiego [câu hỏi/nội dung]` - Nhận 1 câu trả lời từ Jiego Nguyễn.",
        inline=False
    )
    await ctx.send(embed=embed)

# ================= 4. LỆNH AI JIEGO NGỦYỄN =================
@bot.command(name="jiego")
async def jiego_chat(ctx, *, prompt: str):
    async with ctx.typing():
        config = types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION
        )
        
        try:
            response = await bot.loop.run_in_executor(
                None,
                lambda: ai_client.models.generate_content(
                    model="gemini-3.6-flash",
                    contents=prompt,
                    config=config
                )
            )

            if response and hasattr(response, 'text') and response.text:
                await ctx.send(response.text.strip())
            else:
                await ctx.send("Đời không như là mơ và câu trả lời của tôi cũng vậy, thử lại đi.")

        except Exception as e:
            await ctx.send(f"⚠️ Lỗi hệ thống: `{e}`")

# ================= 5. SUY NGHĨ KHI BOT SẴN SÀNG =================
@bot.event
async def on_ready():
    print(f"✅ Bot Jiego Nguyễn đã trực tuyến: {bot.user.name}")

if __name__ == "__main__":
    keep_alive()
    bot.run(DISCORD_TOKEN)
