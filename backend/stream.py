from fastapi.responses import FileResponse
from fastapi import FastAPI
from fastapi.responses import StreamingResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from pathlib import Path
import asyncio
import config as cfg
import camera
import recorder
import gpio_handler


@asynccontextmanager
async def lifespan(_: FastAPI):
    camera.start_camera()
    recorder.start_buffer()
    gpio_handler.start_pir()
    yield
    gpio_handler.stop_pir()
    recorder.stop_buffer()
    camera.stop_camera()


app = FastAPI(lifespan=lifespan)


@app.post("/api/start")
async def api_start():
    success = await asyncio.to_thread(camera.start_camera)
    if success:
        return {"success": True, "running": True}
    return JSONResponse(
        {"success": False, "running": False, "error": "Failed to start camera"},
        status_code=500
    )


@app.post("/api/stop")
async def api_stop():
    await asyncio.to_thread(camera.stop_camera)
    return {"success": True, "running": False}


@app.get("/api/status")
async def api_status():
    return {
        "running": camera.camera_running,
        "fps": camera.current_fps,
        "width": cfg.STREAM_WIDTH,
        "height": cfg.STREAM_HEIGHT,
        "recording": recorder.is_recording,
    }


@app.post("/api/photo")
async def api_photo():
    if not camera.camera_running:
        return JSONResponse({"error": "Camera not running"}, status_code=503)
    try:
        was_recording = recorder.is_recording
        await asyncio.to_thread(recorder.stop_buffer)
        jpeg = await asyncio.to_thread(camera.take_photo)
        await asyncio.to_thread(recorder.start_buffer)
        if was_recording:
            await asyncio.to_thread(recorder.start_recording)
        return Response(content=jpeg, media_type="image/jpeg")
    except Exception as e:
        print(f"Photo capture error: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)


@app.post("/api/record/start")
async def api_start_video():
    if not camera.camera_running:
        return JSONResponse({"error": "Camera not running"}, status_code=503)
    if recorder.is_recording:
        return JSONResponse({"error": "Already recording"}, status_code=400)
    try:
        await asyncio.to_thread(recorder.start_recording)
        return {"success": True, "recording": True}
    except Exception as e:
        print(f"Recording start error: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)


@app.post("/api/record/stop")
async def api_stop_video():
    if not recorder.is_recording:
        return JSONResponse({"error": "Not recording"}, status_code=400)
    try:
        path = await asyncio.to_thread(recorder.stop_recording)
        with open(path, "rb") as f:
            video_data = f.read()
        return Response(content=video_data, media_type="video/mp4")
    except Exception as e:
        print(f"Recording stop error: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)


@app.get("/api/videos")
async def list_videos():
    videos_dir = Path(cfg.VIDEOS_DIR)
    if not videos_dir.exists():
        return []
    videos = []
    for f in sorted(videos_dir.glob("*.mp4"), reverse=True):
        videos.append({
            "name": f.name,
            "size": f.stat().st_size,
            "timestamp": f.stat().st_mtime,
        })
    return videos


@app.get("/api/videos/{filename}")
async def get_video(filename: str):
    videos_dir = Path(cfg.VIDEOS_DIR)
    video_path = (videos_dir / filename).resolve()
    if video_path.parent != videos_dir.resolve() or not video_path.exists():
        return JSONResponse({"error": "Video not found"}, status_code=404)
    return FileResponse(video_path, media_type="video/mp4")


@app.delete("/api/videos/{filename}")
async def delete_video(filename: str):
    videos_dir = Path(cfg.VIDEOS_DIR)
    video_path = (videos_dir / filename).resolve()
    if video_path.parent != videos_dir.resolve() or not video_path.exists():
        return JSONResponse({"error": "Video not found"}, status_code=404)
    video_path.unlink()
    return {"success": True}

@app.get("/api/frame")
async def get_frame():
    if not camera.camera_running:
        return JSONResponse({"error": "Camera not running"}, status_code=503)
    try:
        jpeg = await asyncio.to_thread(camera.capture_frame)
        return Response(content=jpeg, media_type="image/jpeg",
                        headers={"Cache-Control": "no-store"})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.get("/stream")
async def video_stream():
    if not camera.camera_running:
        return JSONResponse({"error": "Camera is not running."}, status_code=503)
    return StreamingResponse(
        camera.generate_frames(),
        media_type='multipart/x-mixed-replace; boundary=frame'
    )


frontend_path = Path(__file__).parent.parent / "frontend"
app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="frontend")