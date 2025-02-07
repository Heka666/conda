#!/usr/bin/env bash

set -o errtrace -o pipefail -o errexit

TEST_SPLITS="${TEST_SPLITS:-1}"
TEST_GROUP="${TEST_GROUP:-1}"

eval "$(sudo python -m conda init bash --dev)"
conda-build tests/test-recipes/activate_deactivate_package
pytest -m "integration" -v --splits ${TEST_SPLITS} --group=${TEST_GROUP}
python -m conda.common.io
