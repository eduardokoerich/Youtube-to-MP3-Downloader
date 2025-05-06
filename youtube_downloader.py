import customtkinter as ctk
from pytubefix import YouTube
import os
from tkinter import filedialog
import threading

#aparencia
ctk.set_appearance_mode('dark')

#diretório de saída
diretorio_output = "."


#função para selecionar o diretório de saída
def selecionar_diretorio():
    global diretorio_output
    diretorio = filedialog.askdirectory()
    if diretorio:
        diretorio_output = diretorio
        label_diretorio.configure(text=f"Diretório de Saída: {diretorio_output}")



#função para baixar o áudio
def download_audio_thread(url, output_path):
    try:
        yt = YouTube(url)
        audio_stream = yt.streams.filter(only_audio=True).first()

        if audio_stream:
            mensagem = f"Baixando áudio de: {yt.title}\n"
            texto_output.insert(ctk.END, mensagem)
            texto_output.see(ctk.END)  
            app.update()

            out_file = audio_stream.download(output_path=output_path)
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

    except Exception as e:
        texto_output.insert(ctk.END, f"Ocorreu um erro: {e}\n")
        texto_output.see(ctk.END)  
        app.update()
    finally:
        mensagem_final = f"Arquivo baixado em: {output_path}\n"
        mensagem_final += "Insira outro URL para baixar outro vídeo\n"
        texto_output.insert(ctk.END, mensagem_final)
        texto_output.see(ctk.END)
        app.update()
        botao_download.configure(state="normal")  # Reabilita o botão após o download


#função para executar o download
def executar_download():
    url = campo_usuario.get()
    texto_output.configure(state="normal")  # Habilita o widget de texto para escrita
    texto_output.delete(1.0, ctk.END)      # Limpa o texto anterior
    texto_output.insert(ctk.END, "Iniciando download...\n")
    botao_download.configure(state="disabled")  # Desabilita o botão durante o download

    thread = threading.Thread(target= download_audio_thread, args=(url, diretorio_output))
    thread.start()  # Inicia a thread para o download do áudio

#Janela Principal
app = ctk.CTk()
app.title('Youtube Downloader')
app.geometry('600x400')
    
    
#Campos

    #Label 
label_usuario = ctk.CTkLabel(app, text= 'Cole aqui a URL do video que deseja baixar: ')
label_usuario.pack(pady=20)

    #Entry
campo_usuario = ctk.CTkEntry(app, placeholder_text='URL do Youtube')
campo_usuario.pack(pady=10)

    #Button Download
botao_download = ctk.CTkButton(app, text='Download', command=executar_download)
botao_download.pack(pady=20)       

    #label exibir diretório de saida
label_diretorio = ctk.CTkLabel(app, text=f"Selecione a pasta para baixar o arquivo: {diretorio_output}")
label_diretorio.pack(pady=5)

    #Botão para selecionar o diretório de saída
botao_selecionar_diretorio = ctk.CTkButton(app, text='Selecionar Pasta', command=selecionar_diretorio)
botao_selecionar_diretorio.pack(pady=10)  
    
    # Widget de Texto para Output
texto_output = ctk.CTkTextbox(app, width=550, height=150)
texto_output.pack(pady=10)
texto_output.insert(ctk.END, "Aguardando download...\n")
texto_output.configure(state="disabled")  # Deixa o texto apenas para leitura

#Iniciar
app.mainloop()