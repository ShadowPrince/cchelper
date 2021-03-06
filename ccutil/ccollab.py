import subprocess
import os
import re
import pipes
from xml.etree import ElementTree

import utils
from utils import verbose

TEE_FILE = "/tmp/cc_output"

def review_url(id):
    return "https://laxm1bapps565.ent.core.medtronic.com/ui#review:id={}".format(id)

def call_ccollab(*args):
    args = ["ccollab", "--no-browser", "--non-interactive"] + list(args)
    verbose("sh > {}", " ".join(args))
    if not utils.args.dry_run:
        output = subprocess.check_output(args)
    else:
        output = ""

    return output

def create_new_review(commits):
    lines = call_ccollab("addchangelist", "new", *commits).splitlines()
    if utils.args.dry_run:
        return "DRY_RUN"

    try:
        review_id = int(re.findall(r"\w+ (\d+).", lines[-1])[0])
    except Exception:
        raise Exception("Failed to get review id!")

    return review_id

def append_to_review(id, commits):
    call_ccollab("addchangelist", id, *commits)

def append_files_to_review(id, files):
    call_ccollab("addchanges", id, *files)

def update_review(id, title, group, overview):
    args = ["admin", "review", "edit", id,
            "--title", title,
            "--custom-field", "Feature=Unknown",
            "--custom-field", "Overview={}".format(overview), ]
    if group:
        args += ["--group", group, ]

    call_ccollab(*args)

def add_participant(id, username, role):
    call_ccollab("admin", "review", "participant", "assign", id, username, role)

def review_files_changed(reviewid):
    output = call_ccollab("admin", "review-xml", str(reviewid))

    xml = ElementTree.fromstring(output)

    result = {}
    for artifact in xml.iter("artifact"):
        result[artifact.find("path").text] = artifact.find("scmVersion").text

    return result

