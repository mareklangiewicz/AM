"""Prepare payloads only; never execute an installer or updater."""
from pathlib import Path
import hashlib,json,subprocess
repo=Path(__file__).resolve().parents[4]
out=Path(__file__).resolve().parent
source='https://raw.githubusercontent.com/mareklangiewicz/AM/main-marek'
recipe=(repo/'programs/x86_64/obsidian').read_text()
body=recipe.split("cat >> ./AM-updater << 'EOF'\n",1)[1].split('\nEOF\n',1)[0]+'\n'
# Match current install.am's literal default substitution for this safe source.
body=body.replace('AMREPO=${AMREPO-}', 'AMREPO=${AMREPO-"'+source+'"}')
(out/'AM-updater').write_text(body)
(out/'catalog.am').write_bytes((repo/'modules/catalog.am').read_bytes())
for name in ('APP-MANAGER','install.am'):
 (out/name).write_bytes((repo/('APP-MANAGER' if name=='APP-MANAGER' else 'modules/install.am')).read_bytes())
for name in ('AM-updater','catalog.am'):
 subprocess.run(['sh','-n',str(out/name)],check=True)
for name in ('APP-MANAGER','install.am'):
 subprocess.run(['bash','-n',str(out/name)],check=True)
files={name:{'bytes':len((out/name).read_bytes()),'sha256':hashlib.sha256((out/name).read_bytes()).hexdigest()} for name in ('AM-updater','catalog.am','APP-MANAGER','install.am')}
(out/'manifest.json').write_text(json.dumps({'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip(),'AMREPO':source,'files':files},indent=2)+'\n')
