import discord
from discord import app_commands
from discord.ext import commands
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# File paths for data storage
PURCHASE_FILE = 'purchases.json'
ROLE_FILE = 'roles.json'
LOGS_FILE = 'logs.json'

# Ensure data files exist
for file_path in (PURCHASE_FILE, ROLE_FILE, LOGS_FILE):
    if not os.path.exists(file_path):
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump({}, f, ensure_ascii=False, indent=4)

# Utility: format money with dots as thousand separators
def format_money(amount: int) -> str:
    return f"{amount:,}".replace(",", ".")

class PurchaseBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        intents.guilds = True
        super().__init__(command_prefix='!', intents=intents)
        # Load persisted data
        self.purchases = self.load_data(PURCHASE_FILE)
        self.role_thresholds = self.load_data(ROLE_FILE)
        self.logs_config = self.load_data(LOGS_FILE)

    def load_data(self, path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def save_data(self, path, data):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def get_user_purchases(self, user_id):
        return self.purchases.get(str(user_id), [])

    def get_user_total(self, user_id):
        return sum(entry['price'] for entry in self.get_user_purchases(user_id))

    def update_roles(self, member: discord.Member):
        total = self.get_user_total(member.id)
        for role_id, threshold in self.role_thresholds.items():
            role = member.guild.get_role(int(role_id))
            if not role:
                continue
            if total >= threshold and role not in member.roles:
                self.loop.create_task(member.add_roles(role, reason='Purchase threshold met'))
            elif total < threshold and role in member.roles:
                self.loop.create_task(member.remove_roles(role, reason='Below purchase threshold'))

    async def setup_hook(self):
        try:
            # Sync slash commands
            synced = await self.tree.sync()
            print(f'✅ Đã đồng bộ {len(synced)} slash commands')
            print(f'🤖 Bot {self.user} đã sẵn sàng!')
        except Exception as e:
            print(f'❌ Lỗi trong setup_hook: {e}')
            raise

# Instantiate the bot
bot = PurchaseBot()

@bot.event
async def on_ready():
    print(f'✅ Bot đã đăng nhập thành công: {bot.user}')
    print(f'📊 Bot ID: {bot.user.id}')
    print(f'🌐 Kết nối tới {len(bot.guilds)} server(s)')
    for guild in bot.guilds:
        print(f'   - {guild.name} (ID: {guild.id})')
    
    # Set custom status/activity after bot is ready
    try:
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name="LewLewStore | /list /rank"
        )
        await bot.change_presence(activity=activity, status=discord.Status.online)
        print('🎯 Đã thiết lập bot status thành công')
    except Exception as e:
        print(f'⚠️ Không thể thiết lập bot status: {e}')

@bot.event
async def on_error(event, *args, **kwargs):
    print(f'❌ Lỗi trong event {event}:')
    import traceback
    traceback.print_exc()

# Global error handler for rate limiting
@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, discord.HTTPException):
        if error.status == 429:  # Rate limited
            await interaction.response.send_message(
                '⏳ Bot đang bị rate limit. Vui lòng thử lại sau vài giây.',
                ephemeral=True
            )
            return
        elif error.status >= 500:  # Server errors
            await interaction.response.send_message(
                '🔧 Discord đang gặp sự cố. Vui lòng thử lại sau.',
                ephemeral=True
            )
            return
    
    # Log unexpected errors
    print(f'❌ Lỗi command không mong muốn: {error}')
    import traceback
    traceback.print_exc()
    
    if not interaction.response.is_done():
        await interaction.response.send_message(
            '❌ Đã xảy ra lỗi không mong muốn. Vui lòng thử lại.',
            ephemeral=True
        )

