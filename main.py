import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import yt_dlp

app = FastAPI(title="VideoVault Core Engine")

class VideoRequest(BaseModel):
    url: str

@app.post("/api/extract")
def extract_video(request: VideoRequest):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(request.url, download=False)
            title = info.get('title', 'Video_Vault')
            
            # 1. Buscamos todas las calidades disponibles
            available_formats = []
            
            for f in info.get('formats', []):
                # Filtramos: Solo queremos formatos que tengan Video (vcodec) Y Audio (acodec)
                # para que el celular no descargue videos mudos.
                if f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                    height = f.get('height')
                    ext = f.get('ext')
                    url = f.get('url')
                    
                    if height and url:
                        available_formats.append({
                            "quality": f"{height}p",
                            "ext": ext,
                            "url": url
                        })
            
            # Limpiamos duplicados (a veces yt-dlp arroja dos formatos 720p iguales)
            unique_formats = {f['quality']: f for f in available_formats}.values()

            # URL de respaldo (la mejor calidad por defecto por si falla el filtro)
            fallback_url = info.get('url') or info.get('entries', [{}])[0].get('url')

            return {
                "title": title,
                "duration": info.get('duration', 0),
                "best_url_default": fallback_url,
                "formats": list(unique_formats) # <--- Aquí enviamos la lista de calidades
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)