feather.replace();

const statusDot = document.getElementById('statusDot');
const statusText = document.getElementById('statusText');
const btnPhoto = document.getElementById('btnPhoto');
const btnRecord = document.getElementById('btnRecord');
const nowText = document.getElementById('nowText');
const infoFrame = document.getElementById('infoFrame');
const fpsText = document.getElementById('fpsText');
const resolutionText = document.getElementById('resolutionText');
const streamImg = document.getElementById('stream');

let isRecording = false;
let framePolling = null;

function startFramePolling() {
    if (framePolling) return;
    framePolling = setInterval(() => {
        streamImg.src = '/api/frame?t=' + Date.now();
    }, 50);
}

function stopFramePolling() {
    if (!framePolling) return;
    clearInterval(framePolling);
    framePolling = null;
    streamImg.removeAttribute('src');
}

setInterval(() => {
    nowText.textContent = new Date().toLocaleString();
}, 1000);

infoFrame.className = 'w-full h-7 bg-zinc-900 flex items-center';
nowText.className = 'text-white font-mono text-xs mx-2';
fpsText.className = 'text-white font-mono text-xs mx-2 ml-auto';
resolutionText.className = 'text-white font-mono text-xs mx-2';

async function checkStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();

        if (data.running) {
            startFramePolling();
            statusDot.className = 'w-2 h-2 bg-red-500 rounded-full animate-pulse';
            statusText.textContent = 'LIVE';
            statusText.className = 'text-red-500 font-mono text-xs';
            fpsText.textContent = data.fps + ' FPS';
            resolutionText.textContent = data.width + 'x' + data.height;
            btnPhoto.disabled = false;
            btnPhoto.className = 'bg-zinc-800 hover:bg-zinc-700 border border-zinc-700 text-white px-5 py-2.5 rounded font-mono text-sm cursor-pointer transition-colors flex items-center gap-2';
            btnRecord.disabled = false;
            if (!isRecording) {
                btnRecord.className = 'bg-zinc-800 hover:bg-zinc-700 border border-zinc-700 text-white px-5 py-2.5 rounded font-mono text-sm cursor-pointer transition-colors flex items-center gap-2';
            }
        } else {
            stopFramePolling();
            statusDot.className = 'w-2 h-2 bg-zinc-600 rounded-full';
            statusText.textContent = 'OFFLINE';
            statusText.className = 'text-zinc-500 font-mono text-xs';
        }
    } catch (error) {
        console.error('Status check failed:', error);
    }
}

async function takePhoto() {
    try {
        btnPhoto.innerHTML = '<svg class="w-4 h-4 animate-spin" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path></svg> SAVING<span class="dots"><span>.</span><span>.</span><span>.</span></span>';
        const response = await fetch('/api/photo', {method: 'POST'});
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-').replace('T', '_');
        a.href = url;
        a.download = `photo_${timestamp}.jpg`;
        a.click();
        setTimeout(() => {
            btnPhoto.innerHTML = '<i data-feather="camera" class="w-4 h-4"></i> SNAPSHOT';
            feather.replace();
        }, 2000);
    } catch (error) {
        alert('Photo failed: ' + error);
    }
}

async function toggleRecord() {
    if (!isRecording) {
        btnRecord.innerHTML = '<svg class="w-4 h-4 animate-spin" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path></svg> STARTING<span class="dots"><span>.</span><span>.</span><span>.</span></span>';
        try {
            const response = await fetch('/api/record/start', {method: 'POST'});
            const data = await response.json();
            if (!response.ok) {
                alert('Error: ' + (data.error || 'Unknown error'));
                btnRecord.innerHTML = '<i data-feather="video" class="w-4 h-4"></i> RECORD';
                feather.replace();
                return;
            }
            isRecording = true;
            btnRecord.innerHTML = '<span class="w-4 h-4 bg-red-500 rounded-full animate-pulse"></span> STOP REC<span class="dots"><span>.</span><span>.</span><span>.</span></span>';
            btnRecord.className = 'bg-red-900 hover:bg-red-800 border border-red-700 text-white px-5 py-2.5 rounded font-mono text-sm cursor-pointer transition-colors flex items-center gap-2';
        } catch (error) {
            alert('Record start failed: ' + error);
            btnRecord.innerHTML = '<i data-feather="video" class="w-4 h-4"></i> RECORD';
            feather.replace();
        }
    } else {
        btnRecord.innerHTML = '<svg class="w-4 h-4 animate-spin" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path></svg> SAVING<span class="dots"><span>.</span><span>.</span><span>.</span></span>';
        try {
            const response = await fetch('/api/record/stop', {method: 'POST'});
            const blob = await response.blob();
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-').replace('T', '_');
            a.href = url;
            a.download = `video_${timestamp}.mp4`;
            a.click();
            isRecording = false;
            btnRecord.innerHTML = '<i data-feather="video" class="w-4 h-4"></i> RECORD';
            btnRecord.className = 'bg-zinc-800 hover:bg-zinc-700 border border-zinc-700 text-white px-5 py-2.5 rounded font-mono text-sm cursor-pointer transition-colors flex items-center gap-2';
            feather.replace();
        } catch (error) {
            alert('Record save failed: ' + error);
        }
    }
}

btnPhoto.addEventListener('click', takePhoto);
btnRecord.addEventListener('click', toggleRecord);

checkStatus();
setInterval(checkStatus, 1000);