@bot.tree.command(name='luu', description='Lưu thông tin người mua và sản phẩm đã bán')
@app_commands.describe(
    buyer='Người mua (mention)',
    quantity='Số lượng',
    product='Tên sản phẩm',
    price='Giá (VND)'
)
@app_commands.checks.has_permissions(administrator=True)
async def luu(interaction: discord.Interaction, buyer: discord.Member, quantity: int, product: str, price: int):
    user_id = str(buyer.id)
    entry = {'quantity': quantity, 'product': product, 'price': price}
    bot.purchases.setdefault(user_id, []).append(entry)
    bot.save_data(PURCHASE_FILE, bot.purchases)
    
    # Send response to admin
    await interaction.response.send_message(
        f'Đã lưu: {buyer.mention} mua **{quantity}×{product}** với giá **{format_money(price)} VND**',
        ephemeral=True
    )
    
    # Update roles
    bot.update_roles(buyer)
    
    # Send log message to configured channel with rate limit protection
    guild_id = str(interaction.guild.id)
    if guild_id in bot.logs_config:
        log_channel_id = bot.logs_config[guild_id]
        log_channel = interaction.guild.get_channel(log_channel_id)
        if log_channel:
            try:
                await log_channel.send(
                    f'📦 **Giao dịch mới:** {buyer.mention} đã mua x{quantity} {product} với giá {format_money(price)} VND'
                )
            except discord.HTTPException as e:
                if e.status == 429:  # Rate limited
                    print(f'⏳ Log channel bị rate limit: {e}')
                else:
                    print(f'❌ Lỗi gửi log: {e}')
            except discord.Forbidden:
                print(f'❌ Bot không có quyền gửi tin nhắn trong channel logs')
            except Exception as e:
                print(f'❌ Lỗi không mong muốn khi gửi log: {e}')

@bot.tree.command(name='setup_role', description='Thiết lập role dựa trên tổng tiền đã mua')
@app_commands.describe(
    role='Role cần gán',
    threshold='Ngưỡng tổng tiền (VND)'
)
@app_commands.checks.has_permissions(administrator=True)
async def setup_role(interaction: discord.Interaction, role: discord.Role, threshold: int):
    bot.role_thresholds[str(role.id)] = threshold
    bot.save_data(ROLE_FILE, bot.role_thresholds)
    await interaction.response.send_message(
        f'Đã thiết lập role **{role.name}** với ngưỡng **{format_money(threshold)} VND**',
        ephemeral=True
    )

