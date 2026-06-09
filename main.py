import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import yt_dlp

app = FastAPI(title="VideoVault Core Engine")

class VideoRequest(BaseModel):
    url: str

@app.post("/api/extract")
def extract_video(request: VideoRequest):
    # Opciones optimizadas con camuflaje para evitar bloqueos
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'format': 'best', 
        'socket_timeout': 10,  
        'retries': 1,          
        # --- EL ESCUDO ANTI-BOTS ---
        'extractor_args': {
            'youtube': ['player_client=android'] # Camuflamos el servidor como un celular Android
        }
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
                "best_url_default": video_url,
                "duration": info.get('duration', 0)
            }
    except Exception as e:
        # Capturamos el error limpiamente
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
