/**
 * SIDEQUEST SPIN WHEEL
 * Direct Redirect Flow using existing api.js
 */

const CONFIG = {
    SEGMENTS: [
        { label: 'MOVIES', icon: '🎬', color: '#FF2D4A', category: 'movies' },
        { label: 'TV SHOWS', icon: '📺', color: '#2DA4FF', category: 'tv' },
        { label: 'ANIME', icon: '🌸', color: '#FF2DDE', category: 'anime' }
    ],
    MIN_SPINS: 4000, 
    SPINS: 5 
};

// State
let isSpinning = false;
let currentRotation = 0;

// DOM Elements
const canvas = document.getElementById('wheelCanvas');
const ctx = canvas.getContext('2d');
const spinBtn = document.getElementById('spinBtn');
const status = document.getElementById('status');

/**
 * INITIALIZATION
 */
function init() {
    drawWheel();
    window.addEventListener('resize', handleResize);
    handleResize();

    spinBtn.addEventListener('click', startSpin);
}

function handleResize() {
    const size = Math.min(window.innerWidth - 60, 500);
    canvas.width = size;
    canvas.height = size;
    drawWheel();
}

/**
 * WHEEL DRAWING
 */
function drawWheel() {
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    const radius = centerX - 10;
    const step = (Math.PI * 2) / CONFIG.SEGMENTS.length;

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    ctx.save();
    ctx.translate(centerX, centerY);
    ctx.rotate(currentRotation);

    CONFIG.SEGMENTS.forEach((seg, i) => {
        const startAngle = i * step;
        const endAngle = (i + 1) * step;

        ctx.beginPath();
        ctx.moveTo(0, 0);
        ctx.arc(0, 0, radius, startAngle, endAngle);
        ctx.fillStyle = seg.color;
        ctx.fill();
        ctx.strokeStyle = '#00000033';
        ctx.lineWidth = 2;
        ctx.stroke();

        ctx.save();
        const labelAngle = startAngle + step / 2;
        ctx.rotate(labelAngle);
        ctx.textAlign = 'right';
        ctx.fillStyle = '#fff';
        ctx.font = `bold ${radius * 0.12}px Orbitron`;
        ctx.fillText(`${seg.icon} ${seg.label}`, radius - 35, 10);
        ctx.restore();
    });

    ctx.restore();
}

/**
 * SPIN LOGIC
 */
async function startSpin() {
    if (isSpinning) return;
    
    isSpinning = true;
    spinBtn.disabled = true;
    status.innerText = "The wheel is deciding...";

    const segmentCount = CONFIG.SEGMENTS.length;
    const targetIdx = Math.floor(Math.random() * segmentCount);
    const step = (Math.PI * 2) / segmentCount;
    const targetAngle = (Math.PI * 2) * CONFIG.SPINS - (targetIdx * step) - (step / 2) - (Math.PI / 2);

    const startTime = performance.now();
    const startAngle = currentRotation;

    function animate(time) {
        const elapsed = time - startTime;
        const progress = Math.min(elapsed / CONFIG.MIN_SPINS, 1);
        const ease = 1 - Math.pow(1 - progress, 4);
        
        const lastRotation = currentRotation;
        currentRotation = startAngle + (targetAngle - startAngle) * ease;
        
        if (Math.floor(currentRotation / step) !== Math.floor(lastRotation / step)) {
            playTick();
        }

        drawWheel();

        if (progress < 1) {
            requestAnimationFrame(animate);
        } else {
            isSpinning = false;
            triggerConfetti();
            const winningSegment = CONFIG.SEGMENTS[targetIdx];
            handleSpinResult(winningSegment.category);
        }
    }

    requestAnimationFrame(animate);
}

/**
 * REDIRECT LOGIC
 */
async function handleSpinResult(category) {
    const status = document.getElementById("status");
    const spinBtn = document.getElementById("spinBtn");

    try {
        status.innerText = "Finding something for you...";
        spinBtn.disabled = true;

        console.log("Category sent:", category);

        // ✅ Robust check: use getSpinRecommendation OR fallback to getTrending
        let data = await api.getSpinRecommendation(category);
        if (!data) {
            console.log("Falling back to getTrending...");
            const trendingData = await api.getTrending(category.replace('movies', 'movie'));
            if (trendingData && trendingData.results) {
                // Pick random 1 from trending results
                data = trendingData.results[Math.floor(Math.random() * trendingData.results.length)];
            }
        }

        console.log("API Response:", data);

        if (!data) {
            throw new Error("No data returned from API");
        }

        // ✅ If API returns array instead of object, pick random item
        const item = Array.isArray(data)
            ? data[Math.floor(Math.random() * data.length)]
            : data;

        if (!item.id) {
            throw new Error("Missing ID in response");
        }

        // ✅ detect type properly
        const type = item.media_type ||
            (category.includes('tv') ? 'tv' : category.includes('anime') ? 'tv' : 'movie');

        console.log(`Redirecting to: details.html?type=${type}&id=${item.id}`);

        // ✅ Redirect like Surprise Me (using relative path for standalone page)
        window.location.href = `../details.html?type=${type}&id=${item.id}`;

    } catch (err) {
        console.error("Spin Error:", err);
        status.innerText = "API Error. Try spinning again!";
        spinBtn.disabled = false;
    }
}

/**
 * EFFECTS
 */
function playTick() {
    const audio = document.getElementById('tickSound');
    if (audio) {
        audio.currentTime = 0;
        audio.volume = 0.2;
        audio.play().catch(() => {});
    }
}

function triggerConfetti() {
    const c = document.getElementById('confettiCanvas');
    if (!c) return;
    c.width = window.innerWidth;
    c.height = window.innerHeight;
    const ctx = c.getContext('2d');
    const pieces = [];
    const colors = ['#FF2D4A', '#2DA4FF', '#FF2DDE', '#FFD700'];

    for (let i = 0; i < 60; i++) {
        pieces.push({
            x: Math.random() * c.width,
            y: Math.random() * c.height - c.height,
            r: Math.random() * 8 + 2,
            d: Math.random() * 10 + 2,
            color: colors[Math.floor(Math.random() * colors.length)]
        });
    }

    function draw() {
        ctx.clearRect(0, 0, c.width, c.height);
        pieces.forEach(p => {
            p.y += p.d;
            ctx.beginPath();
            ctx.fillStyle = p.color;
            ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
            ctx.fill();
        });

        if (pieces.some(p => p.y < c.height)) {
            requestAnimationFrame(draw);
        }
    }
    draw();
}

init();
