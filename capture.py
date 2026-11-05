"""Bounded local X11 capture. No network, audio, shell, or automatic upload."""
import fcntl,json,math,os,re,shutil,subprocess,tempfile
from pathlib import Path
BUDGET=250*1024*1024
class CaptureError(RuntimeError): pass

def duration_seconds(value=5):
    if type(value) is not int or not 1<=value<=15:
        raise CaptureError('Dauer muss eine ganze Zahl von 1 bis 15 Sekunden sein.')
    return value

def run(args,timeout):
    try:
        return subprocess.run(args,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE,timeout=timeout,check=True).stdout
    except (OSError,subprocess.SubprocessError) as exc:
        raise CaptureError('Aufnahme/Konvertierung fehlgeschlagen; Host und Werkzeuge prüfen.') from exc

def screen(display):
    if not re.fullmatch(r':\d+(?:\.\d+)?',display):
        raise CaptureError('Nur eine lokale X11-Anzeige ist erlaubt.')
    raw=run(['xdpyinfo','-display',display],5).decode(errors='replace')
    match=re.search(r'dimensions:\s+(\d+)x(\d+)\s+pixels',raw)
    if not match:raise CaptureError('X11-Bildschirmgröße nicht ermittelt.')
    w,h=map(int,match.groups())
    if not (2<=w<=3840 and 2<=h<=2160):raise CaptureError('Bildschirmgröße außerhalb des Limits.')
    return f'{w}x{h}'

def probe(path):
    try:
        info=json.loads(run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(path)],5))
        streams=[s for s in info['streams'] if s.get('codec_type')=='video']
        seconds=float(info['format']['duration'])
        frames=int(streams[0].get('nb_frames','0'))
        if not streams or not math.isfinite(seconds) or seconds<=0 or frames<2:raise ValueError()
        return seconds
    except (ValueError,KeyError,IndexError,TypeError) as exc:
        raise CaptureError('Ungültiges Aufnahmeergebnis.') from exc

def _record(directory,duration,input_args):
    """Internal input override is for tests; never exposed as command argument."""
    video=directory/'capture.mp4';gif=directory/'capture.gif'
    run(['ffmpeg','-nostdin','-y','-v','error',*input_args,'-t',str(duration),'-an',
         '-vf',"scale=w='trunc(min(1280,iw)/2)*2':h=-2:force_divisible_by=2",'-r','10',
         '-c:v','libx264','-threads','2','-preset','veryfast','-crf','25','-pix_fmt','yuv420p',
         '-fs',str(64*1024*1024),'-movflags','+faststart',str(video)],duration+20)
    run(['ffmpeg','-nostdin','-y','-v','error','-i',str(video),'-t',str(duration),
         '-filter_complex',"fps=8,scale=w='min(800,iw)':h=-1,split[a][b];[a]palettegen=stats_mode=diff[p];[b][p]paletteuse=dither=bayer",
         '-filter_complex_threads','1','-threads','2','-loop','0','-fs',str(64*1024*1024),str(gif)],30)
    for file in [video,gif]:
        file.chmod(0o600)
        actual=probe(file)
        if abs(actual-duration)>.35:raise CaptureError('Aufnahme unvollständig oder Dauerabweichung.')
    return {'duration':duration,'video':str(video),'gif':str(gif)}

def capture(duration=5,output=None,display=None):
    duration=duration_seconds(duration)
    display=display or os.environ.get('DISPLAY','')
    if not display:raise CaptureError('Keine lokale X11-Anzeige konfiguriert.')
    dimensions=screen(display)
    root=Path(output).expanduser() if output else Path.home()/'.local/share/pygdo-snapvid'
    root.mkdir(mode=0o700,parents=True,exist_ok=True)
    if root.is_symlink() or root.stat().st_uid!=os.getuid():raise CaptureError('Unzulässiges Ausgabeverzeichnis.')
    if root.stat().st_mode & 0o077:raise CaptureError('Ausgabeverzeichnis muss privat sein (0700).')
    fd=os.open(root/'.capture.lock',os.O_CREAT|os.O_RDWR|os.O_NOFOLLOW,0o600)
    with os.fdopen(fd,'a') as lock:
        try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError as exc:raise CaptureError('Eine Aufnahme läuft bereits.') from exc
        used=sum(p.stat().st_size for p in root.rglob('*') if p.is_file() and not p.is_symlink())
        if used+128*1024*1024>BUDGET or shutil.disk_usage(root).free<256*1024*1024:
            raise CaptureError('Speicherlimit erreicht; alte Aufnahmen gezielt prüfen.')
        folder=Path(tempfile.mkdtemp(prefix='snapvid-',dir=root))
        try:
            return _record(folder,duration,['-f','x11grab','-framerate','10','-video_size',dimensions,'-i',display])
        except BaseException:
            # Only artifacts created by this failed attempt, never older recordings.
            shutil.rmtree(folder)
            raise
