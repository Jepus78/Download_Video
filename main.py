import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import yt_dlp

app = FastAPI(title="VideoVault Core Engine")

class VideoRequest(BaseModel):
    url: str

@app.post("/api/extract")
def extract_video(request: VideoRequest):
    # Opciones optimizadas para servidores en la nube
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'format': 'best', 
        'socket_timeout': 10,  # Si el sitio no responde en 10 segundos, rompe la conexión
        'retries': 1,          # No intentes descargar una y otra vez si ya te bloquearon
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extraemos la información sin descargar
            info = ydl.extract_info(request.url, download=False)
            
            video_url = info.get('url') or info.get('entries', [{}])[0].get('url')
            title = info.get('title', 'Video_Vault')
            
            if not video_url:
                raise HTTPException(status_code=400, detail="No se pudo extraer la URL directa.")
                
            return {
                "title": title,
                "best_url_default": video_url,  # El nombre exacto que busca Android
                "duration": info.get('duration', 0)
            }
    except Exception as e:
        # Cualquier fallo de yt-dlp se captura aquí y devuelve un error 400 controlado
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # Forzamos el uso del puerto 8080 que configuramos en las variables de Railway
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
