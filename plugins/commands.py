import asyncio 
from pyrogram import Client, filters, enums
from config import LOG_CHANNEL, API_ID, API_HASH, NEW_REQ_MODE
from plugins.database import db
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

LOG_TEXT = """<b>#NewUser
    
ID - <code>{}</code>

Nᴀᴍᴇ - {}</b>
"""

@Client.on_message(filters.command('start'))
async def start_message(c, m):
    if not await db.is_user_exist(m.from_user.id):
        await db.add_user(m.from_user.id, m.from_user.first_name)
        await c.send_message(LOG_CHANNEL, LOG_TEXT.format(m.from_user.id, m.from_user.mention))
    await m.reply_photo(
    "https://te.legra.ph/file/119729ea3cdce4fefb6a1.jpg",
    caption=f"<b>Hello {m.from_user.mention} 👋\n\nI Am Join Request Acceptor Bot. I Can Accept All Old Pending Join Request.\n\nFor All Pending Join Request Use - /accept</b>",
    reply_markup=InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Help", url="https://t.me/HellFire_Academy_Chat?startgroup=true")],
            [InlineKeyboardButton("📢 Updates", url="https://t.me/HellFire_Academy")],
            [InlineKeyboardButton("👨‍💻 Developer", url="https://t.me/Urr_Sanjiii")]
        ]
    )
)

@Client.on_message(filters.command('getsession') & filters.private)
async def get_session(client, message):
    user_id = message.from_user.id
    session = await db.get_session(user_id)

    if session is None:
        msg = await message.reply("**No session found. Please /login first.**")
    else:
        msg = await message.reply(
            f"**Your saved session string:**\n\n`{session}`\n\n⚠️ *Keep this string private.*"
        )
    
    await asyncio.sleep(60)
    try:
        await msg.delete()
        await message.delete()
    except:
        pass

@Client.on_message(filters.command('accept') & filters.private)
async def accept(client, message):
    show = await message.reply("**Please Wait.....**")
    user_data = await db.get_session(message.from_user.id)
    if user_data is None:
        await show.edit("**For Accepte Pending Request You Have To /login First.**")
        return
    try:
        acc = Client("joinrequest", session_string=user_data, api_hash=API_HASH, api_id=API_ID)
        await acc.connect()
    except:
        return await show.edit("**Your Login Session Expired. So /logout First Then Login Again By - /login**")
    show = await show.edit("**Now Forward A Message From Your Channel Or Group With Forward Tag\n\nMake Sure Your Logged In Account Is Admin In That Channel Or Group With Full Rights.**")
    vj = await client.listen(message.chat.id)
    if vj.forward_from_chat and not vj.forward_from_chat.type in [enums.ChatType.PRIVATE, enums.ChatType.BOT]:
        chat_id = vj.forward_from_chat.id
        try:
            info = await acc.get_chat(chat_id)
        except:
            await show.edit("**Error - Make Sure Your Logged In Account Is Admin In This Channel Or Group With Rights.**")
    else:
        return await message.reply("**Message Not Forwarded From Channel Or Group.**")
    await vj.delete()
    msg = await show.edit("**Accepting all join requests... Please wait until it's completed.**")
    try:
        while True:
            await acc.approve_all_chat_join_requests(chat_id)
            await asyncio.sleep(1)
            join_requests = [request async for request in acc.get_chat_join_requests(chat_id)]
            if not join_requests:
                break
        await msg.edit("**Successfully accepted all join requests.**")
    except Exception as e:
        await msg.edit(f"**An error occurred:** {str(e)}")
        
@Client.on_chat_join_request(filters.group | filters.channel)
async def approve_new(client, m):
    if NEW_REQ_MODE == False:
        return 
    try:
        if not await db.is_user_exist(m.from_user.id):
            await db.add_user(m.from_user.id, m.from_user.first_name)
            await client.send_message(LOG_CHANNEL, LOG_TEXT.format(m.from_user.id, m.from_user.mention))
        await client.approve_chat_join_request(m.chat.id, m.from_user.id)
        try:
            buttons = [
                [InlineKeyboardButton("Join Updates", url="https://t.me/HellFire_Academy")],
                [
                    InlineKeyboardButton("Help", url="https://t.me/HellFire_Academy_Chat"),
                    InlineKeyboardButton("Hemtai", url="https://t.me/Adult_Flux")
                ]
            ]
            markup = InlineKeyboardMarkup(buttons)
            await client.send_photo(
                chat_id=m.from_user.id,
                photo="https://i.ibb.co/XrtL03rB/image.png",
                caption='<b><blockquote>ʏᴏᴜʀ ʀᴇǫᴜᴇsᴛ ᴛᴏ ᴊᴏɪɴ "<i>{}</i>" ʜᴀs ʙᴇᴇɴ ᴀᴘᴘʀᴏᴠᴇᴅ.</blockquote></b>'.format(m.chat.title),
                reply_markup=markup
            )
        except:
            pass
    except Exception as e:
        print(str(e))
        pass
