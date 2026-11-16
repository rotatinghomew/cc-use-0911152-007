"""用途签发核对审查人选择的分析及政策身份。"""
import json
from clinic_localizer.cohorts.protocol import ContractError,stable_hash
from clinic_localizer.governance.use_scope import issue_scope

class AnalysisApproval:
    def __init__(self,repository):
        self.repository=repository
        with repository.connect() as c:c.execute("CREATE TABLE IF NOT EXISTS analysis_issuances(issue_id TEXT PRIMARY KEY,run_id TEXT NOT NULL,policy_hash TEXT NOT NULL)")
    def issue(self,issue_id,scope_id,run_id,policy):
        with self.repository.transaction() as c:
            run=c.execute("SELECT status,result_json FROM runs WHERE run_id=?",(run_id,)).fetchone()
            if run is None or run['status']!='finished':raise ContractError("分析尚未完成")
            result=json.loads(run['result_json'])
            if 'analysis_policy' not in result or result['analysis_policy']!=dict(policy):raise ContractError("分析策略与待签发意见不符")
            ids={r['record_id'] for r in c.execute("SELECT cohort_id AS record_id FROM scope_evidence WHERE scope_id=?",(scope_id,))}
            evidence=result.get('analysis_evidence',{})
            if not ids or not ids<=set(evidence):raise ContractError("用途队列不属于该分析")
            for rid in ids:
                current=c.execute("SELECT fingerprint FROM records WHERE record_id=?",(rid,)).fetchone()
                if current is None or current[0]!=evidence[rid]:raise ContractError("分析病例已经更正")
            old=c.execute("SELECT * FROM analysis_issuances WHERE issue_id=?",(issue_id,)).fetchone()
            identity=(run_id,stable_hash(dict(policy)))
            if old and (old['run_id'],old['policy_hash'])!=identity:raise ContractError("签发分析依据不可覆盖")
            value=issue_scope(c,issue_id,scope_id)
            c.execute("INSERT OR IGNORE INTO analysis_issuances VALUES(?,?,?)",(issue_id,*identity))
            return value