@bot.tree.command(name='list', description='Hiển thị thông tin mua hàng của bạn')
async def list_purchases(interaction: discord.Interaction):
    user = interaction.user
    guild = interaction.guild
    entries = bot.get_user_purchases(user.id)

    embed = discord.Embed(color=0xDA1EF3)
    embed.set_author(name=guild.name, icon_url=(guild.icon.url if guild.icon else None))
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)

    if not entries:
        embed.description = f'{user.mention} chưa mua hàng tại LewLewStore.'
        default_roles = [rid for rid, t in bot.role_thresholds.items() if t == 0]
        role_obj = guild.get_role(int(default_roles[0])) if default_roles else None
        embed.add_field(
            name='Hạng',
            value=(role_obj.mention if role_obj else 'Chưa có'),
            inline=False
        )
    else:
        # Build lines with arrow and formatted numbers
        lines = [f'<a:prettyarrowR1:1389650470041026681> x{e["quantity"]} {e["product"]} : {format_money(e["price"])} VND' for e in entries]
        total = bot.get_user_total(user.id)
        # Separate product list and total on distinct lines with sparkles icon
        description = f'## {user.mention} đã mua:\n' + '\n'.join(lines) + f'\n\n<a:Sparkles:1323242208056447007> **Tổng chi:** {format_money(total)} VND'
        embed.description = description
        
        # Determine highest rank
        assigned_role = None
        for rid, threshold in sorted(bot.role_thresholds.items(), key=lambda x: x[1]):
            if total >= threshold:
                assigned_role = rid
        if assigned_role:
            role_obj = guild.get_role(int(assigned_role))
            embed.add_field(name='Hạng', value=(role_obj.mention if role_obj else 'Chưa có'), inline=False)

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name='rank', description='Hiển thị top 20 người mua nhiều nhất')
async def rank(interaction: discord.Interaction):
    guild = interaction.guild
    
    # Calculate total spending for each user
    user_totals = []
    for user_id, purchases in bot.purchases.items():
        total = sum(entry['price'] for entry in purchases)
        user_totals.append((user_id, total))
    
    # Sort by total spending (descending) and take top 20
    user_totals.sort(key=lambda x: x[1], reverse=True)
    top_20 = user_totals[:20]
    
    # Create embed
    embed = discord.Embed(color=0xDA1EF3)
    embed.set_author(name="Top customers tại LewLewStore", icon_url=(guild.icon.url if guild.icon else None))
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    embed.set_footer(text="LewLewStore || discord.gg/lewlewstore", icon_url=(guild.icon.url if guild.icon else None))
    
    # Build description with rankings
    description_lines = []
    for i, (user_id, total) in enumerate(top_20, 1):
        # Only use guild members to avoid rate limiting
        member = guild.get_member(int(user_id))
        if member:
            user_mention = member.mention
        else:
            # Don't fetch users not in guild to avoid rate limiting
            user_mention = f"<@{user_id}>"
        
        # Determine user's role based on spending
        assigned_role = None
        for rid, threshold in sorted(bot.role_thresholds.items(), key=lambda x: x[1], reverse=True):
            if total >= threshold:
                role = guild.get_role(int(rid))
                if role:
                    assigned_role = role
                    break
        
        role_text = assigned_role.mention if assigned_role else "Chưa có hạng"
        description_lines.append(f"#{i} {user_mention} đã chi **{format_money(total)} VND** hạng {role_text}")
    
    if not description_lines:
        embed.description = "Chưa có dữ liệu mua hàng nào."
    else:
        embed.description = "\n".join(description_lines)
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name='checklist', description='Xem thông tin mua hàng của người khác (Admin only)')
@app_commands.describe(
    user='Người dùng cần kiểm tra'
)
@app_commands.checks.has_permissions(administrator=True)
async def checklist(interaction: discord.Interaction, user: discord.Member):
    guild = interaction.guild
    entries = bot.get_user_purchases(user.id)

    embed = discord.Embed(color=0xDA1EF3)
    embed.set_author(name=guild.name, icon_url=(guild.icon.url if guild.icon else None))
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)

    if not entries:
        embed.description = f'{user.mention} chưa mua hàng tại LewLewStore.'
        default_roles = [rid for rid, t in bot.role_thresholds.items() if t == 0]
        role_obj = guild.get_role(int(default_roles[0])) if default_roles else None
        embed.add_field(
            name='Hạng',
            value=(role_obj.mention if role_obj else 'Chưa có'),
            inline=False
        )
    else:
        # Build lines with arrow and formatted numbers
        lines = [f'<a:prettyarrowR1:1389650470041026681> x{e["quantity"]} {e["product"]} : {format_money(e["price"])} VND' for e in entries]
        total = bot.get_user_total(user.id)
        # Separate product list and total on distinct lines with sparkles icon
        description = f'## {user.mention} đã mua:\n' + '\n'.join(lines) + f'\n\n<a:Sparkles:1323242208056447007> **Tổng chi:** {format_money(total)} VND'
        embed.description = description
        
        # Determine highest rank
        assigned_role = None
        for rid, threshold in sorted(bot.role_thresholds.items(), key=lambda x: x[1]):
            if total >= threshold:
                assigned_role = rid
        if assigned_role:
            role_obj = guild.get_role(int(assigned_role))
            embed.add_field(name='Hạng', value=(role_obj.mention if role_obj else 'Chưa có'), inline=False)

    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name='setup_logs', description='Thiết lập kênh logs cho lệnh /luu')
@app_commands.describe(
    channel='Kênh để gửi logs'
)
@app_commands.checks.has_permissions(administrator=True)
async def setup_logs(interaction: discord.Interaction, channel: discord.TextChannel):
    guild_id = str(interaction.guild.id)
    bot.logs_config[guild_id] = channel.id
    bot.save_data(LOGS_FILE, bot.logs_config)
    await interaction.response.send_message(
        f'Đã thiết lập kênh logs: {channel.mention}',
        ephemeral=True
    )

