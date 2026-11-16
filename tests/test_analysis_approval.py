import json,tempfile,unittest
from pathlib import Path
from clinic_localizer.validation_service import Application
from clinic_localizer.cohorts.protocol import ContractError

class AnalysisApprovalTests(unittest.TestCase):
    def test_valid_analysis_scope_sign_and_policy_mismatch(self):
        with tempfile.TemporaryDirectory() as d:
            a=Application(Path(d)/'db');f=json.loads(Path('fixtures/acceptance.json').read_text());run=a.run_fixture(f,Path(d)/'out')
            r=a.repository.list_records()[0];a.repository.register_scope('scope',str(r.payload['population_group']),'validation');a.repository.link_cohort('scope',r.record_id)
            result=a.analysis_approval.issue('issue','scope',run['run_id'],{})
            self.assertEqual(Application(Path(d)/'db').analysis_approval.issue('issue','scope',run['run_id'],{}),result)
            with self.assertRaises(ContractError):a.analysis_approval.issue('new','scope',run['run_id'],{'approve_threshold':.9})
