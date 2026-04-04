// ──────────────────────────────────────
// Color extraction (Canvas API)
// ──────────────────────────────────────
function extractColors(img, nColors) {
    nColors = nColors || 6;
    const canvas = document.getElementById('palette-canvas');
    const ctx = canvas.getContext('2d');
    const w = 200, h = 200;
    canvas.width = w;
    canvas.height = h;
    ctx.drawImage(img, 0, 0, w, h);

    // Top 60% = sky region
    const skyH = Math.floor(h * 0.6);
    const imageData = ctx.getImageData(0, 0, w, skyH);
    const pixels = imageData.data;

    // Quantize colors (32-step buckets)
    const colorMap = {};
    for (let i = 0; i < pixels.length; i += 4) {
        const r = Math.round(pixels[i] / 32) * 32;
        const g = Math.round(pixels[i+1] / 32) * 32;
        const b = Math.round(pixels[i+2] / 32) * 32;
        const key = r + ',' + g + ',' + b;
        colorMap[key] = (colorMap[key] || 0) + 1;
    }

    // Sort by frequency
    const sorted = Object.entries(colorMap)
        .sort((a, b) => b[1] - a[1])
        .slice(0, nColors);

    const totalPixels = sorted.reduce((s, c) => s + c[1], 0);

    return sorted.map(([key, count]) => {
        const [r, g, b] = key.split(',').map(Number);
        const hex = '#' + [r, g, b].map(v => Math.min(255, v).toString(16).padStart(2, '0')).join('');

        // RGB → HSV conversion
        const rf = r / 255, gf = g / 255, bf = b / 255;
        const mx = Math.max(rf, gf, bf), mn = Math.min(rf, gf, bf);
        const d = mx - mn;
        let h = 0, s = mx === 0 ? 0 : d / mx, v = mx;
        if (d !== 0) {
            if (mx === rf) h = ((gf - bf) / d) % 6;
            else if (mx === gf) h = (bf - rf) / d + 2;
            else h = (rf - gf) / d + 4;
            h = Math.round(h * 30);
            if (h < 0) h += 180;
        }

        return {
            hex: hex,
            rgb: [r, g, b],
            hsv: [h, Math.round(s * 255), Math.round(v * 255)],
            percentage: Math.round(count / totalPixels * 1000) / 10,
        };
    });
}

// ──────────────────────────────────────
// Mood classification
// ──────────────────────────────────────
function classifyMood(colors) {
    let avgH = 0, avgS = 0, avgV = 0;
    colors.forEach(c => {
        avgH += c.hsv[0];
        avgS += c.hsv[1];
        avgV += c.hsv[2];
    });
    avgH /= colors.length;
    avgS /= colors.length;
    avgV /= colors.length;

    // Warmth: red/orange/yellow hues contribute to warmth score
    const warmPct = colors
        .filter(c => c.hsv[0] < 30 || c.hsv[0] > 150)
        .reduce((s, c) => s + c.percentage, 0);

    let mood, desc, emoji;
    if (avgV < 80) {
        mood = 'deep_night';
        desc = '아직 깊은 밤, 새벽을 기다리는 고요한 어둠';
        emoji = '🌑';
    } else if (avgV < 130 && avgS < 80) {
        mood = 'blue_hour';
        desc = '파란 시간, 밤과 낮 사이의 몽환적인 순간';
        emoji = '💙';
    } else if (avgH < 15 || avgH > 160) {
        mood = 'burning_dawn';
        desc = '타오르는 새벽, 하늘을 물들이는 붉은 빛';
        emoji = '🔥';
    } else if (avgH >= 15 && avgH < 30) {
        mood = 'golden_dawn';
        desc = '황금빛 새벽, 따스한 빛이 번져오는 순간';
        emoji = '🌟';
    } else if (avgH >= 80 && avgH < 130) {
        mood = 'cool_dawn';
        desc = '차가운 새벽, 맑고 푸른 여명';
        emoji = '🧊';
    } else if (avgH >= 130 && avgH < 160) {
        mood = 'purple_dawn';
        desc = '보랏빛 새벽, 신비로운 여명의 시작';
        emoji = '💜';
    } else {
        mood = 'pastel_dawn';
        desc = '파스텔 새벽, 부드러운 색들이 어우러진 하늘';
        emoji = '🎨';
    }

    return {
        mood: mood,
        description: desc,
        emoji: emoji,
        warmth: Math.round(warmPct * 10) / 10,
        brightness: Math.round(avgV * 10) / 10,
    };
}

// ──────────────────────────────────────
// Photo upload & analysis
// ──────────────────────────────────────
const uploadArea = document.getElementById('upload-area');
const fileInput = document.getElementById('file-input');

// Drag and drop
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('drag-over');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('drag-over');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('drag-over');
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith('image/')) {
        analyzeUpload(file);
    }
});

// File input
fileInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) analyzeUpload(file);
});

function analyzeUpload(file) {
    const reader = new FileReader();
    reader.onload = (e) => {
        const img = new Image();
        img.onload = () => {
            const colors = extractColors(img);
            const mood = classifyMood(colors);
            showUploadResult(e.target.result, colors, mood);
        };
        img.src = e.target.result;
    };
    reader.readAsDataURL(file);
}

function showUploadResult(imgSrc, colors, mood) {
    document.getElementById('upload-area').style.display = 'none';
    const resultEl = document.getElementById('upload-result');
    resultEl.style.display = 'block';

    document.getElementById('upload-preview').src = imgSrc;

    // Palette bar
    const paletteEl = document.getElementById('upload-palette');
    paletteEl.innerHTML = colors.map(c =>
        '<div class="swatch" style="background:' + c.hex + ';flex-grow:' + c.percentage + '" title="' + c.hex + ' (' + c.percentage + '%)">' +
        '<span class="swatch-label">' + c.hex + '</span></div>'
    ).join('');

    // Mood info
    const infoEl = document.getElementById('upload-info');
    infoEl.innerHTML =
        '<span class="upload-mood-emoji">' + mood.emoji + '</span>' +
        '<p class="upload-mood-text">' + mood.description + '</p>' +
        '<div class="card-meta">' +
        '<span class="meta-item">따뜻함 ' + mood.warmth + '%</span>' +
        '<span class="meta-item">밝기 ' + mood.brightness + '</span>' +
        '</div>';
}

function resetUpload() {
    document.getElementById('upload-area').style.display = '';
    document.getElementById('upload-result').style.display = 'none';
    fileInput.value = '';
}

// ──────────────────────────────────────
// Mood filter
// ──────────────────────────────────────
let activeFilter = null;

function filterMood(mood) {
    const cards = document.querySelectorAll('.card');
    const stats = document.querySelectorAll('.stat-item');

    if (activeFilter === mood) {
        activeFilter = null;
        cards.forEach(c => c.classList.remove('hidden'));
        stats.forEach(s => s.classList.remove('active'));
        return;
    }

    activeFilter = mood;
    cards.forEach(c => {
        if (c.dataset.mood === mood) {
            c.classList.remove('hidden');
        } else {
            c.classList.add('hidden');
        }
    });
    stats.forEach(s => {
        s.classList.toggle('active', s.dataset.mood === mood);
    });
}