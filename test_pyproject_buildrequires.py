from pathlib import Path
import io

import pytest
import yaml

from pyproject_buildrequires import generate_requires

testcases = {}
with Path(__file__).parent.joinpath('testcases.yaml').open() as f:
    testcases = yaml.safe_load(f)


@pytest.mark.parametrize('case_name', testcases)
def test_data(case_name, capsys, tmp_path, monkeypatch):
    case = testcases[case_name]

    cwd = tmp_path.joinpath('cwd')
    cwd.mkdir()
    monkeypatch.chdir(cwd)

    if 'pyproject.toml' in case:
        cwd.joinpath('pyproject.toml').write_text(case['pyproject.toml'])

    if 'setup.py' in case:
        cwd.joinpath('setup.py').write_text(case['setup.py'])

    try:
        generate_requires(
            case['freeze_output'],
        )
    except SystemExit as e:
        assert e.code == case['result']
    except Exception as e:
        assert type(e).__name__ == case['except']
    else:
        assert 0 == case['result']

        captured = capsys.readouterr()
        assert captured.out == case['expected']
