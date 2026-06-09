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
            
            available_formats = []
            
            for f in info.get('formats', []):
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
            
            unique_formats = {f['quality']: f for f in available_formats}.values()

            fallback_url = info.get('url') or info.get('entries', [{}])[0].get('url')

            return {
                "title": title,
                "duration": info.get('duration', 0),
                "best_url_default": fallback_url,
                "formats": list(unique_formats)
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
