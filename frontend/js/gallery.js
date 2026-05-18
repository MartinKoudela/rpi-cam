feather.replace();

const grid = document.getElementById('grid');
const loading = document.getElementById('loading');
const empty = document.getElementById('empty');
const videoCount = document.getElementById('videoCount');
const btnRefresh = document.getElementById('btnRefresh');

function formatSize(bytes) {
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

function formatDate(timestamp) {
    const d = new Date(timestamp * 1000);
    return d.toLocaleDateString('cs-CZ') + '  ' + d.toLocaleTimeString('cs-CZ');
}

function createCard(video) {
    const card = document.createElement('div');
    card.className = 'bg-zinc-950 border border-zinc-800 rounded overflow-hidden';
    card.innerHTML = `
        <div class="relative bg-black">
            <video
                src="/api/videos/${video.name}"
                controls
                preload="metadata"
                class="w-full aspect-video"
            ></video>
        </div>
        <div class="px-3 py-2 flex items-center justify-between gap-2">
            <div>
                <div class="text-white font-mono text-xs">${formatDate(video.timestamp)}</div>
                <div class="text-zinc-500 font-mono text-xs mt-0.5">${formatSize(video.size)}</div>
            </div>
            <button
                class="delete-btn bg-zinc-800 hover:bg-red-900 border border-zinc-700 hover:border-red-700 text-zinc-400 hover:text-red-400 p-2 rounded transition-colors cursor-pointer"
                data-name="${video.name}"
                title="Smazat"
            >
                <i data-feather="trash-2" class="w-3.5 h-3.5"></i>
            </button>
        </div>
    `;

    card.querySelector('.delete-btn').addEventListener('click', () => deleteVideo(video.name, card));
    return card;
}

async function deleteVideo(filename, card) {
    if (!confirm(`Smazat ${filename}?`)) return;
    try {
        const res = await fetch(`/api/videos/${filename}`, { method: 'DELETE' });
        if (!res.ok) throw new Error('Delete failed');
        card.remove();
        const remaining = grid.querySelectorAll('div').length;
        videoCount.textContent = `(${remaining})`;
        if (remaining === 0) {
            grid.classList.add('hidden');
            empty.classList.remove('hidden');
        }
    } catch (e) {
        alert('Smazání selhalo: ' + e.message);
    }
}

async function loadVideos() {
    loading.classList.remove('hidden');
    grid.classList.add('hidden');
    empty.classList.add('hidden');
    grid.innerHTML = '';

    try {
        const res = await fetch('/api/videos');
        const videos = await res.json();

        loading.classList.add('hidden');

        if (videos.length === 0) {
            empty.classList.remove('hidden');
            return;
        }

        videoCount.textContent = `(${videos.length})`;
        videos.forEach(v => grid.appendChild(createCard(v)));
        grid.classList.remove('hidden');
        feather.replace();
    } catch (e) {
        loading.classList.add('hidden');
        empty.classList.remove('hidden');
        empty.textContent = 'LOAD ERROR: ' + e.message;
    }
}

btnRefresh.addEventListener('click', loadVideos);
loadVideos();