feather.replace();

const statusDot = document.getElementById('statusDot');
const recDot = document.getElementById('recDot');
const statusText = document.getElementById('statusText');
const placeholder = document.getElementById('placeholder');
const stream = document.getElementById('stream');
const btnStart = document.getElementById('btnStart');
const btnStop = document.getElementById('btnStop');
const btnPhoto = document.getElementById('btnPhoto');
const btnRecord = document.getElementById('btnRecord');
const nowText = document.getElementById('nowText');
const infoFrame = document.getElementById('infoFrame');
const fpsText = document.getElementById('fpsText');
const resolutionText = document.getElementById('resolutionText');
let isRecording = false;


let isRunning = false;

function updateUI(running) {
    isRunning = running;

    if (running) {
        // On
        statusDot.className = 'w-2 h-2 bg-red-500 rounded-full animate-pulse';
        statusText.textContent = 'LIVE';
        statusText.className = 'text-red-500 font-mono text-xs';

        // Information frame
        setInterval(() => {
            nowText.textContent = new Date().toLocaleString();
        }, 1000);
        nowText.className = 'text-white font-mono text-xs mx-2';

        fpsText.className = 'text-white font-mono text-xs mx-2 ml-auto'
        resolutionText.className = 'text-white font-mono text-xs mx-2'

        infoFrame.className = 'w-full h-7 bg-zinc-900 flex items-center';

        // Show stream
        placeholder.classList.add('hidden');
        stream.classList.remove('hidden');
        stream.src = '/stream?' + Date.now();

        // Stop
        btnStart.disabled = true;
        btnStart.className = 'bg-zinc-800 border border-zinc-700 text-zinc-500 px-5 py-2.5 rounded font-mono text-sm cursor-not-allowed transition-colors flex items-center gap-2';

        btnStop.disabled = false;
        btnStop.className = 'bg-red-900 hover:bg-red-800 border border-red-700 text-white px-5 py-2.5 rounded font-mono text-sm cursor-pointer transition-colors flex items-center gap-2';

        btnPhoto.disabled = false;
        btnPhoto.className = 'bg-zinc-800 hover:bg-zinc-700 border border-zinc-700 text-white px-5 py-2.5 rounded font-mono text-sm cursor-pointer transition-colors flex items-center gap-2';

        btnRecord.disabled = false;
        btnRecord.className = 'bg-zinc-800 hover:bg-zinc-700 border border-zinc-700 text-white px-5 py-2.5 rounded font-mono text-sm cursor-pointer transition-colors flex items-center gap-2';

    } else {
        // Off
        statusDot.className = 'w-2 h-2 bg-zinc-600 rounded-full';
        statusText.textContent = 'OFFLINE';
        statusText.className = 'text-zinc-500 font-mono text-xs';

        // Show placeholder
        stream.classList.add('hidden');
        stream.src = '';
        placeholder.classList.remove('hidden');

        // Start
        btnStart.disabled = false;
        btnStart.className = 'bg-emerald-900 hover:bg-emerald-800 border border-emerald-700 text-white px-5 py-2.5 rounded font-mono text-sm cursor-pointer transition-colors flex items-center gap-2';

        btnStop.disabled = true;
        btnStop.className = 'bg-zinc-800 border border-zinc-700 text-zinc-500 px-5 py-2.5 rounded font-mono text-sm cursor-not-allowed transition-colors flex items-center gap-2';

        btnPhoto.disabled = true;
        btnPhoto.className = 'bg-zinc-800 border border-zinc-700 text-zinc-500 px-5 py-2.5 rounded font-mono text-sm cursor-not-allowed transition-colors flex items-center gap-2';

        btnRecord.disabled = true;
        btnRecord.className = 'bg-zinc-800 border border-zinc-700 text-zinc-500 px-5 py-2.5 rounded font-mono text-sm cursor-not-allowed transition-colors flex items-center gap-2';
    }
}

async function checkStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        updateUI(data.running);
        if (data.running) {
            fpsText.textContent = data.fps + ' FPS';
            resolutionText.textContent = data.width + 'x' + data.height;

        }
    } catch (error) {
        console.error('Status check failed:', error);
        updateUI(false);
    }
}

async function startCamera() {
    btnStart.disabled = true;
    btnStart.innerHTML = '<svg class="w-4 h-4 animate-spin" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path></svg> STARTING<span class="dots"><span>.</span><span>.</span><span>.</span></span>';

    try {
        const response = await fetch('/api/start', {method: 'POST'});
        const data = await response.json();

        if (data.success) {
            updateUI(true);
            location.reload();
        } else {
            alert('Camera start unsuccessful ' + (data.error || 'Unknown error'));
            updateUI(false);
        }
    } catch (error) {
        console.error('Start failed:', error);
        alert('Error starting camera');
        updateUI(false);
    }
}

async function stopCamera() {
    btnStop.disabled = true;
    btnStop.innerHTML = '<svg class="w-4 h-4 animate-spin" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path></svg> STOPPING<span class="dots"><span>.</span><span>.</span><span>.</span></span>';

    try {
        const response = await fetch('/api/stop', {method: 'POST'});
        const data = await response.json();
        updateUI(false);
        location.reload();

    } catch (error) {
        console.error('Stop failed:', error);
        updateUI(false);
    }
}

async function takePhoto() {
    try {
        const response = await fetch('/api/photo', {method: 'POST'});
        const data = await response.blob();
        const url = URL.createObjectURL(data);
        const a = document.createElement('a');
        const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-').replace('T', '_');
        btnPhoto.innerHTML = '<svg class="w-4 h-4 animate-spin" viewBox="0 0 24 24">' +
            '<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"></circle>' +
            '<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>' +
            '</svg> SAVING<span class="dots"><span>.</span><span>.</span><span>.</span></span>';

        a.href = url;
        a.download = `photo_${timestamp}.jpg`;
        a.click();
        setTimeout(() => window.location.reload(), 3000);
    } catch (error) {
        alert('Photo failed:' + error);
    }
}

async function toggleRecord() {
    if (!isRecording) {
        btnRecord.innerHTML = '<svg class="w-4 h-4 animate-spin" viewBox="0 0 24 24">' +
            '<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"></circle>' +
            '<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>' +
            '</svg> STARTING <span class="dots blink"><span>.</span><span>.</span><span>.</span></span>';

        try {
            const response = await fetch('/api/record/start', {method: 'POST'});
            const data = await response.json();

            if (!response.ok) {
                alert('Error: ' + (data.error || 'Unknown error'));
                return;
            }

            if (data.success) {
                isRecording = true;
                recDot.className = 'w-2 h-2 bg-red-500 rounded-full animate-pulse';
                btnRecord.innerHTML = '<span class="w-4 h-4 bg-red-500 rounded-full animate-pulse"></span> STOP REC<span class="dots"><span>.</span><span>.</span><span>.</span></span>';
                btnRecord.className = 'bg-red-900 hover:bg-red-800 border border-red-700 text-white px-5 py-2.5 rounded ' +
                    'font-mono text-sm cursor-pointer transition-colors flex items-center gap-2';
            }
        } catch (error) {
            alert('Record start failed: ' + error);
            btnRecord.innerHTML = '<i data-feather="video" class="w-4 h-4"></i> RECORD';
            feather.replace();
        }
    } else {
        btnRecord.innerHTML = '<svg class="w-4 h-4 animate-spin" viewBox="0 0 24 24">' +
            '<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"></circle>' +
            '<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>' +
            '</svg> SAVING<span class="dots"><span>.</span><span>.</span><span>.</span></span>';

        try {
            const response = await fetch('/api/record/stop', {method: 'POST'});
            const data = await response.blob();

            const url = URL.createObjectURL(data);
            const a = document.createElement('a');
            const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-').replace('T', '_');
            a.href = url;
            a.download = `video_${timestamp}.mp4`;
            a.click();

            isRecording = false
            btnRecord.innerHTML = '<i data-feather="video" class="w-4 h-4"></i> RECORD';
            btnRecord.className = 'bg-zinc-800 hover:bg-zinc-700 border border-zinc-700 text-white px-5 py-2.5 rounded ' +
                'font-mono text-sm cursor-pointer transition-colors flex items-center gap-2';
            feather.replace();

        } catch (error) {
            alert('Record save failed: ' + error);

        }
    }
}

async function loadFormats() {
    const response = await fetch('/api/formats');
    const data = await response.json();
    return data;
}

async function switchFormat(format_name) {
    const response = await fetch(`/api/format/${format_name}`, {method: 'POST'});
    const data = await response.json();
    if (data.success) {
        console.log('Switched to:', data.format);
    }
}

async function loadFilters() {
    const response = await fetch('/api/filters');
    const data = await response.json();
    return data;
}

async function switchFilter(filter_name) {
    const response = await fetch(`/api/filter/${filter_name}`, {method: 'POST'});
    const data = await response.json();
    if (data.success) {
        console.log('Switched to:', data.filter);
    }
}


btnStart.addEventListener('click', startCamera);
btnStop.addEventListener('click', stopCamera);
btnPhoto.addEventListener('click', takePhoto);
btnRecord.addEventListener('click', toggleRecord);
checkStatus();

setInterval(checkStatus, 1000);