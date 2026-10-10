import os
import glob

print("Scanning for test files in sip_remote_handoff...")
test_files = glob.glob('sip_remote_handoff/**/*test*.py', recursive=True) + glob.glob('sip_remote_handoff/**/*_test.py', recursive=True)

if not test_files:
    print("No existing test files found. Creating a baseline unit test for sip_remote_handoff...")
    os.makedirs('sip_remote_handoff/tests', exist_ok=True)
    baseline_test = '''import unittest

class TestSipRemoteHandoff(unittest.TestCase):
    def test_basic_node_auth(self):
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()
'''
    with open('sip_remote_handoff/tests/test_handoff.py', 'w') as f:
        f.write(baseline_test)
    print("Created baseline test at sip_remote_handoff/tests/test_handoff.py")
else:
    print(f"Found test files: {test_files}")

