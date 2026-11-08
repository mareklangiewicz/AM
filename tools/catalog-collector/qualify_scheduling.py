"""Offline 5,000-source scheduling check using the actual collector and inert replies."""
import argparse,json,contextlib,io,time
from datetime import datetime,timedelta,timezone
from pathlib import Path
from unittest.mock import patch
import host_catalog as host
from test_batch_collection import BatchCollection
parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
start=time.monotonic(); helper=BatchCollection();rows,sources=helper.configuration(5000)
previous=helper.previous(5000); results=[];profile=dict(source_cap=5000,request_cap=750,total_cap=536870912,seconds_cap=900,reserve=100,response_cap=16777216)
for hour in range(12):
 now=(datetime(2026,11,8,tzinfo=timezone.utc)+timedelta(hours=hour)).strftime('%Y-%m-%dT%H:%M:%SZ');metrics={}
 def read(rid,evidence,allowance,*,rate=None):return b'[]',now
 with patch.object(host,'configuration',return_value=(rows,sources)),patch.object(host,'_response',side_effect=read),patch.object(host,'utc',return_value=now),contextlib.redirect_stdout(io.StringIO()):
  (apps,changed),report=host.collect('a'*40,previous,batch_size=500,metrics=metrics,incremental=True,profile=profile)
 previous.update(changed)
 observed=sum(obj.get('last_success',{}).get('completed_at','')>='2026-11-08' for obj in previous.values())
 results.append(dict(hour=hour,selected=metrics['selected_sources'],attempted=len(report),fresh_sources=observed,first_id=metrics['selected_repository_ids'][0],last_id=metrics['selected_repository_ids'][-1]))
 assert len(report)==500
assert results[9]['fresh_sources']==5000
out=dict(synthetic=True,live_acquisition=False,count=5000,batch_size=500,request_cap=750,ordinary_hourly_allowance=1000,rate_reserve=100,empty_response_bytes=2,seconds=time.monotonic()-start,results=results,limits='Actual oldest-attempt scheduler with mocked successful empty upstream responses; no throughput/quota reliability claim. Population failures and dropped schedules remain exceptions. Historical saved transfer costs are separate.')
args.output.write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
