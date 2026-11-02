import os, subprocess, threading, time, json, hashlib, re
samples=[]
stop=threading.Event()
def monitor():
 while not stop.is_set():
  samples.append((time.monotonic_ns(),time.time_ns()))
  stop.wait(.01)
t=threading.Thread(target=monitor);t.start()
env={k:v for k,v in os.environ.items() if k!='AM_CATALOG_SESSION'}
env['AMREPO']='https://raw.githubusercontent.com/mareklangiewicz/AM/main-marek'
try:
 r=subprocess.run(['sh','-x','/opt/am/modules/catalog.am','https://api.github.com/repos/obsidianmd/obsidian-releases/releases'],env=env,capture_output=True,timeout=100)
finally:
 stop.set();t.join()
steps=[{'monotonic_delta_ns':b[0]-a[0],'wall_delta_ns':b[1]-a[1]} for a,b in zip(samples,samples[1:]) if b[1]<a[1]]
# Never retain the release body or its asset URLs. Numeric trace fields suffice.
trace=[line for line in r.stderr.decode().splitlines() if re.match(r'^\+ (start=|last=|now=|result=|pin=|row=|actual=|fail )',line) or line.startswith('AM catalog:')]
print(json.dumps({'returncode':r.returncode,'body_bytes':len(r.stdout),'body_sha256':hashlib.sha256(r.stdout).hexdigest(),'samples':len(samples),'elapsed_monotonic_seconds':(samples[-1][0]-samples[0][0])/1e9,'backward_steps':steps,'reader_trace':trace},indent=2))