@bot.tree.command(name='respond', description='Hiển thị thông tin tài khoản thanh toán')
@app_commands.describe(
    responder='Chọn loại tài khoản'
)
@app_commands.choices(responder=[
    app_commands.Choice(name='Ngân hàng MB Bank', value='ostk'),
    app_commands.Choice(name='Ví MOMO', value='omomo')
])
async def respond(interaction: discord.Interaction, responder: str):
    if responder == 'ostk':
        embed = discord.Embed(
            title="Số tài khoản ngân hàng của tớ đây nhé",
            description="```MB BANK```\n```7417766666```",
            color=0x040fbd
        )
        embed.set_image(url="https://media.discordapp.net/attachments/1250243575426322552/1385204829705736263/IMG_4979.jpg?ex=686eed47&is=686d9bc7&hm=b30a36e5715c21c04fb9dc233c5765650e40d67185edf9bc61dd821d7c736e8f&=&format=webp&width=289&height=375")
    elif responder == 'omomo':
        embed = discord.Embed(
            title="Tài khoản ví MOMO của tớ đây nhé !!!",
            description="```0915688407```",
            color=0xfc2ab9
        )
        embed.set_image(url="https://cdn.discordapp.com/attachments/1250243575426322552/1310553579547004928/IMG_3928.jpg?ex=686eede2&is=686d9c62&hm=0c5bce3fce3e79f3d34c748fed15b1d4651f4e2d1a66dbda7eedcdfd3567573f")
    
    await interaction.response.send_message(embed=embed)

# Error handlers
@luu.error
async def luu_error(interaction, error):
    if isinstance(error, app_commands.errors.MissingPermissions):
        await interaction.response.send_message('Bạn cần quyền quản trị để sử dụng lệnh này.', ephemeral=True)

@setup_role.error
async def setup_role_error(interaction, error):
    if isinstance(error, app_commands.errors.MissingPermissions):
        await interaction.response.send_message('Bạn cần quyền quản trị để sử dụng lệnh này.', ephemeral=True)

@checklist.error
async def checklist_error(interaction, error):
    if isinstance(error, app_commands.errors.MissingPermissions):
        await interaction.response.send_message('Bạn cần quyền quản trị để sử dụng lệnh này.', ephemeral=True)

@setup_logs.error
async def setup_logs_error(interaction, error):
    if isinstance(error, app_commands.errors.MissingPermissions):
        await interaction.response.send_message('Bạn cần quyền quản trị để sử dụng lệnh này.', ephemeral=True)

if __name__ == '__main__':
    # Get token from environment variable
    TOKEN = os.getenv('DISCORD_BOT_TOKEN')
    
    if not TOKEN:
        print("❌ Lỗi: Bot token chưa được cấu hình!")
        print("📝 Hướng dẫn:")
        print("   1. Tạo bot tại https://discord.com/developers/applications")
        print("   2. Copy bot token")
        print("   3. Thêm environment variable:")
        print("      Key: DISCORD_BOT_TOKEN")
        print("      Value: your_bot_token_here")
        print("   4. Bật Privileged Gateway Intents:")
        print("      - MESSAGE CONTENT INTENT")
        print("      - SERVER MEMBERS INTENT")
        print("\n⚠️  Lưu ý: KHÔNG chia sẻ token với ai khác!")
        exit(1)
    
    try:
        print("🚀 Đang khởi động Discord Store Bot...")
        print(f"📋 Bot ID: {TOKEN[:24]}...")
        bot.run(TOKEN)
    except discord.LoginFailure as e:
        print(f"❌ Lỗi đăng nhập: {e}")
        print("🔧 Kiểm tra:")
        print("   - Bot token có đúng không?")
        print("   - Bot có bị disable không?")
        print("   - Privileged Gateway Intents đã bật chưa?")
    except discord.PrivilegedIntentsRequired as e:
        print(f"❌ Lỗi Privileged Intents: {e}")
        print("🔧 Hướng dẫn sửa lỗi:")
        print("   1. Vào https://discord.com/developers/applications")
        print("   2. Chọn bot của bạn")
        print("   3. Vào tab 'Bot'")
        print("   4. Bật các Privileged Gateway Intents:")
        print("      ✅ MESSAGE CONTENT INTENT")
        print("      ✅ SERVER MEMBERS INTENT")
        print("   5. Save Changes và restart bot")
    except Exception as e:
        print(f"❌ Lỗi không mong muốn: {e}")
        print(f"📝 Chi tiết lỗi: {type(e).__name__}")
        print("🔧 Kiểm tra kết nối internet và thử lại.")
        import traceback
        traceback.print_exc()