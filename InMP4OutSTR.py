# モジュールのインポート
import os, tkinter, tkinter.filedialog, tkinter.messagebox
import speech_recognition as sr
from moviepy.editor import VideoFileClip

############################## 
#1 ファイル選択ダイアログの表示 
##############################
def getOpenFile():
    root = tkinter.Tk()
    root.withdraw()
    FileType = [("動画ファイル", "*.mp4")]
    iDir = os.path.abspath(os.path.dirname(__file__))
    tkinter.messagebox.showinfo('動画分割プログラム','処理ファイルを選択してください！')
    file = tkinter.filedialog.askopenfilename(
        filetypes= FileType,
        title="処理ファイルを選択してください",
        initialdir =iDir
    )
    
    return file

################################################################## 
# 動画ファイルのパスを指定して話している時間帯とテキストを取得する
##################################################################
def GoogleSpeechGetTextTime(video_file_path):
    talking_periods = find_talking_periods(video_file_path)

    print("話している時間帯とテキスト:")
    for start, end, text in talking_periods:
        print(f"開始時間: {start:.2f}秒, 終了時間: {end:.2f}秒, 文章: {text}")
    generate_srt_file(talking_periods,"Output.srt")

#############################################
# 音声からはなしてる時間帯と文字を抽出する処理
#############################################
def find_talking_periods(video_file_path):
    video_clip = VideoFileClip(video_file_path)
    audio = video_clip.audio

    audio_file_path = "temp_audio.wav"
    audio.write_audiofile(audio_file_path, codec='pcm_s16le')  # 音声を一時的なファイルに保存
    audio.close()

    transcribed_text = transcribe_audio(audio_file_path)

    words_per_minute = len(transcribed_text.split()) / (video_clip.duration / 60)  # 分間の単語数を計算
    talking_periods = []

    if words_per_minute > 5:  # 分間の単語数が5以上の場合、喋っているとみなす
        # 文字起こしのテキストから話している時間帯を特定
        text_start_index = 0
        in_talking_period = False
        for i, char in enumerate(transcribed_text):
            if char.isalpha():
                if not in_talking_period:
                    text_start_index = i
                    in_talking_period = True
            else:
                if in_talking_period:
                    text_end_index = i
                    start_time = convert_index_to_time(text_start_index, video_clip.duration, len(transcribed_text))
                    end_time = convert_index_to_time(text_end_index, video_clip.duration, len(transcribed_text))
                    #talking_periods.append((text_start_index,start_time, end_time, transcribed_text[text_start_index:text_end_index]))
                    talking_periods.append((start_time, end_time, transcribed_text[text_start_index:text_end_index]))
                    in_talking_period = False
    os.remove(audio_file_path)
    return talking_periods

############################################################
#Google Speech Recognition APIを使用して音声をテキストに変換
############################################################
def transcribe_audio(audio_file_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file_path) as source:
        audio_data = recognizer.record(source)  # 音声データを録音

    try:
        text = recognizer.recognize_google(audio_data, language="ja-JP")  # Google Speech Recognition APIを使用して音声をテキストに変換
        return text
    except sr.UnknownValueError:
        return ""

######################
# 時間表記変更処理
######################
def convert_index_to_time(index, duration, total_length):
    start_time = index * duration / total_length
    return start_time

###############################################################
# 時間フォーマット処理
###############################################################
def format_time(seconds):
    # 秒数をHH:MM:SS.fff形式にフォーマット
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    milliseconds = int((seconds - int(seconds)) * 1000)  # 秒からミリ秒を計算
    return "{:02}:{:02}:{:02}.{:03}".format(int(hours), int(minutes), int(seconds), milliseconds)


###############################################################
# SRTファイル形式
###############################################################
def generate_srt_file(talking_periods, output_file_path):
  with open(output_file_path, 'w', encoding='utf-8') as srt_file:  # エンコーディングをutf-8に指定
        for idx, (start, end, text) in enumerate(talking_periods, start=1):
            formatted_start = format_time(start)
            formatted_end = format_time(end)
            srt_file.write(f"{idx}\n")
            srt_file.write(f"{formatted_start} --> {formatted_end}\n")
            srt_file.write(f"{text}\n\n")
            print(f"{idx}\n")
            print(f"{formatted_start} --> {formatted_end}\n")
            print(f"{text}\n\n")
            

###############
# main
##############
fileName = getOpenFile()
GoogleSpeechGetTextTime(fileName)