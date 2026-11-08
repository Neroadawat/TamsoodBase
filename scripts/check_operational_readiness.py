"""Read-only operational readiness; nonzero exit means attention, never auto-restart."""
import json,urllib.request,urllib.error
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def backup_age(record,now):
    value=record.get('created_at','')
    try:created=datetime.strptime(value,'%Y%m%dT%H%M%SZ').replace(tzinfo=timezone.utc)
    except ValueError:return None
    hours=(now-created).total_seconds()/3600
    return hours if hours>=0 else None

def check():
    now=datetime.now(timezone.utc);checks=[]
    for path in ['/api/readyz','/api/release']:
        try:
            with urllib.request.urlopen('https://tamsoodbase.vercel.app'+path,timeout=35) as response:
                body=json.load(response);checks.append({'path':path,'http':response.status,'passed':response.status==200 and (body.get('ready') is True if path.endswith('readyz') else bool(body.get('model_release_id')))})
        except (OSError,ValueError) as error:checks.append({'path':path,'passed':False,'error_type':type(error).__name__})
    backup=json.loads((ROOT/'evidence/mysql-backup-latest.json').read_text(encoding='utf-8'));hours=backup_age(backup,now)
    report={'scope':'PUBLIC_HEALTH_AND_RECORDED_BACKUP_FRESHNESS_NOT_NEW_RESTORE','checked_at_utc':now.isoformat(),'http_checks':checks,'http_healthy':all(c['passed'] for c in checks),'recorded_backup_age_hours':round(hours,1) if hours is not None else None,'daily_backup_target_met':hours is not None and hours<=24,'backup_status':'STALE_OR_NOT_REVERIFIED' if hours is None or hours>24 else 'RECORDED_WITHIN_TARGET','new_s3_read_or_restore_performed':False,'backend_endpoint':'QUICK_TUNNEL_TEMPORARY_LAST_CONFIGURED_STATE','stable_endpoint_verified':False,'production_mutated':False,'automation_created':False}
    report['operationally_complete']=report['http_healthy'] and report['daily_backup_target_met'] and report['stable_endpoint_verified']
    (ROOT/'evidence/operational-readiness-2026-11-06.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':
    result=check();print(json.dumps(result));raise SystemExit(0 if result['operationally_complete'] else 2)
