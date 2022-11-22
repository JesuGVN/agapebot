import asyncio
import logging
import config
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types.web_app_info import WebAppInfo
import aioschedule
import fdb

def setData(sql):
   conn = fdb.connect(dsn='DB.FDB', user='SYSDBA', password='masterkey', charset='utf8')
   cur = conn.cursor()
   try:
      cur.execute(sql)
      conn.commit()
      conn.close()
      return True
   except BaseException as e:
      conn.rollback()
      conn.close()
      print("error setcommand: '" + sql + "'" + str(e))
      return False


def GetQuery(sql):
   conn = fdb.connect(dsn='DB.FDB', user='SYSDBA', password='masterkey', charset='utf8')
   cur = conn.cursor()
   try:
      cur.execute(sql)
      return cur.itermap()
   except BaseException as e:
      conn.rollback()
      print(f"error getquery: {e}")
      return []

import locale
locale.setlocale(
    category=locale.LC_ALL,
    locale="Russian"
)

bot = Bot(token=config.token, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)

@dp.message_handler(commands="plan")
async def getplan(message: types.Message):
    btn = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("Ссылка...",
                                                                        web_app=WebAppInfo(url="https://agapeastana.ru")))
    await message.answer("Для получения плана, нажмите кнопку ниже...", reply_markup=btn)

async def send_daily_plan():
    for c in GetQuery("select txt from GET_DAILY;"):
        await bot.send_message(chat_id=5204551702, text=c['TXT'], parse_mode=types.ParseMode.MARKDOWN,
                               disable_web_page_preview=True)

async def send_notif():
    for c in GetQuery("select m.dt,p.name,b.name as bookname,m.chaper from morning_reader m join persons p "
                      "on m.idperson = p.id join books b on m.idbook=b.id where dt=current_date+3;"):
        await bot.send_message(chat_id=5204551702, text=f"<b>Уведомление!!!</b>\nДорогой брат <b>{c['NAME']}</b>"
                                                        ", сегодня вам необходимо записать и отправить утреннее Слово "
                                                        f"по книге\n<code>{c['BOOKNAME']} глава {c['CHAPER']}</code>\n"
                                                        f"на <a href='http://agapeastana.ru'>{c['DT'].strftime('%A %d %B')}</a>")

async def send_topray():
    for c in GetQuery("select g.dt1,g.dt2,p.name,p2.name as name2 from(select d1.dt as dt1,d2.dt as dt2,d1.idperson,"
                      "d2.idperson as idper2 from donate d1, donate d2 where d1.dt=current_date+1 and "
                      "d2.dt=current_date+2)g join persons p on g.idperson=p.id join persons p2 on g.idper2=p2.id;"):
        await bot.send_message(chat_id=5204551702, text=f"<b>МОЛИТВА О ПОЖЕРТВОВАНИИ</b>\n\n{c['DT1'].strftime('%A %d %B')}"
                                                        f": <b>{c['NAME']}</b>\n{c['DT2'].strftime('%A %d %B')}: "
                                                        f"<b>{c['NAME2']}</b>\n\nПолная информация на сайте "
                                                        f"<a href='http://agapeastana.ru/?id=1'>agapeastana.ru</a>")


async def scheduler():
    aioschedule.every().day.at("05:00").do(send_daily_plan)
    aioschedule.every().day.at("09:00").do(send_notif)
    aioschedule.every().day.at("08:00").do(send_topray)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


async def getdt(m: int, y: int):
    if m == 13:
        m = 1
        y = y + 1
    elif m == 0:
        m = 12
        y = y - 1



    mnt = ""

    if m == 1:
      mnt = 'Январь'
    elif m == 2:
      mnt = 'Февраль'
    elif m == 3:
      mnt = 'Март'
    elif m == 4:
      mnt = 'Апрель'
    elif m == 4:
      mnt = 'Май'
    elif m == 4:
      mnt = 'Июнь'
    elif m == 4:
      mnt = 'Июль'
    elif m == 4:
      mnt = 'Август'
    elif m == 4:
      mnt = 'Сентябрь'
    elif m == 4:
      mnt = 'Октябрь'
    elif m == 4:
      mnt = 'Ноябрь'
    elif m == 4:
      mnt = 'Декабрь'

    return f"{mnt}{y}"

from fastapi import FastAPI, Header
import uvicorn
from fastapi.responses import HTMLResponse
from datetime import date
from pydantic import BaseModel

app = FastAPI(title="Agape Astana")

async def get_html(qr: int, indx: int):

    if indx == 1:
        sel1 = 'selected'
        sel2 = ''
        sel3 = ''
    elif indx == 2:
        sel1 = ''
        sel2 = 'selected'
        sel3 = ''
    elif indx == 3:
        sel1 = ''
        sel2 = ''
        sel3 = 'selected'
            

    if qr == 1:
        q1 = 'selected'
        q2 = ''
        tb = 'HTML_GRAPHICS'
    elif qr == 2:
        q1 = ''
        q2 = 'selected'
        tb = 'html_pray'

        
    cb = f'''<select id="cbtype" style="font-size: .9rem;padding: 2px 5px;"onchange="document.location=this.options[this.selectedIndex].value+{indx}">
                <option value="1" {q1}>Утреннее Слово</option>
                <option value="2" {q2}>Молитва о пожертвовании</option>
             </select>             
             <select id="cbid" style="font-size: .9rem;padding: 2px 5px;"onchange="document.location={qr}+this.options[this.selectedIndex].value">' \
                <option value="1" {sel1}>{await getdt(date.today().month - 1, date.today().year)}</option>' \
                <option value="2" {sel2}>{await getdt(date.today().month, date.today().year)}</option>' \
                <option value="3" {sel3}>{await getdt(date.today().month + 1, date.today().year)}</option>
             </select>'''

    for c in GetQuery(f"select html_txt from {tb}(dateadd(month, {indx - 2}, current_date), 0)"):
        return f"{cb}\n\n{c['HTML_TXT']}"

@app.get("/", response_class=HTMLResponse)
async def render_default_html():
    return await get_html(1, 2)

@app.get("/{indx}", response_class=HTMLResponse)
async def render_html(indx: int):
    return await get_html(int(str(indx)[0]), int(str(indx)[1]))


def start_webserver():
    uvicorn.run(app, host="0.0.0.0", port=3434)

import threading
MyThread = threading.Thread(target=start_webserver, daemon=True)
MyThread.start()

async def on_startup(dp):
    asyncio.create_task(scheduler())

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)