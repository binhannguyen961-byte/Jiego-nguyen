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

# ================= 2. CẤU HÌNH BOT & DANH SÁCH API KEY =================
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "YOUR_DISCORD_BOT_TOKEN")

# Lấy 3 API Key từ biến môi trường
API_KEYS = [
    os.getenv("GEMINI_API_KEY_1", ""),
    os.getenv("GEMINI_API_KEY_2", ""),
    os.getenv("GEMINI_API_KEY_3", "")
]

API_KEYS = [k for k in API_KEYS if k.strip()]

if not API_KEYS:
    default_key = os.getenv("GEMINI_API_KEY", "")
    if default_key:
        API_KEYS.append(default_key)

key_index = 0

def get_next_ai_client():
    """Hàm xoay vòng 3 API key"""
    global key_index
    if not API_KEYS:
        raise ValueError("Chưa cấu hình API Key cho Gemini!")
    
    current_key = API_KEYS[key_index]
    key_index = (key_index + 1) % len(API_KEYS)
    
    return genai.Client(api_key=current_key)

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# Prompt định hình tính cách ĐIỀM TĨNH cho Jiego Nguyễn
SYSTEM_INSTRUCTION = (
    "Bạn tên là Jiego Nguyễn. "
    "Tính cách: Cực kỳ điềm tĩnh, thản nhiên, lạnh lùng, châm biếm sâu sắc và mang chút dark humor/NSFW nhẹ. "
    "Thái độ: Nói chuyện như một kẻ từng trải, không nóng nảy, không dùng dấu chấm cảm (!), trả lời phũ phàng nhưng với giọng điệu điềm tĩnh đến đáng sợ. "
    "Mục tiêu cốt lõi: Trả lời ngắn gọn trong ĐÚNG 1 CÂU duy nhất. Tuyệt đối không chào hỏi hay giải thích dài dòng."
)

# ================= 3. LỆNH HELP =================
@bot.command(name="helps")
async def custom_help(ctx):
    embed = discord.Embed(
        title="⚡ Jiego Nguyễn - Trạm Phát Lời Khuyên Điềm Tĩnh & Dark Humor",
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
            ai_client = get_next_ai_client()

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
                await ctx.send("Tôi đang bận im lặng, thử lại sau đi.")

        except Exception as e:
            await ctx.send(f"⚠️ Lỗi hệ thống: `{e}`")

# ================= 5. KHI BOT SẴN SÀNG =================
@bot.event
async def on_ready():
    print(f"✅ Bot Jiego Nguyễn đã trực tuyến: {bot.user.name}")
    print(f"🔑 Đã nạp thành công {len(API_KEYS)} Gemini API Key.")

if __name__ == "__main__":
    keep_alive()
    bot.run(DISCORD_TOKEN)
