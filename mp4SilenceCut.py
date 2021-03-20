#210320 mp4から無音部分を除去するプログラム/佐賀大19238032石塚快@firestarter2501
#実行する前にFFmpegをインストールしてPATHを通すこと!!
#noise,duration等を適宜変更して使用すること

import subprocess
import os
import glob
#動画元素材の取得
def mk_movieList(movie_folder):
    files = os.listdir(movie_folder)
    files = [x for x in files if x[-4:] == '.mp4']
    files = [x for x in files if x[0] != '.']
    return files
 
def mk_starts_ends(wk_dir,movie):
    os.chdir(wk_dir)
    output = subprocess.run(["ffmpeg","-i",movie,"-af", "silencedetect=noise=-30dB:duration=2","-f","null","-"], stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    print(output)
    s = str(output)
    lines = s.split('\\n')
    time_list = []
    for line in lines:
        if "silencedetect" in line:
            words = line.split(" ")
            for i in range(len(words)):
                if "silence_start" in words[i]:
                    time_list.append(float((words[i+1]).replace('\\r',''))+2)
                if "silence_end" in words[i]:
                    time_list.append(float((words[i+1]).replace('\\r',''))-2)
 
    print(time_list)
    starts_ends = list(zip(*[iter(time_list)]*2))
    return starts_ends
 
def mk_jumpcut(wk_dir,movie,starts_ends):
    os.chdir(wk_dir)
    for i in range(len(starts_ends)-1):
        movie_name = movie.split(".")
        splitfile = "./JumpCut/" + movie_name[0] + "_" + str(i) + ".mp4"
        print(splitfile)
        output = subprocess.run(["ffmpeg", "-i",movie,"-ss",str(starts_ends[i][1]),"-t",str(starts_ends[i+1][0]-starts_ends[i][1]),splitfile],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        print(output)
 
#動画の結合
def join_movie(movie_files,out_path):
    videos = glob.glob(movie_files)
    print(videos)
 
    # join対象のlist
    with open("JumpCut/tmp.txt","w") as fp:
        lines = [f"file '{os.path.split(line)[1]}'" for line in videos]
        #1,10,11,~のようになってしまうのを防止。並び替え
        lineList = sorted(lines,key=len)
        fp.write("\n".join(lineList))
 
    output = subprocess.run(["ffmpeg","-f","concat","-i","JumpCut/tmp.txt","-c","copy",out_path],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    print(output)
 
#ディレクトリの指定
print("元動画のディレクトリを絶対パスで指定してください ex. /Users/kishi/Downloads/")
movie_folder = input()
print("動画を出力したいフォルダの絶対パス*.mp4を入力してください ex. /Users/kishi/Downloads/*.mp4")
movie_files = input()
out_path = "join_out.mp4"
 
os.chdir(movie_folder)
wk_dir = os.path.abspath(".")
try:
    os.mkdir("JumpCut")
except:
    pass
 
movie_list = mk_movieList(movie_folder)
 
for movie in movie_list:
    print(movie)
    starts_ends = mk_starts_ends(wk_dir,movie)
    print(starts_ends)
    mk_jumpcut(wk_dir,movie,starts_ends)
    join_movie(movie_files,out_path)
    print(movie_files,out_path)