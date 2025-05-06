import customtkinter as ctk
from pytubefix import YouTube
import os
from tkinter import filedialog, Menu
import threading
from pytubefix.exceptions import RegexMatchError
from moviepy.editor import VideoFileClip, AudioFileClip


# aparencia
ctk.set_appearance_mode('dark') 

# diretório de saída padrão
diretorio_output = "."

# Variáveis globais barra de progresso e label
barra_progresso = None
label_progresso_texto = None

# função para selecionar o diretório de saída
def selecionar_diretorio():
    global diretorio_output
    diretorio = filedialog.askdirectory()
    if diretorio:
        diretorio_output = diretorio
        label_diretorio.configure(text=f"Diretório de Saída: {diretorio_output}")

# função callback para progress bar
def on_progress(stream, chunk, bytes_remaining):
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    percentage = bytes_downloaded / total_size * 100
    if barra_progresso:
        barra_progresso.set(percentage / 100)
    if label_progresso_texto:
        label_progresso_texto.configure(text=f"Progresso: {percentage:.2f}%")

# função para baixar o video em mp4 com qualidade especifica
def download_video_quality_thread(url, output_path, quality):
    global barra_progresso, label_progresso_texto
    try:
        yt = YouTube(url)
        video_stream = yt.streams.filter(file_extension='mp4', res=quality).first()
        audio_stream = yt.streams.filter(only_audio=True).first()

        if video_stream and audio_stream:
            mensagem = f"Baixando video de: {yt.title} na qualidade {quality}\n"
            texto_output.insert(ctk.END, mensagem)
            texto_output.see(ctk.END)
            app.update()

            temp_video_path = os.path.join(output_path, f"temp_video_{yt.video_id}.mp4")
            temp_audio_path = os.path.join(output_path, f"temp_audio_{yt.video_id}.mp4")
            final_video_path = os.path.join(output_path, f"{yt.title.replace(' ', '_')}_{quality}.mp4")

            # Simulação de progresso para o vídeo (substitua com a lógica real se pytube permitir)
            video_stream.download(output_path=output_path, filename=f"temp_video_{yt.video_id}.mp4")
            if barra_progresso: barra_progresso.set(0.5) # 50% após baixar o vídeo
            if label_progresso_texto: label_progresso_texto.configure(text="Progresso: 50.00%")
            app.update()

            mensagem = f"Baixando áudio...\n"
            texto_output.insert(ctk.END, mensagem)
            texto_output.see(ctk.END)
            app.update()

            # Simulação de progresso para o áudio
            audio_stream.download(output_path=output_path, filename=f"temp_audio_{yt.video_id}.mp4")
            app.update()

            mensagem = f"Mesclando vídeo e áudio...\n"
            texto_output.insert(ctk.END, mensagem)
            texto_output.see(ctk.END)
            app.update()

            try:
                video_clip = VideoFileClip(temp_video_path)
                audio_clip = AudioFileClip(temp_audio_path)
                final_clip = video_clip.set_audio(audio_clip)
                final_clip.write_videofile(final_video_path)

                video_clip.close()
                audio_clip.close()
                final_clip.close()

                os.remove(temp_video_path)
                os.remove(temp_audio_path)

                mensagem = f"Vídeo com áudio salvo em: {final_video_path}\n"
                texto_output.insert(ctk.END, mensagem)
                texto_output.see(ctk.END)
                app.update()

            except Exception as e:
                texto_output.insert(ctk.END, f"Erro ao mesclar vídeo e áudio: {e}\n")
                texto_output.see(ctk.END)
                app.update()
                if os.path.exists(temp_video_path):
                    os.remove(temp_video_path)
                if os.path.exists(temp_audio_path):
                    os.remove(temp_audio_path)

        elif video_stream:
            texto_output.insert(ctk.END, f"Aviso: Stream de áudio separado encontrado. O vídeo pode ser baixado sem áudio na qualidade {quality}.\n")
            texto_output.see(ctk.END)
            app.update()
            out_file = video_stream.download(output_path=output_path, filename=f"{yt.title.replace(' ', '_')}_{quality}_no_audio.mp4")
            mensagem = f"Vídeo (sem áudio) salvo em: {out_file}\n"
            texto_output.insert(ctk.END, mensagem)
            texto_output.see(ctk.END)
            app.update()
            if barra_progresso: barra_progresso.set(1)
            if label_progresso_texto: label_progresso_texto.configure(text="Progresso: 100.00%")

        else:
            texto_output.insert(ctk.END, f"Vídeo não disponível para download na qualidade {quality}.\n")
            texto_output.see(ctk.END)
            app.update()
            if barra_progresso: barra_progresso.set(0)
            if label_progresso_texto: label_progresso_texto.configure(text="Progresso: 0.00%")

    except RegexMatchError:
        texto_output.insert(ctk.END, "Erro: URL do YouTube inválido.\n")
        texto_output.see(ctk.END)
        app.update()
        if barra_progresso: barra_progresso.set(0)
        if label_progresso_texto: label_progresso_texto.configure(text="Progresso: 0.00%")
    except Exception as e:
        texto_output.insert(ctk.END, f"Ocorreu um erro ao baixar o vídeo na qualidade {quality}: {e}\n")
        texto_output.see(ctk.END)
        app.update()
        if barra_progresso: barra_progresso.set(0)
        if label_progresso_texto: label_progresso_texto.configure(text="Progresso: 0.00%")
    finally:
        mensagem_final = f"Processo de download concluído.\n"
        mensagem_final += "Insira outro URL para baixar outro vídeo ou áudio\n"
        texto_output.insert(ctk.END, mensagem_final)
        texto_output.see(ctk.END)
        app.update()
        botao_baixar_video.configure(state="normal") # Reabilita o botão de vídeo
        # Define a barra de progresso para 100%
        if barra_progresso:
            barra_progresso.set(1) # 1 representa 100%
        if label_progresso_texto:
            label_progresso_texto.configure(text="Progresso: 100.00%")


