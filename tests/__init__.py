import sys
from pathlib import Path

sys.path.append(str(Path('business_logic/train.py').parent.parent))
sys.path.append(str(Path('business_logic/retrieve.py').parent.parent))
sys.path.append(str(Path('business_logic/mocked_issues.py').parent.parent))
