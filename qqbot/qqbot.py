import configparser
from VITS import Trans,Trans2
from VITS_GENSHIN import Trans_GS
from pycqBot.cqHttpApi import cqHttpApi, cqLog
from pycqBot.data import Message
from waifu.Waifu import Waifu
from waifu.Tools import divede_sentences, load_prompt

import logging
import json
import os
import time
from pycqBot.cqCode import image, record
config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')
voice_model = config['TTS']['model']
osou=config['TTS']['osou']
fckcla=config['LLM']['fckcla'].replace('\\n', '\n')

#vits 音色列表 用于选择
yozo_dict = {"宁宁": 0, "爱瑠": 1, "芳乃": 2, "茉子": 3, "丛雨": 4, "小春": 5, "七海": 6, }
gs_dict = {"派蒙":0,"凯亚":1,"安柏":2,"丽莎":3,"琴":4,"香菱":5,"枫原万叶":6,"迪卢克":7,"温迪":8,"可莉":9,"早柚":10,"托马":11,"芭芭拉":12,"优菈":13,"云堇":14,"钟离":15,"魈":16,"凝光":17,"雷电将军":18,"北斗":19,"甘雨":20,"七七":21,"刻晴":22,"神里绫华":23,"戴因斯雷布":24,"雷泽":25,"神里绫人":26,"罗莎莉亚":27,"阿贝多":28,"八重神子":29,"宵宫":30,"荒泷一斗":31,"九条裟罗":32,"夜兰":33,"珊瑚宫心海":34,"五郎":35,"散兵":36,"女士":37,"达达利亚":38,"莫娜":39,"班尼特":40,"申鹤":41,"行秋":42,"烟绯":43,"久岐忍":44,"辛焱":45,"砂糖":46,"胡桃":47,"重云":48,"菲谢尔":49,"诺艾尔":50,"迪奥娜":51,"鹿野院平藏":52}



#Time_delay=float(config.get('Display', 'displaytime'))
Time_delay=0.5
def load_config():
    with open(f'./qqbot/bot.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data['user_id_list']


def make_qq_bot(callback, waifu: Waifu, send_text, send_voice, tts):
    cqLog(level=logging.INFO, logPath='./qqbot/cqLogs')

    cqapi = cqHttpApi(download_path='./qqbot/download')

    def on_private_msg(message: Message):
        if 'CQ' in message.message:
            return
        callback.set_sender(message.sender)
        try:
            waifu.ask(message.message)
        except Exception as e:
            logging.error(e)

    def on_private_msg_nonstream(message: Message):
        if 'CQ' in message.message:
            return
        try:
            reply = waifu.ask(message.message)
            if reply == '':
            # 处理空回复的情况，例如跳过处理或返回错误信息
                logging.info('Claude BAN了你，没有回应你~')
                message.sender.send_message('Claude BAN了你，没回应你~')
                return
            sentences = divede_sentences(reply) #切割裁剪截断去符号处理
            for st in sentences:
                time.sleep(Time_delay)
                if st == '' or st == ' ':
                    continue
                if send_text:
                    message.sender.send_message(waifu.add_emoji(st))
                    logging.info(f'发送信息: {st}')
                    
                if send_voice:
                    if voice_model=="Edge":
                        emotion = waifu.analyze_emotion(st)
                        print("sned",st,'voice.wav')
                        tts.speak(st, emotion)
                        Trans2(st,0,'voice.wav')
                        file_path = './voice.wav'
                        abs_path = os.path.abspath(file_path)
                        mtime = os.path.getmtime(file_path)
                        local_time = time.localtime(mtime)
                        time_str = time.strftime("%Y-%m-%d %H:%M:%S", local_time)
                        message.sender.send_message("%s" % record(file='file:///' + abs_path))
                        logging.info(f'发送语音({emotion} {time_str}): {st}')
                    elif voice_model=="Vits": #中文，原神VITS
                        if osou in gs_dict:
                            print("aih")
                            emotion = waifu.analyze_emotion(st)
                            print("sned",st,'voice.wav')
                            Trans_GS(st,gs_dict[osou],'voice.wav')
                            file_path = './voice.wav'
                            abs_path = os.path.abspath(file_path)
                            mtime = os.path.getmtime(file_path)
                            local_time = time.localtime(mtime)
                            time_str = time.strftime("%Y-%m-%d %H:%M:%S", local_time)
                            message.sender.send_message("%s" % record(file='file:///' + abs_path))
                            logging.info(f'发送语音({emotion} {time_str}): {st}')
                        elif osou in yozo_dict: #暂时留给日语
                            emotion = waifu.analyze_emotion(st)
                            print("sned",st,'voice.wav')
                            Trans2(st,yozo_dict[osou],'voice.wav')
                            file_path = './voice.wav'
                            abs_path = os.path.abspath(file_path)
                            mtime = os.path.getmtime(file_path)
                            local_time = time.localtime(mtime)
                            time_str = time.strftime("%Y-%m-%d %H:%M:%S", local_time)
                            message.sender.send_message("%s" % record(file='file:///' + abs_path))
                            logging.info(f'发送语音({emotion} {time_str}): {st}')
                    print(osou)
                    print(emotion)
            time.sleep(Time_delay)
            file_name = waifu.finish_ask(reply)
            if not file_name == '':
                file_path = './presets/emoticon/' + file_name
                abs_path = os.path.abspath(file_path)
                message.sender.send_message("%s" % image(file='file:///' + abs_path))
            time.sleep(Time_delay)
            waifu.brain.think(f'{fckcla}')
            time.sleep(Time_delay)
            waifu.brain.think('/reset 请忘记之前的对话。')
        except Exception as e:
            logging.error(e)

    user = load_config()

    bot = cqapi.create_bot(
        group_id_list=[0],
        user_id_list=user
    )
    if callback is None:
        bot.on_private_msg = on_private_msg_nonstream
    else:
        bot.on_private_msg = on_private_msg

    # TODO: 指令功能
    # def echo(commandData, message: Message):
    #     # 回复消息
    #     message.sender.send_message(" ".join(commandData))
    # 设置指令为 echo
    # bot.command(echo, "echo", {
    #     # echo 帮助
    #     "help": [
    #         "#echo - 输出文本"
    #     ],
    #     "type": "all"
    # })
    bot.start(go_cqhttp_path='./qqbot/')