# função para mostrar o menu de qualidade do video
def mostrar_menu_qualidade(event):
    menu_qualidade.post(event.x_root, event.y_root)

# função para executar o download com a qualidade escolhida
def executar_download_video(quality):
    global barra_progresso, label_progresso_texto
    url = campo_usuario.get()
    texto_output.configure(state="normal")
    texto_output.delete(1.0, ctk.END)     # Limpa o texto anterior
    texto_output.insert(ctk.END, f"Iniciando download na qualidade {quality}...\n")
    botao_baixar_video.configure(state="disabled") # Desabilita o botão durante o download

    thread = threading.Thread(target=download_video_quality_thread, args=(url, diretorio_output, quality))
    thread.start()


# função para baixar o áudio
def download_audio_thread(url, output_path):
    global barra_progresso, label_progresso_texto
    try:
        yt = YouTube(url) # Removido on_progress_callback aqui
        audio_stream = yt.streams.filter(only_audio=True).first()

        if audio_stream:
            mensagem = f"Baixando áudio de: {yt.title}\n"
            texto_output.insert(ctk.END, mensagem)
            texto_output.see(ctk.END)
            app.update()

            audio_stream.download(output_path=output_path, filename="audio_temp") 
            if barra_progresso: barra_progresso.set(0.8) # 80% após baixar o áudio
            if label_progresso_texto: label_progresso_texto.configure(text="Progresso: 80.00%")
            app.update()

            out_file = os.path.join(output_path, "audio_temp")
            base, ext = os.path.splitext(out_file)
            new_file = base + '.mp3'
            os.rename(out_file, new_file)

            mensagem = f"Áudio salvo em: {new_file}\n"
            texto_output.insert(ctk.END, mensagem)
            texto_output.see(ctk.END)
            app.update()
        else:
            texto_output.insert(ctk.END, "Música não disponível para download.\n")
            texto_output.see(ctk.END)
            app.update()
            if barra_progresso: barra_progresso.set(0)
            if label_progresso_texto: label_progresso_texto.configure(text="Progresso: 0.00%")

    except Exception as e:
        texto_output.insert(ctk.END, f"Ocorreu um erro: {e}\n")
        texto_output.see(ctk.END)
        app.update()
        if barra_progresso: barra_progresso.set(0)
        if label_progresso_texto: label_progresso_texto.configure(text="Progresso: 0.00%")
    finally:
        mensagem_final = f"Arquivo baixado em: {output_path}\n"
        mensagem_final += "Insira outro URL para baixar outro vídeo\n"
        texto_output.insert(ctk.END, mensagem_final)
        texto_output.see(ctk.END)
        app.update()
        botao_baixar_audio.configure(state="normal") # Reabilita o botão de áudio
        # Define a barra de progresso para 100%
        if barra_progresso:
            barra_progresso.set(1) # 1 representa 100%
        if label_progresso_texto:
            label_progresso_texto.configure(text="Progresso: 100.00%")

