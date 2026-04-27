const playlist = document.getElementById('playlist');
const audio = document.getElementById('audio');
const cover = document.getElementById('cover');
const nowTitle = document.getElementById('now-title');
const nowArtist = document.getElementById('now-artist');
const search = document.getElementById('search');

const prevBtn = document.getElementById('prev');
const nextBtn = document.getElementById('next');
const playBtn = document.getElementById('playpause');
const loopBtn = document.getElementById('loop');
const progress = document.getElementById('progress');

let tracks = [];
let current = 0;
let loop = false;

fetch('music.json')
.then(r => r.json())
.then(data => {
    tracks = data;
    render(data);
});

function render(list){
    playlist.innerHTML = '';

    list.forEach(track => {
        const div = document.createElement('div');
        div.className = 'track';

        div.innerHTML = `
            <img src="${track.cover}">
            <div>
                <strong>${track.title}</strong><br>
                <small>${track.artist}</small>
            </div>
        `;

        div.onclick = () => {
            current = tracks.indexOf(track);
            play(track);
        };

        playlist.appendChild(div);
    });
}

function play(track){
    audio.src = track.file;
    cover.src = track.cover;
    nowTitle.textContent = track.title;
    nowArtist.textContent = track.artist;
    audio.play();
    playBtn.textContent = '⏸';
}

function playIndex(i){
    if(i < 0) i = tracks.length - 1;
    if(i >= tracks.length) i = 0;

    current = i;
    play(tracks[current]);
}

playBtn.onclick = () => {
    if(audio.src === ''){
        playIndex(0);
        return;
    }

    if(audio.paused){
        audio.play();
        playBtn.textContent = '⏸';
    }else{
        audio.pause();
        playBtn.textContent = '▶';
    }
};

nextBtn.onclick = () => playIndex(current + 1);
prevBtn.onclick = () => playIndex(current - 1);

loopBtn.onclick = () => {
    loop = !loop;
    audio.loop = loop;
    loopBtn.classList.toggle('active');
};

audio.onended = () => {
    if(!loop){
        playIndex(current + 1);
    }
};

audio.ontimeupdate = () => {
    if(audio.duration){
        progress.value = (audio.currentTime / audio.duration) * 100;
    }
};

progress.oninput = () => {
    if(audio.duration){
        audio.currentTime = (progress.value / 100) * audio.duration;
    }
};

search.oninput = () => {
    const v = search.value.toLowerCase();

    render(
        tracks.filter(t =>
            t.title.toLowerCase().includes(v) ||
            t.artist.toLowerCase().includes(v)
        )
    );
};