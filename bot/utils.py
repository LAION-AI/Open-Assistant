# -*- coding: utf-8 -*-
import subprocess
from datetime import datetime

import pytz


def get_git_head_hash():
    # get current git hash
    x = subprocess.run(["git", "rev-parse", "HEAD"], stdout=subprocess.PIPE, universal_newlines=True)
    if x.returncode == 0:
        return x.stdout.replace("\n", "")
    return None


def utcnow() -> datetime:
    return datetime.now(pytz.UTC)