# função para executar o download do audio
def executar_download_audio():
    global barra_progresso, label_progresso_texto
    url = campo_usuario.get()
    texto_output.configure(state="normal") # Habilita o widget de texto para escrita
    texto_output.delete(1.0, ctk.END)     # Limpa o texto anterior
    texto_output.insert(ctk.END, "Iniciando download...\n")
    botao_baixar_audio.configure(state="disabled") # Desabilita o botão de áudio

    thread = threading.Thread(target= download_audio_thread, args=(url, diretorio_output))
    thread.start()  # Inicia a thread para o download do áudio

# Janela Principal
app = ctk.CTk()
app.title('Youtube Video Downloader (by @eduardokoerich_)')
app.geometry('600x600')

# Menu de Qualidade
menu_qualidade = Menu(app, tearoff=0)
qualidades_disponiveis = ['240p', '360p', '480p', '720p', '1080p']
for qualidade in qualidades_disponiveis:
    menu_qualidade.add_command(label=qualidade, command=lambda q=qualidade: executar_download_video(q))


# Campos

    # Label URL
label_usuario = ctk.CTkLabel(app, text= 'Cole aqui a URL do video que deseja baixar: ')
label_usuario.pack(pady=20)

    # Entry URL
campo_usuario = ctk.CTkEntry(app, placeholder_text='URL do Youtube')
campo_usuario.pack(pady=10)

    # Frame para botões de download
botao_download_frame = ctk.CTkFrame(app)
botao_download_frame.pack(pady=10)

    # Botão download audio
botao_baixar_audio = ctk.CTkButton(botao_download_frame, text='Baixar MP3 (Somente Áudio)', command=executar_download_audio)
botao_baixar_audio.pack(side=ctk.LEFT, padx=10)

    # botão download video
botao_baixar_video = ctk.CTkButton(botao_download_frame, text='Baixar MP4 (Vídeo)', command=mostrar_menu_qualidade)
botao_baixar_video.pack(side=ctk.LEFT, padx=10)
botao_baixar_video.bind("<Button-1>", mostrar_menu_qualidade) # Bind para mostrar o menu de qualidade

    # Label exibir diretório de saida
label_diretorio = ctk.CTkLabel(app, text=f"Pasta para salvar: {diretorio_output}")
label_diretorio.pack(pady=5)

    # Botão para selecionar o diretório de saída
botao_selecionar_diretorio = ctk.CTkButton(app, text='Selecionar Pasta', command=selecionar_diretorio)
botao_selecionar_diretorio.pack(pady=10)

    # Barra de progresso
barra_progresso = ctk.CTkProgressBar(app, width=400)
barra_progresso.pack(pady=10)
barra_progresso.set(0)

    # Label de progresso
label_progresso_texto = ctk.CTkLabel(app, text="Progresso: 0.00%")
label_progresso_texto.pack(pady=5)

    # Widget de Texto para Output
texto_output = ctk.CTkTextbox(app, width=550, height=150)
texto_output.pack(pady=10)
texto_output.insert(ctk.END, "Aguardando download...\n")
texto_output.configure(state="disabled") # Deixa o texto apenas para leitura

# Iniciar
app.mainloop